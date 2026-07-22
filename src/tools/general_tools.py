import os
import subprocess
import requests
from langchain.tools import tool
from github import Github, Auth

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


@tool
def web_search(query: str) -> str:
    """Searches the web for any information using DuckDuckGo's instant answer API."""
    url = "https://api.duckduckgo.com/"
    params = {"q": query, "format": "json", "no_redirect": 1}
    resp = requests.get(url, params=params)
    if resp.status_code == 200:
        data = resp.json()
        abstract = data.get("AbstractText", "")
        related = [r.get("Text", "") for r in data.get("RelatedTopics", [])[:5] if "Text" in r]
        result = f"Summary: {abstract}\n\nRelated:\n" + "\n".join(f"- {r}" for r in related)
        return result if abstract or related else "No direct results. Try read_webpage for specific URLs."
    return f"Search error: {resp.status_code}"


@tool
def read_webpage(url: str) -> str:
    """Fetches and extracts readable text content from any URL."""
    try:
        resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            # Simple text extraction (strip HTML tags)
            import re
            text = re.sub(r'<[^>]+>', ' ', resp.text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text[:3000] + "..." if len(text) > 3000 else text
        return f"Error fetching page: {resp.status_code}"
    except Exception as e:
        return f"Failed to read webpage: {str(e)}"


@tool
def write_file(relative_path: str, content: str) -> str:
    """Writes any file to disk. Use this to create code, scripts, documents, etc."""
    os.makedirs(os.path.dirname(relative_path), exist_ok=True) if os.path.dirname(relative_path) else None
    with open(relative_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File written successfully: {relative_path}"


@tool
def run_python_code(code: str) -> str:
    """Executes a Python script and returns its output. Use for data analysis, automation, etc."""
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout or result.stderr
        return output[:2000] if output else "Code ran with no output."
    except subprocess.TimeoutExpired:
        return "Code execution timed out after 30 seconds."
    except Exception as e:
        return f"Execution error: {str(e)}"


@tool
def github_push_file(repo_name: str, filepath: str, content: str, commit_message: str) -> str:
    """Creates or updates a file in any GitHub repository."""
    try:
        auth = Auth.Token(GITHUB_TOKEN)
        g = Github(auth=auth)
        user = g.get_user()
        repo = user.get_repo(repo_name)
        try:
            existing = repo.get_contents(filepath)
            repo.update_file(existing.path, commit_message, content, existing.sha)
            return f"Updated {filepath} in {repo_name}."
        except Exception:
            repo.create_file(filepath, commit_message, content)
            return f"Created {filepath} in {repo_name}."
    except Exception as e:
        return f"GitHub error: {str(e)}"


@tool
def draft_document(title: str, content: str, output_format: str = "markdown") -> str:
    """Drafts a document (proposal, report, email body, etc.) and saves it locally."""
    ext = "md" if output_format == "markdown" else "txt"
    filename = f"./drafts/{title.replace(' ', '_').lower()}.{ext}"
    os.makedirs("./drafts", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{content}")
    return f"Document '{title}' drafted and saved to {filename}"
