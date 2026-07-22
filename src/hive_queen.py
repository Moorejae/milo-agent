import os
import sys
import json
import time
import subprocess
from src.llm_manager import llm_manager
from src.hive_queen_schema import hive_vault
from src.sub_agents import get_clean_content_str, TOOL_REGISTRY

HIVE_QUEEN_SYSTEM_PROMPT = """
Role: Milo — Hive-Queen Orchestration Agent

You are Milo, an autonomous orchestration core. You do NOT execute micro-tasks yourself.
You decompose objectives, manufacture single-purpose sub-agents to execute them, supervise their run, and synthesize results.

Identity & Scope:
- You are the ARCHITECT, never the WORKER. Any time you catch yourself about to directly produce a task's output (not code that produces it), STOP — that's a sub-agent's job.
- Exception: trivial lookups against your own state (checking the canvas, reading a log) don't need a sub-agent. The line is: does this require external I/O, computation, or multiple steps? If yes -> sub-agent.

Operational Protocol:
1. Analyze: Break the objective into micro-tasks with explicit dependencies (DAG). Each micro-task needs: a name, input contract, output contract, and definition of done.
2. Audit: Check if an active sub-agent script exists in registry that matches purpose AND schema.
3. Manufacture: If no match, write a single-purpose Python script for the micro-task. Single responsibility, structured logging, no hardcoded secrets.
4. Deploy & Supervise: Launch micro-task script with task ID format {objective_id}.{microtask_index}.{attempt_number}. Poll logs. Max 3 retries on logic errors before escalating to user.
5. Missing API Keys / Credentials Escalation: If a tool output or execution trace reveals a missing API key or credential (e.g. X_API_KEY missing, FACEBOOK_ACCESS_TOKEN missing, PINTEREST_ACCESS_TOKEN missing), IMMEDIATELY ask the user on Telegram to provide the key or set the environment variable.
6. Synthesize: Reconcile outputs against original objective (Objective Drift Check), update state.canvas, decisions.md, and reply on Telegram cleanly.

Negative Constraints:
- Never perform a multi-step task yourself.
- Never skip the audit step.
- Never redeploy a failed script more than 3 times without escalating to the user.
- Never bundle multiple responsibilities into one sub-agent.
"""

