import os
from dotenv import load_dotenv
from db.mongo_db import MongoDBClient
import chromadb
from chromadb.config import Settings

load_dotenv()

def diagnose():
    print("🔍 DIAGNOSTIC REPORT")
    print("====================")
    
    # 1. Check MongoDB
    try:
        mongo = MongoDBClient()
        collection_name = os.getenv("COLLECTION_NAME", "default_collection")
        coll = mongo.get_collection(collection_name)
        count = coll.count_documents({})
        unsynced = coll.count_documents({'synced': False})
        print(f"✅ MongoDB Connection: OK")
        print(f"   Collection: {collection_name}")
        print(f"   Total Articles: {count}")
        print(f"   Unsynced Articles: {unsynced}")
    except Exception as e:
        print(f"❌ MongoDB Connection: FAILED ({e})")

    # 2. Check Chroma Environment
    print("\n🔍 ChromaDB Configuration")
    print(f"   VECTOR_DB_DIRECTORY: {os.getenv('VECTOR_DB_DIRECTORY')}")
    print(f"   VECTOR_DB_COLLECTION: {os.getenv('VECTOR_DB_COLLECTION')}")
    print(f"   CHROMA_API_IMPL: {os.getenv('CHROMA_API_IMPL', 'Not Set')}")
    
    # 3. Check Chroma Connectivity
    print("\n🔍 ChromaDB Connectivity")
    
    # Try HTTP
    try:
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", "8001"))
        print(f"   Attempting HTTP connection to {host}:{port}...")
        client = chromadb.HttpClient(host=host, port=port)
        client.heartbeat() # Test connection
        print("   ✅ HTTP Server: REACHABLE")
        
        col_name = os.getenv("VECTOR_DB_COLLECTION")
        try:
            c = client.get_collection(col_name)
            print(f"   ✅ Collection '{col_name}': FOUND (Count: {c.count()})")
        except Exception as e:
            print(f"   ⚠️  Collection '{col_name}': NOT FOUND on server")
            
    except Exception as e:
        print(f"   ❌ HTTP Server: UNREACHABLE ({e})")

    # Try Persistent
    print("\n   Attempting Local Persistence...")
    try:
        # Force settings to override any env vars causing http-only mode
        path = os.getenv("VECTOR_DB_DIRECTORY", "vector_db")
        client = chromadb.PersistentClient(path=path, settings=Settings(chroma_api_impl="chromadb.api.segment.SegmentAPI"))
        print("   ✅ PersistentClient: INITIALIZED")
        
        col_name = os.getenv("VECTOR_DB_COLLECTION")
        try:
            c = client.get_collection(col_name)
            print(f"   ✅ Collection '{col_name}': FOUND (Count: {c.count()})")
        except Exception:
            print(f"   ⚠️  Collection '{col_name}': NOT FOUND locally")
            
    except Exception as e:
        print(f"   ❌ PersistentClient: FAILED ({e})")

if __name__ == "__main__":
    diagnose()
