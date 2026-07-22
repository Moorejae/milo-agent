import os
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = os.getenv("OBSIDIAN_REPO_NAME", "my-obsidian-vault")

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
            print(f"[MemoryManager] ChromaDB vector engine fallback (Using in-memory/file store): {e}")

        try:
            if GITHUB_TOKEN:
                self.github = Github(GITHUB_TOKEN)
            else:
                self.github = None
        except Exception:
            self.github = None

        # Auto-ingest vault on startup from GitHub repo
        self._initial_vault_sync()

    def _initial_vault_sync(self):
        """Pulls existing lesson files from GitHub my-obsidian-vault repo on startup."""
        if not self.github:
            return
        try:
            user = self.github.get_user()
            try:
                repo = user.get_repo(REPO_NAME)
                contents = repo.get_contents("lessons")
                for f in contents:
                    if f.path.endswith(".md"):
                        text = f.decoded_content.decode("utf-8")
                        doc_id = f.name.replace(".md", "")
                        self.memory_store["lessons"][doc_id] = text
                        if self.chroma_available:
                            try:
                                self.lessons_collection.add(
                                    documents=[text],
                                    metadatas=[{"source": doc_id}],
                                    ids=[doc_id]
                                )
                            except Exception:
                                pass
                print(f"[MemoryManager] Successfully synced {len(self.memory_store['lessons'])} past lessons from GitHub '{REPO_NAME}' vault!")
            except Exception as e:
                print(f"[MemoryManager] Vault remote check status: {e}")
        except Exception as ge:
            print(f"[MemoryManager] Initial vault sync error: {ge}")

    def query_how_i_think(self, query: str = "guidelines", n_results: int = 5):
        docs = []
        if self.chroma_available:
            try:
                results = self.how_i_think_collection.query(query_texts=[query], n_results=n_results)
                docs.extend(results.get('documents', [[]])[0])
            except Exception:
                pass
        docs.extend(list(self.memory_store["how_i_think"].values()))
        return list(filter(None, docs))[:n_results]

    def query_lessons(self, query: str = "lessons learned", n_results: int = 5):
        docs = []
        if self.chroma_available:
            try:
                results = self.lessons_collection.query(query_texts=[query], n_results=n_results)
                docs.extend(results.get('documents', [[]])[0])
            except Exception:
                pass
        docs.extend(list(self.memory_store["lessons"].values()))
        return list(filter(None, docs))[:n_results]
        
    def write_lesson(self, title: str, content: str):
        doc_id = f"lesson_{title.lower().replace(' ', '_')}"
        self.memory_store["lessons"][doc_id] = content
        
        # Persist to local Chroma DB if active
        if self.chroma_available:
            try:
                self.lessons_collection.add(
                    documents=[content],
                    metadatas=[{"source": doc_id}],
                    ids=[doc_id]
                )
            except Exception as e:
                print(f"[MemoryManager] ChromaDB write status: {e}")

        # Sync directly to GitHub Obsidian Vault repository (my-obsidian-vault)
        if self.github:
            try:
                user = self.github.get_user()
                try:
                    repo = user.get_repo(REPO_NAME)
                except Exception:
                    repo = user.create_repo(REPO_NAME, private=True)
                
                path = f"lessons/{doc_id}.md"
                file_text = f"# Lesson: {title}\n\n{content}"
                try:
                    existing = repo.get_contents(path)
                    repo.update_file(path, f"Update lesson: {title}", file_text, existing.sha)
                except Exception:
                    repo.create_file(path, f"Add lesson: {title}", file_text)
                print(f"[MemoryManager] Successfully synced lesson '{title}' to GitHub Obsidian Vault ({REPO_NAME})!")
            except Exception as ge:
                print(f"[MemoryManager] GitHub vault sync status: {ge}")

memory_manager = MemoryManager()
