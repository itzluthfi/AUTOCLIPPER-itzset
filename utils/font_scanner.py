"""
System font scanner.

Scans installed TrueType/OpenType fonts on the host OS and returns a sorted
list of (display_name, absolute_path) tuples. Results are cached on first
access for the lifetime of the process.

Used by the Hook Style settings page so users can pick any font that exists
on their machine.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# Cache (display_name, path) sorted by display name
_FONT_CACHE: Optional[List[Tuple[str, str]]] = None
# Reverse lookup: display_name -> path
_NAME_TO_PATH: Optional[dict] = None
# Forward lookup: path -> display_name
_PATH_TO_NAME: Optional[dict] = None


def _get_font_directories() -> List[Path]:
    """Return list of directories to scan for fonts on the current platform."""
    dirs: List[Path] = []

    if sys.platform == "win32":
        # System fonts
        win_dir = os.environ.get("WINDIR", r"C:\Windows")
        dirs.append(Path(win_dir) / "Fonts")
        # Per-user fonts (Windows 10+)
        local_app = os.environ.get("LOCALAPPDATA")
        if local_app:
            dirs.append(Path(local_app) / "Microsoft" / "Windows" / "Fonts")
    elif sys.platform == "darwin":
        dirs.extend([
            Path("/System/Library/Fonts"),
            Path("/System/Library/Fonts/Supplemental"),
            Path("/Library/Fonts"),
            Path.home() / "Library" / "Fonts",
        ])
    else:
        # Linux / other unix
        dirs.extend([
            Path("/usr/share/fonts"),
            Path("/usr/local/share/fonts"),
            Path.home() / ".fonts",
            Path.home() / ".local" / "share" / "fonts",
        ])

    return [d for d in dirs if d.exists()]


def _read_font_name(path: Path) -> Optional[str]:
    """Try to read the human-readable family/style name from a font file.

    Falls back to the filename stem if Pillow can't open it.
    """
    try:
        # Lazy import so utils/font_scanner can be imported in headless contexts
        from PIL import ImageFont
        font = ImageFont.truetype(str(path), 16)
        family, style = font.getname()
        if family and style and style.lower() != "regular":
            return f"{family} {style}"
        if family:
            return family
    except Exception:
        pass
    # Fallback: use filename stem, prettified
    stem = path.stem
    return stem.replace("_", " ").replace("-", " ").strip() or None


def scan_system_fonts(refresh: bool = False) -> List[Tuple[str, str]]:
    """Scan all installed fonts and return a sorted list of (name, path).

    Results are cached. Pass refresh=True to rebuild the cache.
    Only TTF/OTF/TTC are returned.
    """
    global _FONT_CACHE, _NAME_TO_PATH, _PATH_TO_NAME

    if _FONT_CACHE is not None and not refresh:
        return _FONT_CACHE

    seen_names: dict = {}
    suffixes = (".ttf", ".otf", ".ttc")

    for font_dir in _get_font_directories():
        try:
            for entry in font_dir.rglob("*"):
                if not entry.is_file():
                    continue
                if entry.suffix.lower() not in suffixes:
                    continue
                name = _read_font_name(entry)
                if not name:
                    continue
                # Prefer first occurrence; skip duplicates by display name
                if name not in seen_names:
                    seen_names[name] = str(entry)
        except (PermissionError, OSError):
            # Some directories may be inaccessible; skip silently
            continue

    items = sorted(seen_names.items(), key=lambda kv: kv[0].lower())
    _FONT_CACHE = items
    _NAME_TO_PATH = dict(items)
    _PATH_TO_NAME = {v: k for k, v in items}
    return items


def get_font_names() -> List[str]:
    """Return just the display names, sorted."""
    return [name for name, _ in scan_system_fonts()]


def get_path_for_name(name: str) -> Optional[str]:
    """Resolve a display name to its file path. Returns None if not found."""
    if _NAME_TO_PATH is None:
        scan_system_fonts()
    return _NAME_TO_PATH.get(name) if _NAME_TO_PATH else None


def get_name_for_path(path: str) -> Optional[str]:
    """Resolve a font file path back to its display name."""
    if _PATH_TO_NAME is None:
        scan_system_fonts()
    return _PATH_TO_NAME.get(path) if _PATH_TO_NAME else None


def find_default_font() -> Optional[Tuple[str, str]]:
    """Best-effort default: pick a common bold sans-serif if present."""
    preferred = [
        "Arial Bold",
        "Arial",
        "Segoe UI Bold",
        "Segoe UI",
        "Helvetica Bold",
        "Helvetica",
        "DejaVu Sans Bold",
        "DejaVu Sans",
        "Liberation Sans Bold",
        "Liberation Sans",
    ]
    fonts = scan_system_fonts()
    name_map = {n: p for n, p in fonts}
    for name in preferred:
        if name in name_map:
            return name, name_map[name]
    # Fallback: first font we found, or None
    if fonts:
        return fonts[0]
    return None
