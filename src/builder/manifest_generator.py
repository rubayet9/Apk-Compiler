"""APK Compiler - Android Manifest Generator Module.

Dynamically generates AndroidManifest.xml according to web application settings,
permissions, hardware features, screen orientation, and theme specifications.
"""

from typing import Any, Dict, List
import xml.dom.minidom


class ManifestGenerator:
    """Generates standard-compliant AndroidManifest.xml documents."""

    # Standard permissions mapped to config keys
    OPTIONAL_PERMISSIONS = {
        "camera_permission": ["android.permission.CAMERA"],
        "audio_permission": ["android.permission.RECORD_AUDIO", "android.permission.MODIFY_AUDIO_SETTINGS"],
        "location_permission": ["android.permission.ACCESS_FINE_LOCATION", "android.permission.ACCESS_COARSE_LOCATION"],
        "storage_permission": ["android.permission.READ_EXTERNAL_STORAGE"],
    }

    def generate(self, config: Dict[str, Any]) -> str:
        """Generate AndroidManifest.xml string from configuration dictionary.

        Args:
            config: Build options dictionary containing:
                - package_name (str): e.g. "com.example.webapp"
                - app_name (str): e.g. "My Web App"
                - version_name (str): e.g. "1.0.0"
                - version_code (int): e.g. 1
                - orientation (str): "unspecified", "portrait", "landscape", etc.
                - fullscreen (bool): Whether fullscreen theme is active
                - internet_permission (bool): Enable network access
                - cleartext_traffic (bool): Enable HTTP traffic
                - permissions (list): Extra custom permissions

        Returns:
            Formatted XML string for AndroidManifest.xml.
        """
        package_name = config.get("package_name", "com.apkcompiler.app").strip()
        orientation = config.get("orientation", "unspecified")
        cleartext = "true" if config.get("cleartext_traffic", True) else "false"

        # Map orientation values to valid Android manifest values
        orientation_map = {
            "portrait": "portrait",
            "landscape": "landscape",
            "sensor": "sensor",
            "sensorPortrait": "sensorPortrait",
            "sensorLandscape": "sensorLandscape",
            "user": "user",
            "unspecified": "unspecified",
        }
        android_orientation = orientation_map.get(orientation, "unspecified")

        # Collect permissions
        permissions: List[str] = []
        if config.get("internet_permission", True):
            permissions.append("android.permission.INTERNET")
            permissions.append("android.permission.ACCESS_NETWORK_STATE")

        # Check optional permissions
        for opt_key, perms in self.OPTIONAL_PERMISSIONS.items():
            if config.get(opt_key, False):
                permissions.extend(perms)

        # Custom permissions list from config
        extra_perms = config.get("extra_permissions", [])
        if isinstance(extra_perms, list):
            permissions.extend(extra_perms)

        # Deduplicate while preserving order
        seen = set()
        dedup_permissions = []
        for p in permissions:
            if p not in seen:
                seen.add(p)
                dedup_permissions.append(p)

        # Build XML
        xml_lines = [
            '<?xml version="1.0" encoding="utf-8"?>',
            '<manifest xmlns:android="http://schemas.android.com/apk/res/android"',
            f'    package="{package_name}">',
            '',
        ]

        # Add permissions
        if dedup_permissions:
            xml_lines.append('    <!-- Application Permissions -->')
            for perm in dedup_permissions:
                xml_lines.append(f'    <uses-permission android:name="{perm}" />')
            xml_lines.append('')

        # Hardware features
        xml_lines.extend([
            '    <!-- Hardware features declaration -->',
            '    <uses-feature android:name="android.hardware.camera" android:required="false" />',
            '    <uses-feature android:name="android.hardware.location.gps" android:required="false" />',
            '',
        ])

        # Theme selection
        theme_attr = "@style/AppTheme.FullScreen" if config.get("fullscreen", False) else "@style/AppTheme"

        # Application tag
        xml_lines.extend([
            '    <application',
            '        android:allowBackup="true"',
            '        android:icon="@mipmap/ic_launcher"',
            '        android:label="@string/app_name"',
            '        android:roundIcon="@mipmap/ic_launcher_round"',
            '        android:supportsRtl="true"',
            f'        android:theme="{theme_attr}"',
            f'        android:usesCleartextTraffic="{cleartext}">',
            '',
            '        <!-- Main Web Application Activity -->',
            '        <activity',
            '            android:name=".MainActivity"',
            '            android:exported="true"',
            '            android:configChanges="orientation|screenSize|screenLayout|keyboardHidden|smallestScreenSize"',
            f'            android:screenOrientation="{android_orientation}"',
            '            android:windowSoftInputMode="adjustResize">',
            '            <intent-filter>',
            '                <action android:name="android.intent.action.MAIN" />',
            '                <category android:name="android.intent.category.LAUNCHER" />',
            '            </intent-filter>',
            '        </activity>',
            '',
            '        <!-- FileProvider for file chooser / uploads -->',
            '        <provider',
            f'            android:name="androidx.core.content.FileProvider"',
            f'            android:authorities="{package_name}.fileprovider"',
            '            android:exported="false"',
            '            android:grantUriPermissions="true">',
            '            <meta-data',
            '                android:name="android.support.FILE_PROVIDER_PATHS"',
            '                android:resource="@xml/file_paths" />',
            '        </provider>',
            '',
            '    </application>',
            '</manifest>',
        ])

        return "\n".join(xml_lines)
