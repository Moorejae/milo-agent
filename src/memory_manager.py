import os
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = "my-obsidian-vault"

class MemoryManager:
    def __init__(self):
        self.chroma_available = False
        self.memory_store = {"how_i_think": {}, "lessons": {}}
        
        try:
            import chromadb
            from chromadb.config import Settings
            self.chroma_client = chromadb.Client(Settings(is_persistent=True, persist_directory="./chroma_db"))
            self.how_i_think_collection = self.chroma_client.get_or_create_collection(name="how_i_think")
            self.lessons_collection = self.chroma_client.get_or_create_collection(name="lessons")
            self.chroma_available = True
        except Exception as e:
            print(f"[MemoryManager] ChromaDB vector engine fallback (Using file memory): {e}")

        try:
            self.github = Github(GITHUB_TOKEN)
        except Exception:
            self.github = None

    def query_how_i_think(self, query: str, n_results: int = 3):
        if self.chroma_available:
            try:
                results = self.how_i_think_collection.query(query_texts=[query], n_results=n_results)
                return results.get('documents', [])
            except Exception:
                pass
        return list(self.memory_store["how_i_think"].values())[:n_results]

    def query_lessons(self, query: str, n_results: int = 3):
        if self.chroma_available:
            try:
                results = self.lessons_collection.query(query_texts=[query], n_results=n_results)
                return results.get('documents', [])
            except Exception:
                pass
        return list(self.memory_store["lessons"].values())[:n_results]
        
    def write_lesson(self, title: str, content: str):
        doc_id = f"lesson_{title.replace(' ', '_')}"
        self.memory_store["lessons"][doc_id] = content
        if self.chroma_available:
            try:
                self.lessons_collection.add(
                    documents=[content],
                    metadatas=[{"source": doc_id}],
                    ids=[doc_id]
                )
            except Exception as e:
                print(f"[MemoryManager] Error writing lesson to ChromaDB: {e}")

memory_manager = MemoryManager()
