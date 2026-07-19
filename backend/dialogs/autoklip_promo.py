"""
AutoKlip Promo Dialog
One-time promotional modal that introduces AutoKlip (web/mobile companion).
"""

import webbrowser
import customtkinter as ctk


AUTOKLIP_URL = "https://dub.sh/autoklip"


class AutoKlipPromoDialog(ctk.CTkToplevel):
    """One-time promo modal for AutoKlip multi-platform companion."""

    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)

        self.on_close_callback = on_close_callback

        # Window setup
        self.title("Coba AutoKlip")
        self.geometry("520x440")
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Center on parent
        self.update_idletasks()
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 260
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 220
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self._build_ui()

        # Grab focus after the window is fully rendered to avoid grab errors
        self.after(100, self._grab_focus)

    def _grab_focus(self):
        try:
            self.grab_set()
            self.focus_force()
        except Exception:
            pass

    def _build_ui(self):
        # Main container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=20)

        # Sparkle/emoji header
        ctk.CTkLabel(
            main,
            text="✨",
            font=ctk.CTkFont(size=40),
        ).pack(pady=(0, 4))

        # Title
        ctk.CTkLabel(
            main,
            text="Mau Bikin Klip Lebih Praktis?",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(0, 6))

        # Subtitle
        ctk.CTkLabel(
            main,
            text="Coba AutoKlip — versi online yang lebih ringan",
            font=ctk.CTkFont(size=12),
            text_color=("#9aa0a6", "#9aa0a6"),
        ).pack(pady=(0, 14))

        # Body card
        body = ctk.CTkFrame(
            main,
            fg_color=("#1f1f1f", "#141414"),
            corner_radius=10,
            border_width=1,
            border_color=("#2f2f2f", "#222222"),
        )
        body.pack(fill="x", pady=(0, 14))

        body_text = (
            "Tanpa install, tanpa ribet setup. AutoKlip jalan langsung\n"
            "di browser dan juga tersedia di Android & iOS.\n\n"
            "  •  🌐  Web — buka di browser mana saja\n"
            "  •  📱  Android & iOS — bawa kemana-mana\n"
            "  •  ⚡  Proses di cloud, hemat baterai laptop\n"
            "  •  🎬  Hasil klip kualitas sama"
        )
        ctk.CTkLabel(
            body,
            text=body_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).pack(fill="x", padx=18, pady=14)

        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x")

        self.later_btn = ctk.CTkButton(
            btn_frame,
            text="Nanti Saja",
            width=140,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color=("#3a3a3a", "#2a2a2a"),
            hover_color=("#4a4a4a", "#3a3a3a"),
            command=self._on_close,
        )
        self.later_btn.pack(side="left")

        self.cta_btn = ctk.CTkButton(
            btn_frame,
            text="🚀  Coba AutoKlip Sekarang",
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=("#5865F2", "#4752C4"),
            hover_color=("#4752C4", "#3c45a5"),
            command=self._on_cta,
        )
        self.cta_btn.pack(side="right", fill="x", expand=True, padx=(10, 0))

    def _on_cta(self):
        try:
            webbrowser.open(AUTOKLIP_URL)
        except Exception:
            pass
        self._on_close()

    def _on_close(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.destroy()
        if self.on_close_callback:
            try:
                self.on_close_callback()
            except Exception:
                pass
