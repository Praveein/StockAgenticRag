from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config.llm_config import get_llm_singleton

llm = get_llm_singleton(temperature=0)

system = """You are a helpful assistant that generates web search queries.
Given a user question and a stock ticker, generate 3 distinct web search queries to find comprehensive information.
Focus on:
1. Recent news and events.
2. Financial performance and earnings.
3. Market sentiment and analyst ratings.

Return the queries separated by newlines. Do not number them."""

query_generation_prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "Question: {question}\nTicker: {ticker}")
])

search_query_generator = query_generation_prompt | llm | StrOutputParser()
