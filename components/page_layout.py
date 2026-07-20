"""
Reusable page layout components (header and footer)
"""

import customtkinter as ctk
from pathlib import Path
from PIL import Image
from datetime import datetime


class PageHeader(ctk.CTkFrame):
    """Reusable header component with logo, title, and navigation buttons"""
    
    def __init__(self, parent, app_instance, show_nav_buttons=True, show_back_button=False, page_title=None):
        super().__init__(parent, fg_color="transparent")
        self.app = app_instance
        self.show_nav_buttons = show_nav_buttons
        self.show_back_button = show_back_button
        self.page_title = page_title
        
        self.create_header()
    
    def create_header(self):
        """Create header with logo, title, and navigation"""
        # If back button mode, show back button + page title on left, logo + tagline on right
        if self.show_back_button and self.page_title:
            # Left side: Back button + page title
            left_frame = ctk.CTkFrame(self, fg_color="transparent")
            left_frame.pack(side="left")
            
            ctk.CTkButton(left_frame, text="←", width=40, fg_color="transparent", 
                hover_color=("gray75", "gray25"), 
                command=self.app.on_back if hasattr(self.app, 'on_back') else lambda: self.app.show_page("home")).pack(side="left")
            ctk.CTkLabel(left_frame, text=self.page_title, font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=10)
            
            # Right side: Logo + tagline
            right_frame = ctk.CTkFrame(self, fg_color="transparent")
            right_frame.pack(side="right")
            
            # Try to load icon
            try:
                from utils.helpers import get_bundle_dir
                BUNDLE_DIR = get_bundle_dir()
                ASSETS_DIR = BUNDLE_DIR / "assets"
                ICON_PATH = ASSETS_DIR / "icon.png"
                
                if ICON_PATH.exists():
                    icon_img = Image.open(ICON_PATH)
                    icon_img.thumbnail((32, 32), Image.Resampling.LANCZOS)
                    header_icon = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(32, 32))
                    ctk.CTkLabel(right_frame, image=header_icon, text="").pack(side="left", padx=(0, 10))
                    # Keep reference to prevent garbage collection
                    self.header_icon = header_icon
            except:
                pass
            
            tagline_col = ctk.CTkFrame(right_frame, fg_color="transparent")
            tagline_col.pack(side="left")
            ctk.CTkLabel(tagline_col, text="YT Short Clipper", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(tagline_col, text="Turn long YouTube videos into viral shorts — Powered by AI", 
                font=ctk.CTkFont(size=9), text_color="gray").pack(anchor="w")
            return
        
        # Normal mode: App icon + title on left
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(side="left")
        
        # Try to load icon
        try:
            from utils.helpers import get_bundle_dir
            BUNDLE_DIR = get_bundle_dir()
            ASSETS_DIR = BUNDLE_DIR / "assets"
            ICON_PATH = ASSETS_DIR / "icon.png"
            
            if ICON_PATH.exists():
                icon_img = Image.open(ICON_PATH)
                icon_img.thumbnail((40, 40), Image.Resampling.LANCZOS)
                header_icon = ctk.CTkImage(light_image=icon_img, dark_image=icon_img, size=(40, 40))
                ctk.CTkLabel(title_frame, image=header_icon, text="").pack(side="left", padx=(0, 12))
                # Keep reference to prevent garbage collection
                self.header_icon = header_icon
        except:
            pass
        
        title_col = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(title_col, text="YT Short Clipper", font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(title_col, text="Turn long YouTube videos into viral shorts — Powered by AI", font=ctk.CTkFont(size=11), 
            text_color="gray").pack(anchor="w")
        
        # Navigation buttons on right (if enabled)
        if self.show_nav_buttons:
            nav_frame = ctk.CTkFrame(self, fg_color="transparent")
            nav_frame.pack(side="right")
            
            # Load button icons if available
            try:
                from utils.helpers import get_bundle_dir
                BUNDLE_DIR = get_bundle_dir()
                ASSETS_DIR = BUNDLE_DIR / "assets"
                
                settings_img = Image.open(ASSETS_DIR / "settings.png")
                settings_img.thumbnail((18, 18), Image.Resampling.LANCZOS)
                settings_icon = ctk.CTkImage(light_image=settings_img, dark_image=settings_img, size=(18, 18))
                
                api_img = Image.open(ASSETS_DIR / "api-status.png")
                api_img.thumbnail((18, 18), Image.Resampling.LANCZOS)
                api_icon = ctk.CTkImage(light_image=api_img, dark_image=api_img, size=(18, 18))
                
                lib_img = Image.open(ASSETS_DIR / "lib-status.png")
                lib_img.thumbnail((18, 18), Image.Resampling.LANCZOS)
                lib_icon = ctk.CTkImage(light_image=lib_img, dark_image=lib_img, size=(18, 18))
                
                # Keep references
                self.settings_icon = settings_icon
                self.api_icon = api_icon
                self.lib_icon = lib_icon
            except:
                settings_icon = None
                api_icon = None
                lib_icon = None
            
            ctk.CTkButton(nav_frame, text="Settings", image=settings_icon, compound="left",
                width=90, height=40, font=ctk.CTkFont(size=11),
                fg_color=("#2b2b2b", "#1a1a1a"), hover_color=("#3a3a3a", "#2a2a2a"), corner_radius=10,
                command=lambda: self.app.show_page("settings")).pack(side="left", padx=3)
            
            ctk.CTkButton(nav_frame, text="API", image=api_icon, compound="left",
                width=70, height=40, font=ctk.CTkFont(size=11),
                fg_color=("#2b2b2b", "#1a1a1a"), hover_color=("#3a3a3a", "#2a2a2a"), corner_radius=10,
                command=lambda: self.app.show_page("api_status")).pack(side="left", padx=3)
            
            ctk.CTkButton(nav_frame, text="Library", image=lib_icon, compound="left",
                width=85, height=40, font=ctk.CTkFont(size=11),
                fg_color=("#2b2b2b", "#1a1a1a"), hover_color=("#3a3a3a", "#2a2a2a"), corner_radius=10,
                command=lambda: self.app.show_page("lib_status")).pack(side="left", padx=3)


class PageFooter(ctk.CTkFrame):
    """Reusable footer component with copyright and links"""
    
    def __init__(self, parent, app_instance):
        super().__init__(parent, fg_color="transparent", height=60)
        self.pack_propagate(False)
        self.app = app_instance
        
        self.create_footer()
    
    def create_footer(self):
        """Create footer with separator, copyright, and links"""
        # Separator line
        separator = ctk.CTkFrame(self, height=1, fg_color=("#3a3a3a", "#2a2a2a"))
        separator.pack(fill="x", pady=(0, 12))
        
        # Footer content
        footer_content = ctk.CTkFrame(self, fg_color="transparent")
        footer_content.pack(fill="x")
        
        # Copyright text on left with dynamic year and version
        try:
            from version import __version__
            current_year = datetime.now().year
            copyright_text = f"© {current_year} YT Short Clipper • v{__version__}"
        except:
            copyright_text = "© 2026 YT Short Clipper"
        
        ctk.CTkLabel(footer_content, text=copyright_text, 
            font=ctk.CTkFont(size=10), text_color="gray", anchor="w").pack(side="left")
        
        # Links on right
        links_frame = ctk.CTkFrame(footer_content, fg_color="transparent")
        links_frame.pack(side="right")
        
        # GitHub link
        github_link = ctk.CTkLabel(links_frame, text="⭐ GitHub", 
            font=ctk.CTkFont(size=11), text_color="#ffffff", cursor="hand2")
        github_link.pack(side="left", padx=(0, 15))
        github_link.bind("<Button-1>", lambda e: self.app.open_github())
        
        # Get AI API Key link (cyan/teal)
        api_key_link = ctk.CTkLabel(links_frame, text="🔑 Get AI API Key", 
            font=ctk.CTkFont(size=11), text_color="#00CED1", cursor="hand2")
        api_key_link.pack(side="left", padx=(0, 15))
        api_key_link.bind("<Button-1>", lambda e: self.open_ai_api_key_page())
        
        # AutoKlip link (multi-platform companion)
        autoklip_link = ctk.CTkLabel(links_frame, text="📱 Use AutoKlip (for Web, Android and iOS)", 
            font=ctk.CTkFont(size=11), text_color="#5865F2", cursor="hand2")
        autoklip_link.pack(side="left")
        autoklip_link.bind("<Button-1>", lambda e: self.open_autoklip())

    def open_autoklip(self):
        """Open AutoKlip multi-platform link"""
        import webbrowser
        webbrowser.open("https://dub.sh/autoklip")
    
    def open_ai_api_key_page(self):
        """Open AI API Key page"""
        import webbrowser
        webbrowser.open("https://ai.ytclip.org")

