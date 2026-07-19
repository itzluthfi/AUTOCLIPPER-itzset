import os
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

# Scopes needed
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def upload_to_youtube(
    access_token: str,
    refresh_token: str,
    file_path: str,
    title: str = "AutoClipper Short",
    description: str = "Created with AutoClipper",
    privacy: str = "public",
    tags: list = None,
) -> dict:
    """Upload video ke YouTube. Return video_id atau raise exception."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file not found: {file_path}")

    try:
        creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            scopes=SCOPES,
        )

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Return new access_token so caller can save it
            new_access_token = creds.token
        else:
            new_access_token = access_token

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:500] if tags else [],
                "categoryId": "22",  # People & Blogs
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            file_path,
            chunksize=256 * 1024,
            resumable=True,
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Upload progress: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        youtube_url = f"https://youtu.be/{video_id}"

        logger.info(f"Upload success: {youtube_url}")

        return {
            "video_id": video_id,
            "url": youtube_url,
            "new_access_token": new_access_token,
        }

    except Exception as e:
        logger.error(f"YouTube upload failed: {e}")
        raise
