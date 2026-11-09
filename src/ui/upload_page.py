"""
APK Compiler - Upload Page
Decluttered, modern Glassmorphic source package uploader with native Windows drag-and-drop.
NO gradients, obsidian frosted glass surfaces, senior UI/UX standards, bilingual (EN & BN).
"""

import os
import zipfile
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any, List

import customtkinter as ctk

from src.ui.theme import COLORS, LIGHT_COLORS, FONTS, get_theme_tuple
from src.ui.components import ModernButton, StepIndicator, FileDropZone, GlassCard
from src.utils.i18n import i18n


class UploadPage(ctk.CTkFrame):
    """
    Step 1: Upload Source Package (Web App Folder or Google AI Studio ZIP).
    Features native Windows drag-and-drop via windnd and a decluttered, streamlined layout.
    """

    def __init__(self, master: Any, app_reference: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_reference
        self.selected_path: Optional[str] = None
        self.validation_result: Dict[str, Any] = {
            "has_index": False,
            "is_native_android": False,
            "total_size": 0,
            "app_name": "",
            "package_name": "",
        }

        self._build_ui()

    def _get_step_defs(self) -> List[tuple]:
        return [
            ("1", i18n.t("step_1")),
            ("2", i18n.t("step_2")),
            ("3", i18n.t("step_3")),
            ("4", i18n.t("step_4")),
        ]

    def _build_ui(self):
        # 1. Wizard Step Timeline
        self.step_indicator = StepIndicator(self, current_step=1, steps=self._get_step_defs())
        self.step_indicator.pack(fill="x", padx=28, pady=(16, 12))

        # 2. Main Scrollable Container
        self.scroll_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_body.pack(fill="both", expand=True, padx=28, pady=4)

        # Header Title & Subtitle
        self.header_box = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        self.header_box.pack(fill="x", pady=(0, 16))

        self.title_lbl = ctk.CTkLabel(
            self.header_box,
            text=i18n.t("upload_title"),
            font=FONTS["title"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.title_lbl.pack(anchor="w")

        self.subtitle_lbl = ctk.CTkLabel(
            self.header_box,
            text=i18n.t("upload_subtitle"),
            font=FONTS["subtitle"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        self.subtitle_lbl.pack(anchor="w", pady=(3, 0))

        # 3. Prominent Drag & Drop Zone
        self.drop_zone = FileDropZone(
            self.scroll_body,
            on_select=lambda _p: self._browse_folder(),
            height=180,
        )
        self.drop_zone.pack(fill="x", pady=(0, 16))
        self._update_dropzone_text()

        # 4. Action Buttons Row (Clean & Focused)
        self.btn_bar = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        self.btn_bar.pack(fill="x", pady=(0, 18))

        self.btn_folder = ModernButton(
            self.btn_bar,
            text=i18n.t("btn_browse_folder"),
            variant="secondary",
            width=180,
            command=self._browse_folder,
        )
        self.btn_folder.pack(side="left", padx=(0, 12))

        self.btn_zip = ModernButton(
            self.btn_bar,
            text=i18n.t("btn_browse_zip"),
            variant="secondary",
            width=190,
            command=self._browse_zip,
        )
        self.btn_zip.pack(side="left", padx=(0, 12))

        self.btn_clear = ModernButton(
            self.btn_bar,
            text=i18n.t("btn_reset"),
            variant="outline",
            width=110,
            command=self._reset_selection,
        )
        self.btn_clear.pack(side="left")

        # 5. Verified Package Details Card (Clean & Decluttered, replaces cluttered stats)
        self.package_card = GlassCard(
            self.scroll_body,
            corner_radius=14,
        )
        # Hidden by default until a file is selected
        self._build_package_card_content()

        # 6. Bottom Sticky Navigation Bar
        nav_bar = ctk.CTkFrame(self, fg_color=get_theme_tuple("bg_secondary"), height=64)
        nav_bar.pack(fill="x", side="bottom")

        nav_inner = ctk.CTkFrame(nav_bar, fg_color="transparent")
        nav_inner.pack(fill="both", expand=True, padx=28, pady=12)

        self.btn_back = ModernButton(
            nav_inner,
            text=i18n.t("btn_back_dash"),
            variant="secondary",
            width=140,
            command=self._on_back_click,
        )
        self.btn_back.pack(side="left")

        self.btn_next = ModernButton(
            nav_inner,
            text=i18n.t("btn_continue_config"),
            variant="primary",
            width=230,
            state="disabled",
            command=self._on_next_click,
        )
        self.btn_next.pack(side="right")

    def _build_package_card_content(self):
        """Construct the decluttered verification summary card."""
        self.card_inner = ctk.CTkFrame(self.package_card, fg_color="transparent")
        self.card_inner.pack(fill="both", expand=True, padx=22, pady=18)

        # Header of card
        top_row = ctk.CTkFrame(self.card_inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 10))

        self.card_heading = ctk.CTkLabel(
            top_row,
            text=i18n.t("selected_package_info"),
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.card_heading.pack(side="left")

        self.status_badge = ctk.CTkLabel(
            top_row,
            text="",
            font=FONTS["small_bold"],
            corner_radius=6,
            padx=10,
            pady=3,
        )
        self.status_badge.pack(side="right")

        # Main Info Row (Icon + Details)
        details_row = ctk.CTkFrame(self.card_inner, fg_color="transparent")
        details_row.pack(fill="x", pady=4)

        self.pkg_icon_label = ctk.CTkLabel(
            details_row,
            text="📦",
            font=("Segoe UI", 36),
            width=50,
        )
        self.pkg_icon_label.pack(side="left", padx=(0, 16))

        info_col = ctk.CTkFrame(details_row, fg_color="transparent")
        info_col.pack(side="left", fill="both", expand=True)

        self.pkg_name_label = ctk.CTkLabel(
            info_col,
            text="",
            font=FONTS["title"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.pkg_name_label.pack(anchor="w")

        self.pkg_type_label = ctk.CTkLabel(
            info_col,
            text="",
            font=FONTS["body_bold"],
            text_color=get_theme_tuple("accent"),
            anchor="w",
        )
        self.pkg_type_label.pack(anchor="w", pady=(2, 2))

        self.pkg_meta_label = ctk.CTkLabel(
            info_col,
            text="",
            font=FONTS["small"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        self.pkg_meta_label.pack(anchor="w")

        # Full path pill
        self.path_box = ctk.CTkFrame(
            self.card_inner,
            fg_color=get_theme_tuple("entry_bg"),
            corner_radius=8,
            border_width=1,
            border_color=get_theme_tuple("border"),
        )
        self.path_box.pack(fill="x", pady=(12, 0))

        self.path_text_lbl = ctk.CTkLabel(
            self.path_box,
            text="",
            font=FONTS["code"],
            text_color=get_theme_tuple("text_muted"),
            anchor="w",
            padx=12,
            pady=6,
        )
        self.path_text_lbl.pack(fill="x")

    def _update_dropzone_text(self):
        if not self.selected_path:
            self.drop_zone.update_text(
                title=i18n.t("dropzone_title"),
                subtitle=i18n.t("dropzone_subtitle"),
            )

    def update_language(self, _lang: str = "en"):
        """Refresh all visible labels when language toggles."""
        self.step_indicator.update_steps(self._get_step_defs())
        self.title_lbl.configure(text=i18n.t("upload_title"))
        self.subtitle_lbl.configure(text=i18n.t("upload_subtitle"))
        self.btn_folder.configure(text=i18n.t("btn_browse_folder"))
        self.btn_zip.configure(text=i18n.t("btn_browse_zip"))
        self.btn_clear.configure(text=i18n.t("btn_reset"))
        self.card_heading.configure(text=i18n.t("selected_package_info"))
        self.btn_back.configure(text=i18n.t("btn_back_dash"))
        self.btn_next.configure(text=i18n.t("btn_continue_config"))
        self._update_dropzone_text()

        # Re-render card if path already selected
        if self.selected_path:
            self._render_selected_package()

    def _browse_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Web Application or Android Project Folder")
        if folder_selected:
            self._handle_path_selected(os.path.normpath(folder_selected))

    def _browse_zip(self):
        file_selected = filedialog.askopenfilename(
            title="Select Web App or AI Studio ZIP Archive",
            filetypes=[("ZIP Archive", "*.zip"), ("All Files", "*.*")],
        )
        if file_selected:
            self._handle_path_selected(os.path.normpath(file_selected))

    def _handle_path_selected(self, path: str):
        self.selected_path = path

        app_res = {}
        if self.app and hasattr(self.app, "set_web_app_path"):
            try:
                app_res = self.app.set_web_app_path(path)
            except Exception as e:
                print(f"Controller validation error: {e}")

        val = self._scan_path(path)
        if app_res.get("is_native_android"):
            val["is_native_android"] = True
            val["has_index"] = True
            val["app_name"] = app_res.get("app_name", "Android App")
            val["package_name"] = app_res.get("package_name", "")

        self.validation_result = val
        is_valid = val["has_index"] or val.get("is_native_android", False)

        self.drop_zone.set_file_path(path, is_valid=is_valid)
        self._render_selected_package()

    def _render_selected_package(self):
        """Display the sleek verification summary card."""
        if not self.selected_path:
            self.package_card.pack_forget()
            self.btn_next.configure(state="disabled")
            return

        val = self.validation_result
        is_zip = self.selected_path.lower().endswith(".zip")
        is_native = val.get("is_native_android", False)
        is_valid = val.get("has_index", False) or is_native

        filename = os.path.basename(self.selected_path)
        self.pkg_name_label.configure(text=filename)

        # File size formatting
        total_bytes = val.get("total_size", 0)
        if total_bytes > 1024 * 1024:
            size_str = f"{total_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{max(1, total_bytes // 1024)} KB"

        # Determine type & icons
        if is_native:
            self.pkg_icon_label.configure(text="🤖")
            self.pkg_type_label.configure(
                text=i18n.t("pkg_type_studio"),
                text_color=COLORS["accent"],
            )
            app_title = val.get("app_name") or filename.replace(".zip", "").title()
            meta_info = f"App: {app_title}  •  Size: {size_str}  •  Kotlin / Jetpack Compose"
        elif is_zip:
            self.pkg_icon_label.configure(text="📦")
            self.pkg_type_label.configure(
                text=i18n.t("pkg_type_web") if is_valid else "ZIP Archive",
                text_color=COLORS["accent"] if is_valid else COLORS["error"],
            )
            meta_info = f"ZIP Archive  •  Size: {size_str}"
        else:
            self.pkg_icon_label.configure(text="📁")
            self.pkg_type_label.configure(
                text=i18n.t("pkg_type_web") if is_valid else "Project Folder",
                text_color=COLORS["accent"] if is_valid else COLORS["error"],
            )
            meta_info = f"Directory  •  Size: {size_str}"

        self.pkg_meta_label.configure(text=meta_info)
        self.path_text_lbl.configure(text=f"📍 {self.selected_path}")

        # Status Badge
        if is_valid:
            self.package_card.configure(border_color=COLORS["success"])
            self.status_badge.configure(
                text=i18n.t("pkg_status_ready"),
                fg_color=COLORS["success_subtle"],
                text_color=COLORS["success"],
            )
            self.btn_next.configure(state="normal")
        else:
            self.package_card.configure(border_color=COLORS["error"])
            self.status_badge.configure(
                text=i18n.t("pkg_status_missing"),
                fg_color=COLORS["error_subtle"],
                text_color=COLORS["error"],
            )
            self.btn_next.configure(state="disabled")

        # Show card directly below action buttons
        self.package_card.pack(fill="x", pady=(0, 24))

    def _scan_path(self, path: str) -> Dict[str, Any]:
        """Scan directory or ZIP file and verify structure."""
        res = {
            "has_index": False,
            "is_native_android": False,
            "total_size": 0,
            "app_name": "",
            "package_name": "",
        }

        if not os.path.exists(path):
            return res

        if path.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(path, "r") as z:
                    for info in z.infolist():
                        if info.is_dir():
                            continue
                        name = info.filename
                        basename = os.path.basename(name)
                        res["total_size"] += info.file_size
                        if basename.lower() in ("index.html", "index.htm"):
                            res["has_index"] = True
                        if basename.lower() in ("build.gradle.kts", "build.gradle", "settings.gradle.kts", "settings.gradle"):
                            res["is_native_android"] = True
            except Exception as e:
                print(f"Error reading ZIP: {e}")
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for f in files:
                    full_p = os.path.join(root, f)
                    try:
                        sz = os.path.getsize(full_p)
                    except Exception:
                        sz = 0
                    res["total_size"] += sz

                    if f.lower() in ("index.html", "index.htm"):
                        res["has_index"] = True
                    if f.lower() in ("build.gradle.kts", "build.gradle", "settings.gradle.kts", "settings.gradle"):
                        res["is_native_android"] = True

        if res["is_native_android"]:
            res["has_index"] = True

        return res

    def _reset_selection(self):
        self.selected_path = None
        self.validation_result = {
            "has_index": False,
            "is_native_android": False,
            "total_size": 0,
            "app_name": "",
            "package_name": "",
        }
        self.drop_zone.set_file_path("", is_valid=True)
        self._update_dropzone_text()
        self.package_card.pack_forget()
        self.btn_next.configure(state="disabled")

    def _on_back_click(self):
        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            self.app.main_window.show_page("welcome")

    def _on_next_click(self):
        if not self.validation_result.get("has_index") and not self.validation_result.get("is_native_android"):
            messagebox.showwarning("Warning", i18n.t("alert_invalid"))
            return

        if self.selected_path and self.app and hasattr(self.app, "build_config"):
            folder_name = os.path.basename(os.path.normpath(self.selected_path)).replace(".zip", "")
            if not self.app.build_config.get("app_name"):
                sanitized_title = "".join(c for c in folder_name if c.isalnum() or c in (" ", "_", "-")).strip()
                self.app.build_config["app_name"] = sanitized_title.title() or "My Web App"

        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            if "config" in self.app.main_window.pages:
                self.app.main_window.pages["config"].load_from_app_config()
            self.app.main_window.show_page("config")
