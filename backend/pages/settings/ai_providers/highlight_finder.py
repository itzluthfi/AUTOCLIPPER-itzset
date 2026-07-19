"""
Highlight Finder Settings Page
"""

import customtkinter as ctk

from pages.settings.ai_providers.base_provider import BaseProviderSettingsPage


class HighlightFinderSettingsPage(BaseProviderSettingsPage):
    """Settings page for Highlight Finder AI provider"""
    
    # Load models from API (no fixed list)
    FIXED_MODELS = None
    
    def __init__(self, parent, config, on_save_callback, on_back_callback):
        super().__init__(
            parent=parent,
            title="Highlight Finder",
            provider_key="highlight_finder",
            config=config,
            on_save_callback=on_save_callback,
            on_back_callback=on_back_callback
        )
    
    def _reset_system_message(self):
        """Reset system message to default"""
        from clipper_core import AutoClipperCore
        default_prompt = AutoClipperCore.get_default_prompt()
        self.system_message_textbox.delete("1.0", "end")
        self.system_message_textbox.insert("1.0", default_prompt)
    
    def create_provider_content(self):
        """Create provider settings content with additional info"""
        # Info box
        info_frame = ctk.CTkFrame(self.content, fg_color=("gray85", "gray20"), corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_frame, text="🎯 About Highlight Finder", 
            font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=12, pady=(10, 5))
        ctk.CTkLabel(info_frame, 
            text="Uses GPT models to analyze video transcripts and find\nthe most engaging moments for short-form content.", 
            font=ctk.CTkFont(size=10), text_color="gray", justify="left").pack(anchor="w", padx=12, pady=(0, 10))
        
        # Call parent to create standard fields
        super().create_provider_content()
        
        # Add System Message section after standard fields
        system_section = self.create_section("System Message")
        
        system_frame = ctk.CTkFrame(system_section, fg_color="transparent")
        system_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        ctk.CTkLabel(system_frame, text="System Prompt for Highlight Detection", 
            font=ctk.CTkFont(size=11)).pack(anchor="w")
        
        ctk.CTkLabel(system_frame, 
            text="Customize the AI instructions for finding highlights. Use placeholders:\n{num_clips}, {video_context}, {transcript}", 
            font=ctk.CTkFont(size=9), text_color="gray", justify="left").pack(anchor="w", pady=(2, 5))
        
        # Create scrollable textbox for system message
        self.system_message_textbox = ctk.CTkTextbox(system_frame, height=200, wrap="word")
        self.system_message_textbox.pack(fill="both", expand=True)
        
        # Add reset button
        reset_btn = ctk.CTkButton(system_frame, text="🔄 Reset to Default", height=32,
            fg_color=("gray70", "gray30"), hover_color=("gray60", "gray40"),
            command=self._reset_system_message)
        reset_btn.pack(fill="x", pady=(5, 0))
