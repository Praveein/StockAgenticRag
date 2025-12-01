# Code for retrieval node
from typing import Any, Dict
from rag_graphs.stock_data_rag_graph.graph.state import GraphState
from rag_graphs.stock_data_rag_graph.graph.chains.sql_generation_chain import sql_generation_chain
from utils.logger import logger
import re


def clean_sql_string(input_sql_query):
    input_sql_query = input_sql_query.replace('\n', ' ')

    # Extract the SQL query
    match = re.search(r"```sql\s+(.*?)\s+```", input_sql_query, re.DOTALL)
    if match:
        sql_query = match.group(1)
        return (sql_query)
    else:
        return input_sql_query


def normalize_sql(sql: str) -> str:
    """Fix common LLM typos and non-Postgres date functions."""
    s = sql
    # Table typo sstock_data -> stock_data
    s = re.sub(r"(?i)\bsstock_data\b", "stock_data", s)
    # SQLite-style date('now') -> CURRENT_DATE
    s = re.sub(r"(?i)date\('now'\)", "CURRENT_DATE", s)
    # date('now','-N days') -> CURRENT_DATE - INTERVAL 'N days'
    s = re.sub(r"(?i)date\('now','-(\d+)\s*days?'\)", r"CURRENT_DATE - INTERVAL '\1 days'", s)
    s = re.sub(r"(?i)datetime\('now','-(\d+)\s*days?'\)", r"CURRENT_DATE - INTERVAL '\1 days'", s)
    # Backticks to double quotes
    s = s.replace('`', '"')
    return s


def generate_sql(state:GraphState)->Dict[str, Any]:
    logger.info("---GENERATE SQL---")
    question    = state['question']
    generated_sql   = sql_generation_chain.invoke(question)
    clean_sql_query = clean_sql_string(generated_sql)
    normalized_sql  = normalize_sql(clean_sql_query)
    return {"sql_query": normalized_sql, "question": question}