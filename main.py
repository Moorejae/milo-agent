import sys
import os
from dotenv import load_dotenv

load_dotenv()

from src.milo_supervisor import milo_app, get_clean_content_str

def run_cli():
    print("==================================================")
    print("  Agent Milo — Universal Personal Assistant (PA)  ")
    print("  GitHub -> Cloudflare / Hugging Face / Oracle    ")
    print("==================================================")
    
    if len(sys.argv) > 1 and sys.argv[1] != "--telegram":
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
    if "--telegram" in sys.argv:
        from src.telegram_bot import run_telegram_bot
        run_telegram_bot()
    else:
        run_cli()

if __name__ == "__main__":
    main()
