import os
import json
import time
import threading
from github import Github

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPO_NAME = os.getenv("OBSIDIAN_REPO_NAME", "my-obsidian-vault")

class HiveQueenVault:
    """
    Obsidian Vault Schema & State Manager for Hive-Queen Agent Milo.
    Optimized with repo caching and asynchronous background commits.
    """

    def __init__(self):
        self._repo = None
        try:
            self.github = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None
        except Exception:
            self.github = None

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
            print(f"[HiveQueenVault] GitHub repo access error: {e}")
            return None

    def read_file(self, path: str, default: str = "") -> str:
        repo = self._get_repo()
        if not repo:
            return default
        try:
            content = repo.get_contents(path)
            return content.decoded_content.decode("utf-8")
        except Exception:
            return default

    def write_file(self, path: str, content: str, commit_msg: str = "Update vault file"):
        repo = self._get_repo()
        if not repo:
            return False
        try:
            try:
                existing = repo.get_contents(path)
                repo.update_file(path, commit_msg, content, existing.sha)
            except Exception:
                repo.create_file(path, commit_msg, content)
            print(f"[HiveQueenVault] Committed '{path}' to GitHub.")
            return True
        except Exception as e:
            print(f"[HiveQueenVault] Error writing '{path}': {e}")
            return False

    def write_file_async(self, path: str, content: str, commit_msg: str = "Update vault file"):
        """Dispatches GitHub write to a background thread to prevent HTTP blocking."""
        thread = threading.Thread(target=self.write_file, args=(path, content, commit_msg), daemon=True)
        thread.start()

    def append_log(self, path: str, entry: str, title_fallback: str = "Log"):
        def _bg_append():
            current = self.read_file(path, default=f"# {title_fallback}\n\n")
            updated = current.strip() + f"\n\n{entry.strip()}\n"
            self.write_file(path, updated, commit_msg=f"Append to {path}")
        threading.Thread(target=_bg_append, daemon=True).start()

    # --- REGISTRY MD MANAGER ---
    def get_registry(self) -> str:
        default_registry = (
            "# Sub-Agent Registry\n\n"
            "| agent_id | purpose | input_schema | output_schema | script_path | created | last_used | runs | success_rate | avg_cost | decay_score | status |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        )
        return self.read_file("agents/registry.md", default=default_registry)

    def register_sub_agent(self, agent_id: str, purpose: str, input_schema: str, output_schema: str, script_path: str):
        def _bg_register():
            registry_text = self.get_registry()
            today = time.strftime("%Y-%m-%d")
            new_row = f"| {agent_id} | {purpose} | `{input_schema}` | `{output_schema}` | {script_path} | {today} | {today} | 1 | 100% | $0.00 | 0 | active |"
            if agent_id not in registry_text:
                registry_text += f"\n{new_row}"
                self.write_file("agents/registry.md", registry_text, commit_msg=f"Register sub-agent: {agent_id}")
        threading.Thread(target=_bg_register, daemon=True).start()

    # --- STATE CANVAS MANAGER ---
    def update_canvas(self, objective_id: str, raw_ask: str, microtasks: list):
        """Generates & updates state.canvas JSON structure in Obsidian format asynchronously."""
        canvas_data = {
            "nodes": [
                {
                    "id": f"obj-{objective_id}",
                    "type": "text",
                    "text": f"## OBJECTIVE\n**id:** {objective_id}\n**status:** in_progress\n**raw_ask:** {raw_ask}",
                    "x": -400, "y": -300, "width": 380, "height": 200, "color": "1"
                }
            ],
            "edges": []
        }

        y_offset = -50
        for i, mt in enumerate(microtasks):
            mt_id = f"{objective_id}.{i}.1"
            canvas_data["nodes"].append({
                "id": f"mt-{mt_id}",
                "type": "text",
                "text": f"### Micro-task\n**id:** {mt_id}\n**name:** {mt.get('name')}\n**input_contract:** {mt.get('input_contract')}\n**output_contract:** {mt.get('output_contract')}\n**status:** {mt.get('status', 'queued')}",
                "x": -400, "y": y_offset, "width": 380, "height": 220, "color": "4"
            })
            canvas_data["edges"].append({
                "id": f"e-{i}",
                "fromNode": f"obj-{objective_id}",
                "fromSide": "bottom",
                "toNode": f"mt-{mt_id}",
                "toSide": "top"
            })
            y_offset += 240

        self.write_file_async("state.canvas", json.dumps(canvas_data, indent=2), commit_msg=f"Update state.canvas for {objective_id}")

    # --- DECISIONS & LINEAGE LOGGERS ---
    def log_decision(self, decision: str, justification: str):
        entry = f"### [{time.strftime('%Y-%m-%d %H:%M:%S')}] {decision}\n**Justification:** {justification}\n"
        self.append_log("decisions.md", entry, title_fallback="Architectural Decisions Log")

    def log_lineage(self, parent_id: str, child_id: str, reason: str):
        def _bg_lineage():
            entry = f"| {parent_id} | {child_id} | {reason} | {time.strftime('%Y-%m-%d')} |"
            header = "# Agent Lineage & Genealogy\n\n| Parent Agent | Child Agent | Fork Reason | Date |\n|---|---|---|---|\n"
            current = self.read_file("lineage.md", default=header)
            updated = current.strip() + f"\n{entry}"
            self.write_file("lineage.md", updated, commit_msg=f"Fork lineage: {parent_id} -> {child_id}")
        threading.Thread(target=_bg_lineage, daemon=True).start()

hive_vault = HiveQueenVault()
