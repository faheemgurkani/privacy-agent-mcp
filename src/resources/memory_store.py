from cryptography.fernet import Fernet
import chromadb
import uuid



# class EncryptedVectorStore:
#     def __init__(self, key):
#         self.fernet = Fernet(key)
#         self.client = chromadb.Client()
#         self.collection = self.client.get_or_create_collection("secure_memory")

#     def add_encrypted(self, text, tags=None):
#         encrypted = self.fernet.encrypt(text.encode()).decode()
#         self.collection.add(documents=[encrypted], metadatas=[{"tags": tags or []}], ids=[str(len(self.collection))])

class EncryptedVectorStore:
    
    def __init__(self, key):
        self.fernet = Fernet(key)
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("secure_memory")

    def add_encrypted(self, text, tags=None):
        encrypted = self.fernet.encrypt(text.encode()).decode()
        tag_str = ", ".join(tags) if tags else ""
        unique_id = str(uuid.uuid4())
        self.collection.add(
            documents=[encrypted],
            metadatas=[{"tags": tag_str}],  # <-- FIXED HERE
            ids=[unique_id]
        )


# Instantiating the vector store with an encryption key
from dotenv import load_dotenv
import os

load_dotenv()

key = os.environ.get("ENCRYPTION_KEY")

memory_vector_store = EncryptedVectorStore(key)