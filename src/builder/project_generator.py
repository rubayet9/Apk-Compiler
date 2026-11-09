"""APK Compiler - Android Project Generator Module.

Assembles a complete, self-contained, and buildable Android Gradle project
from templates, customized with application metadata, web assets, icons,
and native WebView wrapping code.
"""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from src.builder.icon_processor import IconProcessor
from src.builder.manifest_generator import ManifestGenerator
from src.builder.web_app_wrapper import WebAppWrapper
from src.utils.config import AppConfig, get_config
from src.utils.file_utils import copy_directory


class ProjectGenerator:
    """Generates complete Android Studio / Gradle projects ready for compilation."""

    def __init__(self, templates_dir: Optional[str] = None, config: Optional[AppConfig] = None):
        self.config_manager = config or get_config()
        self.manifest_gen = ManifestGenerator()
        self.wrapper_gen = WebAppWrapper()

        if templates_dir and os.path.isdir(templates_dir):
            self.templates_dir = templates_dir
        else:
            # Check frozen / app / source candidates
            candidates = []
            if getattr(sys, "frozen", False):
                exe_dir = os.path.dirname(sys.executable)
                candidates.append(os.path.join(exe_dir, "templates", "android_project"))
                candidates.append(os.path.join(exe_dir, "_internal", "templates", "android_project"))
                if hasattr(sys, "_MEIPASS"):
                    candidates.append(os.path.join(sys._MEIPASS, "templates", "android_project"))
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            candidates.append(os.path.join(base, "templates", "android_project"))
            candidates.append(os.path.join(base, "_internal", "templates", "android_project"))

            matched = ""
            for cand in candidates:
                if os.path.isdir(cand):
                    matched = os.path.abspath(cand)
                    break
            self.templates_dir = matched

    def _read_template_or_default(self, rel_path: str, default_content: str) -> str:
        """Read template file from templates directory, or fallback to default string."""
        if self.templates_dir:
            full_path = os.path.join(self.templates_dir, rel_path)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        return f.read()
                except OSError:
                    pass
        return default_content

    def _replace_placeholders(self, text: str, replacements: Dict[str, str]) -> str:
        """Replace all {{KEY}} tokens in template text."""
        result = text
        for key, value in replacements.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def generate_project(self, output_dir: str, config: Dict[str, Any]) -> str:
        """Generate a complete Android Gradle project.

        Args:
            output_dir: Target directory where project will be generated.
            config: Build options dictionary containing:
                - app_name: Name of the application
                - package_name: Application ID / Package name
                - version_name: Version display string (e.g. "1.0.0")
                - version_code: Version integer (e.g. 1)
                - orientation: Screen orientation
                - fullscreen: Fullscreen mode boolean
                - status_bar_color: Hex color string
                - web_app_dir: Path to directory containing web files
                - icon_path: Path to custom icon file (optional)

        Returns:
            Absolute path to generated project directory.
        """
        os.makedirs(output_dir, exist_ok=True)

        app_name = config.get("app_name", "Web App").strip()
        package_name = config.get("package_name", "com.apkcompiler.app").strip()
        version_name = str(config.get("version_name", "1.0.0")).strip()
        version_code = int(config.get("version_code", 1))
        status_bar_color = config.get("status_bar_color", "#1E1E2E")
        sdk_path = config.get("sdk_path") or self.config_manager.get_sdk_path() or ""

        # Placeholders mapping
        placeholders = {
            "APP_NAME": app_name,
            "PACKAGE_NAME": package_name,
            "VERSION_NAME": version_name,
            "VERSION_CODE": str(version_code),
            "STATUS_BAR_COLOR": status_bar_color,
        }

        # 1. Project-level build.gradle
        proj_build_gradle = self._read_template_or_default(
            "build.gradle",
            """buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:8.1.0'
    }
}
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
tasks.register('clean', Delete) {
    delete rootProject.buildDir
}
""",
        )
        with open(os.path.join(output_dir, "build.gradle"), "w", encoding="utf-8") as f:
            f.write(self._replace_placeholders(proj_build_gradle, placeholders))

        # 2. settings.gradle
        settings_gradle = self._read_template_or_default(
            "settings.gradle",
            """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "{{APP_NAME}}"
include ':app'
""",
        )
        with open(os.path.join(output_dir, "settings.gradle"), "w", encoding="utf-8") as f:
            f.write(self._replace_placeholders(settings_gradle, placeholders))

        # 3. gradle.properties (High-Performance settings)
        gradle_props = self._read_template_or_default(
            "gradle.properties",
            """org.gradle.jvmargs=-Xmx2560m -XX:+UseParallelGC -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.vfs.watch=true
android.useAndroidX=true
android.enableJetifier=false
android.nonTransitiveRClass=true
kotlin.incremental=true
""",
        )
        with open(os.path.join(output_dir, "gradle.properties"), "w", encoding="utf-8") as f:
            f.write(self._replace_placeholders(gradle_props, placeholders))

        # 4. local.properties (specifying sdk.dir with forward slashes)
        if sdk_path:
            norm_sdk_path = sdk_path.replace("\\", "/")
            with open(os.path.join(output_dir, "local.properties"), "w", encoding="utf-8") as f:
                f.write(f"sdk.dir={norm_sdk_path}\n")

        # 5. Gradle wrapper files
        wrapper_dir = os.path.join(output_dir, "gradle", "wrapper")
        os.makedirs(wrapper_dir, exist_ok=True)
        wrapper_props = self._read_template_or_default(
            os.path.join("gradle", "wrapper", "gradle-wrapper.properties"),
            """distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
""",
        )
        with open(os.path.join(wrapper_dir, "gradle-wrapper.properties"), "w", encoding="utf-8") as f:
            f.write(wrapper_props)

        # Copy gradlew & gradlew.bat if available in templates
        if self.templates_dir:
            for g_file in ["gradlew", "gradlew.bat"]:
                src_g = os.path.join(self.templates_dir, g_file)
                if os.path.isfile(src_g):
                    shutil.copy2(src_g, os.path.join(output_dir, g_file))

        # 6. App module directory structure
        app_dir = os.path.join(output_dir, "app")
        app_main_dir = os.path.join(app_dir, "src", "main")
        app_res_dir = os.path.join(app_main_dir, "res")
        app_assets_www = os.path.join(app_main_dir, "assets", "www")

        os.makedirs(app_res_dir, exist_ok=True)
        os.makedirs(app_assets_www, exist_ok=True)

        # 7. app/build.gradle
        app_build_gradle = self._read_template_or_default(
            os.path.join("app", "build.gradle"),
            """plugins {
    id 'com.android.application'
}
android {
    namespace '{{PACKAGE_NAME}}'
    compileSdk 34
    defaultConfig {
        applicationId '{{PACKAGE_NAME}}'
        minSdk 21
        targetSdk 34
        versionCode {{VERSION_CODE}}
        versionName '{{VERSION_NAME}}'
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.webkit:webkit:1.8.0'
    implementation 'androidx.core:core:1.12.0'
}
""",
        )
        with open(os.path.join(app_dir, "build.gradle"), "w", encoding="utf-8") as f:
            f.write(self._replace_placeholders(app_build_gradle, placeholders))

        # 8. Resources: layout, values, xml
        layout_dir = os.path.join(app_res_dir, "layout")
        values_dir = os.path.join(app_res_dir, "values")
        xml_dir = os.path.join(app_res_dir, "xml")
        os.makedirs(layout_dir, exist_ok=True)
        os.makedirs(values_dir, exist_ok=True)
        os.makedirs(xml_dir, exist_ok=True)

        # layout/activity_main.xml
        layout_content = self._read_template_or_default(
            os.path.join("app", "src", "main", "res", "layout", "activity_main.xml"),
            """<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="#000000">
    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
    <FrameLayout
        android:id="@+id/customViewContainer"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:background="#000000"
        android:visibility="gone" />
</FrameLayout>
""",
        )
        with open(os.path.join(layout_dir, "activity_main.xml"), "w", encoding="utf-8") as f:
            f.write(layout_content)

        # values/strings.xml
        strings_content = self._read_template_or_default(
            os.path.join("app", "src", "main", "res", "values", "strings.xml"),
            """<resources>
    <string name="app_name">{{APP_NAME}}</string>
</resources>
""",
        )
        with open(os.path.join(values_dir, "strings.xml"), "w", encoding="utf-8") as f:
            f.write(self._replace_placeholders(strings_content, placeholders))

        # values/colors.xml
        colors_content = self._read_template_or_default(
            os.path.join("app", "src", "main", "res", "values", "colors.xml"),
            """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="colorPrimary">#4361EE</color>
    <color name="colorPrimaryDark">#3A0CA3</color>
    <color name="colorAccent">#4CC9F0</color>
    <color name="statusBarColor">{{STATUS_BAR_COLOR}}</color>
</resources>
""",
        )
        with open(os.path.join(values_dir, "colors.xml"), "w", encoding="utf-8") as f:
            f.write(self._replace_placeholders(colors_content, placeholders))

        # values/styles.xml
        styles_content = self._read_template_or_default(
            os.path.join("app", "src", "main", "res", "values", "styles.xml"),
            """<resources>
    <style name="AppTheme" parent="Theme.AppCompat.Light.NoActionBar">
        <item name="colorPrimary">@color/colorPrimary</item>
        <item name="colorPrimaryDark">@color/colorPrimaryDark</item>
        <item name="colorAccent">@color/colorAccent</item>
        <item name="android:statusBarColor">@color/statusBarColor</item>
        <item name="android:windowNoTitle">true</item>
        <item name="android:windowActionBar">false</item>
    </style>
    <style name="AppTheme.FullScreen" parent="AppTheme">
        <item name="android:windowFullscreen">true</item>
        <item name="android:windowContentOverlay">@null</item>
    </style>
</resources>
""",
        )
        with open(os.path.join(values_dir, "styles.xml"), "w", encoding="utf-8") as f:
            f.write(styles_content)

        # xml/file_paths.xml
        file_paths_xml = self.wrapper_gen.generate_file_provider_paths()
        with open(os.path.join(xml_dir, "file_paths.xml"), "w", encoding="utf-8") as f:
            f.write(file_paths_xml)

        # 9. AndroidManifest.xml
        manifest_xml = self.manifest_gen.generate(config)
        with open(os.path.join(app_main_dir, "AndroidManifest.xml"), "w", encoding="utf-8") as f:
            f.write(manifest_xml)

        # 10. Java MainActivity
        pkg_parts = package_name.split(".")
        java_pkg_dir = os.path.join(app_main_dir, "java", *pkg_parts)
        os.makedirs(java_pkg_dir, exist_ok=True)

        main_activity_code = self.wrapper_gen.generate_main_activity(package_name, config)
        with open(os.path.join(java_pkg_dir, "MainActivity.java"), "w", encoding="utf-8") as f:
            f.write(main_activity_code)

        # 11. App Icons
        try:
            icon_proc = IconProcessor()
            custom_icon = config.get("icon_path")
            if custom_icon and os.path.isfile(custom_icon):
                icon_proc.process_icon(custom_icon, app_res_dir)
                icon_proc.create_round_icon(custom_icon, app_res_dir)
            else:
                icon_proc.create_default_icon(app_res_dir, app_name)
        except Exception as icon_err:
            # Fallback if image generation encounters issue
            pass

        # 12. Copy Web Assets to app/src/main/assets/www/
        web_app_dir = config.get("web_app_dir")
        if web_app_dir and os.path.isdir(web_app_dir):
            copy_directory(web_app_dir, app_assets_www, overwrite=True)
        else:
            # Copy default placeholder index.html if assets directory is empty
            if not os.path.isfile(os.path.join(app_assets_www, "index.html")):
                placeholder_html = self._read_template_or_default(
                    os.path.join("app", "src", "main", "assets", "www", "index.html"),
                    "<!DOCTYPE html><html><body><h1>{{APP_NAME}}</h1></body></html>",
                )
                with open(os.path.join(app_assets_www, "index.html"), "w", encoding="utf-8") as f:
                    f.write(self._replace_placeholders(placeholder_html, placeholders))

        return os.path.abspath(output_dir)
