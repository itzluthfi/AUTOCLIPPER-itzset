"""
YouTube Uploader - Upload videos to YouTube using OAuth2
"""

import os
import sys
import json
import pickle
import webbrowser
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# YouTube API scopes
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly'  # For reading channel info
]

# Get app directory
if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else APP_DIR
else:
    APP_DIR = Path(__file__).parent
    BUNDLE_DIR = APP_DIR

CLIENT_SECRET_FILE = APP_DIR / "client_secret.json"
CREDENTIALS_FILE = APP_DIR / "youtube_credentials.json"


class YouTubeUploader:
    """Handle YouTube OAuth and video uploads"""
    
    def __init__(self, status_callback=None):
        self.credentials = None
        self.youtube = None
        self.channel_info = None
        self.status_callback = status_callback or (lambda msg: print(msg))
    
    def is_configured(self) -> bool:
        """Check if client_secret.json exists"""
        return CLIENT_SECRET_FILE.exists()
    
    def is_authenticated(self) -> bool:
        """Check if we have valid credentials"""
        if not CREDENTIALS_FILE.exists():
            return False
        
        try:
            self.credentials = Credentials.from_authorized_user_file(str(CREDENTIALS_FILE), SCOPES)
            if self.credentials and self.credentials.valid:
                return True
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
                self._save_credentials()
                return True
        except Exception:
            pass
        
        return False
    
    def _save_credentials(self):
        """Save credentials to file"""
        with open(CREDENTIALS_FILE, 'w') as f:
            f.write(self.credentials.to_json())
    
    def authenticate(self, callback=None):
        """Start OAuth flow - opens browser for user to login"""
        if not self.is_configured():
            raise Exception("client_secret.json not found. Please set up YouTube API credentials.")
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRET_FILE),
                SCOPES
            )
            
            # Run local server for OAuth callback
            # Try multiple ports if 8080 is busy
            ports_to_try = [8080, 8090, 8888, 9000, 0]  # 0 = random available port
            last_error = None
            
            for port in ports_to_try:
                try:
                    self.credentials = flow.run_local_server(
                        port=port,
                        prompt='consent',
                        success_message='YouTube connected successfully! You can close this window.'
                    )
                    break  # Success, exit loop
                except OSError as e:
                    if "10048" in str(e) or "address already in use" in str(e).lower():
                        last_error = e
                        continue  # Try next port
                    else:
                        raise  # Different error, re-raise
            else:
                # All ports failed
                raise Exception(f"Could not find available port for OAuth callback. Last error: {last_error}")
            
            self._save_credentials()
            
            # Get channel info
            self._init_youtube()
            self._get_channel_info()
            
            if callback:
                callback(True, self.channel_info)
            
            return True
            
        except Exception as e:
            if callback:
                callback(False, str(e))
            raise
    
    def _init_youtube(self):
        """Initialize YouTube API client"""
        if not self.credentials:
            if not self.is_authenticated():
                raise Exception("Not authenticated")
        
        self.youtube = build('youtube', 'v3', credentials=self.credentials)
    
    def _get_channel_info(self):
        """Get authenticated user's channel info"""
        if not self.youtube:
            self._init_youtube()
        
        try:
            response = self.youtube.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()
            
            if response.get('items'):
                channel = response['items'][0]
                self.channel_info = {
                    'id': channel['id'],
                    'title': channel['snippet']['title'],
                    'thumbnail': channel['snippet']['thumbnails'].get('default', {}).get('url', ''),
                    'subscribers': channel['statistics'].get('subscriberCount', '0')
                }
                return self.channel_info
        except Exception as e:
            print(f"Error getting channel info: {e}")
        
        return None
    
    def get_channel_info(self):
        """Public method to get channel info"""
        if self.channel_info:
            return self.channel_info
        
        if self.is_authenticated():
            self._init_youtube()
            return self._get_channel_info()
        
        return None
    
    def disconnect(self):
        """Remove saved credentials"""
        if CREDENTIALS_FILE.exists():
            CREDENTIALS_FILE.unlink()
        self.credentials = None
        self.youtube = None
        self.channel_info = None
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list = None,
        category_id: str = "22",  # 22 = People & Blogs
        privacy_status: str = "private",
        publish_at: str = None,  # ISO 8601 format: "2024-12-25T10:00:00Z"
        progress_callback=None
    ) -> dict:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title (max 100 chars)
            description: Video description (max 5000 chars)
            tags: List of tags
            category_id: YouTube category ID
            privacy_status: 'private', 'unlisted', or 'public'
            publish_at: Schedule publish time in ISO 8601 format (UTC)
            progress_callback: Function to call with upload progress (0-100)
        
        Returns:
            dict with video_id and url on success
        """
        if not self.youtube:
            self._init_youtube()
        
        # Validate inputs
        title = title[:100]  # YouTube max title length
        description = description[:5000]  # YouTube max description length
        tags = tags or []
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
        
        # Add scheduled publish time if provided
        if publish_at:
            body['status']['publishAt'] = publish_at
            # Must be private if scheduled
            if privacy_status != 'private':
                body['status']['privacyStatus'] = 'private'
                self.status_callback("Note: Scheduled videos must be private initially")
        
        # Create media upload
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True,
            chunksize=1024*1024  # 1MB chunks
        )
        
        try:
            if publish_at:
                self.status_callback(f"Scheduling upload for: {publish_at}")
            else:
                self.status_callback(f"Starting upload: {title}")
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status and progress_callback:
                    progress = int(status.progress() * 100)
                    progress_callback(progress)
            
            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            if publish_at:
                self.status_callback(f"Video scheduled successfully: {video_url}")
            else:
                self.status_callback(f"Upload complete: {video_url}")
            
            return {
                'success': True,
                'video_id': video_id,
                'url': video_url,
                'scheduled': bool(publish_at),
                'publish_at': publish_at
            }
            
        except HttpError as e:
            error_msg = f"YouTube API error: {e.resp.status} - {e.content.decode()}"
            self.status_callback(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            self.status_callback(error_msg)
            return {
                'success': False,
                'error': error_msg
            }


def generate_seo_metadata(client, clip_title: str, hook_text: str, model: str = "gpt-4.1", temperature: float = 1.0) -> dict:
    """
    Generate SEO-optimized title and description using GPT
    
    Args:
        client: OpenAI client
        clip_title: Original clip title
        hook_text: Hook text from the clip
        model: GPT model to use
    
    Returns:
        dict with title, description, tags
    """
    prompt = f"""Kamu adalah expert YouTube SEO untuk konten short-form (Shorts/Reels/TikTok).

