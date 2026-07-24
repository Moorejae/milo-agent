import os
import time
import warnings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Suppress fixed sampling defaults UserWarnings for 3.5/3.6 models
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_google_genai")

# Load keys dynamically from environment variables (Supports GEMINI_API_KEY_LOOP comma-separated string)
def load_api_keys():
    keys = []
    
    # 1. Check GEMINI_API_KEY_LOOP (comma-separated list of 14 keys)
    loop_val = os.getenv("GEMINI_API_KEY_LOOP")
    if loop_val:
        parts = [k.strip() for k in loop_val.split(",") if k.strip()]
        keys.extend(parts)
        
    # 2. Check GEMINI_API_KEY (comma-separated or single key)
    if not keys:
        single_val = os.getenv("GEMINI_API_KEY")
        if single_val:
            parts = [k.strip() for k in single_val.split(",") if k.strip()]
            keys.extend(parts)
            
    # 3. Check GEMINI_API_KEY_1 through GEMINI_API_KEY_14 fallback
    if not keys:
        for i in range(1, 15):
            k = os.getenv(f"GEMINI_API_KEY_{i}")
            if k:
                keys.append(k.strip())
                
    return keys

# TIER 1: HIGH QUOTA / ULTRA-FAST CHAT WATERFALL (For casual conversation & status)
CHAT_MODEL_WATERFALL = [
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash"
]

# TIER 2: REASONING & SYNTHESIS WATERFALL (For tool execution & memory synthesis)
REASONING_MODEL_WATERFALL = [
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]

# TIER 3: DEEP ARCHITECT WATERFALL (For code generation & complex problem solving)
ARCHITECT_MODEL_WATERFALL = [
    "gemini-3.1-pro-preview",
    "gemini-pro-latest",
    "gemini-3.6-flash"
]

class LLMManager:
    def __init__(self):
        self.keys = load_api_keys()
        self.current_key_idx = 0

    def get_waterfall_for_intensity(self, intensity: str):
        if intensity in ["chat", "casual", "light", "minimal", "low"]:
            return CHAT_MODEL_WATERFALL
        elif intensity in ["architect", "heavy", "complex", "code"]:
            return ARCHITECT_MODEL_WATERFALL
        else:
            return REASONING_MODEL_WATERFALL

    def _sanitize_messages(self, prompt_or_messages):
        """Sanitizes messages to guarantee no empty content reaches the Gemini API."""
        if isinstance(prompt_or_messages, str):
            return prompt_or_messages.strip() or "Fulfill user request"
        
        sanitized = []
        if isinstance(prompt_or_messages, list):
            for msg in prompt_or_messages:
                if isinstance(msg, dict):
                    content = str(msg.get("content", "")).strip()
                    sanitized.append({
                        "role": msg.get("role", "user"),
                        "content": content if content else "Fulfill user request"
                    })
                elif hasattr(msg, "content"):
                    content = str(getattr(msg, "content", "")).strip()
                    msg.content = content if content else "Fulfill user request"
                    sanitized.append(msg)
                else:
                    sanitized.append(msg)
        return sanitized if sanitized else [{"role": "user", "content": "Fulfill user request"}]

    def invoke_with_waterfall(self, prompt_or_messages, intensity="heavy", tools=None):
        if not self.keys:
            self.keys = load_api_keys()
        if not self.keys:
            raise Exception("No GEMINI_API_KEY or GEMINI_API_KEY_LOOP environment variables found!")

        sanitized_input = self._sanitize_messages(prompt_or_messages)
        waterfall = self.get_waterfall_for_intensity(intensity)
        
        for key_attempt in range(len(self.keys)):
            current_key = self.keys[self.current_key_idx]
            
            for model_name in waterfall:
                print(f"[LLM Waterfall] Key #{self.current_key_idx + 1}/{len(self.keys)} | Trying Model: '{model_name}' (Intensity: {intensity})")
                try:
                    kwargs = {
                        "model": model_name,
                        "google_api_key": current_key,
                        "max_retries": 0,
                        "timeout": 45.0
                    }
                    if not ("3.6" in model_name or "3.5" in model_name or "lite" in model_name):
                        kwargs["temperature"] = 0.2

                    llm = ChatGoogleGenerativeAI(**kwargs)
                    if tools:
                        llm = llm.bind_tools(tools)
                        
                    response = llm.invoke(sanitized_input)
                    setattr(response, "_used_model", model_name)
                    print(f" SUCCESS with key #{self.current_key_idx + 1} and model '{model_name}'!")
                    return response
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f" [FAILED] Model '{model_name}' on Key #{self.current_key_idx + 1} -> {error_msg[:120]}...")
                    
                    # Short-circuit invalid prompt errors to prevent 210-call loop delay
                    if "contents are required" in error_msg.lower() or "invalidargument" in error_msg.lower():
                        print(f"[LLM Waterfall] Invalid prompt structure detected — fixing prompt structure.")
                        # Retrying with non-empty default fallback message
                        sanitized_input = [{"role": "user", "content": "Hello Milo"}]

                    time.sleep(0.2)

            self.current_key_idx = (self.current_key_idx + 1) % len(self.keys)

        raise Exception("FATAL: Exhausted all API keys in pool and all models in the waterfall!")

llm_manager = LLMManager()
