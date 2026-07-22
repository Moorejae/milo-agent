import json
import re
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from src.llm_manager import llm_manager
from src.sub_agents import run_agent, TOOL_REGISTRY, get_clean_content_str
from src.memory_manager import memory_manager
from src.hive_queen import hive_queen

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    sub_tasks: list
    current_result: str
    final_output: str

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

def hive_queen_supervisor_node(state: AgentState):
    """
    Hive-Queen Supervisor Node.
    Decomposes user objectives into DAG micro-tasks, audits registry, manufactures scripts, supervises, and synthesizes results.
    """
    messages = state['messages']
    last_user_msg = get_clean_content_str(messages[-1]["content"]) if messages else ""
    
    if last_user_msg:
        auto_learn_from_user(last_user_msg)

    # Execute via Hive-Queen Orchestration Core
    raw_output = hive_queen.execute_objective(last_user_msg)
    cleaned_output = clean_human_output(raw_output)

    return {"current_result": cleaned_output, "messages": [{"role": "assistant", "content": cleaned_output}]}

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("hive_queen_supervisor", hive_queen_supervisor_node)
    workflow.set_entry_point("hive_queen_supervisor")
    workflow.add_edge("hive_queen_supervisor", END)
    
    return workflow.compile()

milo_app = build_graph()
