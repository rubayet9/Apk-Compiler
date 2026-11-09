"""
APK Compiler - Main Application Controller
Orchestrates the UI and build engine.
"""

import os
import sys
import threading
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import AppConfig, APP_NAME, APP_VERSION, CONFIG_DIR, OUTPUT_DIR
from src.utils.file_utils import validate_web_app, extract_zip, format_file_size, create_temp_dir
from src.builder.apk_builder import APKBuilder


class APKBuilderApp:
    """Main application controller that bridges UI and build engine."""

    def __init__(self):
        self.config = AppConfig()
        self.config.ensure_dirs()

        # Auto-detect and set default JDK and SDK if not set
        if not self.config.get("jdk_path"):
            auto_jdk = self.config.get_jdk_path()
            if auto_jdk:
                self.config.set("jdk_path", auto_jdk)

        if not self.config.get("sdk_path"):
            auto_sdk = self.config.get_sdk_path()
            if auto_sdk:
                self.config.set("sdk_path", auto_sdk)

        # Current build state
        self.web_app_path = None
        self.web_app_files = {}
        self.build_config = {
            "app_name": "",
            "package_name": "com.app.myapp",
            "version_name": "1.0.0",
            "version_code": "1",
            "icon_path": None,
            "orientation": "portrait",
            "status_bar_color": "#1a1a2e",
            "fullscreen": False,
            "internet_permission": True,
        }
        self.current_builder = None
        self.build_thread = None
        self.is_building = False
        self.build_history = self._load_build_history()

        # UI reference (set by main_window)
        self.main_window = None

    def set_web_app_path(self, path):
        """Set the source path (Web App or Native Android) and validate it."""
        if path.lower().endswith('.zip'):
            # Extract ZIP to temp directory
            temp_dir = create_temp_dir()
            extract_zip(path, temp_dir)
            self.web_app_path = self._find_project_root(temp_dir)
        else:
            self.web_app_path = self._find_project_root(path)

        self.web_app_files = validate_web_app(self.web_app_path)
        
        # If native android project, auto-populate build config
        if self.web_app_files.get("is_native_android"):
            if self.web_app_files.get("app_name"):
                self.build_config["app_name"] = self.web_app_files["app_name"]
            if self.web_app_files.get("package_name"):
                self.build_config["package_name"] = self.web_app_files["package_name"]
            if self.web_app_files.get("version_name"):
                self.build_config["version_name"] = str(self.web_app_files["version_name"])
            if self.web_app_files.get("version_code"):
                self.build_config["version_code"] = str(self.web_app_files["version_code"])
            self.build_config["is_native_android"] = True
        else:
            self.build_config["is_native_android"] = False

        return self.web_app_files

    def _find_project_root(self, directory):
        """Find the root directory containing index.html or build.gradle(.kts)."""
        # Check current directory
        if os.path.exists(os.path.join(directory, "index.html")):
            return directory
        if os.path.exists(os.path.join(directory, "build.gradle.kts")) or os.path.exists(os.path.join(directory, "build.gradle")):
            return directory
        if os.path.exists(os.path.join(directory, "app", "build.gradle.kts")) or os.path.exists(os.path.join(directory, "app", "build.gradle")):
            return directory

        # Check subdirectories (one level)
        for item in os.listdir(directory):
            subdir = os.path.join(directory, item)
            if os.path.isdir(subdir):
                if os.path.exists(os.path.join(subdir, "index.html")):
                    return subdir
                if os.path.exists(os.path.join(subdir, "build.gradle.kts")) or os.path.exists(os.path.join(subdir, "build.gradle")):
                    return subdir
                if os.path.exists(os.path.join(subdir, "app", "build.gradle.kts")):
                    return subdir

        return directory

    def _find_web_root(self, directory):
        return self._find_project_root(directory)

    def update_build_config(self, key, value):
        """Update a build configuration value."""
        self.build_config[key] = value

    def get_build_config(self):
        """Get current build configuration."""
        return self.build_config.copy()

    def start_build(self, progress_callback=None, log_callback=None, complete_callback=None, error_callback=None):
        """Start the APK build process in a background thread."""
        if self.is_building:
            return False

        if not self.web_app_path:
            if error_callback:
                error_callback("No Web App or Android project source directory was selected!")
            return False

        self.is_building = True
        output_dir = self.config.get("output_dir", OUTPUT_DIR)
        os.makedirs(output_dir, exist_ok=True)

        def build_worker():
            log_file_path = os.path.join(CONFIG_DIR, "last_build.log")
            try:
                import datetime
                with open(log_file_path, "w", encoding="utf-8") as lf:
                    lf.write(f"=== Build Started: {datetime.datetime.now().isoformat()} ===\n")
                    lf.write(f"App Name: {self.build_config.get('app_name')}\n")
                    lf.write(f"Package: {self.build_config.get('package_name')}\n")
                    lf.write(f"Source: {self.web_app_path}\n\n")

                def safe_log(msg):
                    try:
                        with open(log_file_path, "a", encoding="utf-8") as lf:
                            lf.write(f"{msg}\n")
                    except Exception:
                        pass
                    if log_callback:
                        log_callback(msg)

                builder = APKBuilder(
                    config=self.build_config,
                    web_app_path=self.web_app_path,
                    output_dir=output_dir,
                    app_config=self.config,
                )
                self.current_builder = builder

                apk_path = builder.build(
                    progress_callback=progress_callback,
                    log_callback=safe_log
                )

                self.is_building = False
                self.current_builder = None

                # Save to build history
                self._save_build_to_history(apk_path)

                if complete_callback:
                    complete_callback(apk_path)

            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                try:
                    with open(log_file_path, "a", encoding="utf-8") as lf:
                        lf.write(f"\n[FATAL ERROR]\n{tb}\n")
                except Exception:
                    pass
                self.is_building = False
                self.current_builder = None
                if log_callback:
                    log_callback(f"[Error] {e}")
                if error_callback:
                    error_callback(str(e))

        self.build_thread = threading.Thread(target=build_worker, daemon=True)
        self.build_thread.start()
        return True

    def cancel_build(self):
        """Cancel the current build."""
        if self.current_builder:
            self.current_builder.cancel()
        self.is_building = False

    def _load_build_history(self):
        """Load build history from config directory."""
        history_file = os.path.join(CONFIG_DIR, "build_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_build_to_history(self, apk_path):
        """Save a completed build to history."""
        import datetime
        entry = {
            "app_name": self.build_config.get("app_name", "Unknown"),
            "package_name": self.build_config.get("package_name", ""),
            "version": self.build_config.get("version_name", "1.0.0"),
            "apk_path": apk_path,
            "build_date": datetime.datetime.now().isoformat(),
            "file_size": os.path.getsize(apk_path) if os.path.exists(apk_path) else 0,
        }
        self.build_history.insert(0, entry)
        # Keep only last 20 builds
        self.build_history = self.build_history[:20]

        history_file = os.path.join(CONFIG_DIR, "build_history.json")
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.build_history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_build_history(self):
        """Get build history."""
        return self.build_history

    def check_tools_status(self):
        """Check if required tools (JDK, SDK) are installed."""
        from src.utils.sdk_manager import SDKManager
        sdk_manager = SDKManager(self.config)
        return {
            "jdk_installed": sdk_manager.check_jdk() is not None,
            "sdk_installed": sdk_manager.check_sdk() is not None,
            "jdk_path": sdk_manager.check_jdk(),
            "sdk_path": sdk_manager.check_sdk(),
        }

    def setup_tools(self, progress_callback=None, log_callback=None, complete_callback=None):
        """Download and setup JDK and SDK."""
        from src.utils.sdk_manager import SDKManager
        sdk_manager = SDKManager(self.config)

        def setup_worker():
            try:
                if not sdk_manager.check_jdk():
                    if log_callback:
                        log_callback("Downloading Adoptium OpenJDK 17...")
                    sdk_manager.download_jdk(progress_callback)

                if not sdk_manager.check_sdk():
                    if log_callback:
                        log_callback("Downloading Android SDK tools...")
                    sdk_manager.download_sdk(progress_callback)
                    if log_callback:
                        log_callback("Configuring Android SDK platform tools...")
                    sdk_manager.setup_sdk(progress_callback)

                if complete_callback:
                    complete_callback(True)
            except Exception as e:
                if complete_callback:
                    complete_callback(False, str(e))

        thread = threading.Thread(target=setup_worker, daemon=True)
        thread.start()
