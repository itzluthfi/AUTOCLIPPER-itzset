"""
Clip Editor Dialog - Modifies clip settings before processing
"""

import customtkinter as ctk
from tkinter import messagebox
import re

class ClipEditorDialog(ctk.CTkToplevel):
    """Toplevel modal dialog for editing individual clip properties"""
    
    def __init__(self, parent, highlight_data: dict, on_save_callback):
        super().__init__(parent)
        self.title("✏️ Edit Clip Details")
        
        # Make it modal
        self.transient(parent)
        self.grab_set()
        
        self.highlight = highlight_data.copy()  # Work on a copy
        self.on_save = on_save_callback
        
        # Dimensions & positioning
        self.width = 480
        self.height = 560
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        
        # Center window on parent
        self.update_idletasks()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - self.width) // 2
        y = parent_y + (parent_h - self.height) // 2
        self.geometry(f"+{x}+{y}")
        
        # Setup UI
        self.create_ui()
        
    def create_ui(self):
        """Create editor form widgets"""
        self.configure(fg_color=("#1a1a1a", "#0d0d0d"))
        
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title Label
        ctk.CTkLabel(container, text="✏️ Edit Clip Settings", 
            font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(0, 15))
        
        # Form grid
        form_frame = ctk.CTkScrollableFrame(container, fg_color="transparent", height=410)
        form_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # 1. Clip Title
        ctk.CTkLabel(form_frame, text="Clip Title", 
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(anchor="w", pady=(5, 2))
        self.title_entry = ctk.CTkEntry(form_frame, height=35)
        self.title_entry.pack(fill="x", pady=(0, 10))
        self.title_entry.insert(0, self.highlight.get("title", ""))
        
        # 2. Hook Text
        ctk.CTkLabel(form_frame, text="Hook Text / Headline Overlay", 
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(anchor="w", pady=(5, 2))
        self.hook_entry = ctk.CTkEntry(form_frame, height=35)
        self.hook_entry.pack(fill="x", pady=(0, 10))
        self.hook_entry.insert(0, self.highlight.get("hook_text", ""))
        
        # 3. Start Time Shift
        ctk.CTkLabel(form_frame, text="Start Time (format: hh:mm:ss,ms)", 
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(anchor="w", pady=(5, 2))
        start_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        start_row.pack(fill="x", pady=(0, 10))
        
        self.start_entry = ctk.CTkEntry(start_row, height=35)
        self.start_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.start_entry.insert(0, self.highlight.get("start_time", ""))
        
        ctk.CTkButton(start_row, text="-0.5s", width=48, height=35, fg_color="#333",
            command=lambda: self.adjust_time("start", -0.5)).pack(side="left", padx=2)
        ctk.CTkButton(start_row, text="+0.5s", width=48, height=35, fg_color="#333",
            command=lambda: self.adjust_time("start", 0.5)).pack(side="left", padx=2)
        
        # 4. End Time Shift
        ctk.CTkLabel(form_frame, text="End Time (format: hh:mm:ss,ms)", 
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(anchor="w", pady=(5, 2))
        end_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        end_row.pack(fill="x", pady=(0, 10))
        
        self.end_entry = ctk.CTkEntry(end_row, height=35)
        self.end_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.end_entry.insert(0, self.highlight.get("end_time", ""))
        
        ctk.CTkButton(end_row, text="-0.5s", width=48, height=35, fg_color="#333",
            command=lambda: self.adjust_time("end", -0.5)).pack(side="left", padx=2)
        ctk.CTkButton(end_row, text="+0.5s", width=48, height=35, fg_color="#333",
            command=lambda: self.adjust_time("end", 0.5)).pack(side="left", padx=2)
        
        # Separator
        ctk.CTkFrame(form_frame, height=1, fg_color="gray25").pack(fill="x", pady=10)
        
        # 5. Subtitle Style Preset
        ctk.CTkLabel(form_frame, text="🎨 Subtitle Styling Template", 
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(anchor="w", pady=(5, 2))
            
        style_options_map = {
            "tiktok_bold": "TikTok Bold (White & Yellow)",
            "neon_cyberpunk": "Cyberpunk Neon (White & Neon Green)",
            "vibrant_sunset": "Vibrant Sunset (White & Magenta)",
            "duo_tone_blue": "Duo-Tone Cyan & Blue",
            "drama_red": "Drama Red (White & Red)"
        }
        self.style_dropdown_options = list(style_options_map.values())
        
        current_style = self.highlight.get("subtitle_style", "tiktok_bold")
        default_style_display = style_options_map.get(current_style, "TikTok Bold (White & Yellow)")
        
        self.style_dropdown_var = ctk.StringVar(value=default_style_display)
        self.style_dropdown = ctk.CTkOptionMenu(
            form_frame, 
            values=self.style_dropdown_options, 
            variable=self.style_dropdown_var,
            height=35
        )
        self.style_dropdown.pack(fill="x", pady=(0, 10))
        
        # 6. Speaker Tracking Override
        ctk.CTkLabel(form_frame, text="📷 Speaker/Camera Tracking Mode Override", 
            font=ctk.CTkFont(size=11, weight="bold"), text_color="gray").pack(anchor="w", pady=(5, 2))
            
        tracking_options_map = {
            "opencv": "OpenCV (Standard Face & Motion)",
            "yunet": "YuNet AI (High Accuracy Deep Learning)",
            "mediapipe": "MediaPipe (Lip-Sync Active Speaker)",
            "split_screen": "Split-Screen (Static Host + Guest)"
        }
        self.tracking_dropdown_options = list(tracking_options_map.values())
        
        current_tracking = self.highlight.get("face_tracking_mode", "yunet")
        default_tracking_display = tracking_options_map.get(current_tracking, "YuNet AI (High Accuracy Deep Learning)")
        
        self.tracking_dropdown_var = ctk.StringVar(value=default_tracking_display)
        self.tracking_dropdown = ctk.CTkOptionMenu(
            form_frame, 
            values=self.tracking_dropdown_options, 
            variable=self.tracking_dropdown_var,
            height=35
        )
        self.tracking_dropdown.pack(fill="x", pady=(0, 15))
        
        # Action Buttons row
        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")
        
        ctk.CTkButton(btn_row, text="Cancel", height=38, fg_color="transparent", 
            hover_color="gray25", command=self.destroy).pack(side="left", fill="x", expand=True, padx=(0, 5))
            
        ctk.CTkButton(btn_row, text="✓ Save Changes", height=38, fg_color=("#3B8ED0", "#1F6AA5"), 
            hover_color=("#2E7AB8", "#16527D"), command=self.save_changes).pack(side="right", fill="x", expand=True, padx=(5, 0))
            
    def adjust_time(self, type_name: str, seconds: float):
        """Shift timing values up or down by float seconds and update entries"""
        entry = self.start_entry if type_name == "start" else self.end_entry
        ts_str = entry.get().strip()
        
        try:
            sec_val = self.parse_timestamp(ts_str)
            new_sec = max(0.0, sec_val + seconds)
            new_ts = self.seconds_to_timestamp(new_sec)
            entry.delete(0, "end")
            entry.insert(0, new_ts)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid timestamp format: {e}")

    def parse_timestamp(self, ts: str) -> float:
        """Convert srt timestamp hh:mm:ss,ms to seconds"""
        ts = ts.replace(",", ".")
        parts = ts.split(":")
        if len(parts) != 3:
            raise ValueError("Timestamp must be in hh:mm:ss,ms format")
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])

    def seconds_to_timestamp(self, seconds: float) -> str:
        """Convert float seconds to srt timestamp format hh:mm:ss,ms"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        
    def save_changes(self):
        """Validate input values, save overrides, and close"""
        # Read text values
        title = self.title_entry.get().strip()
        hook = self.hook_entry.get().strip()
        start_ts = self.start_entry.get().strip()
        end_ts = self.end_entry.get().strip()
        
        if not title:
            messagebox.showwarning("Validation Error", "Title cannot be empty")
            return
            
        # Regex format checks for hh:mm:ss,ms
        time_pattern = re.compile(r'^\d{2,}:\d{2}:\d{2}[,\.]\d{3}$')
        if not time_pattern.match(start_ts) or not time_pattern.match(end_ts):
            messagebox.showerror("Validation Error", "Timestamps must match format 'hh:mm:ss,ms'")
            return
            
        try:
            start_sec = self.parse_timestamp(start_ts)
            end_sec = self.parse_timestamp(end_ts)
            if start_sec >= end_sec:
                messagebox.showerror("Validation Error", "Start time must be before End time")
                return
            duration = end_sec - start_sec
        except Exception as e:
            messagebox.showerror("Validation Error", f"Timestamp parse error: {e}")
            return
            
        # Reverse map options values to config names
        style_map = {
            "TikTok Bold (White & Yellow)": "tiktok_bold",
            "Cyberpunk Neon (White & Neon Green)": "neon_cyberpunk",
            "Vibrant Sunset (White & Magenta)": "vibrant_sunset",
            "Duo-Tone Cyan & Blue": "duo_tone_blue",
            "Drama Red (White & Red)": "drama_red"
        }
        selected_style = style_map.get(self.style_dropdown_var.get(), "tiktok_bold")
        
        tracking_map = {
            "OpenCV (Standard Face & Motion)": "opencv",
            "YuNet AI (High Accuracy Deep Learning)": "yunet",
            "MediaPipe (Lip-Sync Active Speaker)": "mediapipe",
            "Split-Screen (Static Host + Guest)": "split_screen"
        }
        selected_tracking = tracking_map.get(self.tracking_dropdown_var.get(), "yunet")
        
        # Save modifications back to clip dict
        self.highlight["title"] = title
        self.highlight["hook_text"] = hook
        self.highlight["start_time"] = start_ts.replace(".", ",")
        self.highlight["end_time"] = end_ts.replace(".", ",")
        self.highlight["duration_seconds"] = duration
        self.highlight["subtitle_style"] = selected_style
        self.highlight["face_tracking_mode"] = selected_tracking
        
        self.on_save(self.highlight)
        self.destroy()
