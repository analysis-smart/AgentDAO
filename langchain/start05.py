"""
使用langServe进行服务
python3.11
pip install "langserve[all]"

替代方案对比建议
方案	核心能力	适用场景	开发复杂度
TRS海贝搜索	全文检索+向量检索，国产认证	企业级数据中台	中
星环科技解决方案	大数据集成与检索	多行业通用搜索	高
自研工具+国产LLM	高度定制化	特定业务需求	高
"""

#!/usr/bin/env python
from typing import List
 
from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.messages import BaseMessage
from langserve import add_routes
import os
 
API_KEY = os.getenv("API_KEY_TYQW")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-plus"
# 1. 加载检索器
loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter()
documents = text_splitter.split_documents(docs)
embeddings = DashScopeEmbeddings(dashscope_api_key=API_KEY)
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever()
 
# 2. 创建工具
retriever_tool = create_retriever_tool(
    retriever,
    "langsmith_search",
    "搜索与LangSmith相关的信息。有关LangSmith的任何问题，您必须使用此工具！",
)
# search = TavilySearchResults()
# tools = [retriever_tool, search]
tools = [retriever_tool]
 
# 3. 创建代理人
prompt = hub.pull("hwchase17/openai-functions-agent")
llm = ChatOpenAI(api_key=API_KEY,base_url=BASE_URL,model=MODEL, temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
 
 
# 4. 应用程序定义
app = FastAPI(
  title="LangChain服务器",
  version="1.0",
  description="使用LangChain的可运行接口的简单API服务器",
)
 
# 5. 添加链路由
# 我们需要添加这些输入/输出模式，因为当前的AgentExecutor缺乏模式。
 
class Input(BaseModel):
    input: str
    chat_history: List[BaseMessage] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "location"}},
    )
 
 
class Output(BaseModel):
    output: str
 
add_routes(
    app,
    agent_executor.with_types(input_type=Input, output_type=Output),
    path="/agent",
)
 
if __name__ == "__main__":
    import uvicorn
 
    uvicorn.run(app, host="localhost", port=8000)
