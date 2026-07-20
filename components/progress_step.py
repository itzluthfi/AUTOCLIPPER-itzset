"""
Progress step component for showing processing status - Card style
"""

import customtkinter as ctk


class ProgressStep(ctk.CTkFrame):
    """A single step card in the progress indicator"""
    
    def __init__(self, parent, step_num: int, title: str):
        super().__init__(parent, fg_color=("gray85", "gray20"), corner_radius=8)
        self.step_num = step_num
        self.status = "pending"  # pending, active, done, error
        
        # Main content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=10)
        
        # Step indicator circle
        self.indicator = ctk.CTkLabel(
            content, 
            text=str(step_num), 
            width=30, 
            height=30,
            fg_color=("gray70", "gray30"), 
            corner_radius=15, 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.indicator.pack(pady=(0, 8))
        
        # Step title
        self.title_label = ctk.CTkLabel(
            content, 
            text=title, 
            font=ctk.CTkFont(size=11, weight="bold"), 
            wraplength=120,
            justify="center"
        )
        self.title_label.pack()
        
        # Status label
        self.status_label = ctk.CTkLabel(
            content, 
            text="Waiting...", 
            font=ctk.CTkFont(size=10), 
            text_color="gray"
        )
        self.status_label.pack(pady=(4, 0))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(content, height=6, width=100)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()

    def set_active(self, status_text: str = "Processing...", progress: float = None):
        """Set step to active state with optional progress and start pulse animation"""
        self.status = "active"
        self.configure(border_width=2)
        self.indicator.configure(fg_color=("#3498db", "#2980b9"), text="●")
        self.status_label.configure(text=status_text, text_color=("#3498db", "#5dade2"))
        
        if progress is None:
            progress = 0.0
        
        self.progress_bar.pack(pady=(6, 0))
        self.progress_bar.set(progress)
        
        # Start pulsing skeleton effect
        self.pulse_idx = 0
        self._pulse()
    
    def _pulse(self):
        """Pulse background and border color to simulate a smooth breathing neon glow animation"""
        if self.status != "active":
            return
        
        # Smooth color cycle simulating a glowing wave sweeping across (16-step sine transition)
        colors_dark = [
            "#1e1e1e", "#202020", "#222222", "#252525", 
            "#292929", "#2e2e2e", "#343434", "#3b3b3b", 
            "#424242", "#3b3b3b", "#343434", "#2e2e2e", 
            "#292929", "#252525", "#222222", "#202020"
        ]
        colors_light = [
            "#e2e2e2", "#e4e4e4", "#e7e7e7", "#eaeaea", 
            "#ededed", "#f0f0f0", "#f4f4f4", "#f8f8f8", 
            "#fcfcfc", "#f8f8f8", "#f4f4f4", "#f0f0f0", 
            "#ededed", "#eaeaea", "#e7e7e7", "#e4e4e4"
        ]
        
        # Gradient glowing blue borders
        borders_dark = [
            "#1f6aa5", "#2274b0", "#257ebb", "#298bc7",
            "#2d98d3", "#31a5df", "#2d98d3", "#298bc7",
            "#257ebb", "#2274b0", "#1f6aa5", "#1c5f98",
            "#19548b", "#164a7e", "#19548b", "#1c5f98"
        ]
        borders_light = [
            "#3b8ed0", "#4aa0db", "#59b2e6", "#68c4f1",
            "#77d6fc", "#68c4f1", "#59b2e6", "#4aa0db",
            "#3b8ed0", "#2f7fc2", "#2471b4", "#1a63a6",
            "#115598", "#1a63a6", "#2471b4", "#2f7fc2"
        ]
        
        idx = self.pulse_idx % len(colors_dark)
        self.pulse_idx += 1
        
        self.configure(
            fg_color=(colors_light[idx], colors_dark[idx]),
            border_color=(borders_light[idx], borders_dark[idx])
        )
        self.after(50, self._pulse)
    
    def set_done(self, status_text: str = "Complete"):
        """Set step to done state"""
        self.status = "done"
        self.configure(fg_color=("gray85", "gray20"), border_width=1, border_color=("#27ae60", "#1e8449"))
        self.indicator.configure(fg_color=("#27ae60", "#1e8449"), text="✓")
        self.status_label.configure(text=status_text, text_color=("#27ae60", "#2ecc71"))
        self.progress_bar.pack_forget()
    
    def set_error(self, status_text: str = "Failed"):
        """Set step to error state"""
        self.status = "error"
        self.configure(fg_color=("gray85", "gray20"), border_width=1, border_color=("#e74c3c", "#c0392b"))
        self.indicator.configure(fg_color=("#e74c3c", "#c0392b"), text="✗")
        self.status_label.configure(text=status_text, text_color=("#e74c3c", "#ec7063"))
        self.progress_bar.pack_forget()
    
    def reset(self):
        """Reset step to initial pending state"""
        self.status = "pending"
        self.configure(fg_color=("gray85", "gray20"), border_width=0)
        self.indicator.configure(fg_color=("gray70", "gray30"), text=str(self.step_num))
        self.status_label.configure(text="Waiting...", text_color="gray")
        self.progress_bar.pack_forget()
        self.progress_bar.set(0)
