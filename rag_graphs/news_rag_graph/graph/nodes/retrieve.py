# Code for retrieval node
from typing import Any, Dict
from rag_graphs.news_rag_graph.graph.state import GraphState
from rag_graphs.news_rag_graph.ingestion import get_news_retriever
from utils.logger import logger

def retrieve(state:GraphState)->Dict[str, Any]:
    logger.info("---RETRIEVE---")
    question    = state['question']
    try:
        retriever   = get_news_retriever()
        if retriever:
            documents   = retriever.invoke(question) or []
        else:
            logger.warning("Retriever unavailable (Chroma down).")
            documents = []
    except Exception as e:
        logger.warning(f"News retriever failed: {e}. Proceeding with empty documents.")
        documents = []

    return {"documents": documents, "question": question}