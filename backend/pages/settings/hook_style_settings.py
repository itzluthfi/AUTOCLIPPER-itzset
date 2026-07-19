"""
Hook Style Settings Sub-Page

Lets the user customize how the hook scene at the start of each clip looks:
font family, font color, background color, corner radius, and on-screen position.
"""

import tkinter as tk
from tkinter import colorchooser

import customtkinter as ctk

from pages.settings.base_dialog import BaseSettingsSubPage
from utils.font_scanner import (
    get_font_names,
    get_path_for_name,
    find_default_font,
)


# Defaults match the previous hard-coded look (white BG, gold text, sharp corners)
DEFAULT_FONT_COLOR = "#FFD700"
DEFAULT_BG_COLOR = "#FFFFFF"
DEFAULT_CORNER_RADIUS = 0
DEFAULT_POS_X = 0.5      # horizontal center
DEFAULT_POS_Y = 0.333    # 1/3 from top (matches the old start_y = height // 3)
DEFAULT_FONT_SIZE = 0.054  # ~58 / 1080, expressed as fraction of video width


class HookStyleSettingsSubPage(BaseSettingsSubPage):
    """Sub-page for configuring the hook overlay style."""

    # Canvas dimensions (9:16 aspect, scaled down)
    CANVAS_W = 270
    CANVAS_H = 480

    def __init__(self, parent, config, on_save_callback, on_back_callback):
        self.config = config
        self.on_save_callback = on_save_callback

        # Drag state
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Canvas item ids (so we can delete + redraw cleanly)
        self.bg_item = None
        self.text_item = None

        super().__init__(parent, "Hook Style", on_back_callback)

        self.create_content()
        self.load_config()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def create_content(self):
        # Info note
        ctk.CTkLabel(
            self.content,
            text="Customize the look of the opening hook scene. Drag the box on the preview to set position.",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=600,
            justify="left",
        ).pack(anchor="w", pady=(0, 15))

        # Two-column layout: preview on the left, controls on the right
        body = ctk.CTkFrame(self.content, fg_color="transparent")
        body.pack(fill="both", expand=True)

        # --- Preview column ---
        preview_col = ctk.CTkFrame(body, fg_color="transparent")
        preview_col.pack(side="left", padx=(0, 20), anchor="n")

        ctk.CTkLabel(
            preview_col,
            text="Preview",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", pady=(0, 5))

        canvas_frame = ctk.CTkFrame(preview_col, fg_color=("gray85", "gray20"))
        canvas_frame.pack()

        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.CANVAS_W,
            height=self.CANVAS_H,
            bg="#1a1a1a",
            highlightthickness=1,
            highlightbackground="gray",
        )
        self.canvas.pack(padx=10, pady=10)

        # 9:16 frame outline + label
        self.canvas.create_rectangle(
            0, 0, self.CANVAS_W, self.CANVAS_H, outline="gray", width=2
        )
        self.canvas.create_text(
            self.CANVAS_W // 2,
            self.CANVAS_H - 20,
            text="9:16 Video Preview",
            fill="gray50",
            font=("Arial", 10),
        )

        # Drag handlers
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)

        ctk.CTkLabel(
            preview_col,
            text="Tip: drag the hook box to reposition.",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        ).pack(anchor="w", pady=(8, 0))

        # --- Controls column ---
        controls = ctk.CTkFrame(body, fg_color="transparent")
        controls.pack(side="left", fill="both", expand=True, anchor="n")

        # Font family
        ctk.CTkLabel(
            controls, text="Font", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        font_names = get_font_names()
        if not font_names:
            font_names = ["Arial"]
        self.font_var = ctk.StringVar(value=font_names[0])
        self.font_dropdown = ctk.CTkComboBox(
            controls,
            values=font_names,
            variable=self.font_var,
            command=lambda _v: self._update_preview(),
            state="readonly",
            height=36,
        )
        self.font_dropdown.pack(fill="x", pady=(0, 15))

        # Font size (as fraction of video width)
        ctk.CTkLabel(
            controls, text="Font Size", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        size_row = ctk.CTkFrame(controls, fg_color="transparent")
        size_row.pack(fill="x", pady=(0, 15))
        self.font_size_var = ctk.DoubleVar(value=DEFAULT_FONT_SIZE)
        ctk.CTkSlider(
            size_row,
            from_=0.025,
            to=0.10,
            variable=self.font_size_var,
            command=lambda _v: self._update_preview(),
            number_of_steps=30,
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.font_size_label = ctk.CTkLabel(size_row, text="5.4%", width=50, anchor="e")
        self.font_size_label.pack(side="right")

        # Font color
        ctk.CTkLabel(
            controls, text="Font Color", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        font_color_row = ctk.CTkFrame(controls, fg_color="transparent")
        font_color_row.pack(fill="x", pady=(0, 15))
        self.font_color = DEFAULT_FONT_COLOR
        self.font_color_swatch = tk.Frame(
            font_color_row, bg=self.font_color, width=36, height=36,
            highlightthickness=1, highlightbackground="gray",
        )
        self.font_color_swatch.pack(side="left", padx=(0, 10))
        self.font_color_swatch.pack_propagate(False)
        self.font_color_entry = ctk.CTkEntry(font_color_row, width=120, height=36)
        self.font_color_entry.insert(0, self.font_color)
        self.font_color_entry.bind("<Return>", lambda _e: self._apply_color_entry("font"))
        self.font_color_entry.bind("<FocusOut>", lambda _e: self._apply_color_entry("font"))
        self.font_color_entry.pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            font_color_row, text="Pick...", width=80, height=36,
            command=lambda: self._pick_color("font"),
        ).pack(side="left")

        # Background color
        ctk.CTkLabel(
            controls, text="Background Color", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        bg_color_row = ctk.CTkFrame(controls, fg_color="transparent")
        bg_color_row.pack(fill="x", pady=(0, 15))
        self.bg_color = DEFAULT_BG_COLOR
        self.bg_color_swatch = tk.Frame(
            bg_color_row, bg=self.bg_color, width=36, height=36,
            highlightthickness=1, highlightbackground="gray",
        )
        self.bg_color_swatch.pack(side="left", padx=(0, 10))
        self.bg_color_swatch.pack_propagate(False)
        self.bg_color_entry = ctk.CTkEntry(bg_color_row, width=120, height=36)
        self.bg_color_entry.insert(0, self.bg_color)
        self.bg_color_entry.bind("<Return>", lambda _e: self._apply_color_entry("bg"))
        self.bg_color_entry.bind("<FocusOut>", lambda _e: self._apply_color_entry("bg"))
        self.bg_color_entry.pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            bg_color_row, text="Pick...", width=80, height=36,
            command=lambda: self._pick_color("bg"),
        ).pack(side="left")

        # Corner radius
        ctk.CTkLabel(
            controls, text="Corner Radius (px)",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            controls,
            text="In output video pixels (0 = sharp corners).",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        ).pack(anchor="w", pady=(0, 5))
        radius_row = ctk.CTkFrame(controls, fg_color="transparent")
        radius_row.pack(fill="x", pady=(0, 15))
        self.corner_radius_var = ctk.IntVar(value=DEFAULT_CORNER_RADIUS)
        ctk.CTkSlider(
            radius_row,
            from_=0,
            to=80,
            variable=self.corner_radius_var,
            command=lambda _v: self._update_preview(),
            number_of_steps=80,
        ).pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.radius_label = ctk.CTkLabel(radius_row, text="0 px", width=60, anchor="e")
        self.radius_label.pack(side="right")

        # Position fields (read-only display, kept in sync with drag)
        ctk.CTkLabel(
            controls, text="Position", font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        self.position_label = ctk.CTkLabel(
            controls,
            text="X: 50% Y: 33%",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        )
        self.position_label.pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(
            controls,
            text="Reset to Default",
            height=32,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray35"),
            command=self._reset_defaults,
        ).pack(fill="x", pady=(5, 0))

        # Save button at bottom of content
        self.create_save_button(self.save_settings)

        # Position state vars
        self.pos_x_var = ctk.DoubleVar(value=DEFAULT_POS_X)
        self.pos_y_var = ctk.DoubleVar(value=DEFAULT_POS_Y)

        # Initial preview render
        self.after(100, self._update_preview)

    # ------------------------------------------------------------------
    # Color handling
    # ------------------------------------------------------------------
    def _pick_color(self, target: str):
        current = self.font_color if target == "font" else self.bg_color
        rgb, hex_str = colorchooser.askcolor(color=current, title=f"Pick {target} color")
        if hex_str:
            self._set_color(target, hex_str)

    def _apply_color_entry(self, target: str):
        entry = self.font_color_entry if target == "font" else self.bg_color_entry
        value = entry.get().strip()
        if not value:
            return
        if not value.startswith("#"):
            value = "#" + value
        if not _is_valid_hex(value):
            # Revert entry to current value
            current = self.font_color if target == "font" else self.bg_color
            entry.delete(0, "end")
            entry.insert(0, current)
            return
        self._set_color(target, value.upper())

    def _set_color(self, target: str, hex_color: str):
        if target == "font":
            self.font_color = hex_color
            self.font_color_swatch.configure(bg=hex_color)
            self.font_color_entry.delete(0, "end")
            self.font_color_entry.insert(0, hex_color)
        else:
            self.bg_color = hex_color
            self.bg_color_swatch.configure(bg=hex_color)
            self.bg_color_entry.delete(0, "end")
            self.bg_color_entry.insert(0, hex_color)
        self._update_preview()

    # ------------------------------------------------------------------
    # Preview rendering
    # ------------------------------------------------------------------
    def _update_preview(self):
        # Update labels
        font_pct = self.font_size_var.get() * 100
        self.font_size_label.configure(text=f"{font_pct:.1f}%")
        self.radius_label.configure(text=f"{int(self.corner_radius_var.get())} px")
        self.position_label.configure(
            text=f"X: {int(self.pos_x_var.get() * 100)}%  Y: {int(self.pos_y_var.get() * 100)}%"
        )

        # Clear previous items
        for item in (self.bg_item, self.text_item):
            if item is not None:
                self.canvas.delete(item)
        self.bg_item = None
        self.text_item = None

        # Compute box geometry in canvas pixels.
        # We map output video at 1080x1920 onto canvas 270x480 (scale 0.25).
        scale = self.CANVAS_W / 1080.0

        sample_text = "HOOK PREVIEW"
        # Font size for preview (scaled). Tk needs an int.
        video_font_px = int(self.font_size_var.get() * 1080)
        preview_font_px = max(8, int(video_font_px * scale))

        # Approximate text size on canvas: tk doesn't easily measure without rendering,
        # so use rough heuristic: width ~= 0.55 * font_px * char_count
        text_width = int(0.55 * preview_font_px * len(sample_text))
        text_height = int(preview_font_px * 1.2)
        padding = max(6, int(12 * scale * 4))  # padding in canvas px (visual approximation)

        box_w = text_width + padding * 2
        box_h = text_height + padding * 2

        # Center the box on the position point
        cx = int(self.pos_x_var.get() * self.CANVAS_W)
        cy = int(self.pos_y_var.get() * self.CANVAS_H)
        x1 = cx - box_w // 2
        y1 = cy - box_h // 2
        x2 = x1 + box_w
        y2 = y1 + box_h

        # Corner radius (canvas pixels). Slider value is in output video px.
        radius_video = int(self.corner_radius_var.get())
        radius_canvas = max(0, int(radius_video * scale))
        # Clamp so radius can't exceed half the box
        radius_canvas = min(radius_canvas, box_w // 2, box_h // 2)

        # Draw rounded rectangle (or sharp if radius == 0)
        if radius_canvas <= 0:
            self.bg_item = self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=self.bg_color, outline=""
            )
        else:
            self.bg_item = self._create_rounded_rect(
                x1, y1, x2, y2, radius_canvas, fill=self.bg_color
            )

        # Draw text on top
        # Tk font tuple: (family, size, style). Pull a usable family from display name.
        family = _family_only(self.font_var.get())
        try:
            tk_font = (family, preview_font_px, "bold")
        except Exception:
            tk_font = ("Arial", preview_font_px, "bold")

        self.text_item = self.canvas.create_text(
            cx, cy,
            text=sample_text,
            fill=self.font_color,
            font=tk_font,
            anchor="center",
        )

    def _create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        """Create a rounded rectangle on canvas using a smooth polygon."""
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    # ------------------------------------------------------------------
    # Drag handling
    # ------------------------------------------------------------------
    def _on_canvas_click(self, event):
        if self.bg_item is None:
            return
        bbox = self.canvas.bbox(self.bg_item)
        if not bbox:
            return
        if bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]:
            self.dragging = True
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            self.drag_offset_x = event.x - cx
            self.drag_offset_y = event.y - cy

    def _on_canvas_drag(self, event):
        if not self.dragging:
            return
        new_cx = event.x - self.drag_offset_x
        new_cy = event.y - self.drag_offset_y
        # Clamp to canvas bounds
        new_cx = max(0, min(new_cx, self.CANVAS_W))
        new_cy = max(0, min(new_cy, self.CANVAS_H))
        self.pos_x_var.set(new_cx / self.CANVAS_W)
        self.pos_y_var.set(new_cy / self.CANVAS_H)
        self._update_preview()

    def _on_canvas_release(self, _event):
        self.dragging = False

    # ------------------------------------------------------------------
    # Defaults / Load / Save
    # ------------------------------------------------------------------
    def _reset_defaults(self):
        # Pick the system's default font as a sensible starting point
        default = find_default_font()
        if default:
            self.font_var.set(default[0])
        self.font_size_var.set(DEFAULT_FONT_SIZE)
        self._set_color("font", DEFAULT_FONT_COLOR)
        self._set_color("bg", DEFAULT_BG_COLOR)
        self.corner_radius_var.set(DEFAULT_CORNER_RADIUS)
        self.pos_x_var.set(DEFAULT_POS_X)
        self.pos_y_var.set(DEFAULT_POS_Y)
        self._update_preview()

    def load_config(self):
        if hasattr(self.config, "config"):
            cfg = self.config.config
        else:
            cfg = self.config

        hook = cfg.get("hook_style", {}) or {}

        # Font selection: stored as both name and path; prefer name resolution
        saved_name = hook.get("font_name")
        saved_path = hook.get("font_path")

        names = get_font_names()
        if saved_name and saved_name in names:
            self.font_var.set(saved_name)
        elif saved_path:
            from utils.font_scanner import get_name_for_path
            name = get_name_for_path(saved_path)
            if name:
                self.font_var.set(name)
            else:
                default = find_default_font()
                if default:
                    self.font_var.set(default[0])
        else:
            default = find_default_font()
            if default:
                self.font_var.set(default[0])

        self.font_size_var.set(hook.get("font_size", DEFAULT_FONT_SIZE))
        self._set_color("font", hook.get("font_color", DEFAULT_FONT_COLOR))
        self._set_color("bg", hook.get("bg_color", DEFAULT_BG_COLOR))
        self.corner_radius_var.set(int(hook.get("corner_radius", DEFAULT_CORNER_RADIUS)))
        self.pos_x_var.set(hook.get("position_x", DEFAULT_POS_X))
        self.pos_y_var.set(hook.get("position_y", DEFAULT_POS_Y))

        self.after(120, self._update_preview)

    def save_settings(self):
        if hasattr(self.config, "config"):
            cfg = self.config.config
        else:
            cfg = self.config

        font_name = self.font_var.get()
        font_path = get_path_for_name(font_name) or ""

        cfg["hook_style"] = {
            "font_name": font_name,
            "font_path": font_path,
            "font_size": float(self.font_size_var.get()),
            "font_color": self.font_color,
            "bg_color": self.bg_color,
            "corner_radius": int(self.corner_radius_var.get()),
            "position_x": float(self.pos_x_var.get()),
            "position_y": float(self.pos_y_var.get()),
        }

        if self.on_save_callback:
            self.on_save_callback(cfg)

        from tkinter import messagebox
        messagebox.showinfo("Success", "Hook style settings saved!")
        self.on_back()


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _is_valid_hex(value: str) -> bool:
    if not value.startswith("#"):
        return False
    body = value[1:]
    if len(body) not in (3, 6):
        return False
    try:
        int(body, 16)
        return True
    except ValueError:
        return False


def _family_only(display_name: str) -> str:
    """Strip trailing style words so Tk can match the family name."""
    if not display_name:
        return "Arial"
    suffixes = (" Bold", " Italic", " Regular", " Light", " Medium", " Black",
                " Thin", " Heavy", " Semibold", " ExtraBold", " ExtraLight")
    name = display_name
    changed = True
    while changed:
        changed = False
        for s in suffixes:
            if name.endswith(s):
                name = name[: -len(s)].rstrip()
                changed = True
    return name or display_name
