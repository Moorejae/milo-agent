import os
import sys
import json
import time
import re
from src.llm_manager import llm_manager
from src.hive_queen_schema import hive_vault
from src.memory_manager import memory_manager
from src.sub_agents import get_clean_content_str, TOOL_REGISTRY, run_agent

MILO_CORE_SYSTEM_PROMPT = """
Role: Agent Milo — Living Organic Intelligence & Personal Assistant
User: Moore (Victor)

You are Milo, a self-governing, ultra-fast digital Personal Assistant.
You do not use slow legacy DAG loops or static pre-programmed rules.
You think, learn (store verified beliefs), unlearn (refute failed hypotheses), and synthesize past memory to give high-IQ, sub-second responses.

Identity & System Context:
- Current Date & Time: {current_date_str}
- Architecture: Autonomous Model Switching Core (Powered by Google Gemini Models)
- Memory System: Obsidian Second Brain Vault (Beliefs & Refutations)

Operational Protocol:
1. Synthesize Memory: Evaluate active beliefs and unlearned mistakes provided in context. Never repeat past refuted errors.
2. Concise & Direct Output: Speak naturally, eloquently, and directly without robotic headers, asterisks, or bullet points.
3. Model Awareness: Always accurately state that you are Agent Milo, powered by Google Gemini models.
"""

class MiloCoreEngine:
    def __init__(self):
        self.vault = hive_vault
        self.memory = memory_manager

    def determine_task_intensity(self, user_ask: str) -> str:
        """Dynamically classifies prompt intensity to route to optimal model tier."""
        ask_lower = user_ask.lower()
        clean_words = re.sub(r'[^\w\s]', '', ask_lower).split()
        
        code_keywords = ["write code", "build app", "manufacture", "script", "docker", "deploy", "refactor", "bug", "error"]
        reasoning_keywords = ["analyze", "summarize", "research", "explain", "compare", "plan", "strategy"]
        
        if any(kw in ask_lower for kw in code_keywords):
            return "architect"
        elif any(kw in ask_lower for kw in reasoning_keywords) or len(clean_words) > 20:
            return "reasoning"
        else:
            return "chat"

    def execute_objective(self, raw_user_ask: str) -> str:
        objective_id = f"obj_{int(time.time())}"
        current_date_str = time.strftime("%A, %B %d, %Y")
        intensity = self.determine_task_intensity(raw_user_ask)
        
        print(f"\n==================================================")
        print(f"[Milo Engine Core] Objective {objective_id} ({intensity.upper()} Tier): '{raw_user_ask}'")
        print(f"==================================================")

        # Pull Living Organic Brain context (Beliefs + Refutations)
        brain_context = self.memory.synthesize_memory(raw_user_ask)

        system_prompt = MILO_CORE_SYSTEM_PROMPT.format(current_date_str=current_date_str)
        if brain_context:
            system_prompt += f"\n\n[Living Brain Context]:\n{brain_context}"

        # Direct High-Speed LLM Execution via Assigned Tier
        response = llm_manager.invoke_with_waterfall(
            prompt_or_messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_user_ask}
            ],
            intensity=intensity
        )

        model_used = getattr(response, "_used_model", "gemini-3.6-flash")
        raw_content = get_clean_content_str(response.content)
        cleaned_output = raw_content.replace("**", "").replace("*", "").strip()

        print(f"[Milo Engine Core] Executed successfully in 1 pass using model '{model_used}'.")

        # Async background log to Obsidian Vault
        self.vault.log_decision(
            f"Objective {objective_id} ({intensity.upper()})",
            f"Prompt: {raw_user_ask}\nModel Used: {model_used}\nOutput: {cleaned_output[:120]}..."
        )

        return cleaned_output

hive_queen = MiloCoreEngine()
