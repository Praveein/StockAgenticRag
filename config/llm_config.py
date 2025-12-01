"""
Configuration for local LLM and embeddings using Ollama.
Supports Gemma 3 4B model for local inference.
"""

import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from utils.logger import logger

load_dotenv()

# Configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")  # Default to qwen2.5-coder:7b
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

def get_llm(temperature: float = 0):
    """
    Get an Ollama LLM instance configured for local inference.
    
    Args:
        temperature: Controls randomness of responses (0 = deterministic, 1 = creative)
    
    Returns:
        Ollama instance
    """
    try:
        llm = OllamaLLM(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=temperature,
        )
        logger.info(f"Initialized Ollama LLM with model: {LLM_MODEL}")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize Ollama LLM: {e}")
        raise

def get_embeddings():
    """
    Get Ollama embeddings instance for local inference.
    
    Returns:
        OllamaEmbeddings instance
    """
    try:
        embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
        logger.info(f"Initialized Ollama Embeddings with model: {EMBEDDING_MODEL}")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to initialize Ollama Embeddings: {e}")
        raise

# Singleton instances for reuse
_llm_instance = None
_embeddings_instance = None

def get_llm_singleton(temperature: float = 0):
    """Get or create a singleton LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_llm(temperature)
    return _llm_instance

def get_embeddings_singleton():
    """Get or create a singleton embeddings instance."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = get_embeddings()
    return _embeddings_instance
