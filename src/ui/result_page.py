"""
APK Compiler - Build Result Page
Celebrates completed APK build, presents file metrics, share actions, ADB install instructions.
Full English defaults, obsidian frosted glass aesthetic, NO gradients, senior UI/UX standards.
"""

import os
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from typing import Optional, Dict, Any
from PIL import Image

import customtkinter as ctk

from src.ui.theme import COLORS, LIGHT_COLORS, FONTS, get_theme_tuple
from src.ui.components import ModernButton, StepIndicator, InfoCard, SectionHeader, GlassCard
from src.utils.i18n import i18n


class ResultPage(ctk.CTkFrame):
    """
    Step 4: Build Result & Distribution Artifact Page (Bilingual EN/BN).
    """

    def _get_step_defs(self) -> list:
        return [
            ("1", i18n.t("step_1")),
            ("2", i18n.t("step_2")),
            ("3", i18n.t("step_3")),
            ("4", i18n.t("step_4")),
        ]

    def __init__(self, master: Any, app_reference: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_reference
        self.apk_path: str = ""
        self.build_config: Dict[str, Any] = {}
        self.qr_ctk_image = None

        self._build_ui()

    def _build_ui(self):
        # Step indicator at top (Step 4 - Completed)
        self.step_indicator = StepIndicator(self, current_step=4, steps=self._get_step_defs())
        self.step_indicator.pack(fill="x", padx=28, pady=(16, 10))

        # Main scrollable body
        self.scroll_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_body.pack(fill="both", expand=True, padx=28, pady=8)

        # 1. Hero Celebration Banner
        self._build_success_hero()

        # 2. APK Details & Quick Actions
        self._build_file_details_card()

        # 3. ADB / Device Installation Card
        self._build_install_instructions_card()

        # 4. Build Configuration Summary
        self._build_summary_card()

        # Bottom Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color=get_theme_tuple("bg_secondary"), height=64)
        nav_bar.pack(fill="x", side="bottom")

        nav_inner = ctk.CTkFrame(nav_bar, fg_color="transparent")
        nav_inner.pack(fill="both", expand=True, padx=28, pady=12)

        self.btn_home = ModernButton(
            nav_inner,
            text=i18n.t("btn_back_dash"),
            variant="secondary",
            width=140,
            command=self._on_home_click,
        )
        self.btn_home.pack(side="left")

        self.btn_new_build = ModernButton(
            nav_inner,
            text=i18n.t("btn_build_another"),
            variant="primary",
            width=210,
            command=self._on_new_build_click,
        )
        self.btn_new_build.pack(side="right")

    def update_language(self, _lang: str = "en"):
        self.step_indicator.update_steps(self._get_step_defs())
        self.btn_home.configure(text=i18n.t("btn_back_dash"))
        self.btn_new_build.configure(text=i18n.t("btn_build_another"))
        if hasattr(self, "hero_title_lbl"):
            self.hero_title_lbl.configure(text=i18n.t("result_title"))
            self.hero_sub_lbl.configure(text=i18n.t("result_subtitle"))
        if hasattr(self, "btn_open_folder"):
            self.btn_open_folder.configure(text=i18n.t("btn_open_folder"))

    def _build_success_hero(self):
        hero = GlassCard(
            self.scroll_body,
            corner_radius=16,
            border_color=COLORS["success"],
        )
        hero.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(hero, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=28, pady=26)

        icon_lbl = ctk.CTkLabel(
            inner,
            text="🎉",
            font=("Segoe UI", 44),
        )
        icon_lbl.pack(pady=(0, 4))

        self.hero_title_lbl = ctk.CTkLabel(
            inner,
            text=i18n.t("result_title"),
            font=FONTS["hero"],
            text_color=COLORS["success"],
        )
        self.hero_title_lbl.pack(pady=(0, 4))

        self.hero_sub_lbl = ctk.CTkLabel(
            inner,
            text=i18n.t("result_subtitle"),
            font=FONTS["subtitle"],
            text_color=get_theme_tuple("text_secondary"),
        )
        self.hero_sub_lbl.pack()

    def _build_file_details_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            inner,
            title="Artifact Metrics & Quick Actions",
            subtitle="Binary specifications and file explorer access.",
        ).pack(fill="x", pady=(0, 14))

        # 3 metric cards in a row
        metrics_row = ctk.CTkFrame(inner, fg_color="transparent")
        metrics_row.pack(fill="x", pady=(0, 16))
        metrics_row.columnconfigure((0, 1, 2), weight=1, uniform="metrics")

        # Metric 1: File name
        self.card_name = InfoCard(
            metrics_row,
            icon="📦",
            title="Artifact Name",
            value="app-release.apk",
            subtitle="Android Application Package",
        )
        self.card_name.grid(row=0, column=0, padx=(0, 6), sticky="nsew")

        # Metric 2: File size
        self.card_size = InfoCard(
            metrics_row,
            icon="💾",
            title="Package Size",
            value="-- MB",
            subtitle="Optimized & Compressed",
        )
        self.card_size.grid(row=0, column=1, padx=4, sticky="nsew")

        # Metric 3: Time
        self.card_time = InfoCard(
            metrics_row,
            icon="⏱️",
            title="Compilation Time",
            value=datetime.now().strftime("%I:%M %p"),
            subtitle=datetime.now().strftime("%d %b, %Y"),
        )
        self.card_time.grid(row=0, column=2, padx=(6, 0), sticky="nsew")

        # File location display
        loc_box = GlassCard(
            inner,
            corner_radius=9,
        )
        loc_box.pack(fill="x", pady=(0, 16))

        loc_inner = ctk.CTkFrame(loc_box, fg_color="transparent")
        loc_inner.pack(fill="x", padx=16, pady=12)

        loc_title = ctk.CTkLabel(
            loc_inner,
            text="Destination Output Path:",
            font=FONTS["small_bold"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        loc_title.pack(anchor="w")

        self.lbl_path = ctk.CTkLabel(
            loc_inner,
            text="Preparing path...",
            font=FONTS["code_bold"],
            text_color=get_theme_tuple("accent"),
            anchor="w",
            wraplength=680,
            justify="left",
        )
        self.lbl_path.pack(anchor="w", pady=(3, 0))

        # Actions Buttons Row
        action_row = ctk.CTkFrame(inner, fg_color="transparent")
        action_row.pack(fill="x")

        self.btn_open_folder = ModernButton(
            action_row,
            text="📂 Open Output Folder",
            variant="primary",
            height=40,
            width=180,
            command=self._open_file_location,
        )
        self.btn_open_folder.pack(side="left", padx=(0, 10))

        self.btn_copy_path = ModernButton(
            action_row,
            text="📋 Copy Path",
            variant="secondary",
            height=40,
            width=130,
            command=self._copy_path_to_clipboard,
        )
        self.btn_copy_path.pack(side="left", padx=(0, 10))

    def _build_install_instructions_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            inner,
            title="Installation Guide (ADB / USB Transfer)",
            subtitle="Install directly to a physical device or Android emulator.",
        ).pack(fill="x", pady=(0, 14))

        split = ctk.CTkFrame(inner, fg_color="transparent")
        split.pack(fill="x")
        split.columnconfigure(0, weight=1)
        split.columnconfigure(1, weight=3)

        # Left: QR Code box
        qr_box = GlassCard(
            split,
            corner_radius=10,
            width=140,
            height=140,
        )
        qr_box.pack_propagate(False)
        qr_box.grid(row=0, column=0, padx=(0, 18), sticky="nsew")

        self.qr_label = ctk.CTkLabel(
            qr_box,
            text="📱\nADB Ready\nDirect Install",
            font=FONTS["small_bold"],
            text_color=get_theme_tuple("text_muted"),
        )
        self.qr_label.place(relx=0.5, rely=0.5, anchor="center")

        # Right: Step-by-step ADB instructions
        guide_box = ctk.CTkFrame(split, fg_color="transparent")
        guide_box.grid(row=0, column=1, sticky="nsew")

        step_1 = ctk.CTkLabel(
            guide_box,
            text="1. On your Android phone, enable Developer Options and USB Debugging in Settings.",
            font=FONTS["body"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        step_1.pack(anchor="w", pady=(0, 4))

        step_2 = ctk.CTkLabel(
            guide_box,
            text="2. Connect your mobile device to your computer via USB cable.",
            font=FONTS["body"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        step_2.pack(anchor="w", pady=(0, 4))

        step_3 = ctk.CTkLabel(
            guide_box,
            text="3. Execute this command in your terminal or Command Prompt:",
            font=FONTS["body"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        step_3.pack(anchor="w", pady=(0, 4))

        # Command strip
        cmd_strip = ctk.CTkFrame(
            guide_box,
            fg_color=COLORS["terminal_bg"],
            corner_radius=8,
            border_width=1,
            border_color=get_theme_tuple("border"),
        )
        cmd_strip.pack(fill="x", pady=(4, 0))

        self.lbl_cmd = ctk.CTkLabel(
            cmd_strip,
            text="adb install -r app-release.apk",
            font=FONTS["code_bold"],
            text_color="#10b981",
        )
        self.lbl_cmd.pack(side="left", padx=12, pady=8)

        btn_copy_cmd = ModernButton(
            cmd_strip,
            text="Copy Command",
            variant="secondary",
            height=28,
            width=110,
            font=FONTS["small_bold"],
            command=self._copy_adb_command,
        )
        btn_copy_cmd.pack(side="right", padx=8, pady=4)

    def _build_summary_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            inner,
            title="Configuration Specification",
            subtitle="Final parameters embedded in the compiled APK.",
        ).pack(fill="x", pady=(0, 12))

        self.summary_container = ctk.CTkFrame(inner, fg_color="transparent")
        self.summary_container.pack(fill="x")

        self._render_summary_rows({
            "App Name": "Android App",
            "Package Identifier": "com.app.myapp",
            "Version": "1.0.0 (Code: 1)",
            "Screen Orientation": "Portrait",
            "Internet Permission": "Granted (android.permission.INTERNET)",
        })

    def _render_summary_rows(self, data: Dict[str, str]):
        for widget in self.summary_container.winfo_children():
            widget.destroy()

        for idx, (k, v) in enumerate(data.items()):
            row = ctk.CTkFrame(
                self.summary_container,
                fg_color=get_theme_tuple("entry_bg") if idx % 2 == 0 else "transparent",
                corner_radius=6,
            )
            row.pack(fill="x", pady=2)

            k_lbl = ctk.CTkLabel(
                row,
                text=k,
                font=FONTS["body_bold"],
                text_color=get_theme_tuple("text_secondary"),
                width=170,
                anchor="w",
            )
            k_lbl.pack(side="left", padx=14, pady=7)

            v_lbl = ctk.CTkLabel(
                row,
                text=str(v),
                font=FONTS["body"],
                text_color=get_theme_tuple("text_primary"),
                anchor="w",
            )
            v_lbl.pack(side="left", fill="x", expand=True, padx=8, pady=7)

    def set_result(self, apk_path: str, build_config: Optional[Dict[str, Any]] = None):
        """Update result page with actual build metrics."""
        self.apk_path = apk_path
        self.build_config = build_config or {}

        fname = os.path.basename(apk_path) if apk_path else "app-release.apk"
        self.card_name.update_value(fname)

        if apk_path and os.path.exists(apk_path):
            sz = os.path.getsize(apk_path)
            if sz > 1024 * 1024:
                size_str = f"{sz / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{max(1, sz // 1024)} KB"
        else:
            size_str = "2.4 MB"

        self.card_size.update_value(size_str)
        self.lbl_path.configure(text=apk_path or "Path unavailable")

        quoted_path = f'"{apk_path}"' if apk_path else "app-release.apk"
        self.lbl_cmd.configure(text=f"adb install -r {quoted_path}")

        self._generate_qr(apk_path)

        cfg = self.build_config
        summary_dict = {
            "App Name": cfg.get("app_name", fname.replace(".apk", "")),
            "Package Identifier": cfg.get("package_name", "com.app.webapp"),
            "Version": f"{cfg.get('version_name', '1.0.0')} (Code: {cfg.get('version_code', '1')})",
            "Screen Orientation": cfg.get("orientation", "portrait").capitalize(),
            "Fullscreen Mode": "Enabled" if cfg.get("fullscreen") else "Standard Window",
            "Internet Access": "Granted" if cfg.get("internet_permission", True) else "Disabled",
            "Output Binary": fname,
        }
        self._render_summary_rows(summary_dict)

    def _generate_qr(self, text_content: str):
        try:
            import qrcode
            qr = qrcode.QRCode(box_size=3, border=1)
            qr.add_data(text_content or "APK Compiler")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            img = img.resize((120, 120), Image.Resampling.LANCZOS)
            self.qr_ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
            self.qr_label.configure(image=self.qr_ctk_image, text="")
        except Exception:
            self.qr_label.configure(text="📱\nADB Ready\nDirect Install")

    def _open_file_location(self):
        if not self.apk_path:
            messagebox.showinfo("Information", "No APK file path recorded.")
            return

        try:
            norm_p = os.path.normpath(self.apk_path)
            if os.path.exists(norm_p):
                if os.name == "nt":
                    subprocess.run(["explorer", "/select,", norm_p])
                else:
                    subprocess.run(["xdg-open", os.path.dirname(norm_p)])
            else:
                folder = os.path.dirname(norm_p)
                if os.path.exists(folder):
                    os.startfile(folder) if os.name == "nt" else subprocess.run(["xdg-open", folder])
                else:
                    messagebox.showwarning("Warning", f"Path not found:\n{norm_p}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")

    def _copy_path_to_clipboard(self):
        if not self.apk_path:
            return
        self.clipboard_clear()
        self.clipboard_append(self.apk_path)
        messagebox.showinfo("Copied", "Full APK file path copied to clipboard!")

    def _copy_adb_command(self):
        cmd = self.lbl_cmd.cget("text")
        self.clipboard_clear()
        self.clipboard_append(cmd)
        messagebox.showinfo("Copied", "ADB install command copied to clipboard!")

    def _on_home_click(self):
        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            self.app.main_window.show_page("welcome")

    def _on_new_build_click(self):
        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            if "upload" in self.app.main_window.pages:
                self.app.main_window.pages["upload"]._reset_selection()
            self.app.main_window.show_page("upload")
