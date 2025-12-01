"""Optional LangSmith tracing integration for LangChain/LangGraph workflows."""
import os
from dotenv import load_dotenv, find_dotenv
from utils.logger import logger


def enable_langsmith_tracing(project_name: str = "StocksInsights"):
    """
    Enable LangChain v2 tracing (LangSmith).
    Loads .env from cwd or parents, and accepts LANGSMITH_API_KEY or LANGCHAIN_API_KEY.
    """
    # Load .env from current dir or parents
    try:
        load_dotenv(find_dotenv(usecwd=True))
    except Exception:
        load_dotenv()

    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    if api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ.setdefault("LANGCHAIN_PROJECT", project_name)
        endpoint = os.getenv("LANGCHAIN_ENDPOINT")
        if endpoint:
            os.environ["LANGCHAIN_ENDPOINT"] = endpoint
        logger.info(f"LangSmith tracing enabled (project={os.environ['LANGCHAIN_PROJECT']}).")
    else:
        logger.info("LangSmith tracing disabled (LANGSMITH_API_KEY not set).")
