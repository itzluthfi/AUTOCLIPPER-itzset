"""
Repliz upload dialog - Select accounts and upload video
"""

import sys
import json
import threading
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image
from datetime import datetime, timedelta


class ReplizUploadDialog(ctk.CTkToplevel):
    """Dialog for selecting Repliz accounts and uploading video"""
    
    def __init__(self, parent, clip_data: dict, access_key: str, secret_key: str, openai_client=None, model: str = "gpt-4.1", temperature: float = 1.0):
        super().__init__(parent)
        
        self.clip_data = clip_data
        self.access_key = access_key
        self.secret_key = secret_key
        self.openai_client = openai_client
        self.model = model
        self.temperature = temperature
        self.accounts = []
        self.selected_accounts = []
        self.account_checkboxes = []
        self.video_url = None
        self.uploading = False
        
        # Window setup
        self.title("Upload via Repliz")
        self.geometry("600x750")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_ui()
        self.load_accounts()
        
        # Set icon after window is created
        self.after(10, self.set_dialog_icon)
    
    def set_dialog_icon(self):
        """Set dialog icon to match main window"""
        try:
            from utils.helpers import get_bundle_dir
            BUNDLE_DIR = get_bundle_dir()
            ASSETS_DIR = BUNDLE_DIR / "assets"
            ICON_PATH = ASSETS_DIR / "icon.png"
            ICON_ICO_PATH = ASSETS_DIR / "icon.ico"
            
            if sys.platform == "win32":
                # Use .ico file directly on Windows
                if ICON_ICO_PATH.exists():
                    self.iconbitmap(str(ICON_ICO_PATH))
                elif ICON_PATH.exists():
                    # Convert PNG to ICO if needed
                    img = Image.open(ICON_PATH)
                    ico_path = ASSETS_DIR / "icon.ico"
                    img.save(str(ico_path), format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (256, 256)])
                    self.iconbitmap(str(ico_path))
            else:
                if ICON_PATH.exists():
                    from tkinter import PhotoImage
                    icon_img = Image.open(ICON_PATH)
                    photo = PhotoImage(icon_img)
                    self.iconphoto(True, photo)
                    self._icon_photo = photo
        except Exception as e:
            pass  # Silently fail if icon can't be set
    
    def create_ui(self):
        """Create dialog UI"""
        # Main scrollable content
        main_scroll = ctk.CTkScrollableFrame(self)
        main_scroll.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        # Header
        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="📤 Upload via Repliz", 
            font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Upload to multiple platforms at once", 
            font=ctk.CTkFont(size=11), text_color="gray").pack(anchor="w", pady=(5, 0))
        
        # Video info
        info_frame = ctk.CTkFrame(main_scroll, fg_color=("gray90", "gray17"), corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        title = self.clip_data.get("title", "Untitled")
        if len(title) > 50:
            title = title[:47] + "..."
        
        ctk.CTkLabel(info_frame, text=f"📹 {title}", 
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", padx=15, pady=(12, 5))
        
        duration = self.clip_data.get("duration", 0)
        ctk.CTkLabel(info_frame, text=f"⏱️ Duration: {duration:.0f}s", 
            font=ctk.CTkFont(size=11), text_color="gray", anchor="w").pack(fill="x", padx=15, pady=(0, 12))
        
        # Metadata section (Title & Description)
        metadata_frame = ctk.CTkFrame(main_scroll, fg_color=("gray90", "gray17"), corner_radius=10)
        metadata_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(metadata_frame, text="📝 Post Details", 
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(fill="x", padx=15, pady=(12, 10))
        
        # Title
        ctk.CTkLabel(metadata_frame, text="Title", 
            font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(fill="x", padx=15)
        self.title_entry = ctk.CTkEntry(metadata_frame, height=35, 
            placeholder_text="Generating...")
        self.title_entry.pack(fill="x", padx=15, pady=(5, 10))
        
        # Description
        ctk.CTkLabel(metadata_frame, text="Description", 
            font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(fill="x", padx=15)
        self.desc_text = ctk.CTkTextbox(metadata_frame, height=100, wrap="word")
        self.desc_text.pack(fill="x", padx=15, pady=(5, 12))
        self.desc_text.insert("1.0", "Generating SEO metadata...")
        self.desc_text.configure(state="disabled")
        
        # Schedule section
        schedule_frame = ctk.CTkFrame(main_scroll, fg_color=("gray90", "gray17"), corner_radius=10)
        schedule_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(schedule_frame, text="📅 Schedule Publishing", 
            font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(fill="x", padx=15, pady=(12, 5))
        
        ctk.CTkLabel(schedule_frame, text="Set when to publish (must be in the future, max 7 days)", 
            font=ctk.CTkFont(size=10), text_color="gray", anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # Date & Time inputs
        schedule_inputs = ctk.CTkFrame(schedule_frame, fg_color="transparent")
        schedule_inputs.pack(fill="x", padx=15, pady=(0, 12))
        
        # Date
        date_frame = ctk.CTkFrame(schedule_inputs, fg_color="transparent")
        date_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(date_frame, text="Date:", width=60, anchor="w", 
            font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        
        # Default: tomorrow
        tomorrow = datetime.now() + timedelta(days=1)
        
        self.day_var = ctk.StringVar(value=str(tomorrow.day).zfill(2))
        self.month_var = ctk.StringVar(value=str(tomorrow.month).zfill(2))
        self.year_var = ctk.StringVar(value=str(tomorrow.year))
        
        ctk.CTkEntry(date_frame, textvariable=self.day_var, width=50, 
            placeholder_text="DD").pack(side="left", padx=(0, 5))
        ctk.CTkLabel(date_frame, text="/").pack(side="left")
        ctk.CTkEntry(date_frame, textvariable=self.month_var, width=50, 
            placeholder_text="MM").pack(side="left", padx=5)
        ctk.CTkLabel(date_frame, text="/").pack(side="left")
        ctk.CTkEntry(date_frame, textvariable=self.year_var, width=70, 
            placeholder_text="YYYY").pack(side="left", padx=(5, 0))
        
        # Time
        time_frame = ctk.CTkFrame(schedule_inputs, fg_color="transparent")
        time_frame.pack(fill="x", pady=(0, 0))
        
        ctk.CTkLabel(time_frame, text="Time:", width=60, anchor="w", 
            font=ctk.CTkFont(size=11, weight="bold")).pack(side="left")
        
        self.hour_var = ctk.StringVar(value="12")
        self.minute_var = ctk.StringVar(value="00")
        
        ctk.CTkEntry(time_frame, textvariable=self.hour_var, width=50, 
            placeholder_text="HH").pack(side="left", padx=(0, 5))
        ctk.CTkLabel(time_frame, text=":").pack(side="left")
        ctk.CTkEntry(time_frame, textvariable=self.minute_var, width=50, 
            placeholder_text="MM").pack(side="left", padx=(5, 0))
        ctk.CTkLabel(time_frame, text="(GMT+7)", 
            font=ctk.CTkFont(size=10, weight="bold"), text_color=("gray40", "gray60")).pack(side="left", padx=(10, 0))
        
        # Loading state for accounts
        self.loading_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        self.loading_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(self.loading_frame, text="⏳ Loading accounts...", 
            font=ctk.CTkFont(size=13), text_color="gray").pack()
        
        # Accounts list (will be shown after loading)
        self.accounts_container = ctk.CTkFrame(main_scroll, fg_color="transparent")
        # Don't pack yet - will be shown after loading
        
        # Bottom buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20), side="bottom")
        
        ctk.CTkButton(btn_frame, text="Cancel", height=40, 
            fg_color="gray", hover_color=("gray70", "gray30"),
            command=self.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.upload_btn = ctk.CTkButton(btn_frame, text="Upload to Selected", height=40,
            fg_color=("#27ae60", "#27ae60"), hover_color=("#229954", "#229954"),
            command=self.start_upload, state="disabled")
        self.upload_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # Start generating metadata
        if self.openai_client:
            self.generate_metadata()
    
    def generate_metadata(self):
        """Generate title and description using AI"""
        def do_generate():
            try:
                hook = self.clip_data.get("hook_text", "")
                title = self.clip_data.get("title", "")
                
                prompt = f"""Generate a catchy social media post title and description for this short video clip.

Video Title: {title}
Hook/Content: {hook}

Requirements:
- Title: Max 100 characters, engaging and clickable
- Description: 2-3 sentences, include relevant hashtags
- Make it viral-worthy and platform-friendly

Return JSON format:
{{
    "title": "...",
    "description": "..."
}}"""
                
                response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a social media expert who creates viral content."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                self.after(0, lambda: self._on_metadata_generated(result))
                
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda msg=err_msg: self._on_metadata_error(msg))
        
        threading.Thread(target=do_generate, daemon=True).start()
    
    def _on_metadata_generated(self, result):
        """Handle successful metadata generation"""
        title = result.get("title", self.clip_data.get("title", ""))
        description = result.get("description", "")
        
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, title)
        
        self.desc_text.configure(state="normal")
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", description)
    
    def _on_metadata_error(self, error):
        """Handle metadata generation error"""
        # Use original title and hook as fallback
        title = self.clip_data.get("title", "Untitled")
        hook = self.clip_data.get("hook_text", "")
        
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, title)
        
        self.desc_text.configure(state="normal")
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", hook if hook else "Check out this video!")
    
    def load_accounts(self):
        """Load Repliz accounts from API"""
        def do_load():
            try:
                import requests
                from requests.auth import HTTPBasicAuth
                
                url = "https://api.repliz.com/public/account"
                params = {"page": 1, "limit": 50}
                
                response = requests.get(
                    url,
                    params=params,
                    auth=HTTPBasicAuth(self.access_key, self.secret_key),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    accounts = data.get("docs", [])
                    self.after(0, lambda: self._on_accounts_loaded(accounts))
                else:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", error_msg)
                    except:
                        pass
                    self.after(0, lambda: self._on_load_error(error_msg))
                    
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda msg=err_msg: self._on_load_error(msg))
        
        threading.Thread(target=do_load, daemon=True).start()
    
    def _on_accounts_loaded(self, accounts):
        """Handle successful accounts loading"""
        self.accounts = accounts
        
        # Hide loading
        self.loading_frame.pack_forget()
        
        if not accounts:
            # No accounts found
            no_accounts_frame = ctk.CTkFrame(self.accounts_container, fg_color="transparent")
            no_accounts_frame.pack(fill="x")
            
            ctk.CTkLabel(no_accounts_frame, 
                text="⚠️ No connected accounts found\n\nPlease connect your social media accounts\nin Repliz dashboard first.", 
                font=ctk.CTkFont(size=12), text_color="gray", justify="center").pack(expand=True)
            self.accounts_container.pack(fill="x", pady=(0, 15))
            return
        
        # Show accounts section
        self.accounts_container.pack(fill="x", pady=(0, 15))
        
        # Header
        header = ctk.CTkFrame(self.accounts_container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header, text="Select Platforms:", 
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(side="left")
        
        ctk.CTkLabel(header, text=f"{len(accounts)} account(s)", 
            font=ctk.CTkFont(size=10), text_color="gray").pack(side="right")
        
        # Select All / Deselect All buttons
        btn_row = ctk.CTkFrame(self.accounts_container, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(btn_row, text="Select All", height=28, width=100,
            font=ctk.CTkFont(size=11), fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"), text_color=("gray10", "gray90"),
            command=self._select_all_accounts).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(btn_row, text="Deselect All", height=28, width=100,
            font=ctk.CTkFont(size=11), fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40"), text_color=("gray10", "gray90"),
            command=self._deselect_all_accounts).pack(side="left")
        
        # Accounts list frame
        accounts_list = ctk.CTkFrame(self.accounts_container, fg_color="transparent")
        accounts_list.pack(fill="x")
        
        # Create checkbox for each account
        for account in accounts:
            self._create_account_checkbox(accounts_list, account)
        
        # Enable upload button
        self.upload_btn.configure(state="normal")

    def _select_all_accounts(self):
        """Select all connected accounts"""
        for account, var in self.account_checkboxes:
            if account.get("isConnected", False):
                var.set(True)

    def _deselect_all_accounts(self):
        """Deselect all accounts"""
        for _, var in self.account_checkboxes:
            var.set(False)
    
    def _create_account_checkbox(self, parent, account):
        """Create checkbox for account selection"""
        platform_type = account.get("type", "unknown")
        platform_icons = {
            "youtube": "📺",
            "tiktok": "🎵",
            "instagram": "📸",
            "threads": "🧵",
            "facebook": "👥"
        }
        icon = platform_icons.get(platform_type, "🔗")
        
        # Account card
        card = ctk.CTkFrame(parent, fg_color=("gray90", "gray20"), corner_radius=8)
        card.pack(fill="x", pady=5)
        
        # Checkbox variable
        var = ctk.BooleanVar(value=False)
        self.account_checkboxes.append((account, var))
        
        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=12, pady=10)
        
        # Checkbox on left
        checkbox = ctk.CTkCheckBox(content, text="", variable=var, width=24)
        checkbox.pack(side="left", padx=(0, 10))
        
        # Account info
        info = ctk.CTkFrame(content, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        
        # Platform + name
        name_label = ctk.CTkLabel(info, 
            text=f"{icon} {account.get('name', 'Unknown')}", 
            font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
        name_label.pack(anchor="w")
        
        # Username + platform type
        username = account.get("username", "")
        if username:
            username_text = f"@{username}" if not username.startswith("@") else username
            detail_label = ctk.CTkLabel(info, 
                text=f"{username_text} • {platform_type.upper()}", 
                font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
            detail_label.pack(anchor="w", pady=(2, 0))
        
        # Connection status on right
        is_connected = account.get("isConnected", False)
        if is_connected:
            status_label = ctk.CTkLabel(content, text="✓", 
                font=ctk.CTkFont(size=14), text_color="green")
            status_label.pack(side="right")
        else:
            status_label = ctk.CTkLabel(content, text="✗", 
                font=ctk.CTkFont(size=14), text_color="red")
            status_label.pack(side="right")
            # Disable checkbox if not connected
            checkbox.configure(state="disabled")
    
    def _on_load_error(self, error):
        """Handle accounts loading error"""
        # Hide loading
        self.loading_frame.pack_forget()
        
        # Show error
        error_frame = ctk.CTkFrame(self, fg_color="transparent")
        error_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        ctk.CTkLabel(error_frame, 
            text=f"❌ Failed to load accounts\n\n{error}", 
            font=ctk.CTkFont(size=12), text_color="red", justify="center").pack(expand=True)
    
    def start_upload(self):
        """Start upload to selected accounts"""
        if self.uploading:
            return
        
        # Get selected accounts
        selected = [acc for acc, var in self.account_checkboxes if var.get()]
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one platform to upload to.")
            return
        
        # Get metadata
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", "end").strip()
        
        if not title:
            messagebox.showerror("Error", "Title cannot be empty")
            return
        
        # Get schedule time (required)
        try:
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            
            schedule_dt = datetime(year, month, day, hour, minute)
            now = datetime.now()
            
            # Check if date is in the future
            if schedule_dt <= now:
                messagebox.showerror("Error", "Schedule time must be in the future")
                return
            
            # Check if date is within 7 days
            max_date = now + timedelta(days=7)
            if schedule_dt > max_date:
                messagebox.showerror("Error", 
                    f"Schedule time cannot be more than 7 days in the future\n\n" +
                    f"Maximum date: {max_date.strftime('%d/%m/%Y %H:%M')}")
                return
            
            # Convert local time to UTC (Indonesia is UTC+7)
            # Subtract 7 hours to convert WIB to UTC
            schedule_dt_utc = schedule_dt - timedelta(hours=7)
            schedule_at = schedule_dt_utc.isoformat() + "Z"
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid date/time format: {str(e)}")
            return
        
        self.selected_accounts = selected
        self.uploading = True
        
        # Disable UI
        self.upload_btn.configure(state="disabled", text="Uploading...")
        
        # Show progress dialog
        self.show_upload_progress(selected, title, description, schedule_at)
    
    def show_upload_progress(self, accounts, title, description, schedule_at):
        """Show upload progress dialog"""
        # Create progress window
        progress_win = ctk.CTkToplevel(self)
        progress_win.title("Upload Progress")
        progress_win.geometry("500x400")
        progress_win.transient(self)
        progress_win.grab_set()
        
        # Set icon for progress window
        try:
            from utils.helpers import get_bundle_dir
            BUNDLE_DIR = get_bundle_dir()
            ASSETS_DIR = BUNDLE_DIR / "assets"
            ICON_ICO_PATH = ASSETS_DIR / "icon.ico"
            
            if sys.platform == "win32" and ICON_ICO_PATH.exists():
                progress_win.iconbitmap(str(ICON_ICO_PATH))
        except:
            pass
        
        # Header
        ctk.CTkLabel(progress_win, text="📤 Uploading to Repliz", 
            font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        
        # Progress list
        progress_frame = ctk.CTkScrollableFrame(progress_win, height=250)
        progress_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Status labels for each account
        status_labels = {}
        for account in accounts:
            card = ctk.CTkFrame(progress_frame, fg_color=("gray90", "gray20"), corner_radius=8)
            card.pack(fill="x", pady=5)
            
            platform_type = account.get("type", "unknown")
            platform_icons = {
                "youtube": "📺",
                "tiktok": "🎵",
                "instagram": "📸",
                "threads": "🧵",
                "facebook": "👥"
            }
            icon = platform_icons.get(platform_type, "🔗")
            
            name = account.get("name", "Unknown")
            username = account.get("username", "")
            
            ctk.CTkLabel(card, text=f"{icon} {name}", 
                font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(10, 2))
            
            if username:
                ctk.CTkLabel(card, text=f"@{username}", 
                    font=ctk.CTkFont(size=10), text_color="gray", anchor="w").pack(fill="x", padx=12, pady=(0, 5))
            
            status_label = ctk.CTkLabel(card, text="⏳ Waiting...", 
                font=ctk.CTkFont(size=11), text_color="gray", anchor="w")
            status_label.pack(fill="x", padx=12, pady=(0, 10))
            
            status_labels[account.get("_id")] = status_label
        
        # Close button (disabled during upload)
        def on_done():
            """Handle Done button click"""
            from tkinter import messagebox
            messagebox.showinfo(
                "Upload Complete",
                "Your videos have been scheduled successfully!\n\n"
                "Please check your Repliz Dashboard to view and manage your scheduled posts:\n"
                "https://repliz.com/user/dashboard"
            )
            progress_win.destroy()
            self.destroy()  # Close main dialog too
        
        close_btn = ctk.CTkButton(progress_win, text="Close", height=40, state="disabled",
            command=on_done)
        close_btn.pack(fill="x", padx=20, pady=(0, 20))
        
        # Start upload process
        def do_upload():
            try:
                # Step 1: Upload video to storage
                self.after(0, lambda: self._update_all_status(status_labels, "📤 Uploading video to storage...", "blue"))
                
                video_path = self.clip_data.get("video")
                video_url = self.upload_video_to_storage(str(video_path))
                
                if not video_url:
                    self.after(0, lambda: self._update_all_status(status_labels, "❌ Failed to upload video to storage", "red"))
                    self.after(0, lambda: close_btn.configure(state="normal"))
                    return
                
                self.video_url = video_url
                self.after(0, lambda: self._update_all_status(status_labels, "✓ Video uploaded to storage", "green"))
                
                # Step 2: Upload to each account
                for account in accounts:
                    account_id = account.get("_id")
                    account_name = account.get("name", "Unknown")
                    
                    self.after(0, lambda aid=account_id: status_labels[aid].configure(
                        text="📤 Scheduling post...", text_color="blue"))
                    
                    success, message = self.upload_to_repliz(account_id, title, description, video_url, schedule_at)
                    
                    if success:
                        self.after(0, lambda aid=account_id, msg=message: status_labels[aid].configure(
                            text=f"✓ {msg}", text_color="green"))
                    else:
                        self.after(0, lambda aid=account_id, msg=message: status_labels[aid].configure(
                            text=f"✗ {msg}", text_color="red"))
                
                # Enable close button
                self.after(0, lambda: close_btn.configure(state="normal", text="Done"))
                
            except Exception as e:
                err_msg = f"❌ Error: {str(e)}"
                self.after(0, lambda msg=err_msg: self._update_all_status(status_labels, msg, "red"))
                self.after(0, lambda: close_btn.configure(state="normal"))
        
        threading.Thread(target=do_upload, daemon=True).start()
    
    def _update_all_status(self, status_labels, text, color="gray"):
        """Update all status labels"""
        for label in status_labels.values():
            label.configure(text=text, text_color=color)
    
    def upload_video_to_storage(self, video_path: str) -> str:
        """Upload video to S3 using pre-signed URL"""
        try:
            import requests
            import uuid
            
            # Get file info
            file_size = Path(video_path).stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            print(f"Uploading video: {file_size_mb:.2f} MB")
            
            # Step 1: Request pre-signed URL from N8N
            filename = f"{uuid.uuid4()}.mp4"
            presigned_url_endpoint = "https://api.ytclip.org/webhook/yt-clipper/presigned-url"
            
            print("Requesting pre-signed URL...")
            response = requests.post(
                presigned_url_endpoint,
                json={
                    "filename": filename
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Failed to get pre-signed URL: HTTP {response.status_code}")
                return None
            
            data = response.json()
            presigned_url = data.get("url")
            public_url = data.get("publicUrl")
            file_key = data.get("key")
            
            if not presigned_url or not public_url:
                print("Invalid response from pre-signed URL endpoint")
                return None
            
            print(f"Got pre-signed URL for key: {file_key}")
            
            # Step 2: Upload directly to S3 using pre-signed URL
            print("Uploading to S3...")
            with open(video_path, 'rb') as f:
                upload_response = requests.put(
                    presigned_url,
                    data=f,
                    headers={
                        'Content-Type': 'video/mp4',
                        'x-amz-acl': 'public-read'  # Make file public
                    },
                    timeout=1800  # 30 minutes for large files
                )
            
            if upload_response.status_code in [200, 204]:
                print(f"Upload success: {public_url}")
                return public_url
            else:
                print(f"S3 upload failed: HTTP {upload_response.status_code}")
                print(f"Response: {upload_response.text}")
                return None
                
        except Exception as e:
            print(f"Upload error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def upload_to_repliz(self, account_id: str, title: str, description: str, video_url: str, schedule_at: str = None) -> tuple:
        """Upload to Repliz API for specific account"""
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            
            url = "https://api.repliz.com/public/schedule"
            
            payload = {
                "title": title,
                "description": description,
                "type": "video",
                "medias": [{
                    "type": "video",
                    "thumbnail": "",
                    "url": video_url
                }],
                "accountId": account_id
            }
            
            # Add schedule time if provided
            if schedule_at:
                payload["scheduleAt"] = schedule_at
            
            response = requests.post(
                url,
                json=payload,
                auth=HTTPBasicAuth(self.access_key, self.secret_key),
                headers={
                    "accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return True, "Scheduled successfully"
            else:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg = error_data.get("message", error_msg)
                except:
                    pass
                return False, error_msg
                
        except Exception as e:
            return False, str(e)
