import os
import time
import requests

RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://milo-agent-7wtv.onrender.com")

def run_keep_alive():
    print(f"==================================================")
    print(f"  Agent Milo Keep-Alive Ping Hack (24/7 Awake)   ")
    print(f"  Target: {RENDER_URL}                           ")
    print(f"==================================================")
    
    while True:
        try:
            resp = requests.get(f"{RENDER_URL}/", timeout=10)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Pinged {RENDER_URL} -> HTTP {resp.status_code} (Success)")
        except Exception as e:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Ping error: {e}")
            
        # Sleep for 10 minutes (600s) - Render free tier sleeps after 15 mins inactivity
        time.sleep(600)

if __name__ == "__main__":
    run_keep_alive()
