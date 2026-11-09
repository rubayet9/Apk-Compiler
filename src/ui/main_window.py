"""
APK Compiler - Main Application Window
Assembles the glassy navigation sidebar, top app bar with bilingual toggle,
responsive viewport, status bar, and page controller.
Full English defaults with instant toggle to Bengali, obsidian frosted glass aesthetic, NO gradients.
Features the official Gemini-generated logo and native Windows integration.
"""

import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any
from PIL import Image

import customtkinter as ctk

from src.ui.theme import COLORS, LIGHT_COLORS, FONTS, get_theme_tuple
from src.ui.components import ModernButton, GlassCard
from src.ui.welcome_page import WelcomePage
from src.ui.upload_page import UploadPage
from src.ui.config_page import ConfigPage
from src.ui.build_page import BuildPage
from src.ui.result_page import ResultPage
from src.ui.settings_page import SettingsPage
from src.utils.i18n import i18n


class HistoryPage(ctk.CTkFrame):
    """
    Dedicated view for listing and managing past APK build operations.
    """

    def __init__(self, master: Any, app_reference: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_reference
        self._build_ui()

    def _build_ui(self):
        self.scroll_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_body.pack(fill="both", expand=True, padx=28, pady=20)

        header_box = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        header_box.pack(fill="x", pady=(0, 20))

        self.title_lbl = ctk.CTkLabel(
            header_box,
            text=i18n.t("history_title"),
            font=FONTS["title"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.title_lbl.pack(anchor="w")

        self.subtitle_lbl = ctk.CTkLabel(
            header_box,
            text=i18n.t("history_subtitle"),
            font=FONTS["subtitle"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        self.subtitle_lbl.pack(anchor="w", pady=(3, 0))

        self.list_container = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        self.list_container.pack(fill="x", pady=(0, 24))

    def update_language(self, _lang: str = "en"):
        self.title_lbl.configure(text=i18n.t("history_title"))
        self.subtitle_lbl.configure(text=i18n.t("history_subtitle"))
        self.refresh()

    def refresh(self):
        for widget in self.list_container.winfo_children():
            widget.destroy()

        history = []
        if self.app and hasattr(self.app, "get_build_history"):
            history = self.app.get_build_history()

        if not history:
            empty_card = GlassCard(
                self.list_container,
                corner_radius=14,
            )
            empty_card.pack(fill="x", pady=24)

            inner = ctk.CTkFrame(empty_card, fg_color="transparent")
            inner.pack(padx=32, pady=42)

            ctk.CTkLabel(inner, text="📜", font=("Segoe UI", 38)).pack(pady=(0, 8))
            ctk.CTkLabel(
                inner,
                text=i18n.t("history_empty_title"),
                font=FONTS["heading"],
                text_color=get_theme_tuple("text_primary"),
            ).pack()
            ctk.CTkLabel(
                inner,
                text=i18n.t("history_empty_desc"),
                font=FONTS["body"],
                text_color=get_theme_tuple("text_muted"),
            ).pack(pady=(6, 0))
            return

        for item in history:
            app_name = item.get("app_name", "Android App")
            package_name = item.get("package_name", "com.app")
            version = item.get("version", "1.0.0")
            apk_path = item.get("apk_path", "")
            file_size_bytes = item.get("file_size", 0)
            date_str = item.get("build_date", "")

            if "T" in date_str:
                date_str = date_str.split("T")[0]

            if file_size_bytes > 1024 * 1024:
                size_str = f"{file_size_bytes / (1024 * 1024):.2f} MB"
            elif file_size_bytes > 1024:
                size_str = f"{file_size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{file_size_bytes} B"

            card = GlassCard(
                self.list_container,
                corner_radius=12,
                hoverable=True,
            )
            card.pack(fill="x", pady=6)

            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=16)

            icon_lbl = ctk.CTkLabel(row, text="📱", font=("Segoe UI", 26))
            icon_lbl.pack(side="left", padx=(0, 16))

            info_col = ctk.CTkFrame(row, fg_color="transparent")
            info_col.pack(side="left", fill="both", expand=True)

            t_row = ctk.CTkFrame(info_col, fg_color="transparent")
            t_row.pack(anchor="w")

            n_lbl = ctk.CTkLabel(
                t_row,
                text=app_name,
                font=FONTS["heading"],
                text_color=get_theme_tuple("text_primary"),
            )
            n_lbl.pack(side="left", padx=(0, 10))

            v_badge = ctk.CTkLabel(
                t_row,
                text=f"v{version}",
                font=FONTS["small_bold"],
                fg_color=get_theme_tuple("accent_subtle"),
                text_color=get_theme_tuple("accent"),
                corner_radius=6,
                padx=8,
                pady=2,
            )
            v_badge.pack(side="left")

            sub_text = f"{package_name}  •  {size_str}  •  {date_str}"
            s_lbl = ctk.CTkLabel(
                info_col,
                text=sub_text,
                font=FONTS["small"],
                text_color=get_theme_tuple("text_secondary"),
                anchor="w",
            )
            s_lbl.pack(anchor="w", pady=(3, 0))

            if apk_path and os.path.exists(apk_path):
                open_btn = ModernButton(
                    row,
                    text=i18n.t("btn_locate_file"),
                    variant="ghost",
                    width=110,
                    height=34,
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


class MainWindow(ctk.CTk):
    """
    Main Application Window with Responsive Grid, Obsidian Glass Sidebar,
    Adaptive Header with Language & Theme Toggles, and Page Controller.
    """

    def __init__(self, app: Optional[Any] = None):
        super().__init__()
        self.app = app
        if self.app:
            self.app.main_window = self

        # Set Windows AppUserModelID for proper taskbar icon integration
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("apkcompiler.web2apk.compiler.1.0")
        except Exception:
            pass

        # Load persisted language and theme from configuration
        saved_lang = "en"
        theme_mode = "Dark"
        if self.app and hasattr(self.app, "config"):
            saved_lang = self.app.config.get("language", "en")
            t_cfg = self.app.config.get("theme", "Dark")
            if str(t_cfg).lower() == "light":
                theme_mode = "Light"
            else:
                theme_mode = "Dark"

        i18n.set_language(saved_lang)
        ctk.set_appearance_mode(theme_mode)
        ctk.set_default_color_theme("blue")

        # Window Setup
        self.title(i18n.t("window_title"))
        self._center_window(1180, 800)
        self.minsize(980, 640)

        # Apply Window and Taskbar Icon (Gemini Logo)
        self._set_app_icon()

        self.current_page_name = "welcome"
        self.pages: Dict[str, ctk.CTkFrame] = {}
        self.nav_buttons: Dict[str, ctk.CTkButton] = {}

        self._build_layout()
        self._init_pages()
        self._init_drag_and_drop()
        self.show_page("welcome")

    def _init_drag_and_drop(self):
        """Register global crash-proof Win32 drag and drop."""
        try:
            from src.utils.win_drop import WinDropHandler
            self.drop_handler = WinDropHandler(self, self._on_global_file_drop)
        except Exception as e:
            print(f"Global drag & drop setup note: {e}")

    def _on_global_file_drop(self, paths: list):
        if not paths:
            return
        target_path = paths[0]
        if not os.path.exists(target_path):
            return

        # Smoothly switch to upload page if on another view
        if self.current_page_name != "upload":
            self.show_page("upload")

        # Pass target path to upload page controller
        upload_page = self.pages.get("upload")
        if upload_page and hasattr(upload_page, "_handle_path_selected"):
            upload_page._handle_path_selected(target_path)

    def _set_app_icon(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        icon_ico = os.path.join(assets_dir, "icon.ico")
        icon_png = os.path.join(assets_dir, "logo_icon.png")

        if os.path.exists(icon_ico):
            try:
                self.iconbitmap(icon_ico)
            except Exception as e:
                print(f"iconbitmap note: {e}")

        if os.path.exists(icon_png):
            try:
                photo = tk.PhotoImage(file=icon_png)
                self.iconphoto(False, photo)
            except Exception as e:
                print(f"iconphoto note: {e}")

    def _center_window(self, width: int, height: int):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = max(0, int((screen_w - width) / 2))
        pos_y = max(0, int((screen_h - height) / 2))
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def _build_layout(self):
        # Responsive root grid: 2 columns (sidebar fixed, content expands), 3 rows
        self.grid_rowconfigure(0, weight=0)  # Top bar
        self.grid_rowconfigure(1, weight=1)  # Main content body
        self.grid_rowconfigure(2, weight=0)  # Status bar
        self.grid_columnconfigure(0, weight=0)  # Sidebar (240px)
        self.grid_columnconfigure(1, weight=1)  # Content area (expands)

        # 1. Left Glass Sidebar (spanning row 0 to 1)
        self.sidebar_frame = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=get_theme_tuple("bg_secondary"),
            border_width=1,
            border_color=get_theme_tuple("border"),
        )
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)
        self._build_sidebar()

        # 2. Top Glass Header Bar (row 0, column 1)
        self.topbar_frame = ctk.CTkFrame(
            self,
            height=60,
            corner_radius=0,
            fg_color=get_theme_tuple("bg_secondary"),
            border_width=1,
            border_color=get_theme_tuple("border"),
        )
        self.topbar_frame.grid(row=0, column=1, sticky="ew")
        self.topbar_frame.grid_propagate(False)
        self._build_topbar()

        # 3. Central Responsive Content Area (row 1, column 1)
        self.content_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=get_theme_tuple("bg_primary"),
            border_width=0,
        )
        self.content_container.grid(row=1, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # 4. Status Bar at Bottom (row 2, spanning columns 0 to 1)
        self.statusbar_frame = ctk.CTkFrame(
            self,
            height=32,
            corner_radius=0,
            fg_color=get_theme_tuple("bg_secondary"),
            border_width=1,
            border_color=get_theme_tuple("border"),
        )
        self.statusbar_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.statusbar_frame.grid_propagate(False)
        self._build_statusbar()

    def _build_sidebar(self):
        # Brand Header inside sidebar with Gemini Logo
        brand_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        brand_box.pack(fill="x", padx=18, pady=(20, 18))

        logo_row = ctk.CTkFrame(brand_box, fg_color="transparent")
        logo_row.pack(fill="x")

        # Render official Gemini logo image inside a sleek glass badge
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        logo_png = os.path.join(assets_dir, "logo_icon.png")
        if os.path.exists(logo_png):
            try:
                pil_logo = Image.open(logo_png)
                logo_ctk = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(32, 32))
                badge_card = GlassCard(logo_row, width=42, height=42, corner_radius=10)
                badge_card.pack_propagate(False)
                badge_card.pack(side="left", padx=(0, 10))
                self.sidebar_logo_lbl = ctk.CTkLabel(
                    badge_card,
                    image=logo_ctk,
                    text="",
                    width=32,
                    height=32,
                )
                self.sidebar_logo_lbl.place(relx=0.5, rely=0.5, anchor="center")
            except Exception:
                self._fallback_logo(logo_row)
        else:
            self._fallback_logo(logo_row)

        title_group = ctk.CTkFrame(logo_row, fg_color="transparent")
        title_group.pack(side="left", fill="both")

        self.app_title_lbl = ctk.CTkLabel(
            title_group,
            text=i18n.t("app_title"),
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.app_title_lbl.pack(anchor="w")

        self.app_badge_lbl = ctk.CTkLabel(
            title_group,
            text=i18n.t("app_subtitle"),
            font=FONTS["caption"],
            text_color=get_theme_tuple("accent"),
            anchor="w",
        )
        self.app_badge_lbl.pack(anchor="w")

        # Hairline Divider
        divider = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color=get_theme_tuple("border"))
        divider.pack(fill="x", padx=16, pady=(0, 16))

        # Navigation Menu Section Label
        self.nav_section_lbl = ctk.CTkLabel(
            self.sidebar_frame,
            text=i18n.t("nav_heading"),
            font=FONTS["caption"],
            text_color=get_theme_tuple("text_muted"),
            anchor="w",
        )
        self.nav_section_lbl.pack(fill="x", padx=20, pady=(0, 8))

        # Nav Buttons (Bilingual supported)
        self.menu_keys = [
            ("welcome", "nav_dashboard", "welcome"),
            ("upload", "nav_new_build", "upload"),
            ("history", "nav_history", "history"),
            ("settings", "nav_settings", "settings"),
        ]

        self.nav_buttons = {}
        for key, text_key, target in self.menu_keys:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=i18n.t(text_key),
                font=FONTS["body_bold"],
                height=40,
                corner_radius=9,
                anchor="w",
                fg_color="transparent",
                text_color=get_theme_tuple("text_secondary"),
                hover_color=(LIGHT_COLORS["bg_card"], COLORS["bg_card"]),
                cursor="hand2",
                command=lambda t=target: self.show_page(t),
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_buttons[key] = btn

        # Sidebar Bottom Glass Hint Card
        sidebar_footer = GlassCard(
            self.sidebar_frame,
            corner_radius=12,
        )
        sidebar_footer.pack(side="bottom", fill="x", padx=14, pady=18)

        footer_inner = ctk.CTkFrame(sidebar_footer, fg_color="transparent")
        footer_inner.pack(fill="both", expand=True, padx=12, pady=12)

        self.hint_title_lbl = ctk.CTkLabel(
            footer_inner,
            text=i18n.t("quick_hint_title"),
            font=FONTS["small_bold"],
            text_color=get_theme_tuple("accent"),
            anchor="w",
        )
        self.hint_title_lbl.pack(anchor="w")

        self.hint_desc_lbl = ctk.CTkLabel(
            footer_inner,
            text=i18n.t("quick_hint_desc"),
            font=FONTS["small"],
            text_color=get_theme_tuple("text_secondary"),
            wraplength=180,
            justify="left",
            anchor="w",
        )
        self.hint_desc_lbl.pack(anchor="w", pady=(3, 0))

    def _fallback_logo(self, parent):
        logo_badge = ctk.CTkLabel(
            parent,
            text="⚡",
            font=("Segoe UI", 20),
            width=36,
            height=36,
            corner_radius=9,
            fg_color=get_theme_tuple("accent_subtle"),
            text_color=get_theme_tuple("accent"),
        )
        logo_badge.pack(side="left", padx=(0, 10))

    def _build_topbar(self):
        # Left: Current page breadcrumb / title
        left_box = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        left_box.pack(side="left", padx=24)

        self.page_title_lbl = ctk.CTkLabel(
            left_box,
            text=i18n.t("page_dashboard"),
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
        )
        self.page_title_lbl.pack(side="left")

        # Right: Engine status badge, Language toggle, Theme switch
        right_box = ctk.CTkFrame(self.topbar_frame, fg_color="transparent")
        right_box.pack(side="right", padx=24)

        self.engine_status_badge = ctk.CTkLabel(
            right_box,
            text=i18n.t("engine_ready"),
            font=FONTS["small_bold"],
            fg_color=get_theme_tuple("bg_card"),
            text_color=COLORS["success"],
            corner_radius=6,
            padx=10,
            pady=4,
        )
        self.engine_status_badge.pack(side="left", padx=(0, 12))

        # Compact Language Toggle Button (EN <-> বাং)
        self.lang_btn = ModernButton(
            right_box,
            text=i18n.t("lang_toggle_btn"),
            variant="secondary",
            height=32,
            width=88,
            font=FONTS["small_bold"],
            command=self.toggle_language,
        )
        self.lang_btn.pack(side="left", padx=(0, 10))

        # Dark / Light Theme Toggle Button
        current_mode = ctk.get_appearance_mode()
        is_dark = (current_mode == "Dark")
        self.theme_btn = ModernButton(
            right_box,
            text=i18n.t("theme_light") if is_dark else i18n.t("theme_dark"),
            variant="secondary",
            height=32,
            width=84,
            font=FONTS["small_bold"],
            command=self.toggle_theme,
        )
        self.theme_btn.pack(side="left")

    def _build_statusbar(self):
        inner = ctk.CTkFrame(self.statusbar_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)

        self.status_lbl = ctk.CTkLabel(
            inner,
            text=i18n.t("status_ready"),
            font=FONTS["small"],
            text_color=get_theme_tuple("text_muted"),
        )
        self.status_lbl.pack(side="left")

        ver_lbl = ctk.CTkLabel(
            inner,
            text="APK Compiler  •  v1.0.0",
            font=FONTS["small"],
            text_color=get_theme_tuple("text_muted"),
        )
        ver_lbl.pack(side="right")

    def _init_pages(self):
        """Instantiate all application pages and grid-stack them for zero-flicker transitions."""
        self.pages["welcome"] = WelcomePage(self.content_container, app_reference=self.app)
        self.pages["upload"] = UploadPage(self.content_container, app_reference=self.app)
        self.pages["config"] = ConfigPage(self.content_container, app_reference=self.app)
        self.pages["build"] = BuildPage(self.content_container, app_reference=self.app)
        self.pages["result"] = ResultPage(self.content_container, app_reference=self.app)
        self.pages["settings"] = SettingsPage(self.content_container, app_reference=self.app)
        self.pages["history"] = HistoryPage(self.content_container, app_reference=self.app)

        # Place all pages in the exact same grid cell for instant, flicker-free tkraise()
        for page_widget in self.pages.values():
            page_widget.grid(row=0, column=0, sticky="nsew")

    def show_page(self, page_name: str):
        """Display the specified page instantaneously with zero black glitch or frame drops."""
        if page_name not in self.pages:
            return

        target_page = self.pages[page_name]
        # Lift target page directly above previous page in Z-order (NO pack_forget, NO black flicker)
        target_page.tkraise()
        self.current_page_name = page_name

        # Update Top Bar Title immediately
        title_key = f"page_{page_name}"
        self.page_title_lbl.configure(text=i18n.t(title_key))

        # Update Sidebar Active Item Highlighting
        for btn_key, btn_widget in self.nav_buttons.items():
            is_active = (btn_key == page_name) or (btn_key == "upload" and page_name in ("upload", "config", "build", "result"))
            if is_active:
                btn_widget.configure(
                    fg_color=get_theme_tuple("accent_subtle"),
                    text_color=get_theme_tuple("accent"),
                )
            else:
                btn_widget.configure(
                    fg_color="transparent",
                    text_color=get_theme_tuple("text_secondary"),
                )

        # Update status bar
        self.set_status(i18n.t("status_active", page=i18n.t(title_key)))

        # Defer any heavy background refreshes slightly so page switch is immediate and 60fps smooth
        self.after(35, lambda pn=page_name, tp=target_page: self._deferred_page_refresh(pn, tp))

    def _deferred_page_refresh(self, page_name: str, target_page: Any):
        """Perform secondary page refresh after transition has smoothly occurred."""
        try:
            if page_name == "welcome" and hasattr(target_page, "refresh_history"):
                target_page.refresh_history()
            elif page_name == "history" and hasattr(target_page, "refresh"):
                target_page.refresh()
            elif page_name == "settings" and hasattr(target_page, "refresh_tools_status"):
                target_page.refresh_tools_status()
        except Exception as e:
            print(f"Deferred refresh note for '{page_name}': {e}")

    def navigate_to(self, page_name: str):
        """Alias for show_page."""
        self.show_page(page_name)

    def set_status(self, text: str):
        """Update bottom status bar message."""
        self.status_lbl.configure(text=text)

    def toggle_language(self):
        """Toggle between English and Bengali across the entire UI."""
        new_lang = i18n.toggle_language()
        if self.app and hasattr(self.app, "config"):
            self.app.config.set("language", new_lang)
            self.app.config.save()
        self.update_language()

    def update_language(self):
        """Update all main window and child page strings."""
        self.title(i18n.t("window_title"))
        self.lang_btn.configure(text=i18n.t("lang_toggle_btn"))
        self.app_title_lbl.configure(text=i18n.t("app_title"))
        self.app_badge_lbl.configure(text=i18n.t("app_subtitle"))
        self.nav_section_lbl.configure(text=i18n.t("nav_heading"))

        for key, text_key, _ in self.menu_keys:
            if key in self.nav_buttons:
                self.nav_buttons[key].configure(text=i18n.t(text_key))

        self.hint_title_lbl.configure(text=i18n.t("quick_hint_title"))
        self.hint_desc_lbl.configure(text=i18n.t("quick_hint_desc"))
        self.engine_status_badge.configure(text=i18n.t("engine_ready"))

        current_mode = ctk.get_appearance_mode()
        is_dark = (current_mode == "Dark")
        self.theme_btn.configure(text=i18n.t("theme_light") if is_dark else i18n.t("theme_dark"))

        # Update top breadcrumb
        title_key = f"page_{self.current_page_name}"
        self.page_title_lbl.configure(text=i18n.t(title_key))
        self.set_status(i18n.t("status_active", page=i18n.t(title_key)))

        # Notify child pages
        for page_obj in self.pages.values():
            if hasattr(page_obj, "update_language"):
                try:
                    page_obj.update_language()
                except Exception as e:
                    print(f"Error updating page language: {e}")

    def toggle_theme(self):
        """Toggle between Dark and Light appearances."""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("Light")
            self.theme_btn.configure(text=i18n.t("theme_dark"))
            if self.app and hasattr(self.app, "config"):
                self.app.config.set("theme", "Light")
                self.app.config.save()
        else:
            ctk.set_appearance_mode("Dark")
            self.theme_btn.configure(text=i18n.t("theme_light"))
            if self.app and hasattr(self.app, "config"):
                self.app.config.set("theme", "Dark")
                self.app.config.save()
