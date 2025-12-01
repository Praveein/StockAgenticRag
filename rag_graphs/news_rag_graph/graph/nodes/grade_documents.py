from dotenv import load_dotenv
from typing import Any, Dict
from rag_graphs.news_rag_graph.graph.chains.retrieval_grader import retrieval_grader
from rag_graphs.news_rag_graph.graph.state import GraphState
from utils.logger import logger

load_dotenv()
def grade_documents(state: GraphState)-> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag to run web search

    Args:
        state(dict): The current graph state

    Returns:
        state(dict): Filtered out irrelevant documents and updated web_search state
    :param state:
    :return:
    """
    logger.info("---CHECK DOCUMENT RELEVANCE TO THE QUESTION---" )
    question    = state.get("question")
    documents   = state.get("documents") or []

    filtered_docs   = []
    web_search      = True

    for d in documents:
        score_text = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade   = str(score_text).strip().lower()

        if grade == "yes":
            logger.info("---GRADE: DOCUMENT RELEVANT---")
            filtered_docs.append(d)
            web_search = False
        else:
            logger.info("---GRADE: DOCUMENT NOT RELEVANT---")
            web_search  = True
            continue

    return {"documents": filtered_docs, "question": question, "web_search": web_search}


