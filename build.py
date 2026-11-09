"""
APK Compiler - PyInstaller Build Script
Packages the application into a standalone .exe file.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build_temp"
ICON_PATH = PROJECT_ROOT / "assets" / "icon.ico"


def create_spec_file():
    """Create PyInstaller spec file."""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Paths
project_root = r'{PROJECT_ROOT}'

a = Analysis(
    [os.path.join(project_root, 'main.py')],
    pathex=[project_root],
    binaries=[],
    datas=[
        (os.path.join(project_root, 'templates'), 'templates'),
        (os.path.join(project_root, 'assets'), 'assets'),
    ],
    hiddenimports=[
        'src.utils.win_drop',
        'customtkinter',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL.ImageFilter',
        'src',
        'src.app',
        'src.ui',
        'src.ui.theme',
        'src.ui.components',
        'src.ui.main_window',
        'src.ui.welcome_page',
        'src.ui.upload_page',
        'src.ui.config_page',
        'src.ui.build_page',
        'src.ui.result_page',
        'src.ui.settings_page',
        'src.builder',
        'src.builder.apk_builder',
        'src.builder.project_generator',
        'src.builder.icon_processor',
        'src.builder.manifest_generator',
        'src.builder.gradle_runner',
        'src.builder.apk_signer',
        'src.builder.web_app_wrapper',
        'src.utils',
        'src.utils.config',
        'src.utils.file_utils',
        'src.utils.sdk_manager',
        'src.utils.i18n',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='APK Compiler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{ICON_PATH}' if os.path.exists(r'{ICON_PATH}') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='APK Compiler',
)
'''
    spec_path = PROJECT_ROOT / "APKCompiler.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    return spec_path


def create_or_update_desktop_shortcut(target_exe: Path, icon_file: Path):
    """Create or update Desktop shortcut to APK Compiler."""
    try:
        desktop = Path(os.environ.get("USERPROFILE", "")) / "Desktop"
        if not desktop.is_dir():
            return

        # Remove old shortcut if exists
        old_shortcut = desktop / "APK Builder Pro.lnk"
        if old_shortcut.is_file():
            try:
                old_shortcut.unlink()
            except Exception:
                pass

        new_shortcut = desktop / "APK Compiler.lnk"
        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{new_shortcut}")
$Shortcut.TargetPath = "{target_exe}"
$Shortcut.WorkingDirectory = "{target_exe.parent}"
$Shortcut.IconLocation = "{icon_file},0"
$Shortcut.Description = "APK Compiler - Web & Native Android Compiler"
$Shortcut.Save()
'''
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, check=False)
        print(f"  ✅ Desktop shortcut created: {new_shortcut}")
    except Exception as e:
        print(f"  ⚠️ Warning creating desktop shortcut: {e}")


def build_exe():
    """Build the .exe using PyInstaller."""
    print("=" * 60)
    print("  APK Compiler - Building .exe")
    print("=" * 60)
    print()

    # Create spec file
    print("[1/4] Creating build configuration...")
    spec_path = create_spec_file()
    print(f"  ✅ Spec file created: {spec_path}")

    # Clean previous builds
    print("\n[2/4] Cleaning previous builds...")
    dist_app_dir = DIST_DIR / "APK Compiler"
    dist_internal = dist_app_dir / "_internal"
    dist_exe = dist_app_dir / "APK Compiler.exe"

    if dist_internal.exists():
        shutil.rmtree(dist_internal, ignore_errors=True)
    if dist_exe.exists():
        try:
            dist_exe.unlink()
        except Exception:
            pass

    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
    print("  ✅ Clean complete")

    # Run PyInstaller
    print("\n[3/4] Building executable (this may take a few minutes)...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(spec_path),
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--noconfirm",
    ]

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=False)

    if result.returncode == 0:
        exe_path = DIST_DIR / "APK Compiler" / "APK Compiler.exe"
        
        # Ensure templates exist in dist
        templates_src = PROJECT_ROOT / "templates"
        templates_dest = DIST_DIR / "APK Compiler" / "templates"
        if templates_src.exists():
            shutil.copytree(str(templates_src), str(templates_dest), dirs_exist_ok=True)

        # Bundle tools (JDK & Android SDK) if available
        tools_src = PROJECT_ROOT / "tools"
        tools_dest = DIST_DIR / "APK Compiler" / "tools"
        if tools_src.exists() and not tools_dest.exists():
            print("\n[4/4] Bundling JDK and Android SDK tools into distribution...")
            try:
                shutil.copytree(str(tools_src), str(tools_dest))
                print("  ✅ Tools successfully bundled with .exe!")
            except Exception as e:
                print(f"  ⚠️ Warning bundling tools: {e}")

        # Update desktop shortcut
        create_or_update_desktop_shortcut(exe_path, ICON_PATH)

        print("\n" + "=" * 60)
        print("  ✅ Build successful!")
        print(f"  📂 Output: {exe_path}")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("  ❌ Build failed!")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)

