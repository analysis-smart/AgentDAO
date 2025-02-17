from typing import List
from fastapi import FastAPI, Depends
from pydantic import BaseModel
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
from langchain_core.messages import BaseMessage
from langchain.chat_models import ChatOpenAI
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
tools = [retriever_tool]

# 3. 创建代理人
prompt = hub.pull("hwchase17/openai-functions-agent")
llm = ChatOpenAI(api_key=API_KEY, base_url=BASE_URL, model=MODEL, temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True  # 添加错误处理
)

# 4. 定义输入输出模型
class Input(BaseModel):
    input: str
    chat_history: List[dict] = []

class Output(BaseModel):
    output: str

# 5. 创建 FastAPI 应用程序
app = FastAPI(
    title="LangChain服务器",
    version="1.0",
    description="使用LangChain的可运行接口的简单API服务器",
)

# 6. 手动定义路由
@app.post("/agent", response_model=Output)
async def run_agent(input_data: Input):
    try:
        # 将 chat_history 转换为 LangChain 的 BaseMessage 格式
        chat_history = [
            BaseMessage.from_dict(msg) for msg in input_data.chat_history
        ]
        
        # 调用 AgentExecutor 运行逻辑
        result = agent_executor.run(input=input_data.input, chat_history=chat_history)
        return {"output": result}
    except Exception as e:
        return {"output": f"Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)