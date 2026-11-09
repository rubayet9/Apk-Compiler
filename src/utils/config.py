"""APK Compiler - Configuration Management Module.

Handles paths, environment settings, persistent JSON configuration,
and discovery of JDK and Android SDK installations.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

APP_NAME = "APK Compiler"
APP_VERSION = "1.0.0"

# Base configuration and tools paths
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".apkcompiler")
TOOLS_DIR = os.path.join(CONFIG_DIR, "tools")
JDK_DIR = os.path.join(TOOLS_DIR, "jdk")
SDK_DIR = os.path.join(TOOLS_DIR, "android-sdk")
OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "APK Compiler Output")
TEMP_DIR = os.path.join(CONFIG_DIR, "temp")
KEYSTORE_DIR = os.path.join(CONFIG_DIR, "keystores")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Fallback legacy path
LEGACY_CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".apkbuilder", "config.json")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "app_name": APP_NAME,
    "app_version": APP_VERSION,
    "jdk_path": "",
    "sdk_path": "",
    "output_dir": OUTPUT_DIR,
    "default_package_prefix": "com.apkcompiler.app",
    "default_target_sdk": 34,
    "default_min_sdk": 21,
    "default_compile_sdk": 34,
    "default_orientation": "unspecified",
    "default_fullscreen": False,
    "default_internet_permission": True,
    "default_cleartext_traffic": True,
    "default_status_bar_color": "#1E1E2E",
    "theme": "Dark",
    "language": "en",
    "auto_clean_temp": True,
}


class AppConfig:
    """Manages application settings, paths, and environment validation."""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or CONFIG_FILE
        self.settings: Dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.ensure_dirs()
        self.load()

    def ensure_dirs(self) -> None:
        """Ensure all required directories exist on disk."""
        directories = [
            CONFIG_DIR,
            TOOLS_DIR,
            JDK_DIR,
            SDK_DIR,
            OUTPUT_DIR,
            TEMP_DIR,
            KEYSTORE_DIR,
        ]
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as err:
                sys.stderr.write(f"Warning: Failed to create directory '{directory}': {err}\n")

    def load(self) -> None:
        """Load configuration from JSON file. Merges with defaults, migrates legacy config if present."""
        target_file = self.config_file
        if not os.path.isfile(target_file) and os.path.isfile(LEGACY_CONFIG_FILE):
            target_file = LEGACY_CONFIG_FILE

        if os.path.isfile(target_file):
            try:
                with open(target_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Ensure output_dir defaults to APK Compiler Output if old default was used
                        if data.get("output_dir") == os.path.join(os.path.expanduser("~"), "APK Builder Output"):
                            data["output_dir"] = OUTPUT_DIR
                        self.settings.update(data)
                        self.settings["app_name"] = APP_NAME
                # Save to new config location if loaded from legacy
                if target_file != self.config_file:
                    self.save()
            except Exception as err:
                sys.stderr.write(f"Warning: Could not read config file '{target_file}': {err}\n")
        else:
            self.save()

    def save(self) -> bool:
        """Save current configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as err:
            sys.stderr.write(f"Error: Failed to save config file '{self.config_file}': {err}\n")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key."""
        return self.settings.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """Set setting value and optionally save to disk."""
        self.settings[key] = value
        if auto_save:
            self.save()

    def _find_javac_in_tree(self, root_dir: str) -> Optional[str]:
        """Check if root_dir or any of its direct subdirectories contains bin/javac."""
        if not os.path.isdir(root_dir):
            return None

        # Check root_dir/bin/javac(.exe)
        javac_name = "javac.exe" if sys.platform == "win32" else "javac"
        direct_bin_javac = os.path.join(root_dir, "bin", javac_name)
        if os.path.isfile(direct_bin_javac):
            return os.path.abspath(root_dir)

        # Check single nested subfolder (e.g. jdk-17.0.x+y/bin/javac)
        try:
            for entry in os.listdir(root_dir):
                sub = os.path.join(root_dir, entry)
                if os.path.isdir(sub):
                    candidate = os.path.join(sub, "bin", javac_name)
                    if os.path.isfile(candidate):
                        return os.path.abspath(sub)
        except OSError:
            pass

        return None

    def get_jdk_path(self) -> Optional[str]:
        """Find and return valid JDK home directory path, or None."""
        # 1. Configured custom path
        custom_path = self.get("jdk_path")
        if custom_path:
            valid = self._find_javac_in_tree(custom_path)
            if valid:
                return valid

        # 2. Bundled JDK inside application / executable directory
        app_dirs = [
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "",
        ]
        for ad in app_dirs:
            if ad and os.path.isdir(ad):
                for candidate_rel in ["tools/jdk", "jdk", "jbr", "tools/jbr"]:
                    cand = os.path.join(ad, *candidate_rel.split("/"))
                    valid = self._find_javac_in_tree(cand)
                    if valid:
                        return valid

        # 3. Managed tool directory in .apkcompiler or legacy .apkbuilder
        managed = self._find_javac_in_tree(JDK_DIR)
        if managed:
            return managed
        legacy_jdk = os.path.join(os.path.expanduser("~"), ".apkbuilder", "tools", "jdk")
        legacy_valid = self._find_javac_in_tree(legacy_jdk)
        if legacy_valid:
            return legacy_valid

        # 4. Android Studio bundled JDK (JBR / JRE)
        if sys.platform == "win32":
            as_candidates = [
                r"C:\Program Files\Android\Android Studio\jbr",
                r"C:\Program Files\Android\Android Studio\jre",
                r"C:\Program Files\Android\jbr",
                os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Android", "Android Studio", "jbr"),
                os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "Android", "Android Studio", "jre"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Android Studio", "jbr"),
                os.path.join(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Android", "Android Studio", "jbr"),
            ]
            for cand in as_candidates:
                if cand and os.path.isdir(cand):
                    valid = self._find_javac_in_tree(cand)
                    if valid:
                        return valid

        # 5. Environment variables (JAVA_HOME, STUDIO_JDK, JDK_HOME)
        for env_key in ["JAVA_HOME", "STUDIO_JDK", "JDK_HOME"]:
            env_val = os.environ.get(env_key)
            if env_val:
                valid = self._find_javac_in_tree(env_val)
                if valid:
                    return valid

        # 6. Which javac on PATH
        javac_bin = shutil.which("javac")
        if javac_bin:
            resolved_bin = os.path.dirname(os.path.abspath(javac_bin))
            candidate_home = os.path.dirname(resolved_bin)
            valid = self._find_javac_in_tree(candidate_home)
            if valid:
                return valid

        # 7. Standard Windows install locations
        if sys.platform == "win32":
            common_roots = [
                os.environ.get("ProgramFiles", r"C:\Program Files"),
                os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
            ]
            subfolders = ["Eclipse Adoptium", "Java", "Microsoft", "BellSoft", "Amazon Corretto", "Zulu", "Semeru"]
            for root in common_roots:
                if not root or not os.path.isdir(root):
                    continue
                for vendor in subfolders:
                    vendor_dir = os.path.join(root, vendor)
                    if os.path.isdir(vendor_dir):
                        try:
                            for entry in os.listdir(vendor_dir):
                                candidate = os.path.join(vendor_dir, entry)
                                valid = self._find_javac_in_tree(candidate)
                                if valid:
                                    return valid
                        except OSError:
                            continue

        return None

    def _is_valid_sdk_root(self, path: str) -> bool:
        """Check whether directory has Android SDK components (platforms, build-tools, or cmdline-tools)."""
        if not path or not os.path.isdir(path):
            return False
        markers = ["platforms", "build-tools", "platform-tools", "cmdline-tools", "tools"]
        for marker in markers:
            if os.path.isdir(os.path.join(path, marker)):
                return True
        return False

    def get_sdk_path(self) -> Optional[str]:
        """Find and return valid Android SDK directory path, or None."""
        # 1. Configured custom path
        custom_path = self.get("sdk_path")
        if custom_path and self._is_valid_sdk_root(custom_path):
            return os.path.abspath(custom_path)

        # 2. Bundled SDK inside application / executable directory
        app_dirs = [
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else "",
        ]
        for ad in app_dirs:
            if ad and os.path.isdir(ad):
                for candidate_rel in ["tools/android-sdk", "tools/sdk", "android-sdk", "sdk"]:
                    cand = os.path.join(ad, *candidate_rel.split("/"))
                    if self._is_valid_sdk_root(cand):
                        return os.path.abspath(cand)

        # 3. Managed tool directory in .apkcompiler or legacy .apkbuilder
        if self._is_valid_sdk_root(SDK_DIR):
            return os.path.abspath(SDK_DIR)
        legacy_sdk = os.path.join(os.path.expanduser("~"), ".apkbuilder", "tools", "android-sdk")
        if self._is_valid_sdk_root(legacy_sdk):
            return os.path.abspath(legacy_sdk)

        # 3. Environment variables
        for env_var in ["ANDROID_HOME", "ANDROID_SDK_ROOT"]:
            env_val = os.environ.get(env_var)
            if env_val and self._is_valid_sdk_root(env_val):
                return os.path.abspath(env_val)

        # 4. Standard local appdata Android SDK on Windows
        if sys.platform == "win32":
            local_app_data = os.environ.get("LOCALAPPDATA", "")
            if local_app_data:
                candidate = os.path.join(local_app_data, "Android", "Sdk")
                if self._is_valid_sdk_root(candidate):
                    return os.path.abspath(candidate)

        # 5. Linux / macOS standard locations
        home = os.path.expanduser("~")
        unix_candidates = [
            os.path.join(home, "Android", "Sdk"),
            os.path.join(home, "Library", "Android", "sdk"),
            "/usr/lib/android-sdk",
        ]
        for candidate in unix_candidates:
            if self._is_valid_sdk_root(candidate):
                return os.path.abspath(candidate)

        return None

    def get_build_tools_path(self) -> Optional[str]:
        """Find newest installed Android SDK build-tools directory path."""
        sdk_path = self.get_sdk_path()
        if not sdk_path:
            return None

        build_tools_dir = os.path.join(sdk_path, "build-tools")
        if not os.path.isdir(build_tools_dir):
            return None

        try:
            versions = [
                d for d in os.listdir(build_tools_dir)
                if os.path.isdir(os.path.join(build_tools_dir, d))
            ]
            if not versions:
                return None

            # Sort versions semver-like: splitting digits
            def parse_ver(v: str):
                parts = []
                for p in v.replace("-", ".").split("."):
                    parts.append(int(p) if p.isdigit() else 0)
                return parts

            sorted_versions = sorted(versions, key=parse_ver, reverse=True)
            return os.path.join(build_tools_dir, sorted_versions[0])
        except Exception:
            return None

    def is_jdk_installed(self) -> bool:
        """Check if a valid JDK is available."""
        return self.get_jdk_path() is not None

    def is_sdk_installed(self) -> bool:
        """Check if a valid Android SDK is available."""
        return self.get_sdk_path() is not None


# Global configuration instance
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Return singleton instance of AppConfig."""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance
