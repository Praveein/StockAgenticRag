from typing import Any, Dict
from dotenv import load_dotenv
from rag_graphs.news_rag_graph.graph.state import GraphState
from langchain_core.documents import Document
from utils.logger import logger
import os

load_dotenv()

# Toggle external web search; default disabled to avoid API costs during dev
ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "false").lower() == "true"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if ENABLE_WEB_SEARCH and TAVILY_API_KEY:
    try:
        from langchain_community.tools import TavilySearchResults
        web_search_tool = TavilySearchResults(max_results=3)
        logger.info("Initialized Tavily Search")
    except Exception as e:
        logger.warning(f"Failed to initialize Tavily Search: {e}. Using mock search.")
        web_search_tool = None
else:
    if ENABLE_WEB_SEARCH and not TAVILY_API_KEY:
        logger.warning("ENABLE_WEB_SEARCH=true but TAVILY_API_KEY not found. Using mock search results.")
    else:
        logger.info("External web search disabled; using mock search.")
    web_search_tool = None

def mock_web_search(query: str):
    """
    Mock web search when Tavily is not available.
    Returns generic relevant content based on query keywords.
    """
    # This is a placeholder that returns generic content
    # In production, you might want to implement local search or other alternatives
    return [
        {
            "content": f"Information about {query}: Based on recent market trends and data, {query} is an important topic in financial analysis. Consider analyzing historical patterns and current market conditions.",
            "source": "local_knowledge_base"
        }
    ]

def web_search(state: GraphState) -> Dict[str, Any]:
    logger.info("---WEB SEARCH---")
    question    = state["question"]
    documents   = state["documents"]

    # Use Tavily if available, otherwise use mock search
    if web_search_tool:
        try:
            tavily_results = web_search_tool.invoke({"query": question})
            joined_result = "\n".join(
                [result["content"] for result in tavily_results]
            )
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}. Using mock search.")
            tavily_results = mock_web_search(question)
            joined_result = "\n".join(
                [result["content"] for result in tavily_results]
            )
    else:
        tavily_results = mock_web_search(question)
        joined_result = "\n".join(
            [result["content"] for result in tavily_results]
        )

    web_results = Document(page_content=joined_result)
    if documents is not None:
        documents.append(web_results)
    else:
        documents   = [web_results]

    return {"documents": documents, "question": question}

if __name__ == "__main__":
    web_search(state={"question":"agent memory", "documents":None})
