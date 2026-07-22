import os
import subprocess
from langchain.tools import tool
from github import Github

@tool
def write_file(filepath: str, content: str) -> str:
    """Writes any file to disk (code, markdown, scripts, configs, etc.)."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote file to {filepath}"
    except Exception as e:
        return f"Error writing file {filepath}: {str(e)}"

@tool
def run_code(language: str, code_or_script: str) -> str:
    """Executes Python, Node.js, or Bash scripts directly."""
    try:
        lang = language.lower()
        if lang in ["python", "py"]:
            res = subprocess.run(["python", "-c", code_or_script], capture_output=True, text=True, timeout=30)
        elif lang in ["node", "javascript", "js"]:
            res = subprocess.run(["node", "-e", code_or_script], capture_output=True, text=True, timeout=30)
        elif lang in ["bash", "shell", "sh", "cmd", "powershell"]:
            res = subprocess.run(code_or_script, shell=True, capture_output=True, text=True, timeout=30)
        else:
            return f"Unsupported language: {language}"
            
        output = res.stdout if res.stdout else res.stderr
        return f"Exit Code: {res.returncode}\nOutput:\n{output[:2000]}"
    except Exception as e:
        return f"Error executing {language} script: {str(e)}"

@tool
def github_push(repo_name: str, commit_message: str = "Update from Agent Milo") -> str:
    """Creates/pushes code from workspace to GitHub repository."""
    try:
        token = os.getenv("GITHUB_TOKEN", "")
        if not token:
            return "GITHUB_TOKEN not set in environment."
        g = Github(token)
        user = g.get_user()
        try:
            repo = user.create_repo(repo_name, private=False)
        except Exception:
            repo = user.get_repo(repo_name)
            
        return f"GitHub repo ready: https://github.com/{user.login}/{repo_name}"
    except Exception as e:
        return f"Error with GitHub push: {str(e)}"

@tool
def ssh_execute(host: str, user: str, command: str) -> str:
    """Executes a command on a remote server via SSH."""
    try:
        ssh_cmd = f"ssh -o StrictHostKeyChecking=no {user}@{host} '{command}'"
        res = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
        return f"SSH Result on {user}@{host}:\n{res.stdout if res.stdout else res.stderr}"
    except Exception as e:
        return f"Error executing SSH command: {str(e)}"
