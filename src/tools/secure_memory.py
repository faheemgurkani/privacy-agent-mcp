import sys
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
import os



load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

original_sys_path = sys.path.copy()

try:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

    from resources.memory_store import EncryptedVectorStore

    def store_secure_memory(text: str, tags: Optional[List[str]] = None) -> str:
        """
        Stores redacted content with encryption for future RAG or auditing.
        """
        memory_vector_store = EncryptedVectorStore(os.getenv("ENCRYPTION_KEY"))

        memory_vector_store.add_encrypted(text, tags=tags)
        
        return "Stored securely"

    if __name__ == "__main__":
        test_text = "My name is [REDACTED_NAME] and SSN is [REDACTED_SSN]."
        test_tags = ["insurance", "sensitive", "user_input"]

        try:
            result = store_secure_memory(test_text, tags=test_tags)
            
            print("Store Result:")
            print(result)
            
        except Exception as e:
            print(f"Error during test: {e}")

finally:
    sys.path = original_sys_path
