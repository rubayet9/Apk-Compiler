"""
APK Compiler - Welcome Page
Modern Glassmorphism Landing Dashboard with Gemini branding.
NO gradients, obsidian frosted glass aesthetic, bilingual (EN & BN).
"""

import os
import subprocess
import tkinter as tk
from typing import Optional, Any
from PIL import Image

import customtkinter as ctk

from src.ui.theme import COLORS, LIGHT_COLORS, FONTS, get_theme_tuple
from src.ui.components import ModernButton, GlassCard, SectionHeader
from src.utils.i18n import i18n


class WelcomePage(ctk.CTkFrame):
    """
    Welcome / Home Dashboard for APK Compiler.
    Displays prominent Gemini logo, quick actions, features grid, and recent builds.
    """

    def __init__(self, master: Any, app_reference: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_reference
        self._build_ui()

    def _build_ui(self):
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
        )
        self.scroll_container.pack(fill="both", expand=True, padx=28, pady=20)

        # 1. Hero Glass Card with Gemini Logo
        self._build_hero_section()

        # 2. Features Grid (3 Columns)
        self._build_features_section()

        # 3. Recent Builds Section
        self._build_recent_builds_section()

    def _build_hero_section(self):
        hero_card = GlassCard(
            self.scroll_container,
            corner_radius=16,
        )
        hero_card.pack(fill="x", pady=(0, 24))

        content = ctk.CTkFrame(hero_card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=32, pady=28)

        # Top row: Left text column, Right logo avatar
        top_hero_row = ctk.CTkFrame(content, fg_color="transparent")
        top_hero_row.pack(fill="x")

        left_col = ctk.CTkFrame(top_hero_row, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True)

        # Badge
        self.hero_badge = ctk.CTkLabel(
            left_col,
            text=i18n.t("dash_badge"),
            font=FONTS["caption"],
            fg_color=get_theme_tuple("accent_subtle"),
            text_color=get_theme_tuple("accent"),
            corner_radius=6,
            padx=10,
            pady=3,
        )
        self.hero_badge.pack(anchor="w", pady=(0, 10))

        # Title
        self.hero_title = ctk.CTkLabel(
            left_col,
            text=i18n.t("dash_hero_title"),
            font=FONTS["display"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.hero_title.pack(anchor="w")

        # Subtitle
        self.hero_subtitle = ctk.CTkLabel(
            left_col,
            text=i18n.t("dash_hero_subtitle"),
            font=FONTS["heading"],
            text_color=get_theme_tuple("accent"),
            anchor="w",
        )
        self.hero_subtitle.pack(anchor="w", pady=(4, 8))

        # Description
        self.hero_desc = ctk.CTkLabel(
            left_col,
            text=i18n.t("dash_hero_desc"),
            font=FONTS["body"],
            text_color=get_theme_tuple("text_secondary"),
            justify="left",
            anchor="w",
        )
        self.hero_desc.pack(anchor="w", pady=(0, 20))

        # Right column: Gemini Logo inside a sleek frosted glass container
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "logo_icon.png")
        if os.path.exists(logo_path):
            try:
                pil_logo = Image.open(logo_path)
                hero_logo_img = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(60, 60))
                hero_badge_card = GlassCard(top_hero_row, width=80, height=80, corner_radius=16)
                hero_badge_card.pack_propagate(False)
                hero_badge_card.pack(side="right", padx=(20, 0), anchor="center")
                self.hero_logo_label = ctk.CTkLabel(
                    hero_badge_card,
                    image=hero_logo_img,
                    text="",
                    width=60,
                    height=60,
                )
                self.hero_logo_label.place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                pass

        # Action Buttons Row
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(anchor="w")

        self.start_btn = ModernButton(
            btn_row,
            text=i18n.t("btn_start_new_build"),
            variant="primary",
            font=FONTS["button_lg"],
            height=44,
            width=210,
            command=self._on_start_click,
        )
        self.start_btn.pack(side="left", padx=(0, 14))

        self.settings_btn = ModernButton(
            btn_row,
            text=i18n.t("btn_env_settings"),
            variant="secondary",
            font=FONTS["button"],
            height=44,
            width=190,
            command=self._on_settings_click,
        )
        self.settings_btn.pack(side="left")

    def _build_features_section(self):
        self.features_header = SectionHeader(
            self.scroll_container,
            title=i18n.t("features_title"),
            subtitle=i18n.t("features_subtitle"),
        )
        self.features_header.pack(fill="x", pady=(0, 14))

        self.grid_frame = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.grid_frame.pack(fill="x", pady=(0, 26))
        self.grid_frame.columnconfigure((0, 1, 2), weight=1, uniform="features")

        features_data = [
            (
                "🚀",
                "feat_zero_title",
                "feat_zero_desc",
            ),
            (
                "🤖",
                "feat_support_title",
                "feat_support_desc",
            ),
            (
                "🔒",
                "feat_sign_title",
                "feat_sign_desc",
            ),
        ]

        self.feature_cards = []
        for idx, (icon, title_key, desc_key) in enumerate(features_data):
            card = GlassCard(
                self.grid_frame,
                corner_radius=14,
                hoverable=True,
            )
            card.grid(row=0, column=idx, padx=6 if idx == 1 else (0 if idx == 0 else 6), sticky="nsew")

            card_inner = ctk.CTkFrame(card, fg_color="transparent")
            card_inner.pack(fill="both", expand=True, padx=20, pady=20)

            icon_box = ctk.CTkLabel(
                card_inner,
                text=icon,
                font=("Segoe UI", 24),
                width=44,
                height=44,
                corner_radius=10,
                fg_color=get_theme_tuple("accent_subtle"),
            )
            icon_box.pack(anchor="w", pady=(0, 12))

            card_title = ctk.CTkLabel(
                card_inner,
                text=i18n.t(title_key),
                font=FONTS["subheading"],
                text_color=get_theme_tuple("text_primary"),
                anchor="w",
            )
            card_title.pack(anchor="w", pady=(0, 6))

            card_desc = ctk.CTkLabel(
                card_inner,
                text=i18n.t(desc_key),
                font=FONTS["small"],
                text_color=get_theme_tuple("text_secondary"),
                justify="left",
                wraplength=230,
                anchor="w",
            )
            card_desc.pack(anchor="w")
            self.feature_cards.append((card_title, card_desc, title_key, desc_key))

    def _build_recent_builds_section(self):
        self.history_header = SectionHeader(
            self.scroll_container,
            title=i18n.t("recent_builds_title"),
            subtitle=i18n.t("recent_builds_desc"),
        )
        self.history_header.pack(fill="x", pady=(0, 14))

        self.history_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.history_container.pack(fill="x", pady=(0, 20))

        self.refresh_history()

    def update_language(self, _lang: str = "en"):
        """Update all text dynamically when language changes."""
        self.hero_badge.configure(text=i18n.t("dash_badge"))
        self.hero_title.configure(text=i18n.t("dash_hero_title"))
        self.hero_subtitle.configure(text=i18n.t("dash_hero_subtitle"))
        self.hero_desc.configure(text=i18n.t("dash_hero_desc"))
        self.start_btn.configure(text=i18n.t("btn_start_new_build"))
        self.settings_btn.configure(text=i18n.t("btn_env_settings"))

        for t_lbl, d_lbl, t_key, d_key in self.feature_cards:
            t_lbl.configure(text=i18n.t(t_key))
            d_lbl.configure(text=i18n.t(d_key))

        self.refresh_history()

    def refresh_history(self):
        """Reload and render recent builds from app controller."""
        for widget in self.history_container.winfo_children():
            widget.destroy()

        history = []
        if self.app and hasattr(self.app, "get_build_history"):
            history = self.app.get_build_history()

        if not history:
            empty_box = GlassCard(
                self.history_container,
                corner_radius=12,
            )
            empty_box.pack(fill="x", pady=4)

            inner = ctk.CTkFrame(empty_box, fg_color="transparent")
            inner.pack(padx=24, pady=28)

            ctk.CTkLabel(inner, text="📭", font=("Segoe UI", 32)).pack(pady=(0, 6))
            ctk.CTkLabel(
                inner,
                text=i18n.t("no_recent_builds"),
                font=FONTS["body_bold"],
                text_color=get_theme_tuple("text_secondary"),
            ).pack()
            return

        for item in history[:5]:
            app_name = item.get("app_name", "Android App")
            package_name = item.get("package_name", "com.app")
            version = item.get("version", "1.0.0")
            apk_path = item.get("apk_path", "")
            file_size_bytes = item.get("file_size", 0)

            if file_size_bytes > 1024 * 1024:
                size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"
            elif file_size_bytes > 1024:
                size_str = f"{file_size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{file_size_bytes} B"

            card = GlassCard(
                self.history_container,
                corner_radius=11,
                hoverable=True,
            )
            card.pack(fill="x", pady=5)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=18, pady=14)

            icon_lbl = ctk.CTkLabel(row, text="📱", font=("Segoe UI", 22))
            icon_lbl.pack(side="left", padx=(0, 14))

            info_block = ctk.CTkFrame(row, fg_color="transparent")
            info_block.pack(side="left", fill="both", expand=True)

            title_row = ctk.CTkFrame(info_block, fg_color="transparent")
            title_row.pack(anchor="w")

            name_lbl = ctk.CTkLabel(
                title_row,
                text=app_name,
                font=FONTS["subheading"],
                text_color=get_theme_tuple("text_primary"),
            )
            name_lbl.pack(side="left", padx=(0, 8))

            ver_badge = ctk.CTkLabel(
                title_row,
                text=f"v{version}",
                font=FONTS["small_bold"],
                fg_color=get_theme_tuple("accent_subtle"),
                text_color=get_theme_tuple("accent"),
                corner_radius=5,
                padx=6,
                pady=1,
            )
            ver_badge.pack(side="left")

            sub_text = f"{package_name}  •  {size_str}"
            s_lbl = ctk.CTkLabel(
                info_block,
                text=sub_text,
                font=FONTS["small"],
                text_color=get_theme_tuple("text_secondary"),
                anchor="w",
            )
            s_lbl.pack(anchor="w", pady=(2, 0))

            if apk_path and os.path.exists(apk_path):
                open_btn = ModernButton(
                    row,
                    text=i18n.t("btn_locate_file"),
                    variant="ghost",
                    width=100,
                    height=32,
                    font=FONTS["small_bold"],
                    command=lambda p=apk_path: self._locate_file(p),
                )
                open_btn.pack(side="right")

    def _locate_file(self, file_path: str):
        try:
            if os.name == "nt":
                subprocess.run(["explorer", f"/select,{os.path.normpath(file_path)}"])
            else:
                subprocess.run(["xdg-open", os.path.dirname(file_path)])
        except Exception as e:
            print(f"Error opening history file: {e}")

    def _on_start_click(self):
        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            self.app.main_window.show_page("upload")

    def _on_settings_click(self):
        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            self.app.main_window.show_page("settings")
