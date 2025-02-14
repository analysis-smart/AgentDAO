"""
对话检索链
1 检索方法需要考虑历史记录和最近的输入
2 最终的LLM链也需要包括整个历史记录
"""
# 更新检索器，接收最近输入和历史对话
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder,ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS

API_KEY = os.getenv("API_KEY_TYQW")
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
model = "qwen-plus"

prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name='chat_history'),
        ("user","{input}"),
        ("user","根据上面的对话，生成一个搜索查询来获取与对话相关的信息")
    ]
)
llm = ChatOpenAI(api_key=API_KEY, base_url=base_url, model=model)
loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide")
try:
    docs = loader.load()
except Exception as e:
    print(f"Error loading web page: {e}")
    docs = []
embeddings = DashScopeEmbeddings(dashscope_api_key=API_KEY)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)
retriever = vector.as_retriever(search_kwargs={"k": 2})
retriever_chain = create_history_aware_retriever(llm,retriever,prompt)

from langchain_core.messages import HumanMessage,AIMessage
chat_history = [HumanMessage(content="Can LangSmith help test my LLM applications?"), AIMessage(content="Yes!")]
# 结合历史记录的对话
retriever_chain.invoke({
    'chat_history':chat_history,
    'input':''
})
# 创建新的链，并回答问题
prompt = ChatPromptTemplate.from_messages([
    ("system", "根据下面的上下文回答用户的问题：\n\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
])
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

document_chain=create_stuff_documents_chain(llm,prompt)
retriever_chain = create_retrieval_chain(retriever_chain,document_chain)

chat_history = [HumanMessage(content="Can LangSmith help test my LLM applications?"), AIMessage(content="Yes!")]
retriever_chain.invoke({
    "chat_history": chat_history,
    "input": "Tell me how"
})