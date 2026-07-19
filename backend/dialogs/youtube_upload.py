"""
YouTube upload dialog with SEO metadata generation
"""

import sys
import json
import threading
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image


class YouTubeUploadDialog(ctk.CTkToplevel):
    """Dialog for uploading video to YouTube with SEO metadata"""
    
    def __init__(self, parent, clip: dict, openai_client, model: str, temperature: float = 1.0):
        super().__init__(parent)
        self.clip = clip
        self.openai_client = openai_client
        self.model = model
        self.temperature = temperature
        self.uploading = False
        
        self.title("Upload to YouTube")
        self.geometry("550x700")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Set icon
        self.set_dialog_icon()
        
        self.create_ui()
        self.generate_seo_metadata()
    
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
        """Create the dialog UI"""
        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        ctk.CTkLabel(main, text="📤 Upload to YouTube", 
            font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))
        
        # Video info
        info_frame = ctk.CTkFrame(main, fg_color=("gray85", "gray20"))
        info_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(info_frame, text=f"📹 {self.clip['title'][:50]}", 
            anchor="w").pack(fill="x", padx=10, pady=10)
        
        # Scrollable content area
        scroll_frame = ctk.CTkScrollableFrame(main, height=400)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Title
        ctk.CTkLabel(scroll_frame, text="Title (max 100 chars)", anchor="w", 
            font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(5, 0))
        self.title_entry = ctk.CTkEntry(scroll_frame, height=40)
        self.title_entry.pack(fill="x", pady=(5, 0))
        self.title_count = ctk.CTkLabel(scroll_frame, text="0/100", 
            text_color="gray", anchor="e")
        self.title_count.pack(fill="x")
        self.title_entry.bind("<KeyRelease>", self.update_title_count)
        
        # Description
        ctk.CTkLabel(scroll_frame, text="Description", anchor="w", 
            font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(10, 0))
        self.desc_text = ctk.CTkTextbox(scroll_frame, height=120)
        self.desc_text.pack(fill="x", pady=(5, 0))
        self.desc_count = ctk.CTkLabel(scroll_frame, text="0/5000", 
            text_color="gray", anchor="e")
        self.desc_count.pack(fill="x")
        self.desc_text.bind("<KeyRelease>", self.update_desc_count)
        
        # Privacy
        privacy_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        privacy_frame.pack(fill="x", pady=(15, 10))
        ctk.CTkLabel(privacy_frame, text="Privacy:", 
            font=ctk.CTkFont(weight="bold")).pack(side="left")
        self.privacy_var = ctk.StringVar(value="private")
        for val, text in [("private", "Private"), ("unlisted", "Unlisted"), ("public", "Public")]:
            ctk.CTkRadioButton(privacy_frame, text=text, variable=self.privacy_var, 
                value=val).pack(side="left", padx=10)
        
        # Schedule option
        schedule_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        schedule_frame.pack(fill="x", pady=(0, 10))
        
        self.schedule_var = ctk.BooleanVar(value=False)
        self.schedule_check = ctk.CTkCheckBox(schedule_frame, text="Schedule publish", 
            variable=self.schedule_var, command=self.toggle_schedule)
        self.schedule_check.pack(side="left")
        
        # Schedule datetime inputs (hidden by default)
        self.schedule_inputs = ctk.CTkFrame(scroll_frame, fg_color=("gray90", "gray17"))
        
        schedule_inner = ctk.CTkFrame(self.schedule_inputs, fg_color="transparent")
        schedule_inner.pack(fill="x", padx=10, pady=10)
        
        # Date
        date_frame = ctk.CTkFrame(schedule_inner, fg_color="transparent")
        date_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(date_frame, text="Date (YYYY-MM-DD)", 
            font=ctk.CTkFont(size=10)).pack(anchor="w")
        self.date_entry = ctk.CTkEntry(date_frame, placeholder_text="2026-01-20", height=35)
        self.date_entry.pack(fill="x")
        
        # Time
        time_frame = ctk.CTkFrame(schedule_inner, fg_color="transparent")
        time_frame.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(time_frame, text="Time (HH:MM)", 
            font=ctk.CTkFont(size=10)).pack(anchor="w")
        self.time_entry = ctk.CTkEntry(time_frame, placeholder_text="14:00", height=35)
        self.time_entry.pack(fill="x")
        
        ctk.CTkLabel(self.schedule_inputs, text="⚠️ Time in UTC timezone", 
            font=ctk.CTkFont(size=10), text_color="orange").pack(pady=(0, 5))
        
        # Generate button
        self.generate_btn = ctk.CTkButton(scroll_frame, text="🔄 Regenerate SEO", 
            height=35, fg_color="gray", command=self.generate_seo_metadata)
        self.generate_btn.pack(fill="x", pady=(10, 0))
        
        # Progress (outside scroll)
        self.progress_frame = ctk.CTkFrame(main, fg_color="transparent")
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", text_color="gray")
        self.progress_label.pack()
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
        
        # Buttons (outside scroll)
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(btn_frame, text="Cancel", height=45, fg_color="gray",
            command=self.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.upload_btn = ctk.CTkButton(btn_frame, text="⬆️ Upload", height=45, 
            fg_color="#c4302b", hover_color="#ff0000", command=self.start_upload)
        self.upload_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
    
    def toggle_schedule(self):
        """Show/hide schedule inputs"""
        if self.schedule_var.get():
            self.schedule_inputs.pack(fill="x", pady=(0, 10))
            # Set default to tomorrow at current time
            from datetime import datetime, timedelta
            tomorrow = datetime.utcnow() + timedelta(days=1)
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, tomorrow.strftime("%Y-%m-%d"))
            self.time_entry.delete(0, "end")
            self.time_entry.insert(0, tomorrow.strftime("%H:%M"))
        else:
            self.schedule_inputs.pack_forget()
    
    def update_title_count(self, event=None):
        """Update title character count"""
        count = len(self.title_entry.get())
        color = "red" if count > 100 else "gray"
        self.title_count.configure(text=f"{count}/100", text_color=color)
    
    def update_desc_count(self, event=None):
        """Update description character count"""
        count = len(self.desc_text.get("1.0", "end-1c"))
        color = "red" if count > 5000 else "gray"
        self.desc_count.configure(text=f"{count}/5000", text_color=color)
    
    def generate_seo_metadata(self):
        """Generate SEO-optimized title and description using GPT"""
        self.generate_btn.configure(state="disabled", text="Generating...")
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, "Generating...")
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", "Generating SEO metadata...")
        
        def do_generate():
            try:
                from youtube_uploader import generate_seo_metadata
                metadata = generate_seo_metadata(
                    self.openai_client,
                    self.clip['title'],
                    self.clip['hook_text'],
                    self.model,
                    self.temperature
                )
                self.after(0, lambda: self.set_metadata(metadata))
            except Exception as e:
                self.after(0, lambda: self.set_metadata({
                    'title': f"🔥 {self.clip['title']}"[:100],
                    'description': f"{self.clip['hook_text']}\n\n#shorts #viral #fyp",
                    'tags': ['shorts', 'viral']
                }))
        
        threading.Thread(target=do_generate, daemon=True).start()
    
    def set_metadata(self, metadata: dict):
        """Set generated metadata in UI"""
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, metadata.get('title', ''))
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", metadata.get('description', ''))
        self.generate_btn.configure(state="normal", text="🔄 Regenerate SEO")
        self.update_title_count()
        self.update_desc_count()
        
        # Save to data.json
        self.save_metadata_to_clip(metadata)
    
    def save_metadata_to_clip(self, metadata: dict):
        """Save generated metadata to clip's data.json"""
        try:
            data_file = self.clip['folder'] / "data.json"
            if data_file.exists():
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {}
            
            data['youtube_title'] = metadata.get('title', '')
            data['youtube_description'] = metadata.get('description', '')
            data['youtube_tags'] = metadata.get('tags', [])
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def start_upload(self):
        """Start the upload process"""
        if self.uploading:
            return
        
        title = self.title_entry.get().strip()
        description = self.desc_text.get("1.0", "end-1c").strip()
        
        if not title:
            messagebox.showerror("Error", "Title is required")
            return
        
        if len(title) > 100:
            messagebox.showerror("Error", "Title must be under 100 characters")
            return
        
        # Validate schedule if enabled
        publish_at = None
        if self.schedule_var.get():
            date_str = self.date_entry.get().strip()
            time_str = self.time_entry.get().strip()
            
            if not date_str or not time_str:
                messagebox.showerror("Error", "Please enter both date and time for scheduled upload")
                return
            
            try:
                from datetime import datetime
                # Parse and validate datetime
                datetime_str = f"{date_str}T{time_str}:00Z"
                publish_dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                
                # Check if in future
                if publish_dt <= datetime.utcnow().replace(tzinfo=publish_dt.tzinfo):
                    messagebox.showerror("Error", "Scheduled time must be in the future")
                    return
                
                publish_at = datetime_str
            except ValueError:
                messagebox.showerror("Error", "Invalid date/time format. Use YYYY-MM-DD and HH:MM")
                return
        
        self.uploading = True
        self.upload_btn.configure(state="disabled", text="Uploading...")
        self.generate_btn.configure(state="disabled")
        self.schedule_check.configure(state="disabled")
        self.progress_frame.pack(fill="x", pady=5)
        self.progress_label.configure(text="Starting upload...")
        
        def do_upload():
            try:
                from youtube_uploader import YouTubeUploader
                uploader = YouTubeUploader(
                    status_callback=lambda m: self.after(0, lambda: self.progress_label.configure(text=m))
                )
                
                result = uploader.upload_video(
                    video_path=str(self.clip['video']),
                    title=title,
                    description=description,
                    privacy_status=self.privacy_var.get(),
                    publish_at=publish_at,
                    progress_callback=lambda p: self.after(0, lambda: self.update_upload_progress(p))
                )
                
                self.after(0, lambda: self.on_upload_complete(result))
                
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda msg=err_msg: self.on_upload_error(msg))
        
        threading.Thread(target=do_upload, daemon=True).start()
    
    def update_upload_progress(self, progress: int):
        """Update upload progress bar"""
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"Uploading... {progress}%")
    
    def on_upload_complete(self, result: dict):
        """Handle upload completion"""
        self.uploading = False
        
        if result.get('success'):
            video_url = result.get('url', '')
            messagebox.showinfo("Success", f"Video uploaded successfully!\n\n{video_url}")
            
            # Save YouTube URL to data.json
            try:
                data_file = self.clip['folder'] / "data.json"
                if data_file.exists():
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    data['youtube_url'] = video_url
                    data['youtube_video_id'] = result.get('video_id', '')
                    with open(data_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
            except:
                pass
            
            self.destroy()
        else:
            self.on_upload_error(result.get('error', 'Unknown error'))
    
    def on_upload_error(self, error: str):
        """Handle upload error"""
        self.uploading = False
        self.upload_btn.configure(state="normal", text="⬆️ Upload")
        self.generate_btn.configure(state="normal")
        self.progress_label.configure(text=f"Error: {error[:50]}")
        messagebox.showerror("Upload Failed", error)
