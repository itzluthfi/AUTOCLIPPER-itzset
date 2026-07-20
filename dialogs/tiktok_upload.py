"""
TikTok upload dialog (Sandbox Mode)
"""

import sys
import json
import threading
import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
from PIL import Image


class TikTokUploadDialog(ctk.CTkToplevel):
    """Dialog for uploading video to TikTok (Sandbox Mode)"""
    
    def __init__(self, parent, clip: dict, config):
        super().__init__(parent)
        self.clip = clip
        self.config = config
        self.uploading = False
        
        self.title("Upload to TikTok")
        self.geometry("550x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Set icon
        self.set_dialog_icon()
        
        self.create_ui()
    
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
        ctk.CTkLabel(main, text="🎵 Upload to TikTok", 
            font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 15))
        
        # Sandbox mode notice
        notice_frame = ctk.CTkFrame(main, fg_color=("orange", "#ff8c00"))
        notice_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(notice_frame, text="ℹ️ Sandbox Mode: Video will be saved as private draft", 
            text_color="white", font=ctk.CTkFont(size=11, weight="bold")).pack(padx=10, pady=8)
        
        # Video info
        info_frame = ctk.CTkFrame(main, fg_color=("gray85", "gray20"))
        info_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(info_frame, text=f"📹 {self.clip['title'][:50]}", 
            anchor="w").pack(fill="x", padx=10, pady=10)
        
        # Scrollable content area
        scroll_frame = ctk.CTkScrollableFrame(main, height=280)
        scroll_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Title/Caption
        ctk.CTkLabel(scroll_frame, text="Caption (max 150 chars for sandbox)", anchor="w", 
            font=ctk.CTkFont(weight="bold")).pack(fill="x", pady=(5, 0))
        
        # Pre-fill with hook text
        default_caption = self.clip.get('hook_text', self.clip['title'])[:150]
        
        self.caption_entry = ctk.CTkTextbox(scroll_frame, height=80)
        self.caption_entry.pack(fill="x", pady=(5, 0))
        self.caption_entry.insert("1.0", default_caption)
        
        self.caption_count = ctk.CTkLabel(scroll_frame, text="0/150", 
            text_color="gray", anchor="e")
        self.caption_count.pack(fill="x")
        self.caption_entry.bind("<KeyRelease>", self.update_caption_count)
        self.update_caption_count()
        
        # Privacy Level
        privacy_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        privacy_frame.pack(fill="x", pady=(15, 10))
        
        ctk.CTkLabel(privacy_frame, text="Privacy Level:", 
            font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(0, 5))
        
        self.privacy_var = ctk.StringVar(value="SELF_ONLY")
        
        privacy_options = [
            ("SELF_ONLY", "Private (Only Me)"),
            ("MUTUAL_FOLLOW_FRIENDS", "Friends"),
            ("FOLLOWER_OF_CREATOR", "Followers"),
            ("PUBLIC_TO_EVERYONE", "Public")
        ]
        
        for value, text in privacy_options:
            ctk.CTkRadioButton(privacy_frame, text=text, variable=self.privacy_var, 
                value=value).pack(anchor="w", padx=20, pady=2)
        
        # Video Settings
        settings_frame = ctk.CTkFrame(scroll_frame, fg_color=("gray90", "gray17"))
        settings_frame.pack(fill="x", pady=(15, 10))
        
        ctk.CTkLabel(settings_frame, text="Video Settings", 
            font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.disable_comment_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(settings_frame, text="Disable comments", 
            variable=self.disable_comment_var).pack(anchor="w", padx=20, pady=2)
        
        self.disable_duet_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(settings_frame, text="Disable duet", 
            variable=self.disable_duet_var).pack(anchor="w", padx=20, pady=2)
        
        self.disable_stitch_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(settings_frame, text="Disable stitch", 
            variable=self.disable_stitch_var).pack(anchor="w", padx=20, pady=(2, 10))
        
        # Info note
        info_note = ctk.CTkFrame(scroll_frame, fg_color=("gray90", "gray17"))
        info_note.pack(fill="x", pady=(10, 0))
        
        note_text = """📝 Note:
• Sandbox mode uploads videos as private drafts
• Open TikTok app to review and publish
• Video will not be public until you publish it manually"""
        
        ctk.CTkLabel(info_note, text=note_text, justify="left", anchor="w",
            font=ctk.CTkFont(size=10), text_color="gray").pack(padx=10, pady=10)
        
        # Progress (outside scroll, before buttons)
        self.progress_frame = ctk.CTkFrame(main, fg_color="transparent")
        self.progress_frame.pack(fill="x", pady=(10, 5))
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="", text_color="gray",
            wraplength=500)
        self.progress_label.pack()
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)
        
        # Buttons (outside scroll)
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(btn_frame, text="Cancel", height=45, fg_color="gray",
            command=self.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.upload_btn = ctk.CTkButton(btn_frame, text="⬆️ Upload to TikTok", height=45, 
            fg_color="#000000", hover_color="#1a1a1a", command=self.start_upload)
        self.upload_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
    
    def update_caption_count(self, event=None):
        """Update caption character count"""
        count = len(self.caption_entry.get("1.0", "end-1c"))
        color = "red" if count > 150 else "gray"
        self.caption_count.configure(text=f"{count}/150", text_color=color)
    
    def start_upload(self):
        """Start the upload process"""
        if self.uploading:
            return
        
        caption = self.caption_entry.get("1.0", "end-1c").strip()
        
        if not caption:
            messagebox.showerror("Error", "Caption is required")
            return
        
        if len(caption) > 150:
            messagebox.showerror("Error", "Caption must be under 150 characters for sandbox mode")
            return
        
        # Check if TikTok is configured and authenticated
        try:
            from tiktok_uploader import TikTokUploader
            uploader = TikTokUploader(self.config)
            
            if not uploader.is_configured():
                messagebox.showerror("Error", 
                    "TikTok not configured.\n\n" +
                    "Please add your Client Key and Client Secret in Settings → Social Accounts → TikTok")
                return
            
            if not uploader.is_authenticated():
                messagebox.showerror("Error", 
                    "TikTok not connected.\n\n" +
                    "Please connect your TikTok account in Settings → Social Accounts → TikTok")
                return
        except ImportError:
            messagebox.showerror("Error", "TikTok uploader module not available")
            return
        except Exception as e:
            messagebox.showerror("Error", f"TikTok uploader error: {str(e)}")
            return
        
        self.uploading = True
        self.upload_btn.configure(state="disabled", text="Uploading...")
        self.progress_frame.pack(fill="x", pady=5)
        self.progress_label.configure(text="Starting upload...")
        
        def do_upload():
            try:
                print("=== Starting TikTok upload thread ===")
                from tiktok_uploader import TikTokUploader
                uploader = TikTokUploader(
                    self.config,
                    status_callback=lambda m: self.after(0, lambda msg=m: self.progress_label.configure(text=msg))
                )
                
                print(f"Calling upload_video with path: {self.clip['video']}")
                result = uploader.upload_video(
                    video_path=str(self.clip['video']),
                    title=caption,
                    privacy_level=self.privacy_var.get(),
                    disable_comment=self.disable_comment_var.get(),
                    disable_duet=self.disable_duet_var.get(),
                    disable_stitch=self.disable_stitch_var.get(),
                    progress_callback=lambda p: self.after(0, lambda prog=p: self.update_upload_progress(prog))
                )
                
                print(f"Upload result: {result}")
                self.after(0, lambda r=result: self.on_upload_complete(r))
                
            except Exception as e:
                print(f"=== EXCEPTION in upload thread ===")
                print(f"Exception type: {type(e).__name__}")
                print(f"Exception message: {str(e)}")
                import traceback
                traceback.print_exc()
                self.after(0, lambda err=str(e): self.on_upload_error(err))
        
        threading.Thread(target=do_upload, daemon=True).start()
    
    def update_upload_progress(self, progress: int):
        """Update upload progress bar"""
        self.progress_bar.set(progress / 100)
        self.progress_label.configure(text=f"Uploading... {progress}%")
    
    def on_upload_complete(self, result: dict):
        """Handle upload completion"""
        self.uploading = False
        
        if result.get('success'):
            publish_id = result.get('publish_id', '')
            mode = result.get('mode', 'sandbox')
            
            message = f"Video uploaded successfully!\n\n"
            if mode == "sandbox":
                message += "📱 Video saved as private draft\n"
                message += "Open TikTok app to review and publish"
            else:
                message += f"Publish ID: {publish_id}"
            
            messagebox.showinfo("Success", message)
            
            # Save TikTok info to data.json
            try:
                data_file = self.clip['folder'] / "data.json"
                if data_file.exists():
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = {}
                
                data['tiktok_publish_id'] = publish_id
                data['tiktok_mode'] = mode
                data['tiktok_uploaded'] = True
                
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error saving TikTok info: {e}")
            
            self.destroy()
        else:
            self.on_upload_error(result.get('error', 'Unknown error'))
    
    def on_upload_error(self, error: str):
        """Handle upload error"""
        self.uploading = False
        self.upload_btn.configure(state="normal", text="⬆️ Upload to TikTok")
        
        # Show first 100 chars in progress label
        short_error = error[:100] + "..." if len(error) > 100 else error
        self.progress_label.configure(text=f"Error: {short_error}")
        
        # Show full error in messagebox
        messagebox.showerror("Upload Failed", error)
