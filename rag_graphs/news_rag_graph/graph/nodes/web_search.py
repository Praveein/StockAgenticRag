from typing import Any, Dict
from dotenv import load_dotenv
from rag_graphs.news_rag_graph.graph.state import GraphState
from langchain_core.documents import Document
from utils.logger import logger
from db.mongo_db import MongoDBClient
from rag_graphs.news_rag_graph.ingestion import DocumentSyncManager
import os
import datetime

load_dotenv()

from rag_graphs.news_rag_graph.graph.chains.search_query_generator import search_query_generator

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
    return [
        {
            "content": f"Mock News Data: Recent reports indicate stable performance for {query}. Analysts suggest monitoring global market trends. (Note: This is a placeholder response as live web search is disabled).",
            "source": "mock_knowledge_base"
        }
    ]

def save_results_to_db(ticker: str, results: list):
    """
    Save web search results to MongoDB and trigger vectorization.
    """
    if not ticker:
        return

    mongo_client = MongoDBClient()
    collection = mongo_client.get_collection()
    
    new_docs_count = 0
    for res in results:
        # Create article object matching the schema
        article = {
            "ticker": ticker,
            "title": f"News for {ticker} - {datetime.datetime.now().strftime('%Y-%m-%d')}",
            "description": res.get("content", ""),
            "link": res.get("source", ""),
            "pubDate": datetime.datetime.now().isoformat(),
            "source": "web_search_agent",
            "synced": False
        }
        
        # Avoid duplicates (simple check)
        if not collection.find_one({"description": article["description"]}):
            collection.insert_one(article)
            new_docs_count += 1
            
    if new_docs_count > 0:
        logger.info(f"Saved {new_docs_count} new articles to MongoDB. Triggering sync...")
        try:
            DocumentSyncManager().sync_documents()
            logger.info("Sync complete.")
        except Exception as e:
            logger.error(f"Failed to sync documents: {e}")

def web_search(state: GraphState) -> Dict[str, Any]:
    logger.info("---WEB SEARCH---")
    question = state["question"]
    documents = state.get("documents") or []
    ticker = state.get("ticker") or ""

    # Generate multiple search queries for better coverage
    try:
        queries_text = search_query_generator.invoke({"question": question, "ticker": ticker})
        search_queries = [q.strip() for q in queries_text.split('\n') if q.strip()]
        logger.info(f"Generated search queries: {search_queries}")
    except Exception as e:
        logger.warning(f"Failed to generate queries: {e}. Fallback to single query.")
        search_queries = [f"{question} {ticker} stock news"]

    all_results = []
    
    # Use Tavily if available, otherwise use mock search
    if web_search_tool:
        for query in search_queries:
            try:
                logger.info(f"Searching for: {query}")
                tavily_results = web_search_tool.invoke({"query": query})
                all_results.extend(tavily_results)
            except Exception as e:
                logger.warning(f"Tavily search failed for '{query}': {e}")
    else:
        # Mock search for each query
        for query in search_queries:
            all_results.extend(mock_web_search(query))

    # Deduplicate results based on content or URL
    unique_results = []
    seen_content = set()
    
    for res in all_results:
        content = res.get("content", "")
        if content not in seen_content:
            seen_content.add(content)
            unique_results.append(res)

    # Save real results to DB for future retrieval
    if ticker and web_search_tool:
        save_results_to_db(ticker, unique_results)

    # Join results for the context
    joined_result = "\n\n".join(
        [f"Source: {res.get('source', 'Unknown')}\nContent: {res.get('content', '')}" for res in unique_results]
    )

    web_results = Document(page_content=joined_result)
    documents.append(web_results)

    return {"documents": documents, "question": question, "ticker": ticker, "web_search_performed": True}

if __name__ == "__main__":
    web_search(state={"question":"agent memory", "documents":None})
