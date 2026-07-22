import os
import requests
from langchain.tools import tool
from src.memory_manager import memory_manager

@tool
def search_second_brain(query: str, section: str = "how_i_think") -> str:
    """Searches the second brain (my-obsidian-vault). Section can be 'how_i_think' or 'lessons'."""
    try:
        if section == "lessons":
            results = memory_manager.query_lessons(query)
        else:
            results = memory_manager.query_how_i_think(query)
        if not results:
            return "No matching notes found in second brain."
        return "\n\n".join([str(res) for res in results])
    except Exception as e:
        return f"Error searching second brain: {str(e)}"

@tool
def write_lesson(title: str, content: str) -> str:
    """Writes a new lesson learned back to the second brain memory vault."""
    try:
        memory_manager.write_lesson(title, content)
        return f"Successfully saved lesson '{title}' to second brain."
    except Exception as e:
        return f"Error writing lesson: {str(e)}"

@tool
def pinterest_search(query: str) -> str:
    """Searches Pinterest for visual inspiration, mood boards, images, or short video clips."""
    token = os.getenv("PINTEREST_ACCESS_TOKEN", "")
    if token:
        try:
            url = f"https://api.pinterest.com/v5/search/pins?query={query}"
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                items = res.json().get("items", [])
                links = [item.get("media", {}).get("images", {}).get("600x", {}).get("url") or item.get("link") for item in items[:5]]
                return f"Found Pinterest results for '{query}':\n" + "\n".join(filter(None, links))
        except Exception as e:
            print(f"Pinterest API search fallback: {e}")
            
    # Web fallback for Pinterest search
    return f"Pinterest search query prepared: '{query}'. Use web search or browser for visual pin details."

@tool
def pinterest_pin(board_id: str, image_url: str, note: str) -> str:
    """Saves and pins an image/clip to a specific Pinterest board."""
    token = os.getenv("PINTEREST_ACCESS_TOKEN", "")
    if not token:
        return f"Simulated Pinning image {image_url} to Pinterest Board '{board_id}' with note: '{note}' (PINTEREST_ACCESS_TOKEN not set)."
    try:
        url = "https://api.pinterest.com/v5/pins"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "board_id": board_id,
            "media_source": {"source_type": "image_url", "url": image_url},
            "note": note
        }
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        if res.status_code in [200, 201]:
            return f"Successfully pinned to board {board_id}!"
        return f"Pinterest API returned status {res.status_code}: {res.text}"
    except Exception as e:
        return f"Error pinning to Pinterest: {str(e)}"
