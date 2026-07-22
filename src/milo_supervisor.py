import json
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from src.llm_manager import llm_manager
from src.sub_agents import run_agent, TOOL_REGISTRY, get_clean_content_str

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    sub_tasks: list
    current_result: str
    final_output: str

SYSTEM_SUPERVISOR_PROMPT = """
You are Agent Milo — an elite, open-ended digital Personal Assistant.
There is no restriction on what you can do for your user. You take orders, plan the best sub-agents and tool combinations, and execute them cleanly.

Your Available Tool Names:
- Memory & Intelligence: search_second_brain, write_lesson, pinterest_search, pinterest_pin
- Code & Development: write_file, run_code, github_push, ssh_execute
- Communication & Productivity: send_email, read_email, calendar_event, draft_document
- Media & Content Creation: text_to_speech, edit_video
- Social Media Management: post_to_x, post_to_instagram, post_to_linkedin, post_to_youtube, schedule_post
- Browser & Research: web_search, read_webpage, browse_web, download_file, summarize_content

Your Objective:
Analyze the user's request and output a JSON execution plan with the sub-agent role, assigned tools, and task complexity ('complex' for heavy reasoning/coding or 'routine' for simple search/fetching/posting).

Format your response strictly as JSON:
{
  "plan_description": "Brief breakdown of what needs to be done",
  "sub_agent_role": "Descriptive Role (e.g., Social Media Specialist / DevOps Engineer / Content Researcher)",
  "task_complexity": "complex" or "routine",
  "assigned_tools": ["list_of_tool_names_from_above"],
  "task_instructions": "Specific task prompt for the sub-agent"
}
"""

def milo_supervisor_node(state: AgentState):
    """
    Agent Milo's Supervisor Node. Parses user requests into dynamic sub-agent execution plans using 14-key pooling and model waterfall.
    """
    messages = state['messages']
    
    response = llm_manager.invoke_with_waterfall(
        prompt_or_messages=[{"role": "system", "content": SYSTEM_SUPERVISOR_PROMPT}] + messages,
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
            "task_instructions": get_clean_content_str(messages[-1]["content"]) if messages else "Fulfill user request"
        }
        
    print(f"[Milo Supervisor] Planned Sub-Agent: '{plan['sub_agent_role']}' (Complexity: {plan.get('task_complexity', 'routine')}) with tools {plan['assigned_tools']}")
    return {"sub_tasks": [plan]}

def dynamic_sub_agent_node(state: AgentState):
    """
    Executes the planned dynamic sub-agent with its assigned toolset.
    """
    sub_tasks = state.get("sub_tasks", [])
    if not sub_tasks:
        return {"current_result": "No sub-task to execute."}
        
    current_plan = sub_tasks[-1]
    role = current_plan.get("sub_agent_role", "General Assistant")
    task = current_plan.get("task_instructions", "")
    tools = current_plan.get("assigned_tools", [])
    complexity = current_plan.get("task_complexity", "routine")
    
    result = run_agent(
        role_description=role,
        task=task,
        tool_names=tools,
        messages=state['messages'],
        intensity=complexity
    )
    
    return {"current_result": result, "messages": [{"role": "assistant", "content": f"[{role} Execution Result]:\n{result}"}]}

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", milo_supervisor_node)
    workflow.add_node("sub_agent", dynamic_sub_agent_node)
    
    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "sub_agent")
    workflow.add_edge("sub_agent", END)
    
    return workflow.compile()

milo_app = build_graph()
