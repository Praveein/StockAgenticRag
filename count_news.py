import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings

# Load environment variables
load_dotenv()

# Configuration
VECTOR_DB_DIRECTORY = os.getenv("VECTOR_DB_DIRECTORY", "vector_db")
VECTOR_DB_COLLECTION = os.getenv("VECTOR_DB_COLLECTION", "news_articles")
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8001"))

def check_chroma_count():
    print(f"🔍 Checking ChromaDB collection: '{VECTOR_DB_COLLECTION}'")
    
    # Try connecting to the server first (since that's what the app uses)
    try:
        print(f"   Connecting to Chroma server at {CHROMA_HOST}:{CHROMA_PORT}...")
        client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
        collection = client.get_collection(name=VECTOR_DB_COLLECTION)
        count = collection.count()
        print(f"✅ Success! Collection '{VECTOR_DB_COLLECTION}' has {count} documents.")
        return
    except Exception as e:
        print(f"⚠️  Could not connect to Chroma server: {e}")

    # Fallback to local persistence check (if server is not running but data exists)
    print(f"   Checking local storage at: {VECTOR_DB_DIRECTORY}...")
    try:
        client = chromadb.PersistentClient(path=VECTOR_DB_DIRECTORY)
        # List collections to see if it exists
        collections = client.list_collections()
        collection_names = [c.name for c in collections]
        
        if VECTOR_DB_COLLECTION in collection_names:
            collection = client.get_collection(name=VECTOR_DB_COLLECTION)
            count = collection.count()
            print(f"✅ Found local collection '{VECTOR_DB_COLLECTION}' with {count} documents.")
        else:
            print(f"❌ Collection '{VECTOR_DB_COLLECTION}' not found in local storage.")
            print(f"   Available collections: {collection_names}")
            
    except Exception as e:
        print(f"❌ Failed to check local storage: {e}")

if __name__ == "__main__":
    check_chroma_count()
