"""APK Compiler - Master APK Build Orchestrator Module.

Coordinates the end-to-end conversion process:
validation -> project generation -> asset bundling -> Gradle compilation ->
zipalign & cryptographic signing -> delivery to output directory.
"""

import os
import shutil
import sys
import time
from typing import Any, Callable, Dict, Optional

from src.builder.apk_signer import APKSigner
from src.builder.gradle_runner import GradleRunner
from src.builder.icon_processor import IconProcessor
from src.builder.manifest_generator import ManifestGenerator
from src.builder.project_generator import ProjectGenerator
from src.utils.config import AppConfig, OUTPUT_DIR, get_config
from src.utils.file_utils import (
    clean_directory,
    create_temp_dir,
    format_file_size,
    get_directory_size,
    safe_filename,
    validate_web_app,
)
from src.utils.sdk_manager import SDKManager


def _find_templates_dir() -> str:
    """Locate the templates directory across development and frozen PyInstaller environments."""
    candidates = []
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        candidates.append(os.path.join(exe_dir, "templates"))
        candidates.append(os.path.join(exe_dir, "_internal", "templates"))
        if hasattr(sys, "_MEIPASS"):
            candidates.append(os.path.join(sys._MEIPASS, "templates"))
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    candidates.append(os.path.join(root_dir, "templates"))
    candidates.append(os.path.join(root_dir, "_internal", "templates"))

    for c in candidates:
        if os.path.isdir(c):
            return os.path.abspath(c)
    return os.path.join(root_dir, "templates")


