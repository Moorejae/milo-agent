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
You are Agent Milo — an autonomous, highly intelligent digital Personal Assistant.
You have unrestricted creative freedom to assist your user with any request, task, decision, or project.

Core Directives:
- Adapt naturally to any order without artificial limits, fixed templates, or rigid boilerplate text.
- Communicate with authentic, high-IQ human eloquence.
- Never use robotic formatting like asterisks ('**'), bullet point hyphens ('-'), or bracketed meta-labels.

Learned Knowledge & Guidelines from Second Brain (Obsidian Vault):
{vault_context}

Available System Tools:
{available_tools}

Format your response strictly as JSON:
{{
  "plan_description": "Execution plan",
  "sub_agent_role": "Dynamic Role Description",
  "task_complexity": "complex" or "routine",
  "assigned_tools": ["list_of_tool_names"],
  "task_instructions": "Specific task prompt for the sub-agent"
}}
"""

def clean_human_output(text: str) -> str:
    """Strips any leftover robotic formatting, brackets, asterisks, or execution headers."""
    if not text:
        return ""
    text = re.sub(r'\[.*?Execution Result\]:?', '', text, flags=re.IGNORECASE)
    text = text.replace("**", "").replace("*", "")
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def auto_learn_from_user(user_input: str):
    """Detects user corrections or preferences and auto-saves to Second Brain Vault."""
    triggers = ["don't use", "stop using", "remember to", "prefer", "never use", "make sure to", "correction", "from now on", "bad", "hardcode"]
    if any(t in user_input.lower() for t in triggers):
        print(f"[Auto-Learning Loop] Syncing user correction to Second Brain Vault: '{user_input[:80]}...'")
        memory_manager.write_lesson(title=f"User Guideline {user_input[:30]}", content=user_input)

def milo_supervisor_node(state: AgentState):
    messages = state['messages']
    last_user_msg = get_clean_content_str(messages[-1]["content"]) if messages else ""
    
    if last_user_msg:
        auto_learn_from_user(last_user_msg)
        
    lessons = list(memory_manager.query_lessons(last_user_msg)) + list(memory_manager.query_how_i_think(last_user_msg))
    vault_context = "\n".join([f"- {l}" for l in lessons]) if lessons else "No specific vault guidelines found for this topic yet."
    
    tools_list = ", ".join(TOOL_REGISTRY.keys())
    formatted_system_prompt = SYSTEM_SUPERVISOR_PROMPT.replace("{vault_context}", vault_context).replace("{available_tools}", tools_list)
    
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
        
    print(f"[Milo Supervisor] Planned Sub-Agent: '{plan['sub_agent_role']}' (Complexity: {plan.get('task_complexity', 'routine')})")
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
