from dotenv import load_dotenv
from langgraph.graph import StateGraph,END
from rag_graphs.stock_data_rag_graph.graph.constants import GENERATE_SQL, EXECUTE_SQL, GENERATE_RESULTS
from rag_graphs.stock_data_rag_graph.graph.state import GraphState
from rag_graphs.stock_data_rag_graph.graph.nodes.generate_sql import generate_sql
from rag_graphs.stock_data_rag_graph.graph.nodes.sql_search import sql_fetch_query
from rag_graphs.stock_data_rag_graph.graph.nodes.generate import generate
from utils.logger import logger


load_dotenv()
from utils.langsmith_tracing import enable_langsmith_tracing
enable_langsmith_tracing("StocksInsights")


graph_builder  = StateGraph(state_schema=GraphState)

graph_builder.add_node(GENERATE_SQL, generate_sql)
graph_builder.add_node(EXECUTE_SQL, sql_fetch_query)
graph_builder.add_node(GENERATE_RESULTS, generate)

def decide_to_retry(state):
    """
    Determines whether to retry SQL generation based on errors.
    """
    error = state.get("error")
    tries = state.get("tries", 0)
    MAX_RETRIES = 3
    
    if error and tries < MAX_RETRIES:
        logger.info(f"---DECISION: RETRY SQL ({tries}/{MAX_RETRIES})---")
        return GENERATE_SQL
    else:
        logger.info("---DECISION: GENERATE RESULTS---")
        return GENERATE_RESULTS

graph_builder.set_entry_point(GENERATE_SQL)
graph_builder.add_edge(GENERATE_SQL, EXECUTE_SQL)
graph_builder.add_conditional_edges(
    EXECUTE_SQL,
    decide_to_retry,
    path_map={
        GENERATE_SQL: GENERATE_SQL,
        GENERATE_RESULTS: GENERATE_RESULTS
    }
)
graph_builder.add_edge(GENERATE_RESULTS, END)


app = graph_builder.compile()
app.get_graph().draw_mermaid_png(output_file_path="stock-data-rag-graph.png")