import os
from src.llm_manager import llm_manager

# Import all tools from tool modules
from src.tools.memory_tools import search_second_brain, write_lesson, pinterest_search, pinterest_pin
from src.tools.dev_tools import write_file, run_code, github_push, ssh_execute
from src.tools.comms_tools import send_email, read_email, calendar_event, draft_document
from src.tools.media_tools import text_to_speech, edit_video
from src.tools.social_tools import post_to_facebook, post_to_x, post_to_instagram, post_to_linkedin, post_to_youtube, schedule_post
from src.tools.research_tools import web_search, read_webpage, browse_web, download_file, summarize_content

# Global Central Tool Registry mapping tool names to executable LangChain @tool objects
TOOL_REGISTRY = {
    # Memory & Intelligence
    "search_second_brain": search_second_brain,
    "write_lesson": write_lesson,
    "pinterest_search": pinterest_search,
    "pinterest_pin": pinterest_pin,
    
    # Code & Development
    "write_file": write_file,
    "run_code": run_code,
    "github_push": github_push,
    "ssh_execute": ssh_execute,
    
    # Communication & Productivity
    "send_email": send_email,
    "read_email": read_email,
    "calendar_event": calendar_event,
    "draft_document": draft_document,
    
    # Media & Content Creation
    "text_to_speech": text_to_speech,
    "edit_video": edit_video,
    
    # Social Media Management
    "post_to_facebook": post_to_facebook,
    "post_to_x": post_to_x,
    "post_to_instagram": post_to_instagram,
    "post_to_linkedin": post_to_linkedin,
    "post_to_youtube": post_to_youtube,
    "schedule_post": schedule_post,
    
    # Browser & Research
    "web_search": web_search,
    "read_webpage": read_webpage,
    "browse_web": browse_web,
    "download_file": download_file,
    "summarize_content": summarize_content
}

def get_clean_content_str(content) -> str:
    """
    Helper to convert string or list-based content into a clean string.
    Properly filters out Gemma internal 'thinking' blocks and extracts pure text responses.
    """
    if not content:
        return ""

    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict):
                # Filter out Gemma 'thinking' blocks
                if part.get("type") == "thinking":
                    continue
                elif part.get("type") == "text" and "text" in part:
                    text_parts.append(part["text"])
                elif "text" in part:
                    text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
        return "\n".join(text_parts).strip()
    
    return str(content).strip()

def run_agent(role_description: str, task: str, tool_names: list, messages: list = None, intensity: str = "routine") -> str:
    """
    Executes a dynamic sub-agent with a assigned subset of tools from TOOL_REGISTRY.
    """
    print(f"[Dynamic Sub-Agent: {role_description}] Running with tools: {tool_names} (Intensity: '{intensity}')")
    
    # Resolve tools from registry
    selected_tools = [TOOL_REGISTRY[name] for name in tool_names if name in TOOL_REGISTRY]
    
    system_prompt = (
        f"You are a specialized sub-agent fulfilling the role: '{role_description}'.\n"
        f"User Task: {task}\n\n"
        "Directives:\n"
        "- Use your available tools if needed to gather information or perform actions.\n"
        "- Provide a direct, concise, high-IQ final answer without robotic fluff or meta-headers.\n"
        "- Do not use asterisks or bullet points in final text output."
    )
    
    input_messages = [{"role": "system", "content": system_prompt}]
    if messages:
        input_messages.extend(messages[-3:])  # Include recent conversation context
        
    response = llm_manager.invoke_with_waterfall(
        prompt_or_messages=input_messages,
        intensity=intensity,
        tools=selected_tools if selected_tools else None
    )
    
    cleaned = get_clean_content_str(response.content)
    return cleaned