Berdasarkan informasi clip berikut, buatkan:
1. Title yang catchy dan SEO-friendly (max 100 karakter, include emoji)
2. Description yang engaging dengan hashtags (max 500 karakter)
3. Tags yang relevan (5-10 tags)

Info Clip:
- Judul: {clip_title}
- Hook: {hook_text}

Format response dalam JSON:
{{
    "title": "judul dengan emoji",
    "description": "deskripsi dengan hashtags",
    "tags": ["tag1", "tag2", "tag3"]
}}

PENTING:
- Title harus under 100 karakter
- Gunakan bahasa Indonesia
- Include trending hashtags seperti #shorts #viral #fyp
- Buat yang clickbait tapi tetap relevan

Return HANYA JSON, tanpa text lain."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse JSON
        if result.startswith("```"):
            import re
            result = re.sub(r"```json?\n?", "", result)
            result = re.sub(r"```\n?", "", result)
        
        metadata = json.loads(result)
        
        # Validate lengths
        metadata['title'] = metadata.get('title', clip_title)[:100]
        metadata['description'] = metadata.get('description', '')[:5000]
        metadata['tags'] = metadata.get('tags', [])[:15]
        
        return metadata
        
    except Exception as e:
        # Fallback to basic metadata
        return {
            'title': f"🔥 {clip_title}"[:100],
            'description': f"{hook_text}\n\n#shorts #viral #fyp #podcast",
            'tags': ['shorts', 'viral', 'fyp', 'podcast', 'indonesia']
        }
