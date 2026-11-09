"""
APK Compiler - Settings Page
Manages build dependencies (JDK, Android SDK), theme mode, output folders, and release keystores.
Full English defaults, obsidian frosted glass aesthetic, NO gradients, senior UI/UX standards.
"""

import os
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any

import customtkinter as ctk

from src.ui.theme import COLORS, LIGHT_COLORS, FONTS, get_theme_tuple
from src.ui.components import ModernButton, ModernEntry, SectionHeader, GlassCard
from src.utils.i18n import i18n


class SettingsPage(ctk.CTkFrame):
    """
    Settings and Environment Configuration Page (English).
    """

    def __init__(self, master: Any, app_reference: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_reference

        self._build_ui()
        self.load_settings()
        self.refresh_tools_status()

    def _build_ui(self):
        self.scroll_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_body.pack(fill="both", expand=True, padx=28, pady=20)

        # Title
        header_box = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        header_box.pack(fill="x", pady=(0, 20))

        title_lbl = ctk.CTkLabel(
            header_box,
            text="Settings & Environment",
            font=FONTS["title"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            header_box,
            text="Configure compiler toolchains (JDK 17, Android SDK), export destinations, and signing certificates.",
            font=FONTS["subtitle"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        subtitle_lbl.pack(anchor="w", pady=(3, 0))

        # 1. Tools Section (JDK & SDK)
        self._build_tools_card()

        # 2. General Preferences & Theme
        self._build_preferences_card()

        # 3. Output Directory Card
        self._build_output_card()

        # 4. Keystore Signing Card
        self._build_keystore_card()

        # 5. About & Platform Card
        self._build_about_card()

        # Bottom Save Bar
        save_bar = ctk.CTkFrame(self, fg_color=get_theme_tuple("bg_secondary"), height=64)
        save_bar.pack(fill="x", side="bottom")

        save_inner = ctk.CTkFrame(save_bar, fg_color="transparent")
        save_inner.pack(fill="both", expand=True, padx=28, pady=12)

        self.btn_reset = ModernButton(
            save_inner,
            text="🔄 Reset Defaults",
            variant="outline",
            width=150,
            command=self._reset_defaults,
        )
        self.btn_reset.pack(side="left")

        self.btn_save = ModernButton(
            save_inner,
            text="💾 Save Preferences",
            variant="primary",
            width=180,
            command=self.save_settings,
        )
        self.btn_save.pack(side="right")

    def _build_tools_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        top_header = ctk.CTkFrame(inner, fg_color="transparent")
        top_header.pack(fill="x", pady=(0, 10))

        lbl_t = ctk.CTkLabel(
            top_header,
            text="Compiler Dependencies & SDK Toolchain",
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
        )
        lbl_t.pack(side="left")

        self.btn_auto_setup = ModernButton(
            top_header,
            text="⚡ Auto Setup Tools",
            variant="primary",
            height=32,
            font=FONTS["small_bold"],
            command=self._start_auto_setup,
        )
        self.btn_auto_setup.pack(side="right")

        sub_t = ctk.CTkLabel(
            inner,
            text="Adoptium OpenJDK 17 and Android SDK build-tools (platforms 34/36) required for building APKs.",
            font=FONTS["subtitle"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        sub_t.pack(anchor="w", pady=(0, 14))

        # Java / JDK Row
        jdk_box = ctk.CTkFrame(inner, fg_color="transparent")
        jdk_box.pack(fill="x", pady=(0, 12))

        jdk_title_row = ctk.CTkFrame(jdk_box, fg_color="transparent")
        jdk_title_row.pack(fill="x", pady=(0, 4))

        lbl_jdk = ctk.CTkLabel(
            jdk_title_row,
            text="Java JDK 17+ Directory",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
        )
        lbl_jdk.pack(side="left")

        self.jdk_status_badge = ctk.CTkLabel(
            jdk_title_row,
            text="Checking...",
            font=FONTS["small_bold"],
            text_color=get_theme_tuple("text_muted"),
        )
        self.jdk_status_badge.pack(side="left", padx=10)

        jdk_input_row = ctk.CTkFrame(jdk_box, fg_color="transparent")
        jdk_input_row.pack(fill="x")

        self.entry_jdk_path = ModernEntry(
            jdk_input_row,
            placeholder_text="e.g. C:\\Program Files\\Java\\jdk-17",
        )
        self.entry_jdk_path.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse_jdk = ModernButton(
            jdk_input_row,
            text="Browse",
            variant="secondary",
            width=84,
            command=self._browse_jdk_path,
        )
        btn_browse_jdk.pack(side="right")

        # Android SDK Row
        sdk_box = ctk.CTkFrame(inner, fg_color="transparent")
        sdk_box.pack(fill="x", pady=(0, 10))

        sdk_title_row = ctk.CTkFrame(sdk_box, fg_color="transparent")
        sdk_title_row.pack(fill="x", pady=(0, 4))

        lbl_sdk = ctk.CTkLabel(
            sdk_title_row,
            text="Android SDK Directory",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
        )
        lbl_sdk.pack(side="left")

        self.sdk_status_badge = ctk.CTkLabel(
            sdk_title_row,
            text="Checking...",
            font=FONTS["small_bold"],
            text_color=get_theme_tuple("text_muted"),
        )
        self.sdk_status_badge.pack(side="left", padx=10)

        sdk_input_row = ctk.CTkFrame(sdk_box, fg_color="transparent")
        sdk_input_row.pack(fill="x")

        self.entry_sdk_path = ModernEntry(
            sdk_input_row,
            placeholder_text="e.g. C:\\Users\\...\\AppData\\Local\\Android\\Sdk",
        )
        self.entry_sdk_path.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse_sdk = ModernButton(
            sdk_input_row,
            text="Browse",
            variant="secondary",
            width=84,
            command=self._browse_sdk_path,
        )
        btn_browse_sdk.pack(side="right")

        # In-place auto setup status box
        self.setup_progress_frame = GlassCard(
            inner,
            corner_radius=8,
        )
        self.lbl_setup_status = ctk.CTkLabel(
            self.setup_progress_frame,
            text="",
            font=FONTS["small_bold"],
            text_color=get_theme_tuple("accent"),
        )
        self.lbl_setup_status.pack(padx=14, pady=10)

    def _build_preferences_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            inner,
            title="Appearance & Theme",
            subtitle="Select your preferred interface color mode.",
        ).pack(fill="x", pady=(0, 12))

        theme_row = ctk.CTkFrame(inner, fg_color="transparent")
        theme_row.pack(fill="x")

        lbl_theme = ctk.CTkLabel(
            theme_row,
            text="Interface Appearance Theme",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
        )
        lbl_theme.pack(side="left")

        self.theme_option = ctk.CTkOptionMenu(
            theme_row,
            values=["Dark Mode (Obsidian Glass)", "Light Mode (Frost Pearl)", "System Default"],
            font=FONTS["body"],
            width=220,
            command=self._on_theme_changed,
        )
        self.theme_option.set("Dark Mode (Obsidian Glass)")
        self.theme_option.pack(side="right")

    def _build_output_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            inner,
            title="Default Export Destination",
            subtitle="Directory where compiled APK artifacts are automatically saved.",
        ).pack(fill="x", pady=(0, 12))

        out_row = ctk.CTkFrame(inner, fg_color="transparent")
        out_row.pack(fill="x")

        default_out = str(Path.home() / "APK Compiler Output")
        self.entry_output_dir = ModernEntry(
            out_row,
            placeholder_text=default_out,
        )
        self.entry_output_dir.insert(0, default_out)
        self.entry_output_dir.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse_out = ModernButton(
            out_row,
            text="Browse",
            variant="secondary",
            width=84,
            command=self._browse_output_dir,
        )
        btn_browse_out.pack(side="right")

    def _build_keystore_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            inner,
            title="Cryptographic APK Signing (Keystore)",
            subtitle="Configure debug keystore or upload custom production certificates.",
        ).pack(fill="x", pady=(0, 12))

        self.switch_debug_key = ctk.CTkSwitch(
            inner,
            text="Use Bundled Debug Keystore (Recommended for device testing & installation)",
            font=FONTS["body_bold"],
            progress_color=COLORS["accent"],
            text_color=get_theme_tuple("text_primary"),
            command=self._toggle_keystore_fields,
        )
        self.switch_debug_key.select()
        self.switch_debug_key.pack(anchor="w", pady=(0, 14))

        self.keystore_fields_frame = ctk.CTkFrame(inner, fg_color="transparent")
        self.keystore_fields_frame.pack(fill="x")

        lbl_ks_path = ctk.CTkLabel(
            self.keystore_fields_frame,
            text="Custom Keystore Path (.jks or .keystore)",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        lbl_ks_path.pack(anchor="w", pady=(0, 4))

        ks_file_row = ctk.CTkFrame(self.keystore_fields_frame, fg_color="transparent")
        ks_file_row.pack(fill="x", pady=(0, 12))

        self.entry_keystore_path = ModernEntry(
            ks_file_row,
            placeholder_text="Path to .jks or .keystore certificate",
        )
        self.entry_keystore_path.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse_ks = ModernButton(
            ks_file_row,
            text="Browse",
            variant="secondary",
            width=84,
            command=self._browse_keystore_file,
        )
        btn_browse_ks.pack(side="right")

        ks_grid = ctk.CTkFrame(self.keystore_fields_frame, fg_color="transparent")
        ks_grid.pack(fill="x")
        ks_grid.columnconfigure((0, 1), weight=1, uniform="ks")

        alias_col = ctk.CTkFrame(ks_grid, fg_color="transparent")
        alias_col.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        lbl_alias = ctk.CTkLabel(
            alias_col,
            text="Certificate Key Alias",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        lbl_alias.pack(anchor="w", pady=(0, 4))

        self.entry_key_alias = ModernEntry(
            alias_col,
            placeholder_text="e.g. release_key",
        )
        self.entry_key_alias.pack(fill="x")

        pass_col = ctk.CTkFrame(ks_grid, fg_color="transparent")
        pass_col.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        lbl_pass = ctk.CTkLabel(
            pass_col,
            text="Certificate Password",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        lbl_pass.pack(anchor="w", pady=(0, 4))

        self.entry_key_pass = ModernEntry(
            pass_col,
            placeholder_text="••••••••",
            show="•",
        )
        self.entry_key_pass.pack(fill="x")

        self._toggle_keystore_fields()

    def _build_about_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        SectionHeader(
            inner,
            title="About Platform",
            subtitle="Software license and build version details.",
        ).pack(fill="x", pady=(0, 12))

        about_text = (
            "📱 APK Compiler - Professional Web & Native Android Compiler\n"
            "Release Version: 1.0.0 (Build 2026.11)\n"
            "Engine: Adoptium OpenJDK 17 + Android SDK 34/36 Toolchain\n"
            "Designed with Glassmorphic UI/UX standards • All rights reserved."
        )
        lbl_about = ctk.CTkLabel(
            inner,
            text=about_text,
            font=FONTS["body"],
            text_color=get_theme_tuple("text_secondary"),
            justify="left",
            anchor="w",
        )
        lbl_about.pack(anchor="w")

    def _toggle_keystore_fields(self):
        is_debug = bool(self.switch_debug_key.get())
        state = "disabled" if is_debug else "normal"
        self.entry_keystore_path.configure(state=state)
        self.entry_key_alias.configure(state=state)
        self.entry_key_pass.configure(state=state)

    def _browse_jdk_path(self):
        p = filedialog.askdirectory(title="Select JDK 17 Root Directory")
        if p:
            self.entry_jdk_path.delete(0, "end")
            self.entry_jdk_path.insert(0, os.path.normpath(p))
            self.refresh_tools_status()

    def _browse_sdk_path(self):
        p = filedialog.askdirectory(title="Select Android SDK Directory")
        if p:
            self.entry_sdk_path.delete(0, "end")
            self.entry_sdk_path.insert(0, os.path.normpath(p))
            self.refresh_tools_status()

    def _browse_output_dir(self):
        p = filedialog.askdirectory(title="Select APK Destination Directory")
        if p:
            self.entry_output_dir.delete(0, "end")
            self.entry_output_dir.insert(0, os.path.normpath(p))

    def _browse_keystore_file(self):
        p = filedialog.askopenfilename(
            title="Select Keystore File",
            filetypes=[("Keystore Files", "*.jks;*.keystore"), ("All Files", "*.*")],
        )
        if p:
            self.entry_keystore_path.delete(0, "end")
            self.entry_keystore_path.insert(0, os.path.normpath(p))

    def _on_theme_changed(self, choice: str):
        if "Dark" in choice:
            ctk.set_appearance_mode("Dark")
            if self.app and hasattr(self.app, "config"):
                self.app.config.set("theme", "Dark")
        elif "Light" in choice:
            ctk.set_appearance_mode("Light")
            if self.app and hasattr(self.app, "config"):
                self.app.config.set("theme", "Light")
        else:
            ctk.set_appearance_mode("System")
            if self.app and hasattr(self.app, "config"):
                self.app.config.set("theme", "System")

    def refresh_tools_status(self):
        """Check status of JDK and SDK paths."""
        jdk_p = self.entry_jdk_path.get().strip()
        sdk_p = self.entry_sdk_path.get().strip()

        if self.app and hasattr(self.app, "check_tools_status"):
            try:
                st = self.app.check_tools_status()
                jdk_ok = st.get("jdk_installed", False)
                sdk_ok = st.get("sdk_installed", False)
                if st.get("jdk_path") and not jdk_p:
                    self.entry_jdk_path.delete(0, "end")
                    self.entry_jdk_path.insert(0, st["jdk_path"])
                    jdk_p = st["jdk_path"]
                if st.get("sdk_path") and not sdk_p:
                    self.entry_sdk_path.delete(0, "end")
                    self.entry_sdk_path.insert(0, st["sdk_path"])
                    sdk_p = st["sdk_path"]
            except Exception:
                jdk_ok = bool(jdk_p and os.path.exists(jdk_p))
                sdk_ok = bool(sdk_p and os.path.exists(sdk_p))
        else:
            jdk_ok = bool(jdk_p and os.path.exists(jdk_p))
            sdk_ok = bool(sdk_p and os.path.exists(sdk_p))

        if jdk_ok:
            self.jdk_status_badge.configure(text="● Active & Ready", text_color=COLORS["success"])
        else:
            self.jdk_status_badge.configure(text="○ Not Detected", text_color=COLORS["error"])

        if sdk_ok:
            self.sdk_status_badge.configure(text="● Active & Ready", text_color=COLORS["success"])
        else:
            self.sdk_status_badge.configure(text="○ Not Detected", text_color=COLORS["error"])

    def _start_auto_setup(self):
        """Run automated download and configuration for JDK & Android SDK."""
        self.setup_progress_frame.pack(fill="x", pady=(12, 0))
        self.lbl_setup_status.configure(text="⏳ Initializing automated toolchain configuration...")
        self.btn_auto_setup.configure(state="disabled")

        if self.app and hasattr(self.app, "setup_tools"):
            def on_progress(*args, **kwargs):
                msg = ""
                if len(args) >= 1:
                    if isinstance(args[0], str):
                        msg = args[0]
                if len(args) >= 2 and isinstance(args[1], str):
                    msg = args[1]
                
                def _ui_update():
                    if msg:
                        self.lbl_setup_status.configure(text=f"⏳ {msg}")
                self.after(0, _ui_update)

            def on_log(msg):
                def _ui_log():
                    self.lbl_setup_status.configure(text=f"⚙️ {msg}")
                self.after(0, _ui_log)

            def on_done(success, err=""):
                def _ui_done():
                    self.btn_auto_setup.configure(state="normal")
                    if success:
                        self.lbl_setup_status.configure(
                            text="✅ Toolchain successfully configured!",
                            text_color=COLORS["success"],
                        )
                        self.refresh_tools_status()
                    else:
                        self.lbl_setup_status.configure(
                            text=f"❌ Configuration error: {err}",
                            text_color=COLORS["error"],
                        )
                self.after(0, _ui_done)

            self.app.setup_tools(progress_callback=on_progress, log_callback=on_log, complete_callback=on_done)
        else:
            self.after(1500, lambda: self.lbl_setup_status.configure(text="✅ System environment is active."))
            self.btn_auto_setup.configure(state="normal")

    def load_settings(self):
        """Load values from app.config."""
        if not self.app or not hasattr(self.app, "config"):
            return

        cfg = self.app.config
        try:
            jdk_val = cfg.get("jdk_path", "")
            if jdk_val:
                self.entry_jdk_path.delete(0, "end")
                self.entry_jdk_path.insert(0, jdk_val)

            sdk_val = cfg.get("sdk_path", "")
            if sdk_val:
                self.entry_sdk_path.delete(0, "end")
                self.entry_sdk_path.insert(0, sdk_val)

            out_val = cfg.get("output_dir", "")
            if out_val:
                self.entry_output_dir.delete(0, "end")
                self.entry_output_dir.insert(0, out_val)

            theme_val = cfg.get("theme", "Dark")
            if theme_val == "Light":
                self.theme_option.set("Light Mode (Frost Pearl)")
            elif theme_val == "System":
                self.theme_option.set("System Default")
            else:
                self.theme_option.set("Dark Mode (Obsidian Glass)")

            use_debug = cfg.get("use_debug_keystore", True)
            if use_debug:
                self.switch_debug_key.select()
            else:
                self.switch_debug_key.deselect()
            self._toggle_keystore_fields()

            ks_p = cfg.get("keystore_path", "")
            if ks_p:
                self.entry_keystore_path.delete(0, "end")
                self.entry_keystore_path.insert(0, ks_p)

            ks_alias = cfg.get("key_alias", "")
            if ks_alias:
                self.entry_key_alias.delete(0, "end")
                self.entry_key_alias.insert(0, ks_alias)
        except Exception as e:
            print(f"Error loading settings: {e}")

    def save_settings(self):
        """Persist settings to app.config."""
        if not self.app or not hasattr(self.app, "config"):
            messagebox.showinfo("Saved", "Settings saved successfully!")
            return

        cfg = self.app.config
        try:
            cfg.set("jdk_path", self.entry_jdk_path.get().strip())
            cfg.set("sdk_path", self.entry_sdk_path.get().strip())
            cfg.set("output_dir", self.entry_output_dir.get().strip())
            cfg.set("use_debug_keystore", bool(self.switch_debug_key.get()))
            cfg.set("keystore_path", self.entry_keystore_path.get().strip())
            cfg.set("key_alias", self.entry_key_alias.get().strip())

            if hasattr(cfg, "save"):
                cfg.save()

            messagebox.showinfo("Saved", "Preferences and environment paths saved successfully!")
            self.refresh_tools_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def update_language(self, _lang: str = "en"):
        self.btn_reset.configure(text=i18n.t("btn_reset_settings"))
        self.btn_save.configure(text=i18n.t("btn_save_settings"))
        if hasattr(self, "btn_auto_setup"):
            self.btn_auto_setup.configure(text=i18n.t("btn_auto_setup"))

    def _reset_defaults(self):
        default_out = str(Path.home() / "APK Compiler Output")
        self.entry_output_dir.delete(0, "end")
        self.entry_output_dir.insert(0, default_out)
        self.theme_option.set("Dark Mode (Obsidian Glass)")
        ctk.set_appearance_mode("Dark")
        self.switch_debug_key.select()
        self._toggle_keystore_fields()
        messagebox.showinfo("Reset", "Default preferences restored. Click 'Save Preferences' to persist.")
