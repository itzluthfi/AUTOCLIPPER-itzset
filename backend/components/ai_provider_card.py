"""
AI Provider Card Component - Collapsible card for AI provider settings
"""

import customtkinter as ctk
from tkinter import messagebox


class AIProviderCard(ctk.CTkFrame):
    """Collapsible card for AI provider configuration"""
    
    def __init__(self, parent, title, description, provider_key, config, on_validate_callback):
        super().__init__(parent, fg_color=("gray90", "gray17"), corner_radius=10)
        
        self.title = title
        self.description = description
        self.provider_key = provider_key
        self.config = config
        self.on_validate = on_validate_callback
        self.is_expanded = False
        
        self.create_ui()
        self.load_config()
    
    def create_ui(self):
        """Create the card UI"""
        # Header (always visible)
        header = ctk.CTkFrame(self, fg_color="transparent", cursor="hand2")
        header.pack(fill="x", padx=15, pady=12)
        header.bind("<Button-1>", lambda e: self.toggle_expand())
        
        # Left: Icon + Title + Description
        left_frame = ctk.CTkFrame(header, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True)
        left_frame.bind("<Button-1>", lambda e: self.toggle_expand())
        
        # Title row
        title_row = ctk.CTkFrame(left_frame, fg_color="transparent")
        title_row.pack(fill="x")
        title_row.bind("<Button-1>", lambda e: self.toggle_expand())
        
        self.title_label = ctk.CTkLabel(title_row, text=self.title, 
            font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
        self.title_label.pack(side="left")
        self.title_label.bind("<Button-1>", lambda e: self.toggle_expand())
        
        # Status indicator
        self.status_label = ctk.CTkLabel(title_row, text="⚠️ Not configured", 
            font=ctk.CTkFont(size=10), text_color="orange", anchor="w")
        self.status_label.pack(side="left", padx=(10, 0))
        self.status_label.bind("<Button-1>", lambda e: self.toggle_expand())
        
        # Description
        self.desc_label = ctk.CTkLabel(left_frame, text=self.description, 
            font=ctk.CTkFont(size=11), text_color="gray", anchor="w")
        self.desc_label.pack(fill="x", pady=(3, 0))
        self.desc_label.bind("<Button-1>", lambda e: self.toggle_expand())
        
        # Right: Expand/Collapse icon
        self.expand_icon = ctk.CTkLabel(header, text="▼", font=ctk.CTkFont(size=16), 
            text_color="gray", cursor="hand2")
        self.expand_icon.pack(side="right")
        self.expand_icon.bind("<Button-1>", lambda e: self.toggle_expand())
        
        # Content (collapsible)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        # Don't pack yet - will be shown on expand
        
        # API URL
        url_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        url_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        ctk.CTkLabel(url_frame, text="API Base URL", font=ctk.CTkFont(size=11, weight="bold"), 
            anchor="w").pack(fill="x")
        self.url_entry = ctk.CTkEntry(url_frame, height=35, 
            placeholder_text="https://api.openai.com/v1")
        self.url_entry.pack(fill="x", pady=(5, 0))
        
        # API Key
        key_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        key_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        key_label_row = ctk.CTkFrame(key_frame, fg_color="transparent")
        key_label_row.pack(fill="x")
        
        ctk.CTkLabel(key_label_row, text="API Key", font=ctk.CTkFont(size=11, weight="bold"), 
            anchor="w").pack(side="left")
        
        self.key_entry = ctk.CTkEntry(key_frame, height=35, show="*",
            placeholder_text="sk-...")
        self.key_entry.pack(fill="x", pady=(5, 0))
        
        # Model
        model_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(model_frame, text="Model", font=ctk.CTkFont(size=11, weight="bold"), 
            anchor="w").pack(fill="x")
        self.model_entry = ctk.CTkEntry(model_frame, height=35,
            placeholder_text="gpt-4.1")
        self.model_entry.pack(fill="x", pady=(5, 0))
        
        # Buttons
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.validate_btn = ctk.CTkButton(btn_frame, text="🔍 Validate", height=35,
            fg_color=("#3B8ED0", "#1F6AA5"), command=self.validate_config)
        self.validate_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.apply_all_btn = ctk.CTkButton(btn_frame, text="📋 Apply URL & Key to All", height=35,
            fg_color="gray", command=self.apply_to_all)
        self.apply_all_btn.pack(side="left", fill="x", expand=True, padx=(5, 0))
    
    def toggle_expand(self):
        """Toggle expand/collapse"""
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            self.content_frame.pack(fill="x", pady=(0, 10))
            self.expand_icon.configure(text="▲")
        else:
            self.content_frame.pack_forget()
            self.expand_icon.configure(text="▼")
    
    def load_config(self):
        """Load configuration from config"""
        providers = self.config.get("ai_providers", {})
        provider = providers.get(self.provider_key, {})
        
        url = provider.get("base_url", "https://api.openai.com/v1")
        api_key = provider.get("api_key", "")
        model = provider.get("model", "")
        
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)
        
        self.key_entry.delete(0, "end")
        self.key_entry.insert(0, api_key)
        
        self.model_entry.delete(0, "end")
        self.model_entry.insert(0, model)
        
        # Update status
        if api_key and model:
            self.status_label.configure(text="✓ Configured", text_color="#27ae60")
        else:
            self.status_label.configure(text="⚠️ Not configured", text_color="orange")
    
    def get_config(self):
        """Get current configuration"""
        return {
            "base_url": self.url_entry.get().strip() or "https://api.openai.com/v1",
            "api_key": self.key_entry.get().strip(),
            "model": self.model_entry.get().strip()
        }
    
    def validate_config(self):
        """Validate API configuration"""
        config = self.get_config()
        
        if not config["api_key"]:
            messagebox.showerror("Error", "API Key is required")
            return
        
        if not config["model"]:
            messagebox.showerror("Error", "Model is required")
            return
        
        # Call parent validation callback
        self.on_validate(self.provider_key, config)
    
    def apply_to_all(self):
        """Apply URL and API Key to all providers"""
        if messagebox.askyesno("Apply to All", 
            "Apply this URL and API Key to all AI providers?\n\n(Models will remain separate)"):
            # Trigger parent callback
            if hasattr(self.master, 'apply_url_key_to_all'):
                self.master.apply_url_key_to_all(self.url_entry.get().strip(), 
                    self.key_entry.get().strip())
