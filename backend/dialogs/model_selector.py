"""
Searchable model dropdown dialog for selecting OpenAI models
"""

import sys
import customtkinter as ctk
from pathlib import Path
from PIL import Image


class SearchableModelDropdown(ctk.CTkToplevel):
    """Dialog for selecting a model from a searchable list"""
    
    def __init__(self, parent, models: list, current_value: str, callback):
        super().__init__(parent)
        self.callback = callback
        self.models = models
        self.filtered_models = models.copy()
        
        self.title("Select Model")
        self.geometry("400x500")
        self.transient(parent)
        self.grab_set()
        
        # Set icon
        self.set_dialog_icon()
        
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self.filter_models)
        
        search_entry = ctk.CTkEntry(self, textvariable=self.search_var, 
            placeholder_text="🔍 Search models...", height=40)
        search_entry.pack(fill="x", padx=10, pady=10)
        search_entry.focus()
        
        self.list_frame = ctk.CTkScrollableFrame(self, height=400)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.model_buttons = []
        self.current_value = current_value
        self.render_models()
    
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
    
    def render_models(self):
        """Render the list of models"""
        for btn in self.model_buttons:
            btn.destroy()
        self.model_buttons.clear()
        
        for model in self.filtered_models:
            is_selected = model == self.current_value
            btn = ctk.CTkButton(
                self.list_frame, 
                text=model, 
                anchor="w",
                fg_color=("gray75", "gray25") if is_selected else "transparent",
                hover_color=("gray70", "gray30"), 
                text_color=("gray10", "gray90"),
                command=lambda m=model: self.select_model(m)
            )
            btn.pack(fill="x", pady=1)
            self.model_buttons.append(btn)
    
    def filter_models(self, *args):
        """Filter models based on search input"""
        search = self.search_var.get().lower()
        if search:
            self.filtered_models = [m for m in self.models if search in m.lower()]
        else:
            self.filtered_models = self.models.copy()
        self.render_models()
    
    def select_model(self, model: str):
        """Select a model and close dialog"""
        self.callback(model)
        self.destroy()
