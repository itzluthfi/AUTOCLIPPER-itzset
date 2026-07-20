"""
Processing page for video processing workflow
"""

import customtkinter as ctk
from components.progress_step import ProgressStep
from utils.logger import get_error_log_path


class ProcessingPage(ctk.CTkFrame):
    """Processing page - shows progress during video processing"""
    
    def __init__(self, parent, on_cancel_callback, on_back_callback, on_open_output_callback, on_browse_callback):
        super().__init__(parent)
        self.on_cancel = on_cancel_callback
        self.on_back = on_back_callback
        self.on_open_output = on_open_output_callback
        self.on_browse = on_browse_callback
        
        self.create_ui()
    
    def open_github(self):
        """Open GitHub repository"""
        import webbrowser
        webbrowser.open("https://github.com/jipraks/yt-short-clipper")
    
    def open_discord(self):
        """Open Discord server"""
        import webbrowser
        webbrowser.open("https://s.id/ytsdiscord")
    
    def show_page(self, page_name: str):
        """Navigate to another page"""
        pass
    
    def create_ui(self):
        """Create the processing page UI"""
        from components.page_layout import PageHeader, PageFooter
        
        self.configure(fg_color=("#1a1a1a", "#0a0a0a"))
        
        # Header
        header = PageHeader(self, self, show_nav_buttons=False, show_back_button=True, page_title="🔍 Phase 1: Finding Highlights")
        header.pack(fill="x", padx=20, pady=(15, 10))
        
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Progress steps - 2 cards horizontal (NEW FLOW)
        steps_frame = ctk.CTkFrame(main, fg_color=("gray90", "gray17"))
        steps_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(steps_frame, text="Progress", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=15, pady=(12, 8))
        
        cards_frame = ctk.CTkFrame(steps_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=10, pady=(0, 12))
        cards_frame.grid_columnconfigure((0, 1), weight=1, uniform="step")
        self.cards_frame = cards_frame
        
        self.steps = []
        step_titles = [
            "Downloading Subtitles",
            "Finding Highlights with AI"
        ]
        
        for i, title in enumerate(step_titles):
            step = ProgressStep(cards_frame, i + 1, title)
            step.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.steps.append(step)
        
        # Current status & Detail Thinking Console
        self.status_frame = ctk.CTkFrame(main)
        self.status_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Initializing...", 
            font=ctk.CTkFont(size=13, weight="bold"), wraplength=480)
        self.status_label.pack(pady=(12, 2))
        
        self.timer_label = ctk.CTkLabel(self.status_frame, text="⏳ Elapsed Time: 0m 0s", 
            font=ctk.CTkFont(size=11), text_color="gray")
        self.timer_label.pack(pady=(0, 5))
        
        ctk.CTkLabel(self.status_frame, text="Detailed Thinking Log / Console Output:", 
            font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w", padx=15)
            
        self.console_box = ctk.CTkTextbox(self.status_frame, font=ctk.CTkFont(family="Consolas", size=11), 
            fg_color=("#0c0c0c", "#080808"), text_color=("#39ff14", "#39ff14"), border_width=1, border_color="#333", height=150)
        self.console_box.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        self.console_box.insert("end", "=== AutoClipper Core Console Log ===\n")
        self.console_box.configure(state="disabled")
        
        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        row1 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 5))
        
        self.cancel_btn = ctk.CTkButton(row1, text="❌ Cancel", height=45, fg_color="#c0392b", 
            hover_color="#e74c3c", command=self.on_cancel)
        self.cancel_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.back_btn = ctk.CTkButton(row1, text="← Back", height=45, state="disabled", command=self.on_back)
        self.back_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        row2 = ctk.CTkFrame(btn_frame, fg_color="transparent")
        row2.pack(fill="x")
        
        self.open_btn = ctk.CTkButton(row2, text="📂 Open Output", height=45, state="disabled", command=self.on_open_output)
        self.open_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.results_btn = ctk.CTkButton(row2, text="📂 Browse Videos", height=45, state="disabled", 
            fg_color="#27ae60", hover_color="#2ecc71", command=self.on_browse)
        self.results_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Footer
        footer = PageFooter(self, self)
        footer.pack(fill="x", padx=20, pady=(10, 15), side="bottom")
    
    def reset_ui(self):
        """Reset UI for new processing"""
        for step in self.steps:
            step.reset()
        
        self.status_label.configure(text="Initializing...")
        
        # Clear console box
        if hasattr(self, 'console_box'):
            self.console_box.configure(state="normal")
            self.console_box.delete("1.0", "end")
            self.console_box.insert("end", "=== AutoClipper Core Console Log ===\n")
            self.console_box.configure(state="disabled")
            
        self.cancel_btn.configure(state="normal")
        self.open_btn.configure(state="disabled")
        self.back_btn.configure(state="disabled")
        self.results_btn.configure(state="disabled")
    
    def switch_to_transcription_mode(self):
        """Rebuild step cards for 3-step AI transcription flow.
        
        Replaces the 2-step layout with:
        1. Download Video
        2. AI Transcription (Whisper)
        3. Finding Highlights with AI
        """
        # Destroy existing step widgets
        for step in self.steps:
            step.destroy()
        self.steps.clear()
        
        # Reconfigure grid for 3 columns
        self.cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="step")
        
        step_titles = [
            "Downloading Video",
            "AI Transcription",
            "Finding Highlights"
        ]
        
        for i, title in enumerate(step_titles):
            step = ProgressStep(self.cards_frame, i + 1, title)
            step.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.steps.append(step)
        
        self.status_label.configure(text="Downloading video...")
    
    def update_status(self, msg: str):
        """Update status label and detailed thinking log"""
        clean_msg = msg.strip()
        if len(clean_msg) > 60:
            if "ffmpeg" in clean_msg.lower():
                label_text = "Running FFmpeg process..."
            elif "yt-dlp" in clean_msg.lower():
                label_text = "Running YT-DLP extraction..."
            else:
                label_text = clean_msg[:57] + "..."
        else:
            label_text = clean_msg
            
        self.status_label.configure(text=label_text)
        if hasattr(self, 'console_box'):
            self.console_box.configure(state="normal")
            self.console_box.insert("end", f"> {clean_msg}\n")
            self.console_box.configure(state="disabled")
            self.console_box.see("end")
    
    def update_tokens(self, gpt_total: int, whisper_minutes: float, tts_chars: int):
        """Update token usage display (deprecated - kept for compatibility)"""
        pass  # No-op since we removed the UI
    
    def on_complete(self):
        """Called when processing completes successfully"""
        self.status_label.configure(text="✅ All clips created successfully!")
        self.cancel_btn.configure(state="disabled")
        self.open_btn.configure(state="normal")
        self.back_btn.configure(state="normal")
        self.results_btn.configure(state="normal")
        for step in self.steps:
            step.set_done("Complete")
    
    def on_cancelled(self):
        """Called when processing is cancelled"""
        self.status_label.configure(text="⚠️ Cancelled by user")
        self.cancel_btn.configure(state="disabled")
        self.back_btn.configure(state="normal")
        for step in self.steps:
            if step.status == "active":
                step.set_error("Cancelled")
    
    def on_error(self, error: str):
        """Called when processing encounters an error"""
        error_log = get_error_log_path()
        
        if error_log:
            error_msg = f"❌ {error}\n\n📄 Error details saved to:\n{error_log}"
        else:
            error_msg = f"❌ {error}"
        
        self.status_label.configure(text=error_msg)
        self.cancel_btn.configure(state="disabled")
        self.back_btn.configure(state="normal")
        for step in self.steps:
            if step.status == "active":
                step.set_error("Failed")
                
    def update_timer_display(self, text: str):
        """Update the live timer text"""
        if hasattr(self, "timer_label"):
            self.timer_label.configure(text=text)
