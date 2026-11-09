"""
APK Compiler - Theme & Design System
Senior UI/UX Design System: Glassmorphism / Obsidian Frost Aesthetic.
Pure solid layered surfaces, crisp 1px glass borders, high-contrast typography, NO gradients.
"""

import sys
import tkinter as tk
import tkinter.font as tkfont
from typing import Dict, Tuple, Any

# -------------------------------------------------------------------------
# Dynamic Font Selection (Prefers Inter / Segoe UI / Roboto)
# -------------------------------------------------------------------------
def _resolve_best_font() -> Tuple[str, str]:
    """Detect the best installed modern sans font and monospace font."""
    preferred_sans = [
        "Segoe UI Variable Text",
        "Segoe UI Variable Display",
        "Inter",
        "Roboto",
        "Segoe UI",
        "SF Pro Display",
        "Helvetica Neue",
        "Arial",
    ]
    preferred_code = [
        "Cascadia Code",
        "JetBrains Mono",
        "Consolas",
        "Fira Code",
        "Courier New",
    ]
    try:
        root = tk._default_root
        if not root:
            temp = tk.Tk()
            temp.withdraw()
            fams = tkfont.families()
            temp.destroy()
        else:
            fams = tkfont.families()
    except Exception:
        fams = ()

    sans = "Segoe UI"
    for f in preferred_sans:
        if f in fams:
            sans = f
            break

    code = "Consolas"
    for f in preferred_code:
        if f in fams:
            code = f
            break

    return sans, code

FONT_FAMILY, FONT_FAMILY_CODE = _resolve_best_font()
FONT_FAMILY_FALLBACK = "Arial"

# -------------------------------------------------------------------------
# Typographic Scale
# -------------------------------------------------------------------------
FONTS: Dict[str, Tuple[str, int, str]] = {
    "display": (FONT_FAMILY, 26, "bold"),
    "hero": (FONT_FAMILY, 22, "bold"),
    "title": (FONT_FAMILY, 18, "bold"),
    "heading": (FONT_FAMILY, 15, "bold"),
    "subheading": (FONT_FAMILY, 13, "bold"),
    "body": (FONT_FAMILY, 12, "normal"),
    "body_bold": (FONT_FAMILY, 12, "bold"),
    "subtitle": (FONT_FAMILY, 12, "normal"),
    "small": (FONT_FAMILY, 10, "normal"),
    "small_bold": (FONT_FAMILY, 10, "bold"),
    "caption": (FONT_FAMILY, 9, "normal"),
    "button": (FONT_FAMILY, 13, "bold"),
    "button_lg": (FONT_FAMILY, 14, "bold"),
    "code": (FONT_FAMILY_CODE, 11, "normal"),
    "code_bold": (FONT_FAMILY_CODE, 11, "bold"),
}

# -------------------------------------------------------------------------
# Obsidian Glass Dark Theme Palette (No Gradients, Solid Translucent Glass)
# -------------------------------------------------------------------------
COLORS: Dict[str, str] = {
    "bg_primary": "#090d16",       # Deep obsidian midnight
    "bg_secondary": "#0e1524",     # Translucent glass panel / sidebar
    "bg_card": "#131d30",          # Frosted glass tile surface
    "bg_card_hover": "#1a273f",    # Hover glass tile elevation
    "bg_card_active": "#20304e",   # Active state
    "bg_well": "#0a0f1a",          # Inset recessed glass well
    "accent": "#38bdf8",           # Electric Sky Blue / Cyan (Vibrant & crisp)
    "accent_hover": "#0ea5e9",     # Deeper sky hover
    "accent_subtle": "#0c253b",    # Translucent glass glow tint
    "primary_btn": "#2563eb",      # High-contrast action blue
    "primary_btn_hover": "#1d4ed8",# Primary button hover
    "success": "#10b981",          # Emerald Green
    "success_hover": "#059669",    # Emerald dark hover
    "success_subtle": "#062b21",   # Emerald glass glow
    "warning": "#f59e0b",          # Amber
    "warning_hover": "#d97706",    # Deep amber hover
    "warning_subtle": "#2d1d05",   # Amber glass glow
    "error": "#ef4444",            # Modern rose red
    "error_hover": "#dc2626",      # Crimson hover
    "error_subtle": "#311014",     # Error glass glow
    "text_primary": "#f8fafc",     # Crisp slate-50 white
    "text_secondary": "#94a3b8",   # Slate-400
    "text_muted": "#64748b",       # Slate-500
    "border": "#212e45",           # Crisp 1px frosted glass hairline
    "border_light": "#2e4162",     # Slightly elevated glass border
    "border_active": "#38bdf8",    # Electric glow border
    "entry_bg": "#0c1322",         # Recessed dark glass input field
    "terminal_bg": "#060910",      # Deep charcoal console
    "progress_bg": "#162033",      # Progress bar track
}

# -------------------------------------------------------------------------
# Frost Pearl Light Theme Palette
# -------------------------------------------------------------------------
LIGHT_COLORS: Dict[str, str] = {
    "bg_primary": "#f8fafc",       # Slate 50
    "bg_secondary": "#ffffff",     # Crisp white
    "bg_card": "#ffffff",          # Pure white glass card
    "bg_card_hover": "#f1f5f9",    # Slate 100 hover
    "bg_card_active": "#e2e8f0",   # Slate 200
    "bg_well": "#f1f5f9",          # Inset well
    "accent": "#0284c7",           # Sky 600
    "accent_hover": "#0369a1",     # Sky 700
    "accent_subtle": "#e0f2fe",    # Sky 100
    "primary_btn": "#2563eb",      # Blue 600
    "primary_btn_hover": "#1d4ed8",# Blue 700
    "success": "#059669",          # Emerald 600
    "success_hover": "#047857",    # Emerald 700
    "success_subtle": "#d1fae5",   # Emerald 100
    "warning": "#d97706",          # Amber 600
    "warning_hover": "#b45309",    # Amber 700
    "warning_subtle": "#fef3c7",   # Amber 100
    "error": "#dc2626",            # Red 600
    "error_hover": "#b91c1c",      # Red 700
    "error_subtle": "#fee2e2",     # Red 100
    "text_primary": "#0f172a",     # Slate 900
    "text_secondary": "#475569",   # Slate 600
    "text_muted": "#94a3b8",       # Slate 400
    "border": "#e2e8f0",           # Slate 200 border
    "border_light": "#cbd5e1",     # Slate 300
    "border_active": "#0284c7",    # Focus border
    "entry_bg": "#ffffff",         # White input field
    "terminal_bg": "#0f172a",      # Stays dark for high code contrast
    "progress_bg": "#e2e8f0",      # Progress track
}

def get_colors(dark_mode: bool = True) -> Dict[str, str]:
    """Return color palette dictionary for the specified mode."""
    return COLORS if dark_mode else LIGHT_COLORS

def get_theme_tuple(key: str) -> Tuple[str, str]:
    """Return a (light_color, dark_color) tuple compatible with CustomTkinter."""
    light_val = LIGHT_COLORS.get(key, "#ffffff")
    dark_val = COLORS.get(key, "#090d16")
    return (light_val, dark_val)

def get_font(font_name: str) -> Tuple[str, int, str]:
    """Return the font tuple by key with fallback to body."""
    return FONTS.get(font_name, (FONT_FAMILY, 12, "normal"))
