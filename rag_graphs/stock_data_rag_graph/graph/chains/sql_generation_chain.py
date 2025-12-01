from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
from utils.logger import logger
from config.llm_config import get_llm_singleton

load_dotenv()
llm = get_llm_singleton(temperature=0)

system = """
You are an AI assistant that converts natural language queries into PostgreSQL SQL queries.
Table: stock_data(id integer, ticker varchar, date date, open double precision, high double precision, low double precision, close double precision, volume bigint)
Rules:
- Use PostgreSQL syntax for dates. For last N days use: date >= CURRENT_DATE - INTERVAL '<N> days'.
- Do NOT use SQLite functions like date('now') or datetime('now').
- Quote identifiers with double quotes only if necessary; single quotes are for string literals.
- All tickers in the database end with '.NS'. If the user asks for a ticker (e.g. 'RELIANCE'), you MUST append '.NS' (e.g. 'RELIANCE.NS') in the SQL query.
- Return only the SQL query, no explanations.
"""

sql_generation_prompt   = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: {question}")
    ]
)
sql_generation_chain    = sql_generation_prompt | llm | StrOutputParser()

if __name__ == "__main__":
    question    = "Query the last 1 month of data for AAPL."

    res         = sql_generation_chain.invoke(input={
                "question": question,
    })

    logger.info(f"Generated SQL Query ={res}")
