from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from config.llm_config import get_llm_singleton

load_dotenv()
llm = get_llm_singleton(temperature=0)

system = "You are a helpful assistant. Use the provided context (news documents) to answer the question concisely."
generation_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "Context: {context}\n\nQuestion: {question}")
])

generation_chain = generation_prompt | llm | StrOutputParser()
