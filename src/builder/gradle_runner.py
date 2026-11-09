"""APK Compiler - Gradle Build Runner Module.

Executes Gradle tasks (assembleDebug, assembleRelease) via Gradle wrapper or system Gradle,
streams build output in real time, tracks progress, and locates generated APK binaries.
"""

import os
import re
import shutil
import subprocess
import sys
import threading
from typing import Callable, Optional


class GradleRunner:
    """Manages execution of Gradle builds with streaming output and progress reporting."""

    # Key Gradle lifecycle task milestones for progress estimation
    TASK_WEIGHTS = {
        "preBuild": 15.0,
        "generateDebugBuildConfig": 20.0,
        "generateReleaseBuildConfig": 20.0,
        "processDebugManifest": 30.0,
        "processReleaseManifest": 30.0,
        "mergeDebugResources": 40.0,
        "mergeReleaseResources": 40.0,
        "processDebugResources": 55.0,
        "processReleaseResources": 55.0,
        "compileDebugJavaWithJavac": 70.0,
        "compileReleaseJavaWithJavac": 70.0,
        "dexBuilderDebug": 80.0,
        "dexBuilderRelease": 80.0,
        "mergeProjectDexDebug": 85.0,
        "mergeProjectDexRelease": 85.0,
        "packageDebug": 92.0,
        "packageRelease": 92.0,
        "assembleDebug": 98.0,
        "assembleRelease": 98.0,
    }

    def __init__(self, project_dir: str, jdk_path: Optional[str] = None, sdk_path: Optional[str] = None):
        self.project_dir = os.path.abspath(project_dir)
        self.jdk_path = jdk_path
        self.sdk_path = sdk_path
        self.process: Optional[subprocess.Popen] = None
        self._cancelled = False

    def cancel(self) -> None:
        """Cancel running build process."""
        self._cancelled = True
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.kill()
            except Exception:
                pass

    def _resolve_gradle_cmd(self) -> list:
        """Find Gradle executable: gradlew.bat, gradlew, or system gradle."""
        is_windows = sys.platform == "win32"
        wrapper_name = "gradlew.bat" if is_windows else "gradlew"
        wrapper_path = os.path.join(self.project_dir, wrapper_name)

        if os.path.isfile(wrapper_path):
            if not is_windows:
                # Ensure executable bit on Unix
                try:
                    os.chmod(wrapper_path, 0o755)
                except OSError:
                    pass
            return [wrapper_path]

        # Check system gradle
        sys_gradle = shutil.which("gradle")
        if sys_gradle:
            return [sys_gradle]

        raise FileNotFoundError(
            f"Gradle wrapper not found at '{wrapper_path}' and no 'gradle' found in system PATH."
        )

    def _prepare_environment(self) -> dict:
        """Build process environment with JAVA_HOME, ANDROID_HOME, and PATH."""
        env = os.environ.copy()

        if self.jdk_path and os.path.isdir(self.jdk_path):
            env["JAVA_HOME"] = self.jdk_path
            jdk_bin = os.path.join(self.jdk_path, "bin")
            env["PATH"] = jdk_bin + os.pathsep + env.get("PATH", "")

        if self.sdk_path and os.path.isdir(self.sdk_path):
            env["ANDROID_HOME"] = self.sdk_path
            env["ANDROID_SDK_ROOT"] = self.sdk_path

        # High performance gradle options: enable daemon with 5-minute idle timeout, UTF-8, parallel GC, memory tuning
        env["GRADLE_OPTS"] = (
            "-Dfile.encoding=UTF-8 "
            "-Dorg.gradle.daemon=true "
            "-Dorg.gradle.daemon.idletimeout=300000 "
            "-Dorg.gradle.parallel=true "
            "-Dorg.gradle.caching=true "
            "-Dorg.gradle.vfs.watch=true "
            "-Dorg.gradle.jvmargs=\"-Xmx2560m -XX:+UseParallelGC -Dfile.encoding=UTF-8\""
        )
        return env

    def _parse_task_name(self, line: str) -> Optional[str]:
        """Extract Gradle task name from output line (e.g. '> Task :app:compileDebugJavaWithJavac')."""
        match = re.search(r"> Task :app:(\w+)", line)
        if match:
            return match.group(1)
        match_simple = re.search(r":app:(\w+)", line)
        if match_simple:
            return match_simple.group(1)
        return None

    def _find_output_apk(self, build_type: str) -> Optional[str]:
        """Locate generated APK file in app/build/outputs/apk/<build_type>/."""
        apk_dir = os.path.join(self.project_dir, "app", "build", "outputs", "apk", build_type)
        if os.path.isdir(apk_dir):
            for file_name in os.listdir(apk_dir):
                if file_name.endswith(".apk"):
                    return os.path.join(apk_dir, file_name)

        # Fallback recursive search inside app/build/outputs/apk/
        base_apk_dir = os.path.join(self.project_dir, "app", "build", "outputs", "apk")
        if os.path.isdir(base_apk_dir):
            for root, _, files in os.walk(base_apk_dir):
                for f in files:
                    if f.endswith(".apk") and (build_type in f.lower() or build_type in root.lower()):
                        return os.path.join(root, f)
            # Any APK found
            for root, _, files in os.walk(base_apk_dir):
                for f in files:
                    if f.endswith(".apk"):
                        return os.path.join(root, f)

        return None

    def _execute_gradle(
        self,
        task: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Run Gradle with task argument and stream real-time output.

        Args:
            task: Gradle task (e.g. "assembleDebug", "assembleRelease").
            progress_callback: Callback receiving (percentage, message).
            log_callback: Callback receiving raw stdout/stderr lines.

        Returns:
            Path to generated APK file.
        """
        self._cancelled = False
        cmd = self._resolve_gradle_cmd()
        cmd.append(task)
        cmd.append("--build-cache")
        cmd.append("--parallel")
        cmd.append("--daemon")
        cmd.append("--watch-fs")
        cmd.append("--stacktrace")

        env = self._prepare_environment()

        if log_callback:
            log_callback(f"Starting build: {' '.join(cmd)}")
            log_callback(f"Working directory: {self.project_dir}")
            if self.jdk_path:
                log_callback(f"Using JAVA_HOME: {self.jdk_path}")
            if self.sdk_path:
                log_callback(f"Using ANDROID_HOME: {self.sdk_path}")

        if progress_callback:
            progress_callback(5.0, f"Initializing Gradle task: {task}...")

        creationflags = 0
        if sys.platform == "win32":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        self.process = subprocess.Popen(
            cmd,
            cwd=self.project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
            creationflags=creationflags,
        )

        last_progress = 5.0
        current_task_desc = "Building..."

        try:
            assert self.process.stdout is not None
            for raw_line in iter(self.process.stdout.readline, ""):
                if self._cancelled:
                    raise RuntimeError("Build process was cancelled by user.")

                line = raw_line.rstrip()
                if not line:
                    continue

                if log_callback:
                    log_callback(line)

                # Track progress based on task execution
                task_name = self._parse_task_name(line)
                if task_name and task_name in self.TASK_WEIGHTS:
                    last_progress = max(last_progress, self.TASK_WEIGHTS[task_name])
                    current_task_desc = f"Executing {task_name}..."
                    if progress_callback:
                        progress_callback(last_progress, current_task_desc)

                # Catch BUILD SUCCESSFUL / FAILED
                if "BUILD SUCCESSFUL" in line:
                    last_progress = 98.0
                    if progress_callback:
                        progress_callback(last_progress, "Build successful! Finalizing APK...")
                elif "BUILD FAILED" in line:
                    if progress_callback:
                        progress_callback(last_progress, "Build failed.")

            self.process.wait()
            return_code = self.process.returncode

            if self._cancelled:
                raise RuntimeError("Build was cancelled.")

            if return_code != 0:
                raise RuntimeError(
                    f"Gradle build failed with exit code {return_code}. Check build logs for details."
                )

            # Determine build type (debug or release)
            build_type = "release" if "release" in task.lower() else "debug"
            apk_path = self._find_output_apk(build_type)

            if not apk_path or not os.path.isfile(apk_path):
                raise FileNotFoundError(
                    f"Build completed, but output APK was not found in project '{self.project_dir}'."
                )

            if progress_callback:
                progress_callback(100.0, f"APK generated: {os.path.basename(apk_path)}")

            if log_callback:
                log_callback(f"Successfully generated APK: {apk_path}")

            return os.path.abspath(apk_path)

        finally:
            self.process = None

    def build_debug(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Run Gradle assembleDebug to generate debug APK.

        Returns:
            Path to generated debug APK file.
        """
        return self._execute_gradle("assembleDebug", progress_callback, log_callback)

    def build_release(
        self,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Run Gradle assembleRelease to generate release APK.

        Returns:
            Path to generated release APK file.
        """
        return self._execute_gradle("assembleRelease", progress_callback, log_callback)
