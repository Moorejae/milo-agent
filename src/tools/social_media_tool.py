import os
import requests

N8N_BASE_URL = os.getenv("N8N_BASE_URL", "https://n8n-milo-3lnl.onrender.com")

def draft_social_post(topic: str, platform: str = "linkedin") -> dict:
    """
    Drafts a viral, high-converting social media post tailored for the target platform.
    """
    print(f"[SocialMediaTool] Drafting {platform.upper()} post for topic: '{topic}'...")
    return {
        "status": "drafted",
        "platform": platform.lower(),
        "topic": topic,
        "suggested_hooks": [
            f"Here is how {topic} is changing the industry...",
            f"Most people get {topic} wrong. Here's why:",
            f"3 lessons I learned from {topic}:"
        ]
    }

def trigger_n8n_social_publish(post_content: str, platform: str = "linkedin") -> dict:
    """
    Triggers the n8n social media workflow to publish or schedule a post.
    """
    webhook_url = f"{N8N_BASE_URL}/webhook/social-publish"
    payload = {
        "platform": platform.lower(),
        "content": post_content
    }
    print(f"[SocialMediaTool] Triggering n8n publishing webhook: {webhook_url}")
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        return {"status_code": resp.status_code, "response": resp.text[:200]}
    except Exception as e:
        print(f"[SocialMediaTool] Webhook trigger error: {e}")
        return {"status": "failed", "error": str(e)}
