"""
TikTok Uploader - Upload videos to TikTok using OAuth2 (Sandbox Mode)

PKCE IMPLEMENTATION NOTES:
- TikTok Desktop requires PKCE (Proof Key for Code Exchange) for OAuth 2.0
- CRITICAL: TikTok Desktop uses HEX encoding, NOT base64url!
  * Standard PKCE: code_challenge = BASE64URL(SHA256(verifier))
  * TikTok Desktop: code_challenge = HEX(SHA256(verifier))
- TikTok QUIRK: Requires BOTH client_secret AND code_verifier (non-standard)
- Code verifier: 64 chars from [A-Z][a-z][0-9]-._~
- Code challenge: Hex-encoded SHA256 hash of verifier

AUTHORIZATION FLOW:
- Local HTTP server on localhost:8080 for OAuth callback
- User authorizes in browser, TikTok redirects to localhost
- App captures auth code from callback

TROUBLESHOOTING:
1. "Something went wrong" error:
   - Check Redirect URI in TikTok Developer Console
   - Must be EXACTLY: https://www.tiktok.com/
   - Case sensitive, no trailing slash

2. "malformed request" error:
   - Redirect URI mismatch between code and TikTok Console
   - Update TikTok Console to use: https://www.tiktok.com/

3. "Invalid client_key" error:
   - Verify Client Key is correct (copy-paste from TikTok Developer)
   - No extra spaces or characters

4. "Scope not authorized" error:
   - Make sure app has these scopes enabled:
     * user.info.basic
     * video.upload
     * video.publish

5. User cancelled authorization:
   - User must copy-paste the redirect URL after authorizing
   - URL should contain 'code=' parameter

TROUBLESHOOTING:
"""

import os
import sys
import json
import time
import secrets
import hashlib
import base64
import webbrowser
import threading
import requests
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs, urlparse

# Get app directory
if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else APP_DIR
else:
    APP_DIR = Path(__file__).parent
    BUNDLE_DIR = APP_DIR

# TikTok API endpoints
SANDBOX_API_BASE = "https://open.tiktokapis.com/v2/"
PRODUCTION_API_BASE = "https://open.tiktokapis.com/v2/"

# OAuth endpoints
AUTHORIZE_URL = "https://www.tiktok.com/v2/auth/authorize/"
TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"

# OAuth scopes for video upload
SCOPES = [
    "user.info.basic",
    "video.upload",
    "video.publish"
]

