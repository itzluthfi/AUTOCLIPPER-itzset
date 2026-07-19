"""
Highlight Selection Page - User selects which highlights to process
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox
from pages.clip_editor_dialog import ClipEditorDialog



class HighlightSelectionPage(ctk.CTkFrame):
    """Page for selecting highlights to process"""
    
    def __init__(self, parent, on_back_callback, on_process_callback, config=None):
        super().__init__(parent)
        self.on_back = on_back_callback
        self.on_process = on_process_callback
        self.config = config or {}
        
        self.highlights = []
        self.session_dir = None
        self.checkboxes = []
        self.checkbox_vars = []
        
        self.create_ui()
    
    def create_ui(self):
        """Create the highlight selection UI"""
        from components.page_layout import PageFooter
        
        # Set background color
        self.configure(fg_color=("#1a1a1a", "#0a0a0a"))
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        # Back button + title
        left_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header.pack(side="left")
        
        ctk.CTkButton(left_header, text="←", width=40, fg_color="transparent",
            hover_color=("gray75", "gray25"), command=self.on_back).pack(side="left")
        ctk.CTkLabel(left_header, text="Select Highlights", 
            font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=10)
        
        # Instructions
        instructions_frame = ctk.CTkFrame(self, fg_color="transparent")
        instructions_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        ctk.CTkLabel(instructions_frame, text="Select which highlights you want to process into short videos",
            font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w")
        
        # Virality score legend
        legend_frame = ctk.CTkFrame(instructions_frame, fg_color="transparent")
        legend_frame.pack(anchor="w", pady=(3, 0))
        
        ctk.CTkLabel(legend_frame, text="Virality Score:", 
            font=ctk.CTkFont(size=10), text_color="gray").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(legend_frame, text="🔥 7-10 High", 
            font=ctk.CTkFont(size=9), text_color="#27ae60").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(legend_frame, text="⚡ 5-6 Medium", 
            font=ctk.CTkFont(size=9), text_color="#f39c12").pack(side="left", padx=(0, 8))
        ctk.CTkLabel(legend_frame, text="💫 1-4 Low", 
            font=ctk.CTkFont(size=9), text_color="#e74c3c").pack(side="left")
        
        # Enhancement options (Caption & Hook)
        options_frame = ctk.CTkFrame(self, fg_color=("#2b2b2b", "#1a1a1a"), corner_radius=8)
        options_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(options_frame, text="Enhancements", 
            font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(10, 5))
        
        # Captions toggle
        captions_row = ctk.CTkFrame(options_frame, fg_color="transparent")
        captions_row.pack(fill="x", padx=12, pady=(0, 3))
        
        ctk.CTkLabel(captions_row, text="💬 Add Captions", font=ctk.CTkFont(size=10), 
            anchor="w").pack(side="left")
        
        self.caption_var = ctk.BooleanVar(value=True)
        self.caption_switch = ctk.CTkSwitch(captions_row, text="ON", variable=self.caption_var, 
            width=36, height=18, command=self.update_caption_switch_text)
        self.caption_switch.pack(side="right")
        
        # Hook toggle
        hook_row = ctk.CTkFrame(options_frame, fg_color="transparent")
        hook_row.pack(fill="x", padx=12, pady=(0, 10))
        
        ctk.CTkLabel(hook_row, text="🪝 Add Hook Text", font=ctk.CTkFont(size=10), 
            anchor="w").pack(side="left")
        
        self.hook_var = ctk.BooleanVar(value=True)
        self.hook_switch = ctk.CTkSwitch(hook_row, text="ON", variable=self.hook_var, 
            width=36, height=18, command=self.update_hook_switch_text)
        self.hook_switch.pack(side="right")
        
        # Separator line
        sep = ctk.CTkFrame(options_frame, height=1, fg_color=("gray75", "gray25"))
        sep.pack(fill="x", padx=12, pady=10)
        
        # Camera Mode section header
        ctk.CTkLabel(options_frame, text="📷 Camera & Speaker Tracking Mode", 
            font=ctk.CTkFont(size=11, weight="bold"), anchor="w").pack(fill="x", padx=12, pady=(0, 5))
            
        # Tracking selection dropdown row
        tracking_row = ctk.CTkFrame(options_frame, fg_color="transparent")
        tracking_row.pack(fill="x", padx=12, pady=(0, 6))
        
        # Load default value from config
        default_mode = "YuNet AI (High Accuracy Deep Learning)"
        if self.config:
            config_dict = self.config.config if hasattr(self.config, 'config') else self.config
            saved_mode = config_dict.get("face_tracking_mode", "yunet")
            if saved_mode == "opencv":
                default_mode = "OpenCV (Standard Face & Motion)"
            elif saved_mode == "mediapipe":
                default_mode = "MediaPipe (Lip-Sync Active Speaker)"
            elif saved_mode == "split_screen":
                default_mode = "Split-Screen (Static Host + Guest)"
                
        self.tracking_dropdown_var = ctk.StringVar(value=default_mode)
        self.tracking_dropdown = ctk.CTkOptionMenu(
            tracking_row,
            values=[
                "OpenCV (Standard Face & Motion)",
                "YuNet AI (High Accuracy Deep Learning)",
                "MediaPipe (Lip-Sync Active Speaker)",
                "Split-Screen (Static Host + Guest)"
            ],
            variable=self.tracking_dropdown_var,
            font=ctk.CTkFont(size=11),
            width=290,
            command=self.update_tracking_description
        )
        self.tracking_dropdown.pack(side="left")
        
        # Help/Info card frame for pros/cons description
        self.tracking_info_frame = ctk.CTkFrame(options_frame, fg_color=("gray90", "gray15"), corner_radius=6)
        self.tracking_info_frame.pack(fill="x", padx=12, pady=(0, 10))
        
        self.tracking_info_label = ctk.CTkLabel(
            self.tracking_info_frame, 
            text="", 
            font=ctk.CTkFont(size=10), 
            anchor="w", 
            justify="left",
            wraplength=450
        )
        self.tracking_info_label.pack(fill="x", padx=10, pady=8)
        
        # Initial description update
        self.update_tracking_description()
        
        # Scrollable list of highlights
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Bottom action buttons
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Select all / Deselect all
        select_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        select_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(select_frame, text="✓ Select All", height=35,
            fg_color=("#3a3a3a", "#2a2a2a"), hover_color=("#4a4a4a", "#3a3a3a"),
            font=ctk.CTkFont(size=11), command=self.select_all).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        ctk.CTkButton(select_frame, text="✗ Deselect All", height=35,
            fg_color=("#3a3a3a", "#2a2a2a"), hover_color=("#4a4a4a", "#3a3a3a"),
            font=ctk.CTkFont(size=11), command=self.deselect_all).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Process button
        self.process_btn = ctk.CTkButton(bottom_frame, text="🎬 Process Selected Clips", height=45,
            font=ctk.CTkFont(size=14, weight="bold"), command=self.process_selected,
            fg_color=("#3B8ED0", "#1F6AA5"), hover_color=("#2E7AB8", "#16527D"))
        self.process_btn.pack(fill="x")
        
        # Add dynamic hover glow transition
        def on_process_enter(event):
            self.process_btn.configure(
                fg_color=("#50a4e6", "#2980b9"),
                border_width=1,
                border_color=("#2ecc71", "#2ecc71")
            )
        def on_process_leave(event):
            self.process_btn.configure(
                fg_color=("#3B8ED0", "#1F6AA5"),
                border_width=0
            )
        self.process_btn.bind("<Enter>", on_process_enter)
        self.process_btn.bind("<Leave>", on_process_leave)
        
        # Footer
        footer = PageFooter(self, self)
        footer.pack(fill="x", padx=20, pady=(10, 15))
    
    def set_highlights(self, highlights: list, session_dir):
        """Set highlights data and populate list"""
        self.highlights = highlights
        self.session_dir = session_dir
        self.populate_list()
    
    def populate_list(self):
        """Populate the highlights list"""
        # Clear existing
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        self.checkboxes = []
        self.checkbox_vars = []
        
        if not self.highlights:
            ctk.CTkLabel(self.list_frame, text="No highlights found",
                font=ctk.CTkFont(size=13), text_color="gray").pack(pady=30)
            return
        
        # Create list items
        for i, highlight in enumerate(self.highlights, 1):
            # Card frame
            card = ctk.CTkFrame(self.list_frame, fg_color=("gray85", "gray20"), corner_radius=10)
            card.pack(fill="x", pady=5, padx=5)
            
            # Main content
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=12)
            
            # Top row: Checkbox + Title + Virality Score
            top_row = ctk.CTkFrame(content, fg_color="transparent")
            top_row.pack(fill="x", pady=(0, 5))
            
            # Checkbox
            var = ctk.BooleanVar(value=True)  # Default selected
            checkbox = ctk.CTkCheckBox(top_row, text="", variable=var, width=24, height=24)
            checkbox.pack(side="left", padx=(0, 10))
            self.checkboxes.append(checkbox)
            self.checkbox_vars.append(var)
            
            # Title
            title = highlight.get("title", "Untitled")
            ctk.CTkLabel(top_row, text=f"#{i}. {title}", 
                font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(side="left", fill="x", expand=True)
            
            # Virality score badge
            virality = highlight.get("virality_score", 0)
            if virality >= 7:
                score_color = "#27ae60"
                score_emoji = "🔥"
            elif virality >= 5:
                score_color = "#f39c12"
                score_emoji = "⚡"
            elif virality > 0:
                score_color = "#e74c3c"
                score_emoji = "💫"
            else:
                score_color = "#95a5a6"
                score_emoji = "❓"
            
            ctk.CTkLabel(top_row, text=f"{score_emoji} {virality}/10",
                font=ctk.CTkFont(size=11, weight="bold"), text_color=score_color).pack(side="right", padx=(10, 0))
            
            # Hook text
            hook_text = highlight.get("hook_text", "")
            if hook_text:
                hook_frame = ctk.CTkFrame(content, fg_color="transparent")
                hook_frame.pack(fill="x", pady=(0, 3))
                ctk.CTkLabel(hook_frame, text=f"🪝 {hook_text}", font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#FFD700", anchor="w", wraplength=650, justify="left").pack(fill="x")
            
            # Description
            description = highlight.get("description", "")
            if description:
                ctk.CTkLabel(content, text=description, font=ctk.CTkFont(size=11),
                    text_color="gray", anchor="w", wraplength=650, justify="left").pack(fill="x", pady=(0, 5))
            
            # Transcript text (conversation content)
            transcript_text = highlight.get("transcript_text", "")
            if transcript_text:
                transcript_frame = ctk.CTkFrame(content, fg_color=("#222222", "#151515"), corner_radius=6)
                transcript_frame.pack(fill="x", pady=(0, 5))
                
                ctk.CTkLabel(transcript_frame, text="💬 Isi Percakapan:", 
                    font=ctk.CTkFont(size=10, weight="bold"), text_color="#aaaaaa",
                    anchor="w").pack(fill="x", padx=10, pady=(8, 2))
                
                # Truncate long transcripts
                display_text = transcript_text[:300]
                if len(transcript_text) > 300:
                    display_text += "..."
                
                ctk.CTkLabel(transcript_frame, text=display_text, 
                    font=ctk.CTkFont(size=10), text_color="#cccccc",
                    anchor="w", wraplength=630, justify="left").pack(fill="x", padx=10, pady=(0, 8))
            
            # Bottom row: Timestamp + Duration
            bottom_row = ctk.CTkFrame(content, fg_color="transparent")
            bottom_row.pack(fill="x")
            
            # Timestamp and duration
            start_time = highlight.get("start_time", "00:00:00,000")
            end_time = highlight.get("end_time", "00:00:00,000")
            duration = highlight.get("duration_seconds", 0)
            
            # Format timestamps (remove milliseconds for display)
            start_display = start_time.split(',')[0]
            end_display = end_time.split(',')[0]
            
            ctk.CTkLabel(bottom_row, text=f"⏱️ {start_display} → {end_display} ({duration:.0f}s)",
                font=ctk.CTkFont(size=10), text_color="gray", anchor="w").pack(side="left")
            
            # Edit button packed to the right
            edit_btn = ctk.CTkButton(
                bottom_row, 
                text="✏️ Edit", 
                width=55, 
                height=22,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=("#3a3a3a", "#2b2b2b"),
                hover_color=("#4a4a4a", "#3b3b3b"),
                command=lambda h_idx=i-1: self.open_edit_dialog(h_idx)
            )
            edit_btn.pack(side="right")
    
    def select_all(self):
        """Select all checkboxes"""
        for var in self.checkbox_vars:
            var.set(True)
    
    def deselect_all(self):
        """Deselect all checkboxes"""
        for var in self.checkbox_vars:
            var.set(False)
    
    def process_selected(self):
        """Process selected highlights"""
        # Get selected highlights
        selected = []
        for i, var in enumerate(self.checkbox_vars):
            if var.get():
                selected.append(self.highlights[i])
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one highlight to process")
            return
        
        # Get enhancement options
        add_captions = self.caption_var.get()
        add_hook = self.hook_var.get()
        
        # Confirm with user
        count = len(selected)
        enhancements = []
        if add_captions:
            enhancements.append("Captions")
        if add_hook:
            enhancements.append("Hook Text")
        
        enhancement_text = " + ".join(enhancements) if enhancements else "No enhancements"
        
        if not messagebox.askyesno("Confirm Processing", 
            f"Process {count} selected clip{'s' if count > 1 else ''}?\n\n"
            f"Enhancements: {enhancement_text}\n\n"
            "Video sections will be downloaded individually for each clip."):
            return
        
        # Call process callback with selected highlights and options
        self.on_process(selected, add_captions, add_hook)
    
    def update_caption_switch_text(self):
        """Update caption switch text based on state"""
        if self.caption_var.get():
            self.caption_switch.configure(text="ON")
        else:
            self.caption_switch.configure(text="OFF")
    
    def update_hook_switch_text(self):
        """Update hook switch text based on state"""
        if self.hook_var.get():
            self.hook_switch.configure(text="ON")
        else:
            self.hook_switch.configure(text="OFF")
    
    def show_page(self, page_name: str):
        """Navigate to another page (for footer compatibility)"""
        pass
    
    def open_github(self):
        """Open GitHub repository"""
        import webbrowser
        webbrowser.open("https://github.com/jipraks/yt-short-clipper")
    
    def open_discord(self):
        """Open Discord server"""
        import webbrowser
        webbrowser.open("https://s.id/ytsdiscord")
        
    def update_tracking_description(self, *args):
        """Update the pros, cons, and requirements help text based on the selected mode"""
        mode_text = self.tracking_dropdown_var.get()
        
        # Update config dict immediately
        config_dict = self.config.config if hasattr(self.config, 'config') else self.config
        
        if "OpenCV" in mode_text:
            new_val = "opencv"
            info = (
                "✅ Kelebihan: Sangat cepat, hemat baterai, pan kamera dinamis mengikuti pergerakan pixel/wajah.\n"
                "❌ Kekurangan: Akurasi pelacakan wajah standar.\n"
                "📌 Syarat: Tanpa syarat tambahan (bawaan sistem)."
            )
        elif "YuNet" in mode_text:
            new_val = "yunet"
            info = (
                "✅ Kelebihan: Deteksi wajah berbasis Deep Learning super akurat (tampak samping, menunduk, tertutup).\n"
                "❌ Kekurangan: Sedikit lebih menggunakan daya CPU dibanding OpenCV biasa.\n"
                "📌 Syarat: Mengunduh model pendeteksi ONNX (~337 KB) otomatis saat pertama kali dipakai."
            )
        elif "MediaPipe" in mode_text:
            new_val = "mediapipe"
            info = (
                "✅ Kelebihan: Kamera otomatis menyorot ke pembicara aktif berdasarkan gerakan bibir.\n"
                "❌ Kekurangan: Proses pemrosesan klip 2x s.d 3x lebih lambat.\n"
                "📌 Syarat: Harus menginstal library MediaPipe terlebih dahulu."
            )
        else: # Split-Screen
            new_val = "split_screen"
            info = (
                "✅ Kelebihan: Layar terbelah vertikal atas-bawah menampilkan Host dan Guest secara bersamaan.\n"
                "❌ Kekurangan: Kamera bersifat statis/kaku (tidak mengikuti gerakan wajah).\n"
                "📌 Syarat: Host harus di kiri & Guest harus di kanan video asli (Lanskap)."
            )
            
        config_dict["face_tracking_mode"] = new_val
        if hasattr(self.config, 'save'):
            self.config.save()
            
        if hasattr(self, 'tracking_info_label'):
            self.tracking_info_label.configure(text=info)
            
    def open_edit_dialog(self, highlight_idx: int):
        """Open the ClipEditorDialog to edit highlight properties and refresh list"""
        highlight_data = self.highlights[highlight_idx]
        
        def save_callback(updated_data):
            self.highlights[highlight_idx] = updated_data
            self.populate_list()  # Refresh all cards
            
        dialog = ClipEditorDialog(self.winfo_toplevel(), highlight_data, save_callback)
        dialog.focus()
