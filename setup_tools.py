"""
APK Compiler - Tools Setup Script
Downloads and configures JDK and Android SDK for first-time setup.
Can be run standalone or called from the main application.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import AppConfig
from src.utils.sdk_manager import SDKManager


def print_progress(message, percent=None):
    """Print progress to console."""
    if percent is not None:
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\r  [{bar}] {percent:.0f}% - {message}", end='', flush=True)
    else:
        print(f"\n  {message}")


def main():
    print("=" * 60)
    print("  APK Compiler - Tools Setup")
    print("=" * 60)
    print()

    config = AppConfig()
    config.ensure_dirs()
    sdk_manager = SDKManager(config)

    # Check JDK
    print("[1/3] Checking JDK...")
    jdk_path = sdk_manager.check_jdk()
    if jdk_path:
        print(f"  ✅ JDK found at: {jdk_path}")
    else:
        print("  ❌ JDK not found. Downloading...")
        try:
            sdk_manager.download_jdk(print_progress)
            print("\n  ✅ JDK installed successfully!")
        except Exception as e:
            print(f"\n  ❌ JDK installation failed: {e}")
            return False

    # Check Android SDK
    print("\n[2/3] Checking Android SDK...")
    sdk_path = sdk_manager.check_sdk()
    if sdk_path:
        print(f"  ✅ Android SDK found at: {sdk_path}")
    else:
        print("  ❌ Android SDK not found. Downloading...")
        try:
            sdk_manager.download_sdk(print_progress)
            print("\n  ✅ Android SDK downloaded!")
        except Exception as e:
            print(f"\n  ❌ SDK download failed: {e}")
            return False

    # Setup SDK components
    print("\n[3/3] Setting up SDK components...")
    try:
        sdk_manager.setup_sdk(print_progress)
        print("\n  ✅ SDK components installed!")
    except Exception as e:
        print(f"\n  ❌ SDK setup failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("  ✅ All tools are ready!")
    print("  You can now run APK Compiler.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

