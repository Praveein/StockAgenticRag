from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from config.llm_config import get_llm_singleton
load_dotenv()

llm                 = get_llm_singleton(temperature=0)

system = """You are a helpful AI assistant which specializes in reading stock data provided in pandas.Dataframe format and answering relevant queries.
            Answer the question user asks directly and concisely.
            Consider the provided context to frame your answer.
            Do not add conversational filler or ask follow-up questions.
"""
generation_prompt   = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Stock Data: {context}\n\nUser question: {question}")
    ]
)

generation_chain    = generation_prompt | llm | StrOutputParser()
