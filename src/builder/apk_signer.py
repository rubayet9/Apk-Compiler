"""APK Compiler - APK Signing & Zipalign Module.

Handles creation of debug/release keystores, 4-byte zipalign optimization,
and cryptographic signing of APKs using Android apksigner (v1, v2, v3 schemes)
with fallback to JDK jarsigner.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from typing import Optional

from src.utils.config import AppConfig, KEYSTORE_DIR, get_config
from src.utils.sdk_manager import SDKManager


class APKSigner:
    """Signs and aligns Android APK packages for distribution and testing."""

    DEBUG_ALIAS = "androiddebugkey"
    DEBUG_PASS = "android"
    DEBUG_DNAME = "CN=Android Debug,O=Android,C=US"

    def __init__(
        self,
        jdk_path: Optional[str] = None,
        sdk_path: Optional[str] = None,
        config: Optional[AppConfig] = None,
    ):
        self.config = config or get_config()
        self.jdk_path = jdk_path or self.config.get_jdk_path()
        self.sdk_path = sdk_path or self.config.get_sdk_path()
        self.sdk_manager = SDKManager(self.config)

    def _get_keytool_cmd(self) -> str:
        """Find keytool binary in JDK or PATH."""
        if self.jdk_path:
            ext = ".exe" if sys.platform == "win32" else ""
            candidate = os.path.join(self.jdk_path, "bin", f"keytool{ext}")
            if os.path.isfile(candidate):
                return candidate

        system_keytool = shutil.which("keytool")
        if system_keytool:
            return system_keytool

        raise FileNotFoundError("keytool executable not found in JDK or system PATH.")

    def _get_jarsigner_cmd(self) -> Optional[str]:
        """Find jarsigner binary in JDK or PATH."""
        if self.jdk_path:
            ext = ".exe" if sys.platform == "win32" else ""
            candidate = os.path.join(self.jdk_path, "bin", f"jarsigner{ext}")
            if os.path.isfile(candidate):
                return candidate

        return shutil.which("jarsigner")

    def _get_java_cmd(self) -> str:
        """Find java binary in JDK or PATH."""
        if self.jdk_path:
            ext = ".exe" if sys.platform == "win32" else ""
            candidate = os.path.join(self.jdk_path, "bin", f"java{ext}")
            if os.path.isfile(candidate):
                return candidate

        system_java = shutil.which("java")
        if system_java:
            return system_java

        return "java"

    def create_debug_keystore(self, keystore_path: Optional[str] = None) -> str:
        """Generate a standard Android debug keystore if it does not already exist.

        Args:
            keystore_path: Path to target keystore file. If omitted, uses KEYSTORE_DIR/debug.keystore.

        Returns:
            Path to debug keystore file.
        """
        if not keystore_path:
            os.makedirs(KEYSTORE_DIR, exist_ok=True)
            keystore_path = os.path.join(KEYSTORE_DIR, "debug.keystore")

        if os.path.isfile(keystore_path):
            return keystore_path

        os.makedirs(os.path.dirname(os.path.abspath(keystore_path)), exist_ok=True)
        keytool_exe = self._get_keytool_cmd()

        cmd = [
            keytool_exe,
            "-genkeypair",
            "-v",
            "-keystore",
            keystore_path,
            "-storepass",
            self.DEBUG_PASS,
            "-alias",
            self.DEBUG_ALIAS,
            "-keypass",
            self.DEBUG_PASS,
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            "10000",
            "-dname",
            self.DEBUG_DNAME,
        ]

        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creationflags,
        )

        if proc.returncode != 0:
            raise RuntimeError(f"Failed to generate debug keystore: {proc.stderr}\n{proc.stdout}")

        return keystore_path

    def zipalign(self, apk_path: str, output_path: str) -> str:
        """Align APK uncompressed data on 4-byte boundaries.

        Args:
            apk_path: Input APK file.
            output_path: Target aligned APK path.

        Returns:
            Path to aligned APK.
        """
        if not os.path.isfile(apk_path):
            raise FileNotFoundError(f"Input APK not found: {apk_path}")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        zipalign_exe = self.sdk_manager.get_zipalign_path()

        if zipalign_exe and os.path.isfile(zipalign_exe):
            cmd = [
                zipalign_exe,
                "-f",  # force overwrite
                "-p",  # page align shared objects
                "4",   # 4-byte alignment
                apk_path,
                output_path,
            ]
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creationflags,
            )
            if proc.returncode == 0 and os.path.isfile(output_path):
                return output_path

        # If zipalign binary failed or is missing, copy input as fallback
        shutil.copy2(apk_path, output_path)
        return output_path

    def _sign_with_apksigner(
        self,
        apk_path: str,
        keystore_path: str,
        alias: str,
        password: str,
        key_password: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> bool:
        """Sign APK using Android SDK apksigner tool."""
        apksigner_path = self.sdk_manager.get_apksigner_path()
        if not apksigner_path:
            return False

        key_pass = key_password if key_password is not None else password
        target_out = output_path or apk_path

        # Determine how to invoke apksigner (.bat vs .jar vs script)
        is_jar = apksigner_path.endswith(".jar")
        if is_jar:
            base_cmd = [self._get_java_cmd(), "-jar", apksigner_path]
        else:
            base_cmd = [apksigner_path]

        cmd = base_cmd + [
            "sign",
            "--ks",
            keystore_path,
            "--ks-key-alias",
            alias,
            "--ks-pass",
            f"pass:{password}",
            "--key-pass",
            f"pass:{key_pass}",
            "--v1-signing-enabled",
            "true",
            "--v2-signing-enabled",
            "true",
            "--v3-signing-enabled",
            "true",
        ]

        if output_path and output_path != apk_path:
            cmd += ["--out", target_out, apk_path]
        else:
            cmd.append(apk_path)

        env = os.environ.copy()
        if self.jdk_path:
            env["JAVA_HOME"] = self.jdk_path
            env["PATH"] = os.path.join(self.jdk_path, "bin") + os.pathsep + env.get("PATH", "")

        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            creationflags=creationflags,
        )

        return proc.returncode == 0

    def _sign_with_jarsigner(
        self,
        apk_path: str,
        keystore_path: str,
        alias: str,
        password: str,
        key_password: Optional[str] = None,
    ) -> bool:
        """Sign APK using JDK jarsigner tool as fallback."""
        jarsigner_exe = self._get_jarsigner_cmd()
        if not jarsigner_exe:
            return False

        key_pass = key_password if key_password is not None else password
        cmd = [
            jarsigner_exe,
            "-sigalg",
            "SHA256withRSA",
            "-digestalg",
            "SHA-256",
            "-keystore",
            keystore_path,
            "-storepass",
            password,
            "-keypass",
            key_pass,
            apk_path,
            alias,
        ]

        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=creationflags,
        )

        return proc.returncode == 0

    def sign_debug(self, apk_path: str, keystore_path: Optional[str] = None) -> str:
        """Sign APK with Android debug credentials.

        First aligns the APK if needed, then signs using apksigner or jarsigner.

        Args:
            apk_path: Path to unaligned or unsigned APK.
            keystore_path: Path to debug keystore. Created automatically if not present.

        Returns:
            Path to signed, aligned APK.
        """
        if not os.path.isfile(apk_path):
            raise FileNotFoundError(f"Target APK does not exist: {apk_path}")

        # Ensure debug keystore exists
        ks_path = keystore_path or self.create_debug_keystore()

        # Step 1: Zipalign before apksigner
        if apk_path.lower().endswith(".apk"):
            aligned_path = apk_path[:-4] + "-aligned.apk"
        else:
            aligned_path = apk_path + "-aligned.apk"

        aligned_path = self.zipalign(apk_path, aligned_path)

        # Step 2: Sign with apksigner (or fallback jarsigner)
        signed = self._sign_with_apksigner(
            aligned_path,
            ks_path,
            self.DEBUG_ALIAS,
            self.DEBUG_PASS,
            self.DEBUG_PASS,
        )

        if not signed:
            # Fallback to jarsigner
            signed = self._sign_with_jarsigner(
                aligned_path,
                ks_path,
                self.DEBUG_ALIAS,
                self.DEBUG_PASS,
                self.DEBUG_PASS,
            )

        if not signed:
            raise RuntimeError("Failed to sign debug APK with both apksigner and jarsigner.")

        return aligned_path

    def sign_release(
        self,
        apk_path: str,
        keystore_path: str,
        alias: str,
        password: str,
        key_password: Optional[str] = None,
    ) -> str:
        """Sign APK with production release keystore.

        Args:
            apk_path: Input APK file.
            keystore_path: Path to release .jks or .keystore file.
            alias: Key alias.
            password: Store password.
            key_password: Key password (defaults to store password if omitted).

        Returns:
            Path to signed, aligned release APK.
        """
        if not os.path.isfile(apk_path):
            raise FileNotFoundError(f"Target APK does not exist: {apk_path}")

        if not os.path.isfile(keystore_path):
            raise FileNotFoundError(f"Keystore file not found: {keystore_path}")

        if apk_path.lower().endswith(".apk"):
            aligned_path = apk_path[:-4] + "-aligned.apk"
        else:
            aligned_path = apk_path + "-aligned.apk"

        # Align APK
        aligned_path = self.zipalign(apk_path, aligned_path)

        # Sign APK
        signed = self._sign_with_apksigner(
            aligned_path,
            keystore_path,
            alias,
            password,
            key_password or password,
        )

        if not signed:
            signed = self._sign_with_jarsigner(
                aligned_path,
                keystore_path,
                alias,
                password,
                key_password or password,
            )

        if not signed:
            raise RuntimeError("Failed to sign release APK with apksigner or jarsigner.")

        return aligned_path
