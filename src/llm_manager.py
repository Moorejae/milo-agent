import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

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

# Corrected Waterfall Priority:
# Tier 1: Highest Intelligence 3.x Flagships (3.6-flash, 3.5-flash, 3.1-pro, pro-latest)
# Tier 2: High-Quota Gemma Models (gemma-4-31b-it, gemma-4-26b-a4b-it -> 14,000 Requests/Day!)
# Tier 3: High-Speed 2.5/2.0 Flash & Lite Fallbacks
FULL_MODEL_WATERFALL = [
    # --- TIER 1: FLAGSHIP 3.X SMARTEST MODELS FIRST ---
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.1-pro-preview",
    "gemini-pro-latest",
    "gemini-flash-latest",
    
    # --- TIER 2: 14,000 RPD MASSIVE QUOTA GEMMA MODELS ---
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it",
    "gemma-2-27b-it",

    # --- TIER 3: HIGH-SPEED FLASH & 2.X FALLBACKS ---
    "gemini-3.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash"
]

# Routine waterfall prioritizing 3.5/3.6 Flash and 14k RPD Gemma before 2.x fallbacks
ROUTINE_MODEL_WATERFALL = [
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]

class LLMManager:
    def __init__(self):
        self.keys = load_api_keys()
        self.current_key_idx = 0

    def get_waterfall_for_intensity(self, intensity: str):
        if intensity in ["heavy", "complex", "antigravity", "architect"]:
            return FULL_MODEL_WATERFALL
        elif intensity in ["light", "routine", "minimal", "low"]:
            return ROUTINE_MODEL_WATERFALL
        else:
            return FULL_MODEL_WATERFALL

    def invoke_with_waterfall(self, prompt_or_messages, intensity="heavy", tools=None):
        if not self.keys:
            self.keys = load_api_keys()
        if not self.keys:
            raise Exception("No GEMINI_API_KEY or GEMINI_API_KEY_LOOP environment variables found!")

        waterfall = self.get_waterfall_for_intensity(intensity)
        
        for key_attempt in range(len(self.keys)):
            current_key = self.keys[self.current_key_idx]
            
            for model_name in waterfall:
                print(f"[LLM Waterfall] Key #{self.current_key_idx + 1}/{len(self.keys)} | Trying Model: '{model_name}' (Intensity: {intensity})")
                try:
                    llm = ChatGoogleGenerativeAI(
                        model=model_name,
                        google_api_key=current_key,
                        temperature=0.2,
                        max_retries=0
                    )
                    if tools:
                        llm = llm.bind_tools(tools)
                        
                    response = llm.invoke(prompt_or_messages)
                    print(f" SUCCESS with key #{self.current_key_idx + 1} and model '{model_name}'!")
                    return response
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f" [FAILED] Model '{model_name}' on Key #{self.current_key_idx + 1} -> {error_msg[:120]}...")
                    time.sleep(0.3)

            self.current_key_idx = (self.current_key_idx + 1) % len(self.keys)

        raise Exception("FATAL: Exhausted all API keys in pool and all models in the waterfall!")

llm_manager = LLMManager()
