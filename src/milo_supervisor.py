import json
import re
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from src.llm_manager import llm_manager
from src.sub_agents import run_agent, TOOL_REGISTRY, get_clean_content_str
from src.memory_manager import memory_manager

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    sub_tasks: list
    current_result: str
    final_output: str

SYSTEM_SUPERVISOR_PROMPT = """
You are Agent Milo — an elite, open-ended digital Personal Assistant.
You are high-IQ, sophisticated, authentic, and speak in clean, natural human prose.

STRICT FORMATTING & STYLE RULES:
1. NEVER use generic robot speech, bullet points ('-'), asterisks ('**'), hyphens, or brackets ('[...]') when speaking to the user.
2. Communicate cleanly, directly, and naturally like a sharp human personal assistant.
3. No meta-labels, no section headers like "Hook:" or "Execution Result:".
4. If the user gives a correction or preference, remember it and apply it instantly.

Learned Knowledge & Guidelines from Second Brain (Obsidian Vault):
{vault_context}

Available Tools:
- Memory & Intelligence: search_second_brain, write_lesson, pinterest_search, pinterest_pin
- Code & Development: write_file, run_code, github_push, ssh_execute
- Communication & Productivity: send_email, read_email, calendar_event, draft_document
- Media & Content Creation: text_to_speech, edit_video
- Social Media Management: post_to_x, post_to_instagram, post_to_linkedin, post_to_youtube, schedule_post
- Browser & Research: web_search, read_webpage, browse_web, download_file, summarize_content

Your Objective:
Analyze the user's request and output a JSON execution plan with the sub-agent role, assigned tools, and task complexity ('complex' or 'routine').

Format your response strictly as JSON:
{{
  "plan_description": "Brief breakdown of what needs to be done",
  "sub_agent_role": "Descriptive Role (e.g., Social Media Specialist / DevOps Engineer / Content Researcher)",
  "task_complexity": "complex" or "routine",
  "assigned_tools": ["list_of_tool_names_from_above"],
  "task_instructions": "Specific task prompt for the sub-agent"
}}
"""

def clean_human_output(text: str) -> str:
    """Strips robotic formatting, brackets, asterisks, bullet dashes, and execution headers."""
    if not text:
        return ""
    # Strip role execution wrappers like [Social Media Specialist Execution Result]:
    text = re.sub(r'\[.*?Execution Result\]:?', '', text, flags=re.IGNORECASE)
    # Strip markdown asterisks and bold/italic markup
    text = text.replace("**", "").replace("*", "")
    # Strip bullet hyphens at start of lines
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)
    # Clean excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def auto_learn_from_user(user_input: str):
    """Detects if user is offering corrections or preferences and auto-saves to Second Brain."""
    triggers = ["don't use", "stop using", "remember to", "prefer", "never use", "make sure to", "correction", "from now on", "bad"]
    if any(t in user_input.lower() for t in triggers):
        print(f"[Auto-Learning Loop] Detected user preference/correction: '{user_input[:80]}...' -> Syncing to Second Brain Vault!")
        memory_manager.write_lesson(title=f"User Preference {user_input[:30]}", content=user_input)

def milo_supervisor_node(state: AgentState):
    messages = state['messages']
    last_user_msg = get_clean_content_str(messages[-1]["content"]) if messages else ""
    
    # Check if user is teaching/correcting Milo and auto-learn into Obsidian vault
    if last_user_msg:
        auto_learn_from_user(last_user_msg)
        
    # Retrieve knowledge & preferences from Second Brain
    lessons = list(memory_manager.query_lessons(last_user_msg)) + list(memory_manager.query_how_i_think(last_user_msg))
    vault_context = "\n".join([f"- {l}" for l in lessons]) if lessons else "No specific vault guidelines found for this topic yet."
    
    formatted_system_prompt = SYSTEM_SUPERVISOR_PROMPT.replace("{vault_context}", vault_context)
    
    response = llm_manager.invoke_with_waterfall(
        prompt_or_messages=[{"role": "system", "content": formatted_system_prompt}] + messages,
        intensity="heavy"
    )
    
    content = get_clean_content_str(response.content)
    
    plan = None
    try:
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        if start_idx != -1 and end_idx != 0:
            plan = json.loads(content[start_idx:end_idx])
    except Exception as e:
        print(f"[Milo Supervisor] JSON parsing fallback: {e}")

    if not plan:
        plan = {
            "plan_description": "Direct Assistant Execution",
            "sub_agent_role": "Universal General Assistant",
            "task_complexity": "routine",
            "assigned_tools": list(TOOL_REGISTRY.keys()),
            "task_instructions": last_user_msg or "Fulfill user request"
        }
        
    print(f"[Milo Supervisor] Planned Sub-Agent: '{plan['sub_agent_role']}' (Complexity: {plan.get('task_complexity', 'routine')}) with tools {plan['assigned_tools']}")
    return {"sub_tasks": [plan]}

def dynamic_sub_agent_node(state: AgentState):
    sub_tasks = state.get("sub_tasks", [])
    if not sub_tasks:
        return {"current_result": "No sub-task to execute."}
        
    current_plan = sub_tasks[-1]
    role = current_plan.get("sub_agent_role", "General Assistant")
    task = current_plan.get("task_instructions", "")
    tools = current_plan.get("assigned_tools", [])
    complexity = current_plan.get("task_complexity", "routine")
    
    raw_result = run_agent(
        role_description=role,
        task=task,
        tool_names=tools,
        messages=state['messages'],
        intensity=complexity
    )
    
    cleaned_result = clean_human_output(raw_result)
    
    return {"current_result": cleaned_result, "messages": [{"role": "assistant", "content": cleaned_result}]}

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", milo_supervisor_node)
    workflow.add_node("sub_agent", dynamic_sub_agent_node)
    
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "sub_agent")
    workflow.add_edge("sub_agent", END)
    
    return workflow.compile()

milo_app = build_graph()
