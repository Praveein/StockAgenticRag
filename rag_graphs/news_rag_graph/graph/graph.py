from dotenv import load_dotenv
from langgraph.graph import StateGraph,END
from rag_graphs.news_rag_graph.graph.constants import RETRIEVE_NEWS, GENERATE_RESULT, GRADE_DOCUMENT, WEB_SEARCH, HALLUCINATION_CHECK
from rag_graphs.news_rag_graph.graph.nodes import retrieve, generate, grade_documents, web_search, check_hallucination
from rag_graphs.news_rag_graph.graph.state import GraphState
from utils.logger import logger

load_dotenv()
from utils.langsmith_tracing import enable_langsmith_tracing
enable_langsmith_tracing("StocksInsights")

def decide_to_generate(state):
    logger.info("---ASSESS GRADED DOCUMENTS---")
    if state["web_search"]:
        logger.info("""---DECISION: NOT ALL DOCUMENTS ARE RELEVANT TO THE QUESTION, INCLUDE WEB SEARCH---""")
        return WEB_SEARCH
    else:
        logger.info("---DECISION: GENERATE---")
        return GENERATE_RESULT

graph_builder  = StateGraph(state_schema=GraphState)

graph_builder.add_node(RETRIEVE_NEWS, retrieve)
graph_builder.add_node(GRADE_DOCUMENT, grade_documents)
graph_builder.add_node(WEB_SEARCH, web_search)
graph_builder.add_node(GENERATE_RESULT, generate)
graph_builder.add_node(HALLUCINATION_CHECK, check_hallucination)

graph_builder.add_edge(RETRIEVE_NEWS, GRADE_DOCUMENT)
graph_builder.add_conditional_edges(
    GRADE_DOCUMENT,
    decide_to_generate,
    path_map={
        WEB_SEARCH: WEB_SEARCH,
        GENERATE_RESULT: GENERATE_RESULT
    }
)
graph_builder.add_edge(WEB_SEARCH, GENERATE_RESULT)
graph_builder.add_edge(GENERATE_RESULT, HALLUCINATION_CHECK)

def decide_after_hallucination(state):
    """
    Decide what to do after hallucination check.
    If not grounded and web search hasn't been done, try web search.
    Otherwise, end.
    """
    grounded = state.get("grounded")
    web_search_performed = state.get("web_search_performed", False)
    
    if not grounded and not web_search_performed:
        logger.info("---DECISION: HALLUCINATION DETECTED, RETRYING WITH WEB SEARCH---")
        return WEB_SEARCH
    else:
        logger.info("---DECISION: END---")
        return END

graph_builder.add_conditional_edges(
    HALLUCINATION_CHECK,
    decide_after_hallucination,
    path_map={
        WEB_SEARCH: WEB_SEARCH,
        END: END
    }
)

graph_builder.set_entry_point(RETRIEVE_NEWS)

app = graph_builder.compile()
app.get_graph().draw_mermaid_png(output_file_path="news-rag-graph.png")