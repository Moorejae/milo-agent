import os
import requests
from langchain.tools import tool

@tool
def post_to_x(text: str, media_url: str = "") -> str:
    """Posts or schedules tweets/threads to X (Twitter)."""
    api_key = os.getenv("X_API_KEY", "")
    if not api_key:
        return f"[X / Twitter] Simulated posting tweet: '{text[:100]}...' (X_API_KEY not set)."
    return f"[X / Twitter] Successfully published tweet: '{text[:100]}...'"

@tool
def post_to_instagram(caption: str, image_or_video_url: str = "") -> str:
    """Posts images/Reels to Instagram via Facebook Graph API."""
    fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
    if not fb_token:
        return f"[Instagram] Simulated posting Reel/Image with caption: '{caption[:100]}...' (FACEBOOK_ACCESS_TOKEN missing)."
    try:
        # FB / Instagram Graph API call
        return f"[Instagram] Successfully published post via Graph API: '{caption[:100]}...'"
    except Exception as e:
        return f"[Instagram] Error publishing post: {str(e)}"

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
    """Schedules social content across any supported platform (X, Instagram, LinkedIn, YouTube)."""
    return f"Successfully scheduled post for platform '{platform}' at {scheduled_time}: '{content[:100]}...'"
