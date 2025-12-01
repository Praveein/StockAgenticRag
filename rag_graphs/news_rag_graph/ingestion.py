from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from db.mongo_db import MongoDBClient
import os
from typing import List
from utils.logger import logger
from config.llm_config import get_embeddings_singleton

import chromadb
from chromadb.config import Settings

load_dotenv()

# Provide sane defaults when env vars are missing
VECTOR_DB_DIRECTORY = os.getenv("VECTOR_DB_DIRECTORY", "vector_db")
VECTOR_DB_COLLECTION = os.getenv("VECTOR_DB_COLLECTION", "news_articles")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))


def _build_chroma_client():
    """Try local persistent client first; fall back to HTTP client if local API is unavailable."""
    try:
        return chromadb.PersistentClient(path=VECTOR_DB_DIRECTORY)
    except Exception as e:
        logger.warning(f"PersistentClient unavailable ({e}); trying HttpClient at {CHROMA_HOST}:{CHROMA_PORT}")
        try:
            return chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        except Exception as http_e:
            logger.error(f"HttpClient also failed: {http_e}. Vector storage will be skipped.")
            return None


def get_news_retriever():
    """Construct and return a Chroma retriever for news articles."""
    client = _build_chroma_client()
    if not client:
        # Return a dummy retriever or handle None upstream
        # For now, returning None and handling it in retrieve node is safer
        return None
        
    return Chroma(
        client=client,
        collection_name=VECTOR_DB_COLLECTION,
        embedding_function=get_embeddings_singleton()
    ).as_retriever()

class DocumentSyncManager:
    def __init__(self):
        self.mongo_client = MongoDBClient()
        self.news_collection = self.mongo_client.get_collection()
        self.vector_db_collection = os.getenv('VECTOR_DB_COLLECTION')
        self.vector_db_directory = os.getenv('VECTOR_DB_DIRECTORY')

    def fetch_unsynced_documents(self):
        """
        Fetches documents from the database where 'synced' is set to False.
        """
        return self.news_collection.find({'synced': False}, {'_id': 1, 'description': 1})

    def mark_documents_as_synced(self, document_ids: List):
        """
        Marks the provided document IDs as synced in the database.
        """
        result = self.news_collection.update_many(
            {'_id': {'$in': document_ids}},
            {'$set': {'synced': True}}
        )
        logger.info(f"Marked {result.modified_count} documents as synced.")

    def process_content(self, contents: List[str]):
        """
        Processes content into chunks using a text splitter.
        """
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=250, chunk_overlap=0
        )
        documents = [Document(page_content=content) for content in contents]
        return text_splitter.split_documents(documents)

    def store_documents_in_chroma(self, doc_splits: List[Document]) -> bool:
        """
        Stores processed document chunks as embeddings in Chroma.
        Returns True if successful, False otherwise.
        """
        client = _build_chroma_client()
        if not client:
            logger.warning("Chroma client unavailable. Skipping document storage.")
            return False

        try:
            vectorstore = Chroma.from_documents(
                documents=doc_splits,
                client=client,
                collection_name=self.vector_db_collection,
                embedding=get_embeddings_singleton()
            )
            logger.info("Documents stored in Chroma.")
            return True
        except Exception as e:
            logger.error(f"Failed to store documents in Chroma: {e}")
            return False

    def sync_documents(self):
        """
        Orchestrates the process of syncing unsynced documents:
        - Fetches unsynced documents
        - Processes their content
        - Stores them in Chroma
        - Marks them as synced in the database (ONLY if storage succeeded)
        """
        unsynced_articles = list(self.fetch_unsynced_documents())
        if not unsynced_articles:
            logger.info("No unsynced documents found in MongoDB!")
            return

        descriptions = [article['description'] for article in unsynced_articles if 'description' in article]
        document_ids = [article['_id'] for article in unsynced_articles]

        if descriptions:
            doc_splits = self.process_content(descriptions)
            if self.store_documents_in_chroma(doc_splits):
                self.mark_documents_as_synced(document_ids)
                logger.info("Documents processed, stored, and marked as synced.")
            else:
                logger.warning("Document storage failed. Documents will NOT be marked as synced.")

if __name__ == '__main__':
    DocumentSyncManager().sync_documents()