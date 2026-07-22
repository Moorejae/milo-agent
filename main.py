import sys
import os
import asyncio
import threading
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.milo_supervisor import milo_app, get_clean_content_str
from src.llm_manager import load_api_keys

load_dotenv()

_telegram_started = False
_telegram_lock = threading.Lock()

def start_telegram_in_thread():
    global _telegram_started
    with _telegram_lock:
        if _telegram_started:
            print("[Cloud Server] Telegram Bot thread is ALREADY running. Skipping duplicate spawn request.")
            return
        _telegram_started = True

    try:
        from src.telegram_bot import run_telegram_bot
        print("[Cloud Server] Spawning single background Telegram Bot listener...")
        run_telegram_bot()
    except Exception as e:
        print(f"[Cloud Server] Telegram bot listener error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    keys = load_api_keys()
    print(f"[STARTUP] TELEGRAM_BOT_TOKEN loaded: {'YES (' + token[:6] + '...)' if token else 'NO'}")
    print(f"[STARTUP] Loaded {len(keys)} GEMINI API keys from environment.")
    
    if token:
        thread = threading.Thread(target=start_telegram_in_thread, daemon=True)
        thread.start()
        print("[Cloud Server] Agent Milo Telegram Bot thread initialized successfully!")
    else:
        print("[Cloud Server] Warning: TELEGRAM_BOT_TOKEN missing from environment secrets.")
    yield

app = FastAPI(title="Agent Milo PA Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {
        "status": "online",
        "service": "Agent Milo — Universal Personal Assistant",
        "architecture": "GitHub -> Render / Cloudflare / Oracle"
    }

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    if not user_message:
        return {"error": "Message parameter is required"}
        
    initial_state = {"messages": [{"role": "user", "content": user_message}], "sub_tasks": [], "current_result": "", "final_output": ""}
    loop = asyncio.get_running_loop()
    output_state = await loop.run_in_executor(None, milo_app.invoke, initial_state)
    
    messages = output_state.get("messages", [])
    response_text = get_clean_content_str(messages[-1].get("content", "")) if messages else output_state.get("current_result", "Done")
    return {"reply": response_text}

def run_cli():
    print("==================================================")
    print("  Agent Milo — Universal Personal Assistant (PA)  ")
    print("  GitHub -> Render / Cloudflare / Oracle          ")
    print("==================================================")
    
    if len(sys.argv) > 1 and sys.argv[1] not in ["--telegram", "--server"]:
        user_input = " ".join(sys.argv[1:])
        print(f"\nYou: {user_input}")
        print("Milo is thinking & deploying sub-agents...")
        initial_state = {"messages": [{"role": "user", "content": user_input}], "sub_tasks": [], "current_result": "", "final_output": ""}
        out = milo_app.invoke(initial_state)
        messages = out.get("messages", [])
        if messages:
            print(f"\nMilo:\n{get_clean_content_str(messages[-1].get('content', ''))}")
        return

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
                
            print("Milo is thinking & deploying sub-agents...")
            initial_state = {"messages": [{"role": "user", "content": user_input}], "sub_tasks": [], "current_result": "", "final_output": ""}
            out = milo_app.invoke(initial_state)
            messages = out.get("messages", [])
            if messages:
                print(f"\nMilo:\n{get_clean_content_str(messages[-1].get('content', ''))}")
        except KeyboardInterrupt:
            break

def main():
    port = int(os.getenv("PORT", "10000"))
    if "--telegram" in sys.argv:
        from src.telegram_bot import run_telegram_bot
        run_telegram_bot()
    elif "--server" in sys.argv or os.getenv("SPACE_ID") or os.getenv("CONTAINER_PORT") or os.getenv("PORT") or os.getenv("RENDER"):
        print(f"Starting Agent Milo Web API & Telegram Server on port {port}...")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, workers=1)
    else:
        # Default for cloud deployment: run FastAPI web server & Telegram bot thread
        print(f"Starting Agent Milo 24/7 Cloud Server on port {port}...")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, workers=1)

if __name__ == "__main__":
    main()
