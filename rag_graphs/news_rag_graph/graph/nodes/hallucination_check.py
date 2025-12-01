from typing import Any, Dict
from rag_graphs.news_rag_graph.graph.state import GraphState
from rag_graphs.news_rag_graph.graph.chains.hallucination_grader import hallucination_grader
from utils.logger import logger

def check_hallucination(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the generation is grounded in the document.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates generation if hallucinated
    """
    logger.info("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.strip().lower()

    if "yes" in grade:
        logger.info("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        return {"generation": generation, "grounded": True}
    else:
        logger.info("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS---")
        # We don't overwrite generation yet, letting the graph decide whether to retry or end
        # If the graph ends here, the last generation (which was hallucinated) would be returned
        # So we should probably return the apology here, but if we retry, it will be overwritten.
        # To be safe, we return the apology. If we retry, GENERATE_RESULT will overwrite it.
        return {"generation": "I apologize, but I could not find sufficient information in the retrieved documents to answer your question accurately.", "grounded": False}
