"""
APK Compiler - Configuration Page
Configure Android APK settings: App name, package name, version, icon, orientation, permissions.
Obsidian frosted glass aesthetic, NO gradients, bilingual support (EN & BN).
Features the Gemini logo as default launcher app icon.
"""

import os
import re
from tkinter import filedialog, colorchooser, messagebox
from typing import Optional, Dict, Any, Tuple, List
from PIL import Image

import customtkinter as ctk

from src.ui.theme import COLORS, LIGHT_COLORS, FONTS, get_theme_tuple
from src.ui.components import ModernButton, ModernEntry, StepIndicator, SectionHeader, GlassCard
from src.utils.i18n import i18n


class ConfigPage(ctk.CTkFrame):
    """
    Step 2: Android App Configuration Page.
    """

    def __init__(self, master: Any, app_reference: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_reference
        self.selected_icon_path: Optional[str] = None
        self.icon_ctk_image = None
        self.default_ctk_image = None
        self._auto_package_name_enabled = True

        self._build_ui()
        self.load_from_app_config()

    def _get_step_defs(self) -> List[tuple]:
        return [
            ("1", i18n.t("step_1")),
            ("2", i18n.t("step_2")),
            ("3", i18n.t("step_3")),
            ("4", i18n.t("step_4")),
        ]

    def _build_ui(self):
        # Step Indicator at top (Step 2)
        self.step_indicator = StepIndicator(self, current_step=2, steps=self._get_step_defs())
        self.step_indicator.pack(fill="x", padx=28, pady=(16, 10))

        # Scrollable form container
        self.scroll_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_body.pack(fill="both", expand=True, padx=28, pady=4)

        # Title
        self.header_box = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        self.header_box.pack(fill="x", pady=(0, 16))

        self.title_lbl = ctk.CTkLabel(
            self.header_box,
            text=i18n.t("config_title"),
            font=FONTS["title"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.title_lbl.pack(anchor="w")

        self.subtitle_lbl = ctk.CTkLabel(
            self.header_box,
            text=i18n.t("config_subtitle"),
            font=FONTS["subtitle"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        self.subtitle_lbl.pack(anchor="w", pady=(3, 0))

        # 1. General Identity Card
        self._build_general_card()

        # 2. Visuals & Icon Card
        self._build_appearance_card()

        # 3. Permissions & System Card
        self._build_system_card()

        # Bottom Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color=get_theme_tuple("bg_secondary"), height=64)
        nav_bar.pack(fill="x", side="bottom")

        nav_inner = ctk.CTkFrame(nav_bar, fg_color="transparent")
        nav_inner.pack(fill="both", expand=True, padx=28, pady=12)

        self.btn_back = ModernButton(
            nav_inner,
            text=i18n.t("btn_back_upload"),
            variant="secondary",
            width=150,
            command=self._on_back_click,
        )
        self.btn_back.pack(side="left")

        self.btn_next = ModernButton(
            nav_inner,
            text=i18n.t("btn_start_compilation"),
            variant="primary",
            width=230,
            command=self._on_next_click,
        )
        self.btn_next.pack(side="right")

    def _build_general_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        self.sec_identity = SectionHeader(
            inner,
            title=i18n.t("app_identity_section"),
            subtitle="Display name and unique Android package identifier (Application ID).",
        )
        self.sec_identity.pack(fill="x", pady=(0, 14))

        # App Name Field
        self.lbl_name = ctk.CTkLabel(
            inner,
            text=f"{i18n.t('app_name_label')} *",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.lbl_name.pack(anchor="w", pady=(0, 4))

        self.entry_name = ModernEntry(
            inner,
            placeholder_text=i18n.t("app_name_ph"),
        )
        self.entry_name.pack(fill="x", pady=(0, 12))
        self.entry_name.bind("<KeyRelease>", self._on_app_name_changed)

        # Package Name Field
        self.lbl_pkg = ctk.CTkLabel(
            inner,
            text=f"{i18n.t('package_name_label')} *",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.lbl_pkg.pack(anchor="w", pady=(0, 4))

        self.entry_pkg = ModernEntry(
            inner,
            placeholder_text=i18n.t("package_name_ph"),
        )
        self.entry_pkg.pack(fill="x", pady=(0, 4))
        self.entry_pkg.bind("<KeyRelease>", self._on_package_name_manual_edit)

        self.lbl_pkg_hint = ctk.CTkLabel(
            inner,
            text="💡 Example: com.developer.appname (minimum 2 segments separated by dot).",
            font=FONTS["small"],
            text_color=get_theme_tuple("text_muted"),
            anchor="w",
        )
        self.lbl_pkg_hint.pack(anchor="w", pady=(0, 14))

        # Versions Grid (Version Name + Version Code)
        ver_grid = ctk.CTkFrame(inner, fg_color="transparent")
        ver_grid.pack(fill="x")
        ver_grid.columnconfigure((0, 1), weight=1, uniform="ver")

        # Version Name
        ver_left = ctk.CTkFrame(ver_grid, fg_color="transparent")
        ver_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.lbl_ver_name = ctk.CTkLabel(
            ver_left,
            text=i18n.t("version_name_label"),
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.lbl_ver_name.pack(anchor="w", pady=(0, 4))

        self.entry_ver_name = ModernEntry(
            ver_left,
            placeholder_text=i18n.t("version_name_ph"),
        )
        self.entry_ver_name.insert(0, "1.0.0")
        self.entry_ver_name.pack(fill="x")

        # Version Code
        ver_right = ctk.CTkFrame(ver_grid, fg_color="transparent")
        ver_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.lbl_ver_code = ctk.CTkLabel(
            ver_right,
            text=i18n.t("version_code_label"),
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.lbl_ver_code.pack(anchor="w", pady=(0, 4))

        self.entry_ver_code = ModernEntry(
            ver_right,
            placeholder_text=i18n.t("version_code_ph"),
        )
        self.entry_ver_code.insert(0, "1")
        self.entry_ver_code.pack(fill="x")

    def _build_appearance_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 18))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        self.sec_visuals = SectionHeader(
            inner,
            title=i18n.t("app_icon_section"),
            subtitle=i18n.t("app_icon_desc"),
        )
        self.sec_visuals.pack(fill="x", pady=(0, 14))

        # Icon Picker Row
        icon_row = ctk.CTkFrame(inner, fg_color="transparent")
        icon_row.pack(fill="x", pady=(0, 16))

        # Thumbnail frame
        self.icon_preview_frame = GlassCard(
            icon_row,
            width=68,
            height=68,
            corner_radius=12,
        )
        self.icon_preview_frame.pack_propagate(False)
        self.icon_preview_frame.pack(side="left", padx=(0, 18))

        self.icon_display_label = ctk.CTkLabel(
            self.icon_preview_frame,
            text="📱",
            font=("Segoe UI", 28),
        )
        self.icon_display_label.place(relx=0.5, rely=0.5, anchor="center")

        # Set default Gemini logo as icon preview
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        default_icon = os.path.join(assets_dir, "logo_icon.png")
        if os.path.exists(default_icon):
            try:
                img = Image.open(default_icon).resize((56, 56), Image.Resampling.LANCZOS)
                self.default_ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(56, 56))
                self.icon_display_label.configure(image=self.default_ctk_image, text="")
            except Exception:
                pass

        # Icon Info and Choose Button
        icon_meta = ctk.CTkFrame(icon_row, fg_color="transparent")
        icon_meta.pack(side="left", fill="both", expand=True)

        self.lbl_icon_title = ctk.CTkLabel(
            icon_meta,
            text=i18n.t("app_icon_section"),
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.lbl_icon_title.pack(anchor="w")

        self.lbl_icon_status = ctk.CTkLabel(
            icon_meta,
            text=i18n.t("app_icon_desc"),
            font=FONTS["small"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        self.lbl_icon_status.pack(anchor="w", pady=(2, 6))

        btn_row = ctk.CTkFrame(icon_meta, fg_color="transparent")
        btn_row.pack(anchor="w")

        self.btn_select_icon = ModernButton(
            btn_row,
            text=i18n.t("btn_browse_icon"),
            variant="secondary",
            height=32,
            font=FONTS["small_bold"],
            command=self._choose_icon,
        )
        self.btn_select_icon.pack(side="left", padx=(0, 8))

        self.btn_remove_icon = ModernButton(
            btn_row,
            text=i18n.t("btn_reset_icon"),
            variant="outline",
            height=32,
            font=FONTS["small"],
            command=self._clear_icon,
        )

        # Orientation & Status Bar row
        display_grid = ctk.CTkFrame(inner, fg_color="transparent")
        display_grid.pack(fill="x", pady=(4, 0))
        display_grid.columnconfigure((0, 1), weight=1, uniform="display")

        # Orientation Dropdown
        orient_col = ctk.CTkFrame(display_grid, fg_color="transparent")
        orient_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.lbl_orient = ctk.CTkLabel(
            orient_col,
            text=i18n.t("orientation_label"),
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.lbl_orient.pack(anchor="w", pady=(0, 4))

        self.orient_option = ctk.CTkOptionMenu(
            orient_col,
            values=[i18n.t("orientation_portrait"), i18n.t("orientation_landscape"), i18n.t("orientation_auto")],
            height=40,
            corner_radius=9,
            font=FONTS["body"],
            fg_color=get_theme_tuple("entry_bg"),
            button_color=get_theme_tuple("bg_card"),
            button_hover_color=get_theme_tuple("accent"),
            text_color=get_theme_tuple("text_primary"),
        )
        self.orient_option.set(i18n.t("orientation_portrait"))
        self.orient_option.pack(fill="x")

        # Status Bar Color
        color_col = ctk.CTkFrame(display_grid, fg_color="transparent")
        color_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self.lbl_color = ctk.CTkLabel(
            color_col,
            text=i18n.t("status_color_label"),
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.lbl_color.pack(anchor="w", pady=(0, 4))

        color_input_row = ctk.CTkFrame(color_col, fg_color="transparent")
        color_input_row.pack(fill="x")

        self.color_swatch = ctk.CTkLabel(
            color_input_row,
            text="",
            width=38,
            height=38,
            corner_radius=8,
            fg_color="#090d16",
            cursor="hand2",
        )
        self.color_swatch.pack(side="left", padx=(0, 8))
        self.color_swatch.bind("<Button-1>", lambda _e: self._pick_color())

        self.entry_status_color = ModernEntry(
            color_input_row,
            placeholder_text="#090d16",
        )
        self.entry_status_color.insert(0, "#090d16")
        self.entry_status_color.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.entry_status_color.bind("<KeyRelease>", self._on_color_text_change)

        self.btn_pick_color = ModernButton(
            color_input_row,
            text="🎨",
            variant="secondary",
            width=48,
            height=38,
            command=self._pick_color,
        )
        self.btn_pick_color.pack(side="right")

    def _build_system_card(self):
        card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        card.pack(fill="x", pady=(0, 20))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)

        self.sec_behavior = SectionHeader(
            inner,
            title=i18n.t("behavior_section"),
            subtitle="Android permissions and window behavior.",
        )
        self.sec_behavior.pack(fill="x", pady=(0, 14))

        # Switch 1: Internet Permission
        self.switch_internet = ctk.CTkSwitch(
            inner,
            text=f"🌐  {i18n.t('chk_internet')}",
            font=FONTS["body_bold"],
            progress_color=COLORS["accent"],
            text_color=get_theme_tuple("text_primary"),
        )
        self.switch_internet.select()
        self.switch_internet.pack(anchor="w", pady=(0, 12))

        # Switch 2: Fullscreen Mode
        self.switch_fullscreen = ctk.CTkSwitch(
            inner,
            text=f"📱  {i18n.t('chk_fullscreen')}",
            font=FONTS["body_bold"],
            progress_color=COLORS["accent"],
            text_color=get_theme_tuple("text_primary"),
        )
        self.switch_fullscreen.pack(anchor="w", pady=(0, 6))

    def update_language(self, _lang: str = "en"):
        """Update form strings when language changes."""
        self.step_indicator.update_steps(self._get_step_defs())
        self.title_lbl.configure(text=i18n.t("config_title"))
        self.subtitle_lbl.configure(text=i18n.t("config_subtitle"))
        self.btn_back.configure(text=i18n.t("btn_back_upload"))
        self.btn_next.configure(text=i18n.t("btn_start_compilation"))

        self.lbl_name.configure(text=f"{i18n.t('app_name_label')} *")
        self.lbl_pkg.configure(text=f"{i18n.t('package_name_label')} *")
        self.lbl_ver_name.configure(text=i18n.t("version_name_label"))
        self.lbl_ver_code.configure(text=i18n.t("version_code_label"))

        self.lbl_icon_title.configure(text=i18n.t("app_icon_section"))
        self.btn_select_icon.configure(text=i18n.t("btn_browse_icon"))
        self.btn_remove_icon.configure(text=i18n.t("btn_reset_icon"))

        self.lbl_orient.configure(text=i18n.t("orientation_label"))
        self.orient_option.configure(
            values=[i18n.t("orientation_portrait"), i18n.t("orientation_landscape"), i18n.t("orientation_auto")]
        )
        self.lbl_color.configure(text=i18n.t("status_color_label"))
        self.switch_internet.configure(text=f"🌐  {i18n.t('chk_internet')}")
        self.switch_fullscreen.configure(text=f"📱  {i18n.t('chk_fullscreen')}")

    def _on_app_name_changed(self, _event=None):
        if not self._auto_package_name_enabled:
            return

        name = self.entry_name.get().strip()
        if not name:
            sanitized = "myapp"
        else:
            sanitized = re.sub(r"[^a-zA-Z0-9]", "", name).lower()
            if not sanitized or not sanitized[0].isalpha():
                sanitized = "app" + sanitized

        auto_pkg = f"com.app.{sanitized}"
        self.entry_pkg.delete(0, "end")
        self.entry_pkg.insert(0, auto_pkg)

    def _on_package_name_manual_edit(self, _event=None):
        self._auto_package_name_enabled = False

    def _choose_icon(self):
        icon_file = filedialog.askopenfilename(
            title="Select App Launcher Icon (PNG or JPG)",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp"), ("All Files", "*.*")],
        )
        if icon_file and os.path.exists(icon_file):
            self.set_icon_path(os.path.normpath(icon_file))

    def set_icon_path(self, icon_path: str):
        try:
            self.selected_icon_path = icon_path
            img = Image.open(icon_path)
            img = img.resize((56, 56), Image.Resampling.LANCZOS)
            self.icon_ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(56, 56))

            self.icon_display_label.configure(image=self.icon_ctk_image, text="")
            fname = os.path.basename(icon_path)
            self.lbl_icon_status.configure(
                text=f"✅ Selected: {fname}",
                text_color=COLORS["success"],
            )
            self.btn_remove_icon.pack(side="left")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load icon: {e}")

    def _clear_icon(self):
        self.selected_icon_path = None
        self.icon_ctk_image = None
        if self.default_ctk_image:
            self.icon_display_label.configure(image=self.default_ctk_image, text="")
        else:
            self.icon_display_label.configure(image=None, text="📱")

        self.lbl_icon_status.configure(
            text=i18n.t("app_icon_desc"),
            text_color=get_theme_tuple("text_secondary"),
        )
        self.btn_remove_icon.pack_forget()

    def _pick_color(self):
        current_hex = self.entry_status_color.get().strip() or "#090d16"
        chosen = colorchooser.askcolor(color=current_hex, title="Select Status Bar Color")
        if chosen and chosen[1]:
            hex_val = chosen[1]
            self.entry_status_color.delete(0, "end")
            self.entry_status_color.insert(0, hex_val)
            self.color_swatch.configure(fg_color=hex_val)

    def _on_color_text_change(self, _event=None):
        txt = self.entry_status_color.get().strip()
        if re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", txt):
            self.color_swatch.configure(fg_color=txt)

    def load_from_app_config(self):
        """Pre-populate fields with configuration from controller."""
        if not self.app or not hasattr(self.app, "build_config"):
            return

        cfg = self.app.build_config
        if cfg.get("app_name"):
            self.entry_name.delete(0, "end")
            self.entry_name.insert(0, cfg["app_name"])

        if cfg.get("package_name"):
            self.entry_pkg.delete(0, "end")
            self.entry_pkg.insert(0, cfg["package_name"])
            self._auto_package_name_enabled = False

        if cfg.get("version_name"):
            self.entry_ver_name.delete(0, "end")
            self.entry_ver_name.insert(0, cfg["version_name"])

        if cfg.get("version_code"):
            self.entry_ver_code.delete(0, "end")
            self.entry_ver_code.insert(0, str(cfg["version_code"]))

        if cfg.get("status_bar_color"):
            self.entry_status_color.delete(0, "end")
            self.entry_status_color.insert(0, cfg["status_bar_color"])
            self.color_swatch.configure(fg_color=cfg["status_bar_color"])

        if cfg.get("icon_path") and os.path.exists(cfg["icon_path"]):
            self.set_icon_path(cfg["icon_path"])

        orientation = cfg.get("orientation", "portrait").lower()
        if orientation == "landscape":
            self.orient_option.set(i18n.t("orientation_landscape"))
        elif orientation in ("both", "sensor"):
            self.orient_option.set(i18n.t("orientation_auto"))
        else:
            self.orient_option.set(i18n.t("orientation_portrait"))

        if cfg.get("fullscreen"):
            self.switch_fullscreen.select()
        else:
            self.switch_fullscreen.deselect()

        if cfg.get("internet_permission", True):
            self.switch_internet.select()
        else:
            self.switch_internet.deselect()

    def get_config_dict(self) -> Dict[str, Any]:
        """Collect current values from all form fields."""
        orient_val = self.orient_option.get()
        if "Landscape" in orient_val or "ল্যান্ডস্কেপ" in orient_val:
            orient = "landscape"
        elif "Sensor" in orient_val or "সেন্সর" in orient_val:
            orient = "sensor"
        else:
            orient = "portrait"

        # If no custom icon chosen, pass default app icon
        icon_to_use = self.selected_icon_path
        if not icon_to_use:
            assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
            default_app_icon = os.path.join(assets_dir, "default_app_icon.png")
            if os.path.exists(default_app_icon):
                icon_to_use = default_app_icon

        return {
            "app_name": self.entry_name.get().strip(),
            "package_name": self.entry_pkg.get().strip(),
            "version_name": self.entry_ver_name.get().strip() or "1.0.0",
            "version_code": self.entry_ver_code.get().strip() or "1",
            "icon_path": icon_to_use,
            "orientation": orient,
            "status_bar_color": self.entry_status_color.get().strip() or "#090d16",
            "fullscreen": bool(self.switch_fullscreen.get()),
            "internet_permission": bool(self.switch_internet.get()),
        }

    def _validate_inputs(self) -> Tuple[bool, str]:
        app_name = self.entry_name.get().strip()
        if not app_name:
            return False, "Please enter an Application Name."

        pkg_name = self.entry_pkg.get().strip()
        if not pkg_name:
            return False, "Please enter a Package Identifier (e.g. com.company.app)."

        pkg_pattern = r"^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)+$"
        if not re.match(pkg_pattern, pkg_name):
            return False, "Invalid Package ID format! Example: com.company.appname (minimum 2 segments separated by dot)."

        ver_code = self.entry_ver_code.get().strip()
        if not ver_code.isdigit() or int(ver_code) <= 0:
            return False, "Version Code must be a positive integer (e.g. 1, 2, 3)."

        return True, ""

    def _on_back_click(self):
        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            self.app.main_window.show_page("upload")

    def _on_next_click(self):
        is_valid, err_msg = self._validate_inputs()
        if not is_valid:
            messagebox.showwarning("Incomplete Information", err_msg)
            return

        cfg = self.get_config_dict()

        if self.app:
            if hasattr(self.app, "build_config"):
                self.app.build_config.update(cfg)
            if hasattr(self.app, "update_build_config"):
                for k, v in cfg.items():
                    self.app.update_build_config(k, v)

        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            self.app.main_window.show_page("build")
            build_page = self.app.main_window.pages.get("build")
            if build_page and hasattr(build_page, "start_build"):
                self.after(50, build_page.start_build)
