"""
APK Compiler - Build Progress Page
Displays step-by-step progress, animated progress bar, real-time build logs, and error recovery.
Full English defaults, obsidian frosted glass aesthetic, NO gradients, senior UI/UX standards.
"""

import os
import queue
import time
from datetime import datetime
from typing import Optional, List, Dict, Any

import customtkinter as ctk

from src.ui.theme import COLORS, LIGHT_COLORS, FONTS, get_theme_tuple
from src.ui.components import ModernButton, StepIndicator, ProgressCard, SectionHeader, GlassCard
from src.utils.i18n import i18n


class BuildPage(ctk.CTkFrame):
    """
    Step 3: Build progress tracking and real-time log monitoring (Bilingual EN/BN).
    """

    BUILD_STEP_KEYS = [
        "step_prep",
        "step_copy",
        "step_res",
        "step_compile",
        "step_sign",
        "step_done",
    ]

    @property
    def BUILD_STEPS(self) -> List[str]:
        return [i18n.t(k) for k in self.BUILD_STEP_KEYS]

    def _get_step_defs(self) -> List[tuple]:
        return [
            ("1", i18n.t("step_1")),
            ("2", i18n.t("step_2")),
            ("3", i18n.t("step_3")),
            ("4", i18n.t("step_4")),
        ]

    def __init__(self, master: Any, app_reference: Optional[Any] = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app_reference
        self.current_step_idx = 0
        self.is_running = False
        self.generated_apk_path: Optional[str] = None
        self.step_labels: List[ctk.CTkLabel] = []
        self.step_icons: List[ctk.CTkLabel] = []
        self.log_queue: queue.Queue = queue.Queue()

        self._build_ui()
        self._poll_log_queue()

    def update_language(self, _lang: str = "en"):
        self.step_indicator.update_steps(self._get_step_defs())
        self.title_lbl.configure(text=i18n.t("build_title"))
        self.subtitle_lbl.configure(text=i18n.t("build_subtitle"))
        self.progress_card.title_label.configure(text=i18n.t("build_progress_title"))
        self.btn_cancel.configure(text=i18n.t("btn_cancel_build"))
        self.btn_proceed.configure(text=i18n.t("btn_view_result"))
        for idx, lbl in enumerate(self.step_labels):
            if idx < len(self.BUILD_STEPS):
                lbl.configure(text=self.BUILD_STEPS[idx])

    def _build_ui(self):
        # Step indicator at top (Step 3)
        self.step_indicator = StepIndicator(self, current_step=3)
        self.step_indicator.pack(fill="x", padx=28, pady=(14, 8))

        # Main scrollable body
        self.scroll_body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_body.pack(fill="both", expand=True, padx=28, pady=8)

        # Title
        header_box = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        header_box.pack(fill="x", pady=(0, 16))

        self.title_lbl = ctk.CTkLabel(
            header_box,
            text="Compiling Android Package",
            font=FONTS["title"],
            text_color=get_theme_tuple("text_primary"),
            anchor="w",
        )
        self.title_lbl.pack(anchor="w")

        self.subtitle_lbl = ctk.CTkLabel(
            header_box,
            text="Executing automated Gradle toolchain, resource packaging, and cryptographic APK signing.",
            font=FONTS["subtitle"],
            text_color=get_theme_tuple("text_secondary"),
            anchor="w",
        )
        self.subtitle_lbl.pack(anchor="w", pady=(3, 0))

        # Progress Card
        self.progress_card = ProgressCard(
            self.scroll_body,
            title="Overall Compilation Progress",
            initial_status="Initializing build toolchain...",
            height=110,
        )
        self.progress_card.pack(fill="x", pady=(0, 18))

        # Main horizontal split: Steps Checklist (Left) & Real-time Terminal Log (Right)
        split_frame = ctk.CTkFrame(self.scroll_body, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, pady=(0, 10))
        split_frame.columnconfigure(0, weight=2)
        split_frame.columnconfigure(1, weight=3)

        # Left: Steps Checklist Card
        steps_card = GlassCard(
            split_frame,
            corner_radius=14,
        )
        steps_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        steps_inner = ctk.CTkFrame(steps_card, fg_color="transparent")
        steps_inner.pack(fill="both", expand=True, padx=20, pady=20)

        SectionHeader(
            steps_inner,
            title="Build Pipeline Stages",
            subtitle="Track progress through compilation stages",
        ).pack(fill="x", pady=(0, 12))

        self._build_steps_checklist(steps_inner)

        # Right: Real-time Monospace Log Terminal
        log_card = GlassCard(
            split_frame,
            corner_radius=14,
        )
        log_card.grid(row=0, column=1, sticky="nsew")

        log_inner = ctk.CTkFrame(log_card, fg_color="transparent")
        log_inner.pack(fill="both", expand=True, padx=20, pady=20)

        log_header_box = ctk.CTkFrame(log_inner, fg_color="transparent")
        log_header_box.pack(fill="x", pady=(0, 8))

        log_title = ctk.CTkLabel(
            log_header_box,
            text="Real-time Build Console",
            font=FONTS["heading"],
            text_color=get_theme_tuple("text_primary"),
        )
        log_title.pack(side="left")

        btn_clear_log = ModernButton(
            log_header_box,
            text="Clear",
            variant="outline",
            height=26,
            width=54,
            font=FONTS["small"],
            command=self._clear_logs,
        )
        btn_clear_log.pack(side="right")

        self.log_textbox = ctk.CTkTextbox(
            log_inner,
            height=270,
            font=FONTS["code"],
            fg_color=COLORS["terminal_bg"],
            text_color="#38bdf8",
            corner_radius=9,
            border_width=1,
            border_color=get_theme_tuple("border"),
            wrap="word",
        )
        self.log_textbox.pack(fill="both", expand=True)

        # Bottom Action Bar
        nav_bar = ctk.CTkFrame(self, fg_color=get_theme_tuple("bg_secondary"), height=64)
        nav_bar.pack(fill="x", side="bottom")

        nav_inner = ctk.CTkFrame(nav_bar, fg_color="transparent")
        nav_inner.pack(fill="both", expand=True, padx=28, pady=12)

        self.btn_cancel = ModernButton(
            nav_inner,
            text="✖ Cancel Build",
            variant="danger",
            width=160,
            command=self.cancel_build,
        )
        self.btn_cancel.pack(side="left")

        self.btn_proceed = ModernButton(
            nav_inner,
            text="View Release Artifact →",
            variant="success",
            width=200,
            state="disabled",
            command=self._on_proceed_click,
        )
        self.btn_proceed.pack(side="right")

    def _build_steps_checklist(self, parent: ctk.CTkFrame):
        self.step_labels = []
        self.step_icons = []

        for idx, step_name in enumerate(self.BUILD_STEPS):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=7)

            icon = ctk.CTkLabel(
                row,
                text="⏳" if idx == 0 else "○",
                font=("Segoe UI", 14),
                width=24,
                text_color=get_theme_tuple("accent") if idx == 0 else get_theme_tuple("text_muted"),
            )
            icon.pack(side="left", padx=(0, 10))

            lbl = ctk.CTkLabel(
                row,
                text=step_name,
                font=FONTS["body_bold"] if idx == 0 else FONTS["body"],
                text_color=get_theme_tuple("text_primary") if idx == 0 else get_theme_tuple("text_secondary"),
                anchor="w",
            )
            lbl.pack(side="left", fill="x", expand=True)

            self.step_icons.append(icon)
            self.step_labels.append(lbl)

    def _clear_logs(self):
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except Exception:
                break
        self.log_textbox.delete("1.0", "end")

    def _poll_log_queue(self):
        """Periodically drain log_queue in the main GUI thread."""
        try:
            lines = []
            while not self.log_queue.empty() and len(lines) < 60:
                lines.append(self.log_queue.get_nowait())

            if lines:
                ts = datetime.now().strftime("%H:%M:%S")
                batch_text = "".join(f"[{ts}] {line}\n" for line in lines)
                self.log_textbox.insert("end", batch_text)
                self.log_textbox.see("end")
        except Exception:
            pass
        finally:
            self.after(50, self._poll_log_queue)

    def append_log(self, text: str):
        """Append line to console log safely via queue."""
        self.log_queue.put(text)

    def update_progress(self, step_index: int, percent: float, log_message: str = ""):
        """Update checklist step, progress bar, and append log."""
        if log_message:
            self.append_log(log_message)

        def _do_update():
            self.current_step_idx = max(0, min(len(self.BUILD_STEPS) - 1, step_index))

            for i in range(len(self.BUILD_STEPS)):
                if i < self.current_step_idx:
                    self.step_icons[i].configure(text="✅", text_color=COLORS["success"])
                    self.step_labels[i].configure(
                        font=FONTS["body"],
                        text_color=COLORS["success"],
                    )
                elif i == self.current_step_idx:
                    self.step_icons[i].configure(text="⏳", text_color=COLORS["accent"])
                    self.step_labels[i].configure(
                        font=FONTS["body_bold"],
                        text_color=get_theme_tuple("text_primary"),
                    )
                else:
                    self.step_icons[i].configure(
                        text="○",
                        text_color=get_theme_tuple("text_muted"),
                    )
                    self.step_labels[i].configure(
                        font=FONTS["body"],
                        text_color=get_theme_tuple("text_muted"),
                    )

            step_text = self.BUILD_STEPS[self.current_step_idx]
            self.progress_card.set_progress(percent, status_text=step_text)

        self.after(0, _do_update)

    def start_build(self):
        """Start build process with the application controller."""
        if self.is_running:
            return

        try:
            self.is_running = True
            self.generated_apk_path = None
            self.title_lbl.configure(text="Compiling Android Package...")
            self.btn_cancel.configure(state="normal", text="✖ Cancel Build", variant="danger")
            self.btn_proceed.configure(state="disabled")

            # Reset UI
            self._clear_logs()
            self.progress_card.set_progress(0.02, "Initializing build toolchain...")
            self.update_progress(0, 0.05, "Starting automated Android compilation pipeline...")

            # Call app controller if available
            if self.app and hasattr(self.app, "start_build"):
                def on_progress(p, msg=""):
                    norm_p = p / 100.0 if p > 1.0 else p
                    norm_p = max(0.0, min(1.0, norm_p))
                    if norm_p < 0.12:
                        step_idx = 0
                    elif norm_p < 0.25:
                        step_idx = 1
                    elif norm_p < 0.40:
                        step_idx = 2
                    elif norm_p < 0.85:
                        step_idx = 3
                    elif norm_p < 0.98:
                        step_idx = 4
                    else:
                        step_idx = 5
                    self.update_progress(step_idx, norm_p, msg)

                def on_log(line):
                    self.append_log(line)

                def on_complete(apk_path):
                    self.after(0, lambda: self.build_complete(apk_path))

                def on_error(err):
                    self.after(0, lambda: self.build_failed(err))

                success = self.app.start_build(
                    progress_callback=on_progress,
                    log_callback=on_log,
                    complete_callback=on_complete,
                    error_callback=on_error,
                )

                if not success and not getattr(self.app, "is_building", False):
                    if self.is_running:
                        self.build_failed("Unable to initiate build. Please verify source package files.")
            else:
                self._run_simulated_build()
        except Exception as e:
            self.is_running = False
            self.build_failed(f"Build initialization error: {e}")

    def _run_simulated_build(self):
        """Simulated build runner for offline preview/testing."""
        import threading

        def worker():
            steps = [
                (0, 0.15, "Setting up Android project environment...", 1.0),
                (1, 0.35, "Copying web assets, scripts, and stylesheets...", 1.2),
                (2, 0.55, "Generating AndroidManifest.xml and processing resources...", 1.0),
                (3, 0.75, "Compiling Java/Kotlin classes into Android Dalvik bytecode...", 1.5),
                (4, 0.90, "Packaging APK and applying cryptographic signatures...", 1.2),
                (5, 1.00, "Build completed successfully!", 0.8),
            ]

            for s_idx, pct, msg, sleep_t in steps:
                if not self.is_running:
                    return
                self.update_progress(s_idx, pct, msg)
                time.sleep(sleep_t)

            if self.is_running:
                dummy_output = os.path.join(os.path.expanduser("~"), "APK Compiler Output", "app-release.apk")
                self.build_complete(dummy_output)

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def build_complete(self, apk_path: str):
        """Called when APK build succeeds."""
        self.is_running = False
        self.generated_apk_path = apk_path
        self.append_log(f"Build Succeeded! Output file: {apk_path}")

        def _do_complete():
            self.title_lbl.configure(text="🎉 Build Completed Successfully!")

            for i in range(len(self.BUILD_STEPS)):
                self.step_icons[i].configure(text="✅", text_color=COLORS["success"])
                self.step_labels[i].configure(text_color=COLORS["success"])

            self.progress_card.set_progress(1.0, "APK successfully compiled and signed!")

            self.btn_cancel.configure(state="disabled")
            self.btn_proceed.configure(state="normal")

            if self.app and hasattr(self.app, "main_window") and self.app.main_window:
                if "result" in self.app.main_window.pages:
                    cfg = self.app.get_build_config() if hasattr(self.app, "get_build_config") else {}
                    self.app.main_window.pages["result"].set_result(apk_path, cfg)
                self.after(1200, self._on_proceed_click)

        self.after(0, _do_complete)

    def build_failed(self, error_message: str):
        """Called when APK build fails."""
        self.is_running = False
        self.append_log(f"[ERROR] {error_message}")

        def _do_fail():
            self.title_lbl.configure(text="❌ Build Compilation Failed")
            self.progress_card.set_error(error_message)

            if self.current_step_idx < len(self.step_icons):
                self.step_icons[self.current_step_idx].configure(text="❌", text_color=COLORS["error"])
                self.step_labels[self.current_step_idx].configure(text_color=COLORS["error"])

            self.btn_cancel.configure(
                text="← Back to Configuration",
                variant="secondary",
                state="normal",
                command=self._on_back_to_config,
            )
            self.btn_proceed.configure(
                text="🔄 Retry Build",
                variant="primary",
                state="normal",
                command=self.start_build,
            )

        self.after(0, _do_fail)

    def cancel_build(self):
        """Cancel ongoing build."""
        self.is_running = False
        if self.app and hasattr(self.app, "cancel_build"):
            self.app.cancel_build()

        self.append_log("Build process was cancelled by user.")
        self.progress_card.set_error("Build Cancelled")
        self.title_lbl.configure(text="Build Cancelled")

        self.btn_cancel.configure(
            text="← Back to Configuration",
            variant="secondary",
            command=self._on_back_to_config,
        )

    def _on_back_to_config(self):
        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            self.app.main_window.show_page("config")

    def _on_proceed_click(self):
        if self.app and hasattr(self.app, "main_window") and self.app.main_window:
            self.app.main_window.show_page("result")