# Redirect URI for TikTok OAuth
# For Desktop app: Use localhost with custom port
# MUST match exactly in TikTok Developer Console
REDIRECT_URI = "http://localhost:8080/callback"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from TikTok"""
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_GET(self):
        """Handle GET request from OAuth callback"""
        # Parse query parameters properly
        parsed_url = urlparse(self.path)
        query = parsed_url.query
        params = parse_qs(query)
        
        if 'code' in params:
            # Get the first value and ensure it's properly decoded
            self.server.auth_code = params['code'][0]
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            success_html = """
            <html>
            <head><title>TikTok Connected</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #00f2ea;">✓ TikTok Connected!</h1>
                <p>You can close this window and return to YT Short Clipper.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        elif 'error' in params:
            self.server.auth_error = params.get('error_description', ['Unknown error'])[0]
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = f"""
            <html>
            <head><title>TikTok Connection Failed</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1 style="color: #ff0000;">✗ Connection Failed</h1>
                <p>{self.server.auth_error}</p>
                <p>Please close this window and try again.</p>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())


class TikTokUploader:
    """Handle TikTok OAuth and video uploads"""
    
    def __init__(self, config, status_callback=None):
        """
        Initialize TikTok uploader
        
        Args:
            config: Config manager instance
            status_callback: Function to call with status messages
        """
        self.config = config
        self.status_callback = status_callback or (lambda msg: print(msg))
        
        # Load TikTok config
        tiktok_config = self.config.get("tiktok", {})
        self.client_key = tiktok_config.get("client_key", "")
        self.client_secret = tiktok_config.get("client_secret", "")
        self.mode = tiktok_config.get("mode", "sandbox")
        self.access_token = tiktok_config.get("access_token", "")
        self.refresh_token = tiktok_config.get("refresh_token", "")
        self.token_expires_at = tiktok_config.get("token_expires_at", 0)
        
        # API base URL
        self.api_base = SANDBOX_API_BASE if self.mode == "sandbox" else PRODUCTION_API_BASE
        
        # Store code_verifier for OAuth flow
        self.code_verifier = None
    
    def is_configured(self) -> bool:
        """Check if client credentials are configured"""
        return bool(self.client_key and self.client_secret)
    
    def is_authenticated(self) -> bool:
        """Check if we have valid access token"""
        if not self.access_token:
            return False
        
        # Check if token is expired
        if time.time() >= self.token_expires_at:
            # Try to refresh token
            if self.refresh_token:
                return self._refresh_access_token()
            return False
        
        return True
    
    def authenticate(self, callback=None):
        """
        Start OAuth flow - opens browser for user to authorize
        
        Args:
            callback: Function to call when auth completes (success, data)
        """
        if not self.is_configured():
            error = "TikTok credentials not configured. Please add Client Key and Client Secret in Settings."
            if callback:
                callback(False, error)
            raise Exception(error)
        
        try:
            # Generate CSRF token
            csrf_token = secrets.token_urlsafe(32)
            
            # For Sandbox mode, try without PKCE first
            # Some TikTok Sandbox apps might not support PKCE
            use_pkce = True  # TikTok requires PKCE even for Sandbox
            
            auth_params = {
                "client_key": self.client_key,
                "scope": ",".join(SCOPES),
                "response_type": "code",
                "redirect_uri": REDIRECT_URI,
                "state": csrf_token
            }
            
            if use_pkce:
                # Generate PKCE code verifier (43-128 characters)
                # TikTok Desktop: Use unreserved characters [A-Z] / [a-z] / [0-9] / "-" / "." / "_" / "~"
                import string
                verifier_chars = string.ascii_letters + string.digits + '-._~'
                self.code_verifier = ''.join(secrets.choice(verifier_chars) for _ in range(64))
                
                # Generate code challenge
                # TikTok Desktop: Use HEX encoding (not base64url!)
                # code_challenge = HEX(SHA256(code_verifier))
                challenge_bytes = hashlib.sha256(self.code_verifier.encode('utf-8')).digest()
                code_challenge = challenge_bytes.hex()  # Hex encoding, not base64!
                
                # Store PKCE state for verification
                self.pkce_store = {
                    "verifier": self.code_verifier,
                    "challenge": code_challenge,
                    "timestamp": time.time()
                }
                
                auth_params["code_challenge"] = code_challenge
                auth_params["code_challenge_method"] = "S256"
                
                # Debug logging
                self.status_callback(f"PKCE Debug (TikTok Desktop - HEX encoding):")
                self.status_callback(f"  Verifier length: {len(self.code_verifier)}")
                self.status_callback(f"  Verifier: {self.code_verifier[:20]}...")
                self.status_callback(f"  Challenge (HEX): {code_challenge[:20]}...")
                
                # Deterministic verification - recompute challenge to ensure consistency
                recomputed_challenge = hashlib.sha256(self.code_verifier.encode('utf-8')).hexdigest()
                
                if recomputed_challenge != code_challenge:
                    raise Exception("PKCE verification failed: challenge mismatch!")
                
                self.status_callback(f"  ✓ PKCE verification passed")
                self.status_callback(f"Using PKCE with HEX encoding (TikTok Desktop requirement)")
            else:
                self.code_verifier = None
                self.status_callback("Using OAuth without PKCE (Sandbox mode)")
            
            auth_url = f"{AUTHORIZE_URL}?{urlencode(auth_params)}"
            
            self.status_callback(f"Authorization URL: {auth_url}")
            self.status_callback(f"Redirect URI: {REDIRECT_URI}")
            self.status_callback(f"Client Key: {self.client_key[:10]}...")
            
            # Start local server for callback
            server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
            server.auth_code = None
            server.auth_error = None
            server.csrf_token = csrf_token
            
            # Open browser
            self.status_callback("Opening browser for TikTok authorization...")
            webbrowser.open(auth_url)
            
            # Wait for callback (timeout after 5 minutes)
            timeout = time.time() + 300
            while server.auth_code is None and server.auth_error is None:
                server.handle_request()
                if time.time() > timeout:
                    raise Exception("Authorization timeout - please try again")
            
            # Check for errors
            if server.auth_error:
                raise Exception(f"Authorization failed: {server.auth_error}")
            
            if not server.auth_code:
                raise Exception("No authorization code received")
            
            # Clean auth code (remove any trailing artifacts)
            auth_code = server.auth_code.strip()
            
            self.status_callback(f"Received auth code: {auth_code[:10]}...")
            self.status_callback(f"Auth code length: {len(auth_code)}")
            
            # Exchange code for access token
            self.status_callback("Exchanging authorization code for access token...")
            
            # CRITICAL: Verify code_verifier consistency before exchange
            if self.code_verifier:
                # Assert that stored verifier matches current verifier
                if hasattr(self, 'pkce_store'):
                    stored_verifier = self.pkce_store.get("verifier")
                    if stored_verifier != self.code_verifier:
                        raise Exception("PKCE state mismatch: verifier changed between authorize and token exchange!")
                    self.status_callback(f"✓ PKCE state verified: verifier consistent")
                
                self.status_callback(f"Using code verifier: {self.code_verifier[:20]}...")
            
            self._exchange_code_for_token(auth_code, self.code_verifier)
            
            # Get user info
            user_info = self._get_user_info()
            
            if callback:
                callback(True, user_info)
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.status_callback(f"Authentication error: {error_msg}")
            if callback:
                callback(False, error_msg)
            raise
    
    def _exchange_code_for_token(self, auth_code: str, code_verifier: str = None):
        """Exchange authorization code for access token (with optional PKCE)"""
        
        token_data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,  # TikTok requires this even with PKCE
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI
        }
        
        # Add code_verifier for PKCE flow
        # NOTE: TikTok requires BOTH client_secret AND code_verifier (non-standard)
        if code_verifier:
            token_data["code_verifier"] = code_verifier
            
            # Deterministic debug - recompute challenge and compare
            if hasattr(self, 'pkce_store'):
                original_challenge = self.pkce_store.get("challenge")
                # TikTok Desktop uses HEX encoding, not base64url
                recomputed_challenge = hashlib.sha256(code_verifier.encode('utf-8')).hexdigest()
                
                self.status_callback(f"PKCE Token Exchange Debug:")
                self.status_callback(f"  Challenge sent to TikTok: {original_challenge[:30]}...")
                self.status_callback(f"  Challenge recomputed now:    {recomputed_challenge[:30]}...")
                self.status_callback(f"  Match: {original_challenge == recomputed_challenge}")
                self.status_callback(f"  Sending BOTH client_secret + code_verifier (TikTok requirement)")
                
                if original_challenge != recomputed_challenge:
                    raise Exception("PKCE challenge mismatch detected before token exchange!")
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        }
        
        # Sanitized debug log (hide sensitive data)
        debug_data = {k: (v[:10] + "..." if len(str(v)) > 10 else v) for k, v in token_data.items()}
        self.status_callback(f"Token request data: {debug_data}")
        
        try:
            # Send as form data (application/x-www-form-urlencoded)
            response = requests.post(TOKEN_URL, data=token_data, headers=headers)
            
            self.status_callback(f"Token response status: {response.status_code}")
            
            # Log response for debugging
            try:
                result = response.json()
                # Don't log full response if successful (contains sensitive tokens)
                if result.get("error"):
                    self.status_callback(f"Token response: {result}")
            except:
                self.status_callback(f"Token response (raw): {response.text}")
                raise
            
            # Check for error in response body (TikTok returns 200 with error)
            if result.get("error"):
                error_detail = result.get('error_description', result.get('message', result['error']))
                
                # Additional debug info
                self.status_callback(f"Error details from TikTok:")
                self.status_callback(f"  - Error: {result.get('error')}")
                self.status_callback(f"  - Description: {result.get('error_description')}")
                self.status_callback(f"  - Log ID: {result.get('log_id')}")
                
                raise Exception(f"Token exchange failed: {error_detail}")
            
            # Check HTTP status
            response.raise_for_status()
            
            # Save tokens
            self.access_token = result.get("access_token")
            self.refresh_token = result.get("refresh_token", "")
            expires_in = result.get("expires_in", 86400)  # Default 24 hours
            self.token_expires_at = time.time() + expires_in
            
            if not self.access_token:
                raise Exception("No access token in response")
            
            self.status_callback(f"✓ Access token received successfully!")
            self.status_callback(f"Token preview: {self.access_token[:10]}...")
            
            # Save to config
            self._save_tokens()
            
        except requests.exceptions.RequestException as e:
            self.status_callback(f"Request error: {str(e)}")
            raise
        except Exception as e:
            self.status_callback(f"Token exchange error: {str(e)}")
            raise
    
    def _refresh_access_token(self) -> bool:
        """Refresh expired access token"""
        if not self.refresh_token:
            return False
        
        try:
            token_data = {
                "client_key": self.client_key,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token
            }
            
            response = requests.post(TOKEN_URL, data=token_data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("error"):
                return False
            
            # Update tokens
            self.access_token = result["access_token"]
            self.refresh_token = result.get("refresh_token", self.refresh_token)
            expires_in = result.get("expires_in", 86400)
            self.token_expires_at = time.time() + expires_in
            
            # Save to config
            self._save_tokens()
            
            return True
            
        except Exception as e:
            self.status_callback(f"Token refresh failed: {e}")
            return False
    
    def _save_tokens(self):
        """Save tokens to config"""
        tiktok_config = self.config.get("tiktok", {})
        tiktok_config.update({
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_expires_at": self.token_expires_at
        })
        self.config.set("tiktok", tiktok_config)
    
    def _get_user_info(self) -> dict:
        """Get authenticated user's info"""
        if not self.access_token:
            return None
        
        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.api_base}user/info/",
                headers=headers,
                params={"fields": "open_id,union_id,avatar_url,display_name"}
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("error"):
                return None
            
            user_data = result.get("data", {}).get("user", {})
            
            return {
                "open_id": user_data.get("open_id", ""),
                "display_name": user_data.get("display_name", "TikTok User"),
                "avatar_url": user_data.get("avatar_url", "")
            }
            
        except Exception as e:
            self.status_callback(f"Error getting user info: {e}")
            return None
    
    def get_user_info(self) -> dict:
        """Public method to get user info"""
        if self.is_authenticated():
            return self._get_user_info()
        return None
    
    def disconnect(self):
        """Remove saved tokens"""
        self.access_token = ""
        self.refresh_token = ""
        self.token_expires_at = 0
        
        tiktok_config = self.config.get("tiktok", {})
        tiktok_config.pop("access_token", None)
        tiktok_config.pop("refresh_token", None)
        tiktok_config.pop("token_expires_at", None)
        self.config.set("tiktok", tiktok_config)
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        privacy_level: str = "SELF_ONLY",  # SELF_ONLY, MUTUAL_FOLLOW_FRIENDS, FOLLOWER_OF_CREATOR, PUBLIC_TO_EVERYONE
        disable_duet: bool = False,
        disable_comment: bool = False,
        disable_stitch: bool = False,
        progress_callback=None
    ) -> dict:
        """
        Upload video to TikTok
        
        Args:
            video_path: Path to video file
            title: Video title/caption (max 150 chars for sandbox)
            description: Additional description
            privacy_level: Privacy setting
            disable_duet: Disable duet feature
            disable_comment: Disable comments
            disable_stitch: Disable stitch feature
            progress_callback: Function to call with upload progress (0-100)
        
        Returns:
            dict with success status and video info
        """
        if not self.is_authenticated():
            return {
                "success": False,
                "error": "Not authenticated. Please connect TikTok account first."
            }
        
        try:
            # Step 1: Initialize upload
            self.status_callback("Initializing TikTok upload...")
            
            video_size = os.path.getsize(video_path)
            
            # TikTok Sandbox workaround: Use single chunk upload
            # Some Sandbox apps have issues with multi-chunk uploads
            # Upload entire file as 1 chunk
            chunk_size = video_size  # Single chunk = entire file
            total_chunks = 1
            
            # Debug logging to console
            print(f"\n=== TikTok Upload Debug ===")
            print(f"Video size: {video_size} bytes ({video_size / (1024*1024):.2f} MB)")
            print(f"Chunk size: {chunk_size} bytes (single chunk)")
            print(f"Total chunks: {total_chunks}")
            
            init_data = {
                "post_info": {
                    "title": title[:150],  # Max 150 chars for sandbox
                    "privacy_level": privacy_level,
                    "disable_duet": disable_duet,
                    "disable_comment": disable_comment,
                    "disable_stitch": disable_stitch,
                    "video_cover_timestamp_ms": 1000  # Use frame at 1 second as cover
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": video_size,
                    "chunk_size": chunk_size,
                    "total_chunk_count": total_chunks
                }
            }
            
            print(f"Init data source_info: {init_data['source_info']}")
            print(f"=========================\n")
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            print(f"Init endpoint: {self.api_base}post/publish/video/init/")
            print(f"Init headers: Authorization=Bearer {self.access_token[:20]}...")
            print(f"Init data: {json.dumps(init_data, indent=2)}")
            
            response = requests.post(
                f"{self.api_base}post/publish/video/init/",
                headers=headers,
                json=init_data
            )
            
            print(f"Init response status: {response.status_code}")
            print(f"Init response headers: {dict(response.headers)}")
            print(f"Init response body: {response.text}")
            
            # Check status code before parsing JSON
            if response.status_code != 200:
                error_msg = f"Init failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if error_data.get("error"):
                        error_code = error_data["error"].get("code", "")
                        error_msg = error_data["error"].get("message", error_msg)
                        print(f"Error details: {json.dumps(error_data, indent=2)}")
                        
                        # Provide helpful message for common errors
                        if error_code == "unaudited_client_can_only_post_to_private_accounts":
                            error_msg = (
                                "❌ TikTok Account Must Be Private\n\n"
                                "Sandbox apps can only upload to PRIVATE accounts.\n\n"
                                "Fix:\n"
                                "1. Open TikTok app on your phone\n"
                                "2. Go to Settings → Privacy\n"
                                "3. Turn ON 'Private Account'\n"
                                "4. Try uploading again\n\n"
                                "Note: Videos will still be saved as private drafts in sandbox mode."
                            )
                except:
                    error_msg = f"{error_msg}: {response.text}"
                raise Exception(error_msg)
            
            result = response.json()
            
            if result.get("error"):
                error_detail = result.get('error', {}).get('message', 'Unknown error')
                print(f"Error in response body: {json.dumps(result, indent=2)}")
                raise Exception(f"Upload init failed: {error_detail}")
            
            publish_id = result["data"]["publish_id"]
            upload_url = result["data"]["upload_url"]
            
            print(f"Got publish_id: {publish_id}")
            print(f"Got upload_url: {upload_url[:50]}...")
            
            # Step 2: Upload video chunks with Content-Range headers
            self.status_callback(f"Uploading video: {title}")
            print(f"Opening video file: {video_path}")
            
            with open(video_path, 'rb') as f:
                print(f"Video file opened successfully")
                for i in range(total_chunks):
                    start = i * chunk_size
                    end = min(start + chunk_size, video_size) - 1
                    
                    print(f"Processing chunk {i+1}/{total_chunks}")
                    
                    # Read chunk
                    f.seek(start)
                    chunk_data = f.read(end - start + 1)
                    print(f"Read {len(chunk_data)} bytes from file")
                    
                    # Upload chunk with Content-Range header
                    chunk_headers = {
                        "Content-Type": "video/mp4",
                        "Content-Range": f"bytes {start}-{end}/{video_size}"
                    }
                    
                    print(f"Uploading chunk {i+1}/{total_chunks}: bytes {start}-{end}/{video_size}")
                    print(f"Upload URL: {upload_url[:80]}...")
                    print(f"Headers: {chunk_headers}")
                    
                    try:
                        chunk_response = requests.put(
                            upload_url,
                            headers=chunk_headers,
                            data=chunk_data,
                            timeout=300  # 5 minute timeout
                        )
                        print(f"Chunk upload response status: {chunk_response.status_code}")
                        print(f"Chunk upload response: {chunk_response.text[:200]}")
                        chunk_response.raise_for_status()
                        print(f"Chunk {i+1} uploaded successfully")
                    except Exception as chunk_error:
                        print(f"ERROR uploading chunk {i+1}: {chunk_error}")
                        raise
                    
                    # Update progress
                    if progress_callback:
                        progress = int(((i + 1) / total_chunks) * 90)  # 0-90%
                        progress_callback(progress)
                    
                    self.status_callback(f"Uploaded chunk {i+1}/{total_chunks}")
            
            print(f"All chunks uploaded successfully")
            
            # Step 3: Complete upload
            self.status_callback("Finalizing upload...")
            
            complete_headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            complete_data = {
                "publish_id": publish_id
            }
            
            print(f"Calling complete endpoint with publish_id: {publish_id}")
            print(f"Complete URL: {self.api_base}post/publish/video/complete/")
            print(f"Complete data: {complete_data}")
            
            try:
                complete_response = requests.post(
                    f"{self.api_base}post/publish/video/complete/",
                    headers=complete_headers,
                    json=complete_data,
                    timeout=60
                )
                print(f"Complete response status: {complete_response.status_code}")
                print(f"Complete response body: {complete_response.text}")
                complete_response.raise_for_status()
                
                complete_result = complete_response.json()
                print(f"Complete result parsed: {complete_result}")
                
                if complete_result.get("error") and complete_result["error"].get("code") != "ok":
                    error_msg = complete_result.get('error', {}).get('message', 'Unknown error')
                    print(f"ERROR from complete endpoint: {error_msg}")
                    raise Exception(f"Complete upload failed: {error_msg}")
                
                print(f"Upload completed successfully!")
            except Exception as complete_error:
                print(f"ERROR in complete endpoint: {complete_error}")
                raise
            
            if progress_callback:
                progress_callback(100)
            
            self.status_callback("Upload complete! Video is being processed by TikTok...")
            
            # Note: In sandbox mode, video goes to drafts
            mode_note = " (Sandbox: Video saved as draft)" if self.mode == "sandbox" else ""
            
            return {
                "success": True,
                "publish_id": publish_id,
                "message": f"Video uploaded successfully{mode_note}",
                "mode": self.mode
            }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"TikTok API error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if error_data.get("error"):
                    error_msg += f" - {error_data['error'].get('message', 'Unknown error')}"
                    print(f"HTTP Error details: {json.dumps(error_data, indent=2)}")
                else:
                    error_msg += f" - {e.response.text}"
            except:
                error_msg += f" - {e.response.text}"
            
            print(f"HTTPError: {error_msg}")
            self.status_callback(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            print(f"Exception: {error_msg}")
            import traceback
            traceback.print_exc()
            self.status_callback(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
