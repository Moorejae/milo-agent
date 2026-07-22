import sys
import os
import asyncio
import threading
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.milo_supervisor import milo_app, get_clean_content_str

load_dotenv()

app = FastAPI(title="Agent Milo PA Service")

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
        "architecture": "GitHub -> HF Spaces / Cloudflare / Oracle"
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

def start_telegram_in_thread():
    try:
        from src.telegram_bot import run_telegram_bot
        print("[Cloud Server] Spawning background Telegram Bot listener...")
        run_telegram_bot()
    except Exception as e:
        print(f"[Cloud Server] Telegram bot listener error: {e}")

@app.on_event("startup")
def on_startup():
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if token:
        thread = threading.Thread(target=start_telegram_in_thread, daemon=True)
        thread.start()
        print("[Cloud Server] Agent Milo Telegram Bot thread initialized successfully!")
    else:
        print("[Cloud Server] Warning: TELEGRAM_BOT_TOKEN missing from environment secrets.")

def run_cli():
    print("==================================================")
    print("  Agent Milo — Universal Personal Assistant (PA)  ")
    print("  GitHub -> Cloudflare / Hugging Face / Oracle    ")
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
    port = int(os.getenv("PORT", "7860"))
    if "--telegram" in sys.argv:
        from src.telegram_bot import run_telegram_bot
        run_telegram_bot()
    elif "--server" in sys.argv or os.getenv("SPACE_ID") or os.getenv("CONTAINER_PORT") or os.getenv("PORT"):
        print(f"Starting Agent Milo Web API & Telegram Server on port {port}...")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
    else:
        # Default for container execution: run FastAPI web server & Telegram bot thread
        print(f"Starting Agent Milo 24/7 Cloud Server on port {port}...")
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    main()
