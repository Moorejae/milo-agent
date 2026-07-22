import os
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = os.getenv("OBSIDIAN_REPO_NAME", "my-obsidian-vault")

class MemoryManager:
    """
    Pure GitHub-backed memory manager.
    No ChromaDB, no local vector store, no 79MB ONNX downloads.
    All lessons and guidelines live permanently in the GitHub Obsidian Vault.
    """

    def __init__(self):
        # In-process cache — populated from GitHub on startup
        self.lessons: dict[str, str] = {}
        self.how_i_think: dict[str, str] = {}

        try:
            self.github = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None
        except Exception:
            self.github = None

        self._initial_vault_sync()

    def _get_repo(self):
        if not self.github:
            return None
        try:
            user = self.github.get_user()
            try:
                return user.get_repo(REPO_NAME)
            except Exception:
                return user.create_repo(REPO_NAME, private=True)
        except Exception as e:
            print(f"[MemoryManager] GitHub repo access error: {e}")
            return None

    def _initial_vault_sync(self):
        """Pulls all existing lesson files from GitHub on startup into in-process cache."""
        repo = self._get_repo()
        if not repo:
            print("[MemoryManager] GitHub vault not available — running with empty in-process memory.")
            return

        count = 0
        for folder, store in [("lessons", self.lessons), ("how_i_think", self.how_i_think)]:
            try:
                contents = repo.get_contents(folder)
                for f in contents:
                    if f.path.endswith(".md"):
                        key = f.name.replace(".md", "")
                        store[key] = f.decoded_content.decode("utf-8")
                        count += 1
            except Exception:
                pass  # Folder may not exist yet — that is fine

        print(f"[MemoryManager] Synced {count} entries from GitHub '{REPO_NAME}' vault on startup.")

    def query_lessons(self, query: str = "", n_results: int = 5) -> list[str]:
        """Returns the most relevant lessons from the in-process cache (simple keyword match)."""
        results = []
        q = query.lower()
        for content in self.lessons.values():
            if not q or any(word in content.lower() for word in q.split()):
                results.append(content)
            if len(results) >= n_results:
                break
        # Fall back to most recent entries if no keyword match
        if not results:
            results = list(self.lessons.values())[:n_results]
        return results

    def query_how_i_think(self, query: str = "", n_results: int = 5) -> list[str]:
        """Returns guidelines from the how_i_think folder."""
        results = list(self.how_i_think.values())[:n_results]
        return results

    def write_lesson(self, title: str, content: str):
        """Writes a lesson to both the in-process cache and the GitHub Obsidian Vault."""
        key = f"lesson_{title.lower().replace(' ', '_')}"
        self.lessons[key] = content

        repo = self._get_repo()
        if not repo:
            return

        path = f"lessons/{key}.md"
        file_text = f"# Lesson: {title}\n\n{content}"
        try:
            existing = repo.get_contents(path)
            repo.update_file(path, f"Update: {title}", file_text, existing.sha)
        except Exception:
            try:
                repo.create_file(path, f"Add: {title}", file_text)
            except Exception as e:
                print(f"[MemoryManager] GitHub write error: {e}")
                return

        print(f"[MemoryManager] Lesson '{title}' committed to GitHub '{REPO_NAME}' vault.")

    def write_how_i_think(self, title: str, content: str):
        """Writes a guideline/rule to the how_i_think folder in the Obsidian Vault."""
        key = f"guideline_{title.lower().replace(' ', '_')}"
        self.how_i_think[key] = content

        repo = self._get_repo()
        if not repo:
            return

        path = f"how_i_think/{key}.md"
        file_text = f"# Guideline: {title}\n\n{content}"
        try:
            existing = repo.get_contents(path)
            repo.update_file(path, f"Update guideline: {title}", file_text, existing.sha)
        except Exception:
            try:
                repo.create_file(path, f"Add guideline: {title}", file_text)
            except Exception as e:
                print(f"[MemoryManager] GitHub guideline write error: {e}")


memory_manager = MemoryManager()
