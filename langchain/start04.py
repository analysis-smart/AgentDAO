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