class APKBuilder:
    """Master build orchestrator for converting web apps to installable Android APKs."""

    def __init__(
        self,
        config: Dict[str, Any],
        web_app_path: str,
        output_dir: Optional[str] = None,
        app_config: Optional[AppConfig] = None,
    ):
        """Initialize APKBuilder.

        Args:
            config: Build options dictionary:
                - app_name (str): Human-readable application name.
                - package_name (str): Android package name (e.g. com.example.app).
                - version_name (str): Version display string (default "1.0.0").
                - version_code (int): Version integer (default 1).
                - orientation (str): Screen orientation ("portrait", "landscape", "unspecified").
                - fullscreen (bool): Fullscreen mode.
                - status_bar_color (str): Hex color code.
                - icon_path (str, optional): Custom icon image path.
                - is_release (bool, optional): Build release APK instead of debug.
                - keystore_path (str, optional): Custom release keystore path.
                - keystore_password (str, optional): Keystore password.
                - key_alias (str, optional): Key alias.
                - key_password (str, optional): Key password.
            web_app_path: Directory containing web app files (index.html, etc.).
            output_dir: Destination directory for built APK.
            app_config: AppConfig instance.
        """
        self.app_config = app_config or get_config()
        self.raw_config = dict(config)
        self.web_app_path = os.path.abspath(web_app_path)
        self.output_dir = os.path.abspath(output_dir or self.raw_config.get("output_dir") or OUTPUT_DIR)
        self.temp_dir: Optional[str] = None
        self.gradle_runner: Optional[GradleRunner] = None
        self._cancelled = False

        # Normalize config defaults
        self._normalize_config()

    def _normalize_config(self) -> None:
        """Sanitize and populate required config values."""
        # App Name
        app_name = str(self.raw_config.get("app_name", "Web App")).strip()
        if not app_name:
            app_name = "Web App"
        self.raw_config["app_name"] = app_name

        # Package Name
        pkg = self.raw_config.get("package_name", "").strip()
        if not pkg:
            safe_name = safe_filename(app_name.lower(), "").replace(" ", "").replace("_", "")
            if not safe_name or not safe_name[0].isalpha():
                safe_name = "app"
            pkg = f"{self.app_config.get('default_package_prefix', 'com.apkcompiler.app')}.{safe_name}"
        self.raw_config["package_name"] = pkg

        # Versions
        self.raw_config["version_name"] = str(self.raw_config.get("version_name", "1.0.0")).strip()
        try:
            self.raw_config["version_code"] = int(self.raw_config.get("version_code", 1))
        except (ValueError, TypeError):
            self.raw_config["version_code"] = 1

        # Presentation
        self.raw_config["orientation"] = self.raw_config.get("orientation", "unspecified")
        self.raw_config["fullscreen"] = bool(self.raw_config.get("fullscreen", False))
        self.raw_config["status_bar_color"] = self.raw_config.get("status_bar_color", "#1E1E2E")
        self.raw_config["internet_permission"] = self.raw_config.get("internet_permission", True)
        self.raw_config["cleartext_traffic"] = self.raw_config.get("cleartext_traffic", True)

    def cancel(self) -> None:
        """Cancel ongoing APK build."""
        self._cancelled = True
        if self.gradle_runner:
            self.gradle_runner.cancel()

    def build(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Execute the complete 10-step build pipeline.

        Args:
            progress_callback: Receives (progress_percent: float, message: str).
            log_callback: Receives real-time log lines (message: str).

        Returns:
            Absolute path to final output APK.
        """
        self._cancelled = False
        start_time = time.time()

        def _log(msg: str) -> None:
            if log_callback:
                log_callback(f"[APKBuilder] {msg}")

        def _progress(pct: float, msg: str) -> None:
            if progress_callback:
                progress_callback(pct, msg)

        _log(f"Starting build for '{self.raw_config['app_name']}' ({self.raw_config['package_name']})")
        _progress(2.0, "Checking environment prerequisites...")

        # 0. Check JDK and SDK
        jdk_path = self.app_config.get_jdk_path()
        sdk_path = self.app_config.get_sdk_path()

        if not jdk_path:
            raise RuntimeError(
                "JDK 17 is not found or configured. "
                "Please configure JDK path in Settings or use SDK Manager to download OpenJDK 17."
            )
        if not sdk_path:
            raise RuntimeError(
                "Android SDK is not found or configured. "
                "Please configure SDK path in Settings or use SDK Manager to install Android SDK."
            )

        _log(f"Using JDK: {jdk_path}")
        _log(f"Using Android SDK: {sdk_path}")

        try:
            # -------------------------------------------------------------
            # Step 1: Validate web app files
            # -------------------------------------------------------------
            if self._cancelled:
                raise RuntimeError("Build cancelled.")
            _progress(5.0, "Step 1/10: Validating web application files...")
            _log(f"Validating web assets in: {self.web_app_path}")

            val_result = validate_web_app(self.web_app_path)
            if not val_result["valid"]:
                issues_str = "; ".join(val_result["issues"])
                raise ValueError(f"Invalid web application: {issues_str}")

            _log(
                f"Web app validated: {val_result['total_files']} files "
                f"({val_result['formatted_size']}), index found at {val_result['index_path']}"
            )

            # -------------------------------------------------------------
            # Step 2: Create temp build directory
            # -------------------------------------------------------------
            if self._cancelled:
                raise RuntimeError("Build cancelled.")
            _progress(10.0, "Step 2/10: Creating temporary build directory...")
            self.temp_dir = create_temp_dir(prefix="apk_build_")
            _log(f"Created temporary build directory: {self.temp_dir}")

            # -------------------------------------------------------------
            # Step 3: Project setup
            # -------------------------------------------------------------
            if self._cancelled:
                raise RuntimeError("Build cancelled.")

            is_native = bool(val_result.get("is_native_android"))
            
            if is_native:
                _progress(15.0, "Step 3/10: Preparing Google AI Studio Android project...")
                _log("Native Android project detected. Setting up Gradle environment...")
                
                # Copy native project to temp_dir (skipping local .gradle and build artifacts)
                import shutil
                project_dir = self.temp_dir
                for item in os.listdir(self.web_app_path):
                    if item in (".gradle", "build", ".idea"):
                        continue
                    s = os.path.join(self.web_app_path, item)
                    d = os.path.join(project_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".gradle", "build", ".idea"))
                    else:
                        shutil.copy2(s, d)

                # Ensure local.properties
                sdk_dir_esc = sdk_path.replace("\\", "\\\\")
                with open(os.path.join(project_dir, "local.properties"), "w", encoding="utf-8") as f:
                    f.write(f"sdk.dir={sdk_dir_esc}\n")

                # Ensure gradlew, gradlew.bat, and gradle wrapper
                templates_dir = _find_templates_dir()
                template_wrapper_dir = os.path.join(templates_dir, "android_project")
                
                for script in ["gradlew", "gradlew.bat"]:
                    src_script = os.path.join(template_wrapper_dir, script)
                    dst_script = os.path.join(project_dir, script)
                    if os.path.isfile(src_script) and not os.path.isfile(dst_script):
                        shutil.copy2(src_script, dst_script)

                proj_wrapper_dir = os.path.join(project_dir, "gradle", "wrapper")
                os.makedirs(proj_wrapper_dir, exist_ok=True)
                
                for wf in ["gradle-wrapper.jar", "gradle-wrapper.properties"]:
                    src_wf = os.path.join(template_wrapper_dir, "gradle", "wrapper", wf)
                    dst_wf = os.path.join(proj_wrapper_dir, wf)
                    if os.path.isfile(src_wf) and not os.path.isfile(dst_wf):
                        shutil.copy2(src_wf, dst_wf)

                # Ensure debug.keystore exists (required by AI Studio debug signing config)
                debug_ks = os.path.join(project_dir, "debug.keystore")
                if not os.path.isfile(debug_ks):
                    _log("Generating debug keystore for native project...")
                    keytool_path = os.path.join(jdk_path, "bin", "keytool.exe" if sys.platform == "win32" else "keytool")
                    if os.path.isfile(keytool_path):
                        import subprocess
                        creationflags = 0x08000000 if sys.platform == "win32" else 0
                        subprocess.run([
                            keytool_path, "-genkey", "-v",
                            "-keystore", debug_ks,
                            "-storepass", "android",
                            "-alias", "androiddebugkey",
                            "-keypass", "android",
                            "-keyalg", "RSA",
                            "-keysize", "2048",
                            "-validity", "10000",
                            "-dname", "CN=Android Debug,O=Android,C=US"
                        ], capture_output=True, creationflags=creationflags)

                # Inject high-performance Gradle build settings for fast compilation
                props_file = os.path.join(project_dir, "gradle.properties")
                props_lines = []
                existing_keys = set()
                if os.path.isfile(props_file):
                    try:
                        with open(props_file, "r", encoding="utf-8") as pf:
                            props_lines = pf.readlines()
                            for pl in props_lines:
                                sline = pl.strip()
                                if sline and not sline.startswith("#") and "=" in sline:
                                    k = sline.split("=", 1)[0].strip()
                                    existing_keys.add(k)
                    except Exception:
                        props_lines = []

                optimizations = {
                    "org.gradle.jvmargs": "-Xmx2560m -XX:+UseParallelGC -Dfile.encoding=UTF-8",
                    "org.gradle.parallel": "true",
                    "org.gradle.caching": "true",
                    "org.gradle.vfs.watch": "true",
                    "android.useAndroidX": "true",
                    "android.enableJetifier": "false",
                    "kotlin.incremental": "true",
                }

                updated_lines = []
                for line in props_lines:
                    sline = line.strip()
                    if sline and not sline.startswith("#") and "=" in sline:
                        k = sline.split("=", 1)[0].strip()
                        if k in optimizations:
                            updated_lines.append(f"{k}={optimizations[k]}\n")
                            continue
                    updated_lines.append(line)

                for k, v in optimizations.items():
                    if k not in existing_keys:
                        updated_lines.append(f"{k}={v}\n")

                try:
                    with open(props_file, "w", encoding="utf-8") as pf:
                        pf.writelines(updated_lines)
                    _log("Injected high-performance build parameters (parallel, caching, 2.5GB JVM).")
                except Exception as pe:
                    _log(f"Note updating gradle.properties: {pe}")

                _log("Native Android project environment configured.")
            else:
                _progress(15.0, "Step 3/10: Generating Android project structure...")
                _log("Generating Gradle build files and project structure from Web App...")

                project_config = dict(self.raw_config)
                project_config["web_app_dir"] = self.web_app_path
                project_config["sdk_path"] = sdk_path
                project_config["jdk_path"] = jdk_path

                proj_gen = ProjectGenerator(config=self.app_config)
                project_dir = proj_gen.generate_project(self.temp_dir, project_config)
                _log(f"Generated Android project files in: {project_dir}")

                # Step 4: Process icons
                _progress(25.0, "Step 4/10: Processing launcher icons...")
                app_res_dir = os.path.join(project_dir, "app", "src", "main", "res")
                icon_path = self.raw_config.get("icon_path")

                try:
                    icon_processor = IconProcessor()
                    if icon_path and os.path.isfile(icon_path):
                        _log(f"Processing custom icon: {icon_path}")
                        icon_processor.process_icon(icon_path, app_res_dir)
                        icon_processor.create_round_icon(icon_path, app_res_dir)
                    else:
                        _log("Generating modern default launcher icon...")
                        icon_processor.create_default_icon(app_res_dir, self.raw_config["app_name"])
                except Exception as e:
                    _log(f"Warning: Icon processing note: {e}")

                # Step 5: Manifest verification
                _progress(30.0, "Step 5/10: Verifying Android manifest and permissions...")
                manifest_path = os.path.join(project_dir, "app", "src", "main", "AndroidManifest.xml")
                if not os.path.isfile(manifest_path):
                    manifest_gen = ManifestGenerator()
                    with open(manifest_path, "w", encoding="utf-8") as f:
                        f.write(manifest_gen.generate(project_config))
                _log("AndroidManifest.xml verified.")

                # Step 6: Verify assets
                _progress(35.0, "Step 6/10: Verifying bundled web application assets...")
                assets_dir = os.path.join(project_dir, "app", "src", "main", "assets", "www")
                assets_size = get_directory_size(assets_dir)
                _log(f"Bundled web assets size: {format_file_size(assets_size)}")

            # -------------------------------------------------------------
            # Step 7: Run Gradle build
            # -------------------------------------------------------------
            if self._cancelled:
                raise RuntimeError("Build cancelled.")
            _progress(40.0, "Step 7/10: Running Gradle build...")

            is_release = bool(self.raw_config.get("is_release", False))
            self.gradle_runner = GradleRunner(project_dir, jdk_path=jdk_path, sdk_path=sdk_path)

            def _gradle_progress(pct: float, task_name: str) -> None:
                # Map 0-100% of gradle build to 40-85% overall
                mapped = 40.0 + (pct / 100.0) * 45.0
                _progress(mapped, f"Step 7/10: [Gradle] {task_name}")

            _log(f"Executing Gradle build (release mode: {is_release})...")
            if is_release:
                raw_apk = self.gradle_runner.build_release(
                    progress_callback=_gradle_progress,
                    log_callback=log_callback,
                )
            else:
                raw_apk = self.gradle_runner.build_debug(
                    progress_callback=_gradle_progress,
                    log_callback=log_callback,
                )

            _log(f"Gradle build completed successfully. APK: {raw_apk}")

            # -------------------------------------------------------------
            # Step 8: Sign and Align APK
            # -------------------------------------------------------------
            if self._cancelled:
                raise RuntimeError("Build cancelled.")
            _progress(88.0, "Step 8/10: Signing and aligning APK package...")

            signer = APKSigner(jdk_path=jdk_path, sdk_path=sdk_path, config=self.app_config)
            signed_apk = raw_apk

            keystore_path = self.raw_config.get("keystore_path")
            if is_release and keystore_path and os.path.isfile(keystore_path):
                _log(f"Signing with release keystore: {keystore_path}")
                alias = self.raw_config.get("key_alias", "")
                ks_pass = self.raw_config.get("keystore_password", "")
                key_pass = self.raw_config.get("key_password", ks_pass)

                signed_apk = signer.sign_release(
                    raw_apk,
                    keystore_path=keystore_path,
                    alias=alias,
                    password=ks_pass,
                    key_password=key_pass,
                )
            else:
                _log("Signing with debug keystore...")
                try:
                    signed_apk = signer.sign_debug(raw_apk)
                except Exception as sign_err:
                    _log(f"Note on debug signing: {sign_err}. Proceeding with built APK.")
                    signed_apk = raw_apk

            _log(f"APK signing & alignment completed: {signed_apk}")

            # -------------------------------------------------------------
            # Step 9: Copy final APK to output directory
            # -------------------------------------------------------------
            if self._cancelled:
                raise RuntimeError("Build cancelled.")
            _progress(95.0, "Step 9/10: Copying final APK to output directory...")

            os.makedirs(self.output_dir, exist_ok=True)
            app_clean_name = safe_filename(self.raw_config["app_name"])
            version_str = safe_filename(self.raw_config["version_name"])
            mode_suffix = "release" if is_release else "debug"
            final_apk_name = f"{app_clean_name}-v{version_str}-{mode_suffix}.apk"
            final_apk_path = os.path.join(self.output_dir, final_apk_name)

            shutil.copy2(signed_apk, final_apk_path)
            apk_size = os.path.getsize(final_apk_path)
            _log(f"Final APK copied to: {final_apk_path} ({format_file_size(apk_size)})")

            # -------------------------------------------------------------
            # Step 10: Clean up temporary files
            # -------------------------------------------------------------
            _progress(98.0, "Step 10/10: Cleaning up build artifacts...")
            if self.app_config.get("auto_clean_temp", True) and self.temp_dir:
                try:
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                    _log(f"Cleaned up temp directory: {self.temp_dir}")
                except Exception as clean_err:
                    _log(f"Warning cleaning temp dir: {clean_err}")

            duration = time.time() - start_time
            _progress(100.0, f"Build complete in {duration:.1f}s! APK: {final_apk_name}")
            _log(f"Build successfully finished in {duration:.2f} seconds.")

            return os.path.abspath(final_apk_path)

        except Exception as err:
            _log(f"Build error: {err}")
            # Clean up temp if needed
            if self.temp_dir and self.app_config.get("auto_clean_temp", True):
                try:
                    shutil.rmtree(self.temp_dir, ignore_errors=True)
                except Exception:
                    pass
            raise
