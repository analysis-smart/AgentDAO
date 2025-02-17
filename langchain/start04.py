"""
代理人 - LLM决定要采取的步骤
1 确定代理有哪些工具的访问权限
"""
from langchain.tools.retriever import create_retriever_tool
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import WebBaseLoader
import os

API_KEY = os.getenv("API_KEY_TYQW")
loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide")
docs = loader.load()
embeddings = DashScopeEmbeddings(dashscope_api_key=API_KEY)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever(search_kwargs={"k": 2})

# 将检索器设置为一个工具
retriever_tool = create_retriever_tool(
    retriever,'langsmith_search',"搜索与LangSmith相关的信息。有关LangSmith的任何问题，您必须使用此工具！"
)
# 使用一个搜索工具
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent,AgentExecutor
from langchain_core.messages import HumanMessage,AIMessage
# search = TavilySearchResults()

# tools = [retriever_tool,search]
tools = [retriever_tool]

from langchain import hub

prompt = hub.pull("hwchase17/openai-functions-agent")
API_KEY = os.getenv("API_KEY_TYQW")
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
model = "qwen-plus"
llm = ChatOpenAI(api_key=API_KEY, base_url=base_url, model=model)
agent = create_openai_functions_agent(llm,tools,prompt)
# agent_executor = AgentExecutor(agent,tools,verbose=True)
# 使用工厂方法创建Executor
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True  # 添加错误处理
)
agent_executor.invoke({"input": "langsmith如何帮助测试？"})
agent_executor.invoke({"input": "旧金山的天气如何？"})
chat_history = [HumanMessage(content="LangSmith可以帮助测试我的LLM应用程序吗？"), AIMessage(content="可以！")]
agent_executor.invoke({
    "chat_history": chat_history,
    "input": "告诉我如何进行"
})