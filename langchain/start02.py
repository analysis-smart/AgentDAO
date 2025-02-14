"""
使用 LangChain 和通义千问构建一个基于向量存储的  基本的检索链
"""
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain_core.documents import Document
import os

# 配置参数
model = "qwen-plus"
API_KEY = os.getenv("API_KEY_TYQW")
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 加载网页内容
loader = WebBaseLoader("https://docs.smith.langchain.com/user_guide")
try:
    docs = loader.load()
except Exception as e:
    print(f"Error loading web page: {e}")
    docs = []

# 配置嵌入模型
embeddings = DashScopeEmbeddings(dashscope_api_key=API_KEY)

# 分割文档并构建向量存储
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(docs)
vector = FAISS.from_documents(documents, embeddings)

# 初始化语言模型和提示模板
llm = ChatOpenAI(api_key=API_KEY, base_url=base_url, model=model)
prompt = ChatPromptTemplate.from_template(
    """Answer the following question based only on the provided context:

<context>
{context}
</context>

Question: {input}"""
)
document_chain = create_stuff_documents_chain(llm, prompt)

# 直接传递文档并生成回答
# document_chain.invoke({
#     "input":"how can langsmith help with testing?",
#     "context":[Document(page_content="langsmith can let you visualize test results")]
# })

# 使用检索器获取文档并传递给 LLM
retriever = vector.as_retriever(search_kwargs={"k": 2})  # 返回前 2 个最相似的文档
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# 提出问题并获取答案
question = "how can langsmith help with testing?"
try:
    response = retrieval_chain.invoke({"input": question})
    print(f"Answer: {response['answer']}")
except Exception as e:
    print(f"Error generating answer: {e}")