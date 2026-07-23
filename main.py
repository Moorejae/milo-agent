import sys
import os
import time
import asyncio
import threading
import requests
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.milo_supervisor import milo_app, get_clean_content_str
from src.llm_manager import load_api_keys

load_dotenv()

def keep_alive_ping():
    """Background thread that pings both Milo and n8n Render servers every 10 minutes to prevent 15-min inactivity sleep."""
    milo_url = os.getenv("RENDER_EXTERNAL_URL", "https://milo-agent-7wtv.onrender.com")
    n8n_url = os.getenv("N8N_RENDER_URL", "https://n8n-milo.onrender.com")
    time.sleep(30) # Initial wait after boot
    while True:
        for url in [milo_url, n8n_url]:
            try:
                resp = requests.get(f"{url}/", timeout=10)
                print(f"[Keep-Alive Ping] Sent HTTP ping to {url} -> HTTP {resp.status_code}")
            except Exception as e:
                print(f"[Keep-Alive Ping] Ping {url} status: {e}")
        time.sleep(600) # Ping every 10 minutes (600 seconds)

@asynccontextmanager
async def lifespan(app: FastAPI):
    keys = load_api_keys()
    print(f"[STARTUP] Loaded {len(keys)} GEMINI API keys from environment.")
    print("[Cloud Server] Mode: Pure API Gateway & Reasoning Engine for n8n/Telegram Webhooks.")
        
    # Start Keep-Alive self-ping thread
    ping_thread = threading.Thread(target=keep_alive_ping, daemon=True)
    ping_thread.start()
    print("[Cloud Server] Keep-Alive self-ping thread started for Milo & n8n (10-minute interval).")

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
        "mode": "n8n AI Engine & Webhook API Gateway",
        "architecture": "Telegram -> n8n Cloud (Render) -> Milo API (Render) -> GitHub"
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
    else:
        print(f"Starting Agent Milo 24/7 API Engine on port {port}...")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, workers=1)

if __name__ == "__main__":
    main()
