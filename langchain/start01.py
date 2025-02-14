# langchain文档 https://www.langchain.asia/get_started/quickstart
# 提示符、模型和输出解析器的基础知识
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import os
API_KEY = os.getenv("API_KEY_TYQW")
base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
model="deepseek-v3" # "qwen-plus" "deepseek-r1"

llm = ChatOpenAI(api_key=API_KEY,base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",model=model)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are world class technical documentation writer."),
    ("user", "{input}")
])
 
output_parser = StrOutputParser()

chain = prompt | llm | output_parser

inv = chain.invoke("你好")
print(111111,inv)