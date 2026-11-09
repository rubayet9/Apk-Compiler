"""
APK Compiler - Reusable UI Components
Senior UI/UX Component Library: Glassmorphism / Obsidian Frost Aesthetic.
Solid translucent surfaces, 1px glass borders, high-contrast typography, NO gradients.
"""

import os
import tkinter as tk
from typing import Callable, List, Optional, Tuple, Union, Any
from PIL import Image

import customtkinter as ctk

from src.ui.theme import COLORS, LIGHT_COLORS, FONTS, get_theme_tuple, get_font


class GlassCard(ctk.CTkFrame):
    """
    Frosted glass container card with subtle border and optional hover elevation.
    NO gradients — uses solid translucent dark glass aesthetic.
    """

    def __init__(
        self,
        master: Any,
        hoverable: bool = False,
        border_width: int = 1,
        corner_radius: int = 14,
        **kwargs
    ):
        self._hoverable = hoverable
        self._default_fg = kwargs.pop("fg_color", get_theme_tuple("bg_card"))
        self._hover_fg = kwargs.pop("hover_color", get_theme_tuple("bg_card_hover"))
        self._default_border = kwargs.pop("border_color", get_theme_tuple("border"))
        self._hover_border = get_theme_tuple("border_light")

        super().__init__(
            master,
            fg_color=self._default_fg,
            corner_radius=corner_radius,
            border_width=border_width,
            border_color=self._default_border,
            **kwargs
        )

        if self._hoverable:
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)

    def _on_enter(self, _e=None):
        self.configure(fg_color=self._hover_fg, border_color=self._hover_border)

    def _on_leave(self, _e=None):
        self.configure(fg_color=self._default_fg, border_color=self._default_border)


class ModernButton(ctk.CTkButton):
    """
    Styled button supporting multiple variants:
    primary, secondary, success, danger, outline, ghost.
    Features subtle hover transitions, rounded corners, and hand cursor.
    """

    def __init__(
        self,
        master: Any,
        variant: str = "primary",
        **kwargs
    ):
        self._variant = variant
        defaults = {
            "corner_radius": 10,
            "font": FONTS["button"],
            "cursor": "hand2",
            "height": 42,
        }
        defaults.update(self._get_variant_styles(variant))
        defaults.update(kwargs)
        super().__init__(master, **defaults)

    @staticmethod
    def _get_variant_styles(variant: str) -> dict:
        if variant == "primary":
            return {
                "fg_color": get_theme_tuple("primary_btn"),
                "hover_color": (LIGHT_COLORS["primary_btn_hover"], COLORS["primary_btn_hover"]),
                "text_color": "#ffffff",
                "border_width": 0,
            }
        elif variant == "secondary":
            return {
                "fg_color": get_theme_tuple("bg_card"),
                "hover_color": (LIGHT_COLORS["bg_card_hover"], COLORS["bg_card_hover"]),
                "text_color": get_theme_tuple("text_primary"),
                "border_width": 1,
                "border_color": get_theme_tuple("border"),
            }
        elif variant == "success":
            return {
                "fg_color": get_theme_tuple("success"),
                "hover_color": (LIGHT_COLORS["success_hover"], COLORS["success_hover"]),
                "text_color": "#ffffff",
                "border_width": 0,
            }
        elif variant == "danger":
            return {
                "fg_color": get_theme_tuple("error"),
                "hover_color": (LIGHT_COLORS["error_hover"], COLORS["error_hover"]),
                "text_color": "#ffffff",
                "border_width": 0,
            }
        elif variant == "outline":
            return {
                "fg_color": "transparent",
                "hover_color": (LIGHT_COLORS["accent_subtle"], COLORS["accent_subtle"]),
                "text_color": get_theme_tuple("accent"),
                "border_width": 1,
                "border_color": get_theme_tuple("accent"),
            }
        elif variant == "ghost":
            return {
                "fg_color": "transparent",
                "hover_color": (LIGHT_COLORS["bg_card_hover"], COLORS["bg_card_hover"]),
                "text_color": get_theme_tuple("text_secondary"),
                "border_width": 0,
            }
        return {}

    def set_variant(self, variant: str):
        self._variant = variant
        styles = self._get_variant_styles(variant)
        super().configure(**styles)

    def configure(self, require_redraw=False, **kwargs):
        if "variant" in kwargs:
            variant = kwargs.pop("variant")
            self._variant = variant
            var_styles = self._get_variant_styles(variant)
            kwargs.update(var_styles)
        return super().configure(require_redraw=require_redraw, **kwargs)


class ModernEntry(ctk.CTkEntry):
    """
    Modern recessed glass input field with styled border, placeholder, and font.
    """

    def __init__(
        self,
        master: Any,
        placeholder_text: str = "",
        **kwargs
    ):
        defaults = {
            "corner_radius": 9,
            "border_width": 1,
            "border_color": get_theme_tuple("border"),
            "fg_color": get_theme_tuple("entry_bg"),
            "text_color": get_theme_tuple("text_primary"),
            "placeholder_text_color": get_theme_tuple("text_muted"),
            "placeholder_text": placeholder_text,
            "font": FONTS["body"],
            "height": 42,
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)


class IconButton(ctk.CTkButton):
    """
    Compact icon/emoji button with subtle glass hover.
    """

    def __init__(
        self,
        master: Any,
        icon_text: str = "📁",
        label_text: str = "",
        variant: str = "secondary",
        width: int = 42,
        height: int = 42,
        command: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        display_text = f"{icon_text}  {label_text}".strip() if label_text else icon_text
        defaults = {
            "text": display_text,
            "width": width if not label_text else max(width, 100),
            "height": height,
            "corner_radius": 9,
            "font": FONTS["small_bold"] if label_text else ("Segoe UI", 16),
            "command": command,
            "cursor": "hand2",
        }
        styles = ModernButton._get_variant_styles(variant)
        defaults.update(styles)
        defaults.update(kwargs)
        super().__init__(master, **defaults)


class StepIndicator(ctk.CTkFrame):
    """
    Modern Wizard Step Timeline (English Default).
    Features glowing active step pill, completed check badges, and connecting hairline tracks.
    """

    DEFAULT_STEPS = [
        ("1", "Source Package"),
        ("2", "Configuration"),
        ("3", "Compilation"),
        ("4", "Release Ready"),
    ]

    def __init__(
        self,
        master: Any,
        current_step: int = 1,
        steps: Optional[List[Tuple[str, str]]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=get_theme_tuple("bg_secondary"),
            corner_radius=12,
            border_width=1,
            border_color=get_theme_tuple("border"),
            height=66,
            **kwargs
        )
        self.step_defs = steps or self.DEFAULT_STEPS
        self.current_step = current_step
        self._build_ui()

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(expand=True, fill="x", padx=24, pady=10)

        total_steps = len(self.step_defs)

        for idx, (num_str, label_text) in enumerate(self.step_defs, start=1):
            col_idx = (idx - 1) * 2
            container.grid_columnconfigure(col_idx, weight=0)

            is_completed = idx < self.current_step
            is_active = idx == self.current_step

            # Step item container
            step_box = ctk.CTkFrame(container, fg_color="transparent")
            step_box.grid(row=0, column=col_idx, sticky="w")

            if is_completed:
                badge_bg = COLORS["success"]
                badge_fg = "#ffffff"
                badge_text = "✓"
                text_col = COLORS["success"]
                font_weight = FONTS["small_bold"]
            elif is_active:
                badge_bg = COLORS["accent"]
                badge_fg = "#090d16"
                badge_text = num_str
                text_col = get_theme_tuple("accent")
                font_weight = FONTS["body_bold"]
            else:
                badge_bg = (LIGHT_COLORS["border"], COLORS["border"])
                badge_fg = (LIGHT_COLORS["text_muted"], COLORS["text_muted"])
                badge_text = num_str
                text_col = get_theme_tuple("text_muted")
                font_weight = FONTS["small"]

            # Step pill row
            pill_row = ctk.CTkFrame(step_box, fg_color="transparent")
            pill_row.pack(side="left")

            badge = ctk.CTkLabel(
                pill_row,
                text=badge_text,
                font=FONTS["small_bold"],
                width=26,
                height=26,
                corner_radius=13,
                fg_color=badge_bg,
                text_color=badge_fg,
            )
            badge.pack(side="left", padx=(0, 8))

            title = ctk.CTkLabel(
                pill_row,
                text=label_text,
                font=font_weight,
                text_color=text_col,
            )
            title.pack(side="left")

            # Connector line between steps
            if idx < total_steps:
                line_col = col_idx + 1
                container.grid_columnconfigure(line_col, weight=1)
                line_color = COLORS["success"] if idx < self.current_step else get_theme_tuple("border")
                line = ctk.CTkFrame(container, fg_color=line_color, height=2)
                line.grid(row=0, column=line_col, sticky="ew", padx=16)

    def set_step(self, step: int):
        """Update active step (1-indexed)."""
        self.current_step = max(1, min(len(self.step_defs), step))
        self._build_ui()

    def update_steps(self, steps: List[Tuple[str, str]]):
        """Update step definitions dynamically (e.g. for language changes)."""
        self.step_defs = steps
        self._build_ui()


class FileDropZone(ctk.CTkFrame):
    """
    Modern glass dropzone card for uploading Web App folders or ZIP archives.
    Solid translucent dark glass, 1px border, hover glow, English guidance.
    """

    def __init__(
        self,
        master: Any,
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=get_theme_tuple("bg_card"),
            corner_radius=14,
            border_width=1,
            border_color=get_theme_tuple("border"),
            **kwargs
        )
        self.on_select = on_select
        self.selected_path: Optional[str] = None

        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        self.inner_frame = ctk.CTkFrame(self, fg_color="transparent", cursor="hand2")
        self.inner_frame.pack(expand=True, fill="both", padx=28, pady=26)

        self.icon_label = ctk.CTkLabel(
            self.inner_frame,
            text="📦",
            font=("Segoe UI", 42),
            cursor="hand2",
        )
        self.icon_label.pack(pady=(4, 6))

        self.main_text_label = ctk.CTkLabel(
            self.inner_frame,
            text="Choose Source Package or Project Directory",
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
            cursor="hand2",
        )
        self.main_text_label.pack(pady=2)

        self.sub_text_label = ctk.CTkLabel(
            self.inner_frame,
            text="Supports Google AI Studio exports (.zip), native Android folders, or Web Apps (with index.html)",
            font=FONTS["subtitle"],
            text_color=get_theme_tuple("text_secondary"),
            cursor="hand2",
        )
        self.sub_text_label.pack(pady=2)

        # Selected path badge
        self.path_badge_frame = ctk.CTkFrame(
            self.inner_frame,
            fg_color=get_theme_tuple("entry_bg"),
            corner_radius=8,
            border_width=1,
            border_color=get_theme_tuple("accent"),
        )
        self.path_label = ctk.CTkLabel(
            self.path_badge_frame,
            text="",
            font=FONTS["code_bold"],
            text_color=get_theme_tuple("accent"),
        )
        self.path_label.pack(side="left", padx=14, pady=6)

    def _bind_events(self):
        for widget in [self, self.inner_frame, self.icon_label, self.main_text_label, self.sub_text_label]:
            widget.bind("<Button-1>", self._on_clicked)
            widget.bind("<Enter>", self._on_hover_enter)
            widget.bind("<Leave>", self._on_hover_leave)

    def _on_hover_enter(self, _e=None):
        self.configure(border_color=get_theme_tuple("accent"), fg_color=get_theme_tuple("bg_card_hover"))

    def _on_hover_leave(self, _e=None):
        if not self.selected_path:
            self.configure(border_color=get_theme_tuple("border"), fg_color=get_theme_tuple("bg_card"))
        else:
            self.configure(fg_color=get_theme_tuple("bg_card"))

    def _on_clicked(self, _e=None):
        if self.on_select:
            self.on_select(self.selected_path or "")

    def set_file_path(self, path: str, is_valid: bool = True):
        """Update display with selected path and validation state."""
        self.selected_path = path
        if path:
            short_path = path if len(path) < 65 else f"...{path[-60:]}"
            is_zip = path.lower().endswith(".zip")
            icon = "📦" if is_zip else "📁"
            self.icon_label.configure(text=icon)
            self.main_text_label.configure(
                text=f"{'ZIP Archive' if is_zip else 'Project Directory'} Selected"
            )
            self.sub_text_label.configure(text="Click to select another file or folder")
            self.path_label.configure(text=f"📍 {short_path}")
            self.path_badge_frame.pack(pady=(12, 0))

            if is_valid:
                self.configure(border_color=COLORS["success"])
            else:
                self.configure(border_color=COLORS["error"])
        else:
            self.path_badge_frame.pack_forget()
            self.icon_label.configure(text="📦")
            self.main_text_label.configure(text="Choose Source Package or Project Directory")
            self.sub_text_label.configure(
                text="Supports Google AI Studio exports (.zip), native Android folders, or Web Apps (with index.html)"
            )
            self.configure(border_color=get_theme_tuple("border"))

    def update_text(self, title: str, subtitle: str):
        """Update placeholder text based on language if no file is selected."""
        if not self.selected_path:
            self.main_text_label.configure(text=title)
            self.sub_text_label.configure(text=subtitle)


class ProgressCard(ctk.CTkFrame):
    """
    Glass status HUD card with real-time percentage badge and detailed status text.
    """

    def __init__(
        self,
        master: Any,
        title: str = "Overall Compilation Progress",
        initial_status: str = "Ready to build...",
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=get_theme_tuple("bg_card"),
            corner_radius=14,
            border_width=1,
            border_color=get_theme_tuple("border"),
            **kwargs
        )
        self.title_text = title
        self.progress_val = 0.0
        self._build_ui(title, initial_status)

    def _build_ui(self, title: str, initial_status: str):
        self.pack_propagate(False)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 6))

        self.title_label = ctk.CTkLabel(
            header,
            text=title,
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
        )
        self.title_label.pack(side="left")

        self.percent_label = ctk.CTkLabel(
            header,
            text="0%",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("accent"),
        )
        self.percent_label.pack(side="right")

        self.progress_bar = ctk.CTkProgressBar(
            self,
            orientation="horizontal",
            mode="determinate",
            height=10,
            corner_radius=5,
            fg_color=get_theme_tuple("progress_bg"),
            progress_color=get_theme_tuple("accent"),
        )
        self.progress_bar.pack(fill="x", padx=18, pady=(4, 8))
        self.progress_bar.set(0.0)

        status_box = ctk.CTkFrame(self, fg_color="transparent")
        status_box.pack(fill="x", padx=18, pady=(0, 12))

        self.status_icon = ctk.CTkLabel(
            status_box,
            text="⚡",
            font=FONTS["body"],
        )
        self.status_icon.pack(side="left", padx=(0, 6))

        self.status_label = ctk.CTkLabel(
            status_box,
            text=initial_status,
            font=FONTS["body"],
            text_color=get_theme_tuple("text_secondary"),
        )
        self.status_label.pack(side="left")

    def set_progress(self, percent: float, status_text: Optional[str] = None):
        """Update progress bar (percent 0.0 to 1.0 or 0 to 100)."""
        if percent > 1.0:
            percent = percent / 100.0
        percent = max(0.0, min(1.0, percent))
        self.progress_val = percent

        self.progress_bar.set(percent)
        display_pct = int(round(percent * 100))
        self.percent_label.configure(text=f"{display_pct}%")

        if percent >= 1.0:
            self.progress_bar.configure(progress_color=COLORS["success"])
            self.percent_label.configure(text_color=COLORS["success"])
            self.status_icon.configure(text="✅")

        if status_text:
            self.status_label.configure(text=status_text)

    def set_error(self, message: str):
        """Set error state styling."""
        self.progress_bar.configure(progress_color=COLORS["error"])
        self.percent_label.configure(text="Failed", text_color=COLORS["error"])
        self.status_icon.configure(text="❌")
        self.status_label.configure(text=message, text_color=COLORS["error"])


class InfoCard(ctk.CTkFrame):
    """
    Glass card displaying a key-value metric with icon, title, value, and optional badge.
    """

    def __init__(
        self,
        master: Any,
        icon: str = "⚡",
        title: str = "",
        value: str = "",
        subtitle: Optional[str] = None,
        badge: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=get_theme_tuple("bg_card"),
            corner_radius=12,
            border_width=1,
            border_color=get_theme_tuple("border"),
            **kwargs
        )
        self._build_ui(icon, title, value, subtitle, badge)

    def _build_ui(
        self,
        icon: str,
        title: str,
        value: str,
        subtitle: Optional[str],
        badge: Optional[str],
    ):
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=16, pady=14)

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 6))

        icon_lbl = ctk.CTkLabel(top_row, text=icon, font=("Segoe UI", 18))
        icon_lbl.pack(side="left", padx=(0, 8))

        self.title_lbl = ctk.CTkLabel(
            top_row,
            text=title,
            font=FONTS["subheading"],
            text_color=get_theme_tuple("text_secondary"),
        )
        self.title_lbl.pack(side="left")

        if badge:
            badge_lbl = ctk.CTkLabel(
                top_row,
                text=badge,
                font=FONTS["small_bold"],
                fg_color=get_theme_tuple("accent_subtle"),
                text_color=get_theme_tuple("accent"),
                corner_radius=6,
                padx=8,
                pady=2,
            )
            badge_lbl.pack(side="right")

        self.value_lbl = ctk.CTkLabel(
            inner,
            text=value,
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.value_lbl.pack(fill="x")

        if subtitle:
            self.sub_lbl = ctk.CTkLabel(
                inner,
                text=subtitle,
                font=FONTS["small"],
                text_color=get_theme_tuple("text_muted"),
                anchor="w",
            )
            self.sub_lbl.pack(fill="x", pady=(2, 0))
        else:
            self.sub_lbl = None

    def update_value(self, value: str, subtitle: Optional[str] = None):
        """Update value and optional subtitle dynamically."""
        self.value_lbl.configure(text=value)
        if subtitle and self.sub_lbl:
            self.sub_lbl.configure(text=subtitle)


class SectionHeader(ctk.CTkFrame):
    """
    Styled section header with title, optional subtitle, and hairline divider.
    """

    def __init__(
        self,
        master: Any,
        title: str,
        subtitle: Optional[str] = None,
        action_widget: Optional[ctk.CTkBaseClass] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui(title, subtitle, action_widget)

    def _build_ui(self, title: str, subtitle: Optional[str], action_widget: Optional[ctk.CTkBaseClass]):
        top_row = ctk.CTkFrame(self, fg_color="transparent")
        top_row.pack(fill="x")

        title_lbl = ctk.CTkLabel(
            top_row,
            text=title,
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
        )
        title_lbl.pack(side="left")

        if action_widget:
            action_widget.pack(side="right")

        if subtitle:
            sub_lbl = ctk.CTkLabel(
                self,
                text=subtitle,
                font=FONTS["subtitle"],
                text_color=get_theme_tuple("text_secondary"),
                anchor="w",
            )
            sub_lbl.pack(fill="x", pady=(2, 6))

        divider = ctk.CTkFrame(
            self,
            fg_color=get_theme_tuple("border"),
            height=1,
        )
        divider.pack(fill="x", pady=(6, 12))
