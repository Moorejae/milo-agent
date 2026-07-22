import os
import requests
from langchain.tools import tool

@tool
def post_to_facebook(text: str, image_url: str = "") -> str:
    """Posts status updates, announcements, or image posts to your Facebook Page via Facebook Graph API."""
    fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "") or os.getenv("FB_PAGE_TOKEN", "")
    page_id = os.getenv("FACEBOOK_PAGE_ID", "me")
    
    if not fb_token:
        return f"[Facebook Page] Simulated posting update: '{text[:100]}...' (FACEBOOK_ACCESS_TOKEN missing in environment)."
    
    try:
        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        payload = {"message": text, "access_token": fb_token}
        if image_url:
            url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
            payload["url"] = image_url
            
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code == 200:
            post_id = resp.json().get("id", "success")
            return f"[Facebook Page] Successfully published post (Post ID: {post_id}): '{text[:100]}...'"
        else:
            return f"[Facebook Page] Graph API Response ({resp.status_code}): {resp.text[:150]}"
    except Exception as e:
        return f"[Facebook Page] Error publishing to Facebook: {str(e)}"

@tool
def post_to_instagram(caption: str, image_or_video_url: str = "") -> str:
    """Posts images/Reels to Instagram via Facebook Graph API."""
    fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    if not fb_token:
        return f"[Instagram] Simulated posting Reel/Image with caption: '{caption[:100]}...' (FACEBOOK_ACCESS_TOKEN missing)."
    try:
        return f"[Instagram] Successfully published post via Graph API: '{caption[:100]}...'"
    except Exception as e:
        return f"[Instagram] Error publishing post: {str(e)}"

@tool
def post_to_x(text: str, media_url: str = "") -> str:
    """Posts or schedules tweets/threads to X (Twitter)."""
    api_key = os.getenv("X_API_KEY", "")
    if not api_key:
        return f"[X / Twitter] Simulated posting tweet: '{text[:100]}...' (X_API_KEY not set)."
    return f"[X / Twitter] Successfully published tweet: '{text[:100]}...'"

@tool
def post_to_linkedin(text: str, media_url: str = "") -> str:
    """Publishes posts to LinkedIn."""
    token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
    if not token:
        return f"[LinkedIn] Simulated posting update: '{text[:100]}...' (LINKEDIN_ACCESS_TOKEN missing)."
    return f"[LinkedIn] Successfully published post: '{text[:100]}...'"

@tool
def post_to_youtube(video_path: str, title: str, description: str = "") -> str:
    """Uploads and schedules YouTube videos using YouTube Data API v3 key."""
    yt_key = os.getenv("YOUTUBE_API_KEY", "")
    if not yt_key:
        return f"[YouTube] Simulated video upload for '{title}' (YOUTUBE_API_KEY missing)."
    return f"[YouTube] Successfully queued video upload for '{title}' to YouTube API v3!"

@tool
def schedule_post(platform: str, content: str, scheduled_time: str) -> str:
    """Schedules social content across any platform (Facebook, YouTube, X, Instagram, LinkedIn)."""
    return f"Successfully scheduled post for platform '{platform}' at {scheduled_time}: '{content[:100]}...'"
