"""APK Compiler - JDK & Android SDK Manager Module.

Manages discovery, automated downloading, configuration, and tools resolution
for Adoptium OpenJDK 17 and Android SDK Command-line Tools.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from typing import Callable, Optional

from src.utils.config import (
    AppConfig,
    JDK_DIR,
    SDK_DIR,
    TOOLS_DIR,
    get_config,
)
from src.utils.file_utils import clean_directory, extract_zip, format_file_size

# Official distribution download URLs
JDK_DOWNLOAD_URL = "https://api.adoptium.net/v3/binary/latest/17/ga/windows/x64/jdk/hotspot/normal/eclipse"
SDK_CMDLINE_TOOLS_URL = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"

# Predefined license hashes for headless Android SDK installation
KNOWN_LICENSES = {
    "android-sdk-license": [
        "24333f8a63b6825ea9c5514f83c2829b004d1fee",
        "d56f5187479451eabf01fb78af6dfcb131a6481e",
        "84831b9409646a918e30573bab4c9c91346d8abd",
    ],
    "android-sdk-preview-license": [
        "84831b9409646a918e30573bab4c9c91346d8abd",
    ],
    "android-googletv-license": [
        "601085b94cd77f0b54ff8640695544944146e216",
    ],
}


class SDKManager:
    """Manages JDK and Android SDK discovery, installation, and command-line utilities."""

    def __init__(self, config: Optional[AppConfig] = None):
        self.config = config or get_config()

    def check_jdk(self) -> Optional[str]:
        """Check if a valid JDK is available and return its root directory path."""
        return self.config.get_jdk_path()

    def check_sdk(self) -> Optional[str]:
        """Check if a valid Android SDK is available and return its root directory path."""
        return self.config.get_sdk_path()

    def _download_file(
        self,
        url: str,
        dest_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> None:
        """Download file with progress reporting.

        Args:
            url: Download URL.
            dest_path: Destination file path.
            progress_callback: Optional callback receiving (percentage: 0-100, message: str).
        """
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "APKBuilderPro/1.0.0 (Windows NT 10.0; Win64; x64)"},
        )

        with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
            total_size_hdr = response.info().get("Content-Length")
            total_size = int(total_size_hdr) if total_size_hdr else 0
            downloaded = 0
            block_size = 65536  # 64 KB

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded += len(buffer)

                if progress_callback:
                    if total_size > 0:
                        pct = min(100.0, (downloaded / total_size) * 100.0)
                        msg = f"Downloaded {format_file_size(downloaded)} / {format_file_size(total_size)} ({pct:.1f}%)"
                    else:
                        pct = 0.0
                        msg = f"Downloaded {format_file_size(downloaded)}"
                    progress_callback(pct, msg)

    def download_jdk(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> str:
        """Download and extract Adoptium OpenJDK 17 for Windows x64.

        Args:
            progress_callback: Callback for download and extraction progress.

        Returns:
            Absolute path to installed JDK directory.
        """
        os.makedirs(TOOLS_DIR, exist_ok=True)
        temp_zip = os.path.join(TOOLS_DIR, "jdk17_download.zip")

        try:
            if progress_callback:
                progress_callback(0.0, "Starting OpenJDK 17 download...")

            self._download_file(JDK_DOWNLOAD_URL, temp_zip, progress_callback)

            if progress_callback:
                progress_callback(90.0, "Extracting OpenJDK 17...")

            clean_directory(JDK_DIR)
            temp_extract = os.path.join(TOOLS_DIR, "jdk_extract_tmp")
            clean_directory(temp_extract)

            extract_zip(temp_zip, temp_extract)

            # Check if archive extracted into a subfolder like jdk-17.0.x+y
            entries = os.listdir(temp_extract)
            if len(entries) == 1 and os.path.isdir(os.path.join(temp_extract, entries[0])):
                nested_dir = os.path.join(temp_extract, entries[0])
                for item in os.listdir(nested_dir):
                    shutil.move(os.path.join(nested_dir, item), JDK_DIR)
            else:
                for item in entries:
                    shutil.move(os.path.join(temp_extract, item), JDK_DIR)

            # Cleanup
            clean_directory(temp_extract)
            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract, ignore_errors=True)

            detected_jdk = self.check_jdk()
            if not detected_jdk:
                # If nested in JDK_DIR
                detected_jdk = self.config._find_javac_in_tree(JDK_DIR)

            if not detected_jdk:
                raise RuntimeError("OpenJDK download completed, but javac executable was not found.")

            self.config.set("jdk_path", detected_jdk)

            if progress_callback:
                progress_callback(100.0, f"OpenJDK 17 installed successfully: {detected_jdk}")

            return detected_jdk
        finally:
            if os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                except OSError:
                    pass

    def download_sdk(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> str:
        """Download and install Android SDK Command-line Tools.

        Extracts to: <SDK_DIR>/cmdline-tools/latest/

        Args:
            progress_callback: Callback for download and extraction progress.

        Returns:
            Path to Android SDK directory.
        """
        os.makedirs(SDK_DIR, exist_ok=True)
        temp_zip = os.path.join(TOOLS_DIR, "cmdline_tools.zip")

        try:
            if progress_callback:
                progress_callback(0.0, "Starting Android SDK commandline-tools download...")

            self._download_file(SDK_CMDLINE_TOOLS_URL, temp_zip, progress_callback)

            if progress_callback:
                progress_callback(85.0, "Extracting Android SDK commandline-tools...")

            # Target directory structure expected by sdkmanager:
            # SDK_DIR/cmdline-tools/latest/bin/sdkmanager.bat
            latest_dir = os.path.join(SDK_DIR, "cmdline-tools", "latest")
            clean_directory(latest_dir)

            temp_extract = os.path.join(TOOLS_DIR, "sdk_extract_tmp")
            clean_directory(temp_extract)

            extract_zip(temp_zip, temp_extract)

            # The zip contains a top-level "cmdline-tools" folder
            top_extracted = os.path.join(temp_extract, "cmdline-tools")
            source_dir = top_extracted if os.path.isdir(top_extracted) else temp_extract

            for item in os.listdir(source_dir):
                shutil.move(os.path.join(source_dir, item), latest_dir)

            # Cleanup
            clean_directory(temp_extract)
            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract, ignore_errors=True)

            self.config.set("sdk_path", SDK_DIR)

            if progress_callback:
                progress_callback(100.0, f"Android SDK commandline-tools installed at {latest_dir}")

            return SDK_DIR
        finally:
            if os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                except OSError:
                    pass

    def _write_licenses(self, sdk_root: str) -> None:
        """Write pre-accepted Android SDK licenses directly to avoid interactive prompts."""
        licenses_dir = os.path.join(sdk_root, "licenses")
        os.makedirs(licenses_dir, exist_ok=True)

        for license_name, hashes in KNOWN_LICENSES.items():
            license_path = os.path.join(licenses_dir, license_name)
            existing = set()
            if os.path.isfile(license_path):
                try:
                    with open(license_path, "r", encoding="utf-8") as f:
                        existing = {line.strip() for line in f if line.strip()}
                except OSError:
                    pass

            for h in hashes:
                existing.add(h)

            try:
                with open(license_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(sorted(existing)) + "\n")
            except OSError as err:
                sys.stderr.write(f"Warning: Failed to write license file {license_name}: {err}\n")

    def setup_sdk(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bool:
        """Accept licenses and install build-tools (34.0.0), platform (android-34), and platform-tools.

        Args:
            progress_callback: Callback receiving (percentage, message).

        Returns:
            True if installation succeeded.
        """
        sdk_root = self.check_sdk()
        if not sdk_root:
            raise RuntimeError("Android SDK root not found. Please run download_sdk() first.")

        jdk_path = self.check_jdk()
        if not jdk_path:
            raise RuntimeError("JDK not found. Please install or download JDK first.")

        # 1. Write known licenses directly
        self._write_licenses(sdk_root)

        # Locate sdkmanager executable
        bat_name = "sdkmanager.bat" if sys.platform == "win32" else "sdkmanager"
        candidate_paths = [
            os.path.join(sdk_root, "cmdline-tools", "latest", "bin", bat_name),
            os.path.join(sdk_root, "cmdline-tools", "bin", bat_name),
            os.path.join(sdk_root, "tools", "bin", bat_name),
        ]

        sdkmanager_exe = None
        for p in candidate_paths:
            if os.path.isfile(p):
                sdkmanager_exe = p
                break

        if not sdkmanager_exe:
            raise FileNotFoundError(f"sdkmanager executable not found in SDK: {sdk_root}")

        env = os.environ.copy()
        env["JAVA_HOME"] = jdk_path
        env["ANDROID_HOME"] = sdk_root
        env["ANDROID_SDK_ROOT"] = sdk_root
        env["PATH"] = os.path.join(jdk_path, "bin") + os.pathsep + env.get("PATH", "")

        packages = [
            "platforms;android-34",
            "build-tools;34.0.0",
            "platform-tools",
        ]

        total_steps = len(packages) + 1

        # Accept all licenses via sdkmanager as well
        if progress_callback:
            progress_callback(10.0, "Accepting Android SDK licenses...")

        try:
            lic_proc = subprocess.Popen(
                [sdkmanager_exe, f"--sdk_root={sdk_root}", "--licenses"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )
            # Send 'y\n' repeated to accept all prompts
            lic_proc.communicate(input="y\n" * 20, timeout=60)
        except Exception:
            # Non-critical if pre-written licenses exist
            pass

        # Install required SDK packages
        for idx, pkg in enumerate(packages, start=1):
            if progress_callback:
                pct = 10.0 + (idx / total_steps) * 85.0
                progress_callback(pct, f"Installing Android package: {pkg}...")

            cmd = [
                sdkmanager_exe,
                f"--sdk_root={sdk_root}",
                pkg,
            ]

            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
            )

            stdout, _ = process.communicate(input="y\n", timeout=600)
            if process.returncode != 0:
                raise RuntimeError(f"Failed to install SDK package '{pkg}'. Output:\n{stdout}")

        if progress_callback:
            progress_callback(100.0, "Android SDK setup complete with platform and build-tools 34.0.0.")

        return True

    def get_aapt_path(self) -> Optional[str]:
        """Return path to aapt2 or aapt executable inside build-tools."""
        build_tools = self.config.get_build_tools_path()
        if not build_tools:
            return None

        ext = ".exe" if sys.platform == "win32" else ""
        candidates = [
            os.path.join(build_tools, f"aapt2{ext}"),
            os.path.join(build_tools, f"aapt{ext}"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def get_dx_path(self) -> Optional[str]:
        """Return path to d8 or dx tool in build-tools."""
        build_tools = self.config.get_build_tools_path()
        if not build_tools:
            return None

        ext = ".bat" if sys.platform == "win32" else ""
        candidates = [
            os.path.join(build_tools, f"d8{ext}"),
            os.path.join(build_tools, f"dx{ext}"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    def get_zipalign_path(self) -> Optional[str]:
        """Return path to zipalign executable in build-tools."""
        build_tools = self.config.get_build_tools_path()
        if not build_tools:
            return None

        ext = ".exe" if sys.platform == "win32" else ""
        candidate = os.path.join(build_tools, f"zipalign{ext}")
        if os.path.isfile(candidate):
            return candidate
        return None

    def get_apksigner_path(self) -> Optional[str]:
        """Return path to apksigner tool in build-tools."""
        build_tools = self.config.get_build_tools_path()
        if not build_tools:
            return None

        ext = ".bat" if sys.platform == "win32" else ""
        candidate = os.path.join(build_tools, f"apksigner{ext}")
        if os.path.isfile(candidate):
            return candidate

        # Also check jar format
        jar_candidate = os.path.join(build_tools, "lib", "apksigner.jar")
        if os.path.isfile(jar_candidate):
            return jar_candidate

        return None
