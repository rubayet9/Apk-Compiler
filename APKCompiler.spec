# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Paths
project_root = r'C:\Projects\Apk file maker'

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
    hooksconfig={},
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
    icon=r'C:\Projects\Apk file maker\assets\icon.ico' if os.path.exists(r'C:\Projects\Apk file maker\assets\icon.ico') else None,
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
