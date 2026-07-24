import os
import threading
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = os.getenv("OBSIDIAN_REPO_NAME", "my-obsidian-vault")

class MemoryManager:
    """
    The Living Organic Brain Memory Manager.
    Stores Active Beliefs (verified principles) and Refutations (unlearned lessons / failed hypotheses).
    All memory is synchronized with the GitHub Obsidian Vault asynchronously.
    """

    def __init__(self):
        self.lessons: dict[str, str] = {}
        self.beliefs: dict[str, str] = {}
        self.refutations: dict[str, str] = {}
        self._repo = None

        try:
            self.github = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None
        except Exception:
            self.github = None

        threading.Thread(target=self._initial_vault_sync, daemon=True).start()

    def _get_repo(self):
        if self._repo:
            return self._repo
        if not self.github:
            return None
        try:
            user = self.github.get_user()
            try:
                self._repo = user.get_repo(REPO_NAME)
            except Exception:
                self._repo = user.create_repo(REPO_NAME, private=True)
            return self._repo
        except Exception as e:
            print(f"[MemoryManager] GitHub repo access error: {e}")
            return None

    def _initial_vault_sync(self):
        """Pulls all memory entries from GitHub in background."""
        repo = self._get_repo()
        if not repo:
            print("[MemoryManager] GitHub vault not available — running with empty in-process memory.")
            return

        count = 0
        for folder, store in [("lessons", self.lessons), ("beliefs", self.beliefs), ("refutations", self.refutations)]:
            try:
                contents = repo.get_contents(folder)
                for f in contents:
                    if f.path.endswith(".md"):
                        key = f.name.replace(".md", "")
                        store[key] = f.decoded_content.decode("utf-8")
                        count += 1
            except Exception:
                pass

        print(f"[MemoryManager] Synced {count} brain entries (Beliefs & Refutations) from GitHub '{REPO_NAME}' vault in background.")

    def synthesize_memory(self, query: str = "") -> str:
        """Synthesizes active beliefs and past refutations into a clean prompt context string."""
        context_parts = []
        
        # Include verified active beliefs
        if self.beliefs:
            beliefs_list = list(self.beliefs.values())[:3]
            context_parts.append("Active Beliefs & Proven Guidelines:\n- " + "\n- ".join(beliefs_list))
            
        # Include unlearned lessons / refutations so Milo never repeats mistakes
        if self.refutations:
            refutations_list = list(self.refutations.values())[:3]
            context_parts.append("Refuted Hypotheses & Unlearned Mistakes (DO NOT REPEAT):\n- " + "\n- ".join(refutations_list))

        if not context_parts and self.lessons:
            lessons_list = list(self.lessons.values())[:3]
            context_parts.append("Learned Preferences:\n- " + "\n- ".join(lessons_list))

        return "\n\n".join(context_parts) if context_parts else "No previous brain entries found."

    def write_belief(self, title: str, content: str):
        """Writes an active belief/principle to Obsidian Vault asynchronously."""
        key = f"belief_{title.lower().replace(' ', '_')}"
        self.beliefs[key] = content
        self._bg_commit_file(f"beliefs/{key}.md", f"# Belief: {title}\n\n{content}", f"Add belief: {title}")

    def write_refutation(self, title: str, reason: str):
        """Archives a failed hypothesis/unlearned lesson to Obsidian Vault asynchronously."""
        key = f"refutation_{title.lower().replace(' ', '_')}"
        content = f"Failed Hypothesis: {title}\nReason Refuted / Unlearned: {reason}"
        self.refutations[key] = content
        self._bg_commit_file(f"refutations/{key}.md", f"# Refutation: {title}\n\n{content}", f"Add refutation: {title}")

    def write_lesson(self, title: str, content: str):
        key = f"lesson_{title.lower().replace(' ', '_')}"
        self.lessons[key] = content
        self._bg_commit_file(f"lessons/{key}.md", f"# Lesson: {title}\n\n{content}", f"Add lesson: {title}")

    def _bg_commit_file(self, path: str, file_text: str, commit_msg: str):
        def _bg_write():
            repo = self._get_repo()
            if not repo:
                return
            try:
                existing = repo.get_contents(path)
                repo.update_file(path, commit_msg, file_text, existing.sha)
            except Exception:
                try:
                    repo.create_file(path, commit_msg, file_text)
                except Exception as e:
                    print(f"[MemoryManager] GitHub write error on {path}: {e}")
        threading.Thread(target=_bg_write, daemon=True).start()

memory_manager = MemoryManager()
