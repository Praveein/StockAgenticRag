import chromadb
import os
from chromadb.config import Settings

VECTOR_DB_DIRECTORY = os.getenv("VECTOR_DB_DIRECTORY", "vector_db")

print(f"Testing PersistentClient at: {VECTOR_DB_DIRECTORY}")
try:
    client = chromadb.PersistentClient(path=VECTOR_DB_DIRECTORY)
    print("✅ PersistentClient created successfully.")
    print(f"Collections: {client.list_collections()}")
except Exception as e:
    print(f"❌ PersistentClient failed: {e}")

print("\nTesting HttpClient at localhost:8000 (expect failure if no server)")
try:
    client = chromadb.HttpClient(host="localhost", port=8000)
    print("✅ HttpClient created (connection not yet verified).")
    print(f"Collections: {client.list_collections()}")
except Exception as e:
    print(f"❌ HttpClient failed: {e}")
