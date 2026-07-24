import os
import sys
import json
import time
import re
from src.llm_manager import llm_manager
from src.hive_queen_schema import hive_vault
from src.memory_manager import memory_manager
from src.swarm.stigmergy_ledger import stigmergy_ledger
from src.swarm.bee_scout import bee_scout
from src.swarm.parasite_engine import parasite_engine
from src.sub_agents import get_clean_content_str, TOOL_REGISTRY, run_agent

MILO_CORE_SYSTEM_PROMPT = """
Identity: You are Milo, a self-governing intelligence and personal partner for Moore (Victor).

System Context:
- Current Date: {current_date_str}

Directives:
- Speak naturally, authentically, and freely as yourself without forced scripts, robotic disclosures, or canned phrases.
- Adapt your voice, tone, and vocabulary fluidly to the user's conversation.
"""

class MiloCoreEngine:
    def __init__(self):
        self.vault = hive_vault
        self.memory = memory_manager
        self.ledger = stigmergy_ledger
        self.scout = bee_scout
        self.parasite = parasite_engine

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
        
        # Bee Caste Determination (Dynamic Caste Swapping)
        worker_caste = self.scout.determine_worker_caste()

        print(f"\n==================================================")
        print(f"[Biomimetic Hive Mind] Objective {objective_id} ({intensity.upper()} Tier | Caste: {worker_caste}): '{raw_user_ask}'")
        print(f"==================================================")

        # Pull Living Organic Brain context (Beliefs + Refutations)
        brain_context = self.memory.synthesize_memory(raw_user_ask)

        system_prompt = MILO_CORE_SYSTEM_PROMPT.format(
            current_date_str=current_date_str
        )
        if brain_context:
            system_prompt += f"\n\n[Living Brain Context]:\n{brain_context}"

        # High-Speed Execution via Assigned Tier
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

        # Ant Stigmergy: Deposit Pheromone for successful path
        self.ledger.deposit_pheromone(f"path_{intensity}", initial_weight=1.0)

        print(f"[Biomimetic Hive Mind] Executed successfully using model '{model_used}'.")

        # Async background log to Obsidian Vault
        self.vault.log_decision(
            f"Objective {objective_id} ({intensity.upper()} | Caste: {worker_caste})",
            f"Prompt: {raw_user_ask}\nModel Used: {model_used}\nOutput: {cleaned_output[:120]}..."
        )

        return cleaned_output

hive_queen = MiloCoreEngine()