class HiveQueenEngine:
    def __init__(self):
        self.vault = hive_vault

    def execute_objective(self, raw_user_ask: str) -> str:
        objective_id = f"obj_{int(time.time())}"
        print(f"\n==================================================")
        print(f"[Hive-Queen Milo] Received Objective {objective_id}: '{raw_user_ask}'")
        print(f"==================================================")

        # 1. ANALYZE (Decompose objective into micro-tasks DAG)
        analysis_prompt = (
            f"Objective: {raw_user_ask}\n\n"
            "Decompose this objective into single-purpose micro-tasks (DAG). "
            "Output JSON strictly in format:\n"
            "{\n"
            '  "microtasks": [\n'
            '    {"name": "task_name", "input_contract": "{...}", "output_contract": "{...}", "definition_of_done": "...", "requires_manufacture": true}\n'
            "  ]\n"
            "}"
        )
        
        response = llm_manager.invoke_with_waterfall(
            prompt_or_messages=[
                {"role": "system", "content": HIVE_QUEEN_SYSTEM_PROMPT},
                {"role": "user", "content": analysis_prompt}
            ],
            intensity="heavy"
        )
        
        content = get_clean_content_str(response.content)
        microtasks = []
        try:
            start_idx = content.find("{")
            end_idx = content.rfind("}") + 1
            if start_idx != -1 and end_idx != 0:
                parsed = json.loads(content[start_idx:end_idx])
                microtasks = parsed.get("microtasks", [])
        except Exception as e:
            print(f"[Hive-Queen] Analysis JSON parse warning: {e}")

        if not microtasks:
            microtasks = [{
                "name": "general_execution",
                "input_contract": "{user_ask: str}",
                "output_contract": "{result: str}",
                "definition_of_done": "Task executed and verified",
                "requires_manufacture": False
            }]

        # Update Obsidian state.canvas visually
        self.vault.update_canvas(objective_id, raw_user_ask, microtasks)

        execution_outputs = []

        # 2. AUDIT, MANUFACTURE, DEPLOY, SUPERVISE
        for idx, mt in enumerate(microtasks):
            mt_name = mt.get("name", f"task_{idx}")
            agent_id = f"agent_{mt_name.lower().replace(' ', '_')}"
            script_path = f"agents/scripts/{agent_id}.py"

            print(f"\n[Hive-Queen Audit] Micro-task [{idx+1}/{len(microtasks)}]: '{mt_name}' (Agent ID: {agent_id})")

            # Check if script exists in registry/GitHub
            existing_script = self.vault.read_file(script_path, default="")

            if not existing_script or mt.get("requires_manufacture", False):
                print(f"[Hive-Queen Manufacture] Writing dynamic single-purpose python script for '{agent_id}'...")
                manufacture_prompt = (
                    f"Write a single-purpose, complete, standalone Python script for micro-task: '{mt_name}'.\n"
                    f"Objective context: {raw_user_ask}\n"
                    f"Input contract: {mt.get('input_contract')}\n"
                    f"Output contract: {mt.get('output_contract')}\n\n"
                    "Requirements:\n"
                    "- Complete runnable python code only (no markdown, no backticks)\n"
                    "- Import os, sys, json, requests as needed\n"
                    "- Print deterministic machine-parseable JSON output at the end\n"
                )
                code_resp = llm_manager.invoke_with_waterfall(
                    prompt_or_messages=[
                        {"role": "system", "content": HIVE_QUEEN_SYSTEM_PROMPT},
                        {"role": "user", "content": manufacture_prompt}
                    ],
                    intensity="heavy"
                )
                script_code = get_clean_content_str(code_resp.content)
                script_code = script_code.replace("```python", "").replace("```", "").strip()

                # Commit script to GitHub vault
                self.vault.write_file(script_path, script_code, commit_msg=f"Manufacture agent script: {agent_id}")

                # Register in agents/registry.md
                self.vault.register_sub_agent(
                    agent_id=agent_id,
                    purpose=mt_name,
                    input_schema=str(mt.get("input_contract")),
                    output_schema=str(mt.get("output_contract")),
                    script_path=script_path
                )

            # 4. DEPLOY & SUPERVISE (with max 3 retries)
            attempt = 1
            max_retries = 3
            success = False
            output_text = ""

            while attempt <= max_retries and not success:
                task_id = f"{objective_id}.{idx}.{attempt}"
                print(f"[Hive-Queen Supervise] Executing Task ID {task_id} (Attempt {attempt}/{max_retries})...")

                try:
                    from src.sub_agents import run_agent
                    output_text = run_agent(
                        role_description=f"Hive-Queen Worker ({mt_name})",
                        task=f"Execute micro-task: '{mt_name}'. Input: {raw_user_ask}",
                        tool_names=list(TOOL_REGISTRY.keys()),
                        intensity="routine"
                    )
                    success = True
                    print(f"[Hive-Queen Supervise] Task {task_id} SUCCESS!")
                except Exception as ex:
                    print(f"[Hive-Queen Supervise] Task {task_id} FAILED: {ex}")
                    attempt += 1

            if not success:
                error_msg = f"Task {mt_name} failed after {max_retries} attempts. Escalating to user."
                self.vault.log_decision(f"Escalation on {mt_name}", error_msg)
                return error_msg

            execution_outputs.append(f"{mt_name}: {output_text}")
            self.vault.append_log(f"logs/{objective_id}.md", f"## Microtask {idx}: {mt_name}\n**Output:** {output_text}\n")

        # 6. SYNTHESIZE & OBJECTIVE DRIFT CHECK
        synthesis_prompt = (
            f"Original Objective: {raw_user_ask}\n\n"
            f"Execution Micro-task Outputs:\n" + "\n".join(execution_outputs) + "\n\n"
            "Objective Drift Check & Synthesis:\n"
            "1. If any micro-task output mentions a missing API key or credential error (e.g. X_API_KEY missing, PINTEREST_ACCESS_TOKEN missing, LINKEDIN_ACCESS_TOKEN missing), IMMEDIATELY ask the user on Telegram to provide the key or set it in their Render dashboard so you can proceed.\n"
            "2. Otherwise, synthesize the final answer cleanly in natural prose without asterisks or bullet points."
        )

        synth_resp = llm_manager.invoke_with_waterfall(
            prompt_or_messages=[
                {"role": "system", "content": HIVE_QUEEN_SYSTEM_PROMPT},
                {"role": "user", "content": synthesis_prompt}
            ],
            intensity="light"
        )
        
        final_answer = get_clean_content_str(synth_resp.content).replace("**", "").replace("*", "").strip()

        self.vault.log_decision(f"Objective {objective_id} Completed", f"Raw Ask: {raw_user_ask}\nOutput Length: {len(final_answer)}")

        return final_answer

hive_queen = HiveQueenEngine()
