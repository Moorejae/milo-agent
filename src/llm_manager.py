import os
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# Load keys dynamically from environment variables or fallback
def load_api_keys():
    keys = []
    # Check GEMINI_API_KEY_1 through GEMINI_API_KEY_14
    for i in range(1, 15):
        k = os.getenv(f"GEMINI_API_KEY_{i}")
        if k:
            keys.append(k)
            
    # Check single GEMINI_API_KEY fallback
    if not keys:
        single_key = os.getenv("GEMINI_API_KEY")
        if single_key:
            keys.append(single_key)
            
    return keys

# Prioritized list of supported 3.x models in descending order
FULL_MODEL_WATERFALL = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-cyber",
    "gemini-3.1-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.0",
]

class LLMManager:
    def __init__(self):
        self.keys = load_api_keys()
        self.current_key_idx = 0

    def get_waterfall_for_intensity(self, intensity: str):
        if intensity == "heavy" or intensity == "antigravity":
            return FULL_MODEL_WATERFALL
        elif intensity == "cyber":
            idx = FULL_MODEL_WATERFALL.index("gemini-3.5-flash-cyber") if "gemini-3.5-flash-cyber" in FULL_MODEL_WATERFALL else 0
            return FULL_MODEL_WATERFALL[idx:]
        elif intensity == "minimal":
            idx = FULL_MODEL_WATERFALL.index("gemini-3.5-flash-lite") if "gemini-3.5-flash-lite" in FULL_MODEL_WATERFALL else 0
            return FULL_MODEL_WATERFALL[idx:]
        else:
            return FULL_MODEL_WATERFALL

    def invoke_with_waterfall(self, prompt_or_messages, intensity="heavy", tools=None):
        if not self.keys:
            self.keys = load_api_keys()
        if not self.keys:
            raise Exception("No GEMINI_API_KEY environment variables found!")

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
                    time.sleep(0.5)

            self.current_key_idx = (self.current_key_idx + 1) % len(self.keys)

        raise Exception("FATAL: Exhausted all API keys and all models in the waterfall!")

llm_manager = LLMManager()
