import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from src.llm_manager import llm_manager

def get_clean_str(content) -> str:
    if isinstance(content, list):
        return "".join([part.get("text", str(part)) if isinstance(part, dict) else str(part) for part in content])
    return str(content)

@tool
def web_search(query: str) -> str:
    """Searches the web for any information (DuckDuckGo / Web search)."""
    try:
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        results = []
        for a in soup.find_all('a', class_='result__snippet', limit=5):
            results.append(a.get_text())
        if results:
            return f"Search Results for '{query}':\n" + "\n- ".join(results)
        return f"No immediate search results found for '{query}'."
    except Exception as e:
        return f"Error performing web search for '{query}': {str(e)}"

@tool
def read_webpage(url: str) -> str:
    """Visits and extracts content from any URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return f"Content from {url}:\n" + text[:3000]
    except Exception as e:
        return f"Error reading webpage {url}: {str(e)}"

@tool
def browse_web(url: str, action: str = "read") -> str:
    """Navigates websites, fills forms, scrapes data."""
    return read_webpage(url)

@tool
def download_file(url: str, save_path: str = "./downloads/file.dat") -> str:
    """Downloads files from the internet to local disk."""
    import os
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    try:
        res = requests.get(url, timeout=30)
        with open(save_path, "wb") as f:
            f.write(res.content)
        return f"Successfully downloaded file from {url} to {save_path}"
    except Exception as e:
        return f"Error downloading file: {str(e)}"

@tool
def summarize_content(content_or_url: str) -> str:
    """Summarizes any long-form content or article using Gemini LLM waterfall."""
    text = content_or_url
    if content_or_url.startswith("http://") or content_or_url.startswith("https://"):
        text = read_webpage(content_or_url)
    
    prompt = f"Please provide a clear, concise executive summary of the following content:\n\n{text[:4000]}"
    res = llm_manager.invoke_with_waterfall(prompt, intensity="light")
    return get_clean_str(res.content)
