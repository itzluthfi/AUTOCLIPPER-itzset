# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for YT Short Clipper - macOS (.app bundle)

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect OpenCV data (haar cascades)
opencv_data = collect_data_files('cv2')

# Icon path (macOS uses .icns)
icon_path = 'assets/icon.icns' if os.path.exists('assets/icon.icns') else None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        *opencv_data,
        ('assets', 'assets'),
        ('clipper_core.py', '.'),
        ('youtube_uploader.py', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        '_tkinter',
        'customtkinter',
        'openai',
        'cv2',
        'numpy',
        'PIL',
        'PIL._tkinter_finder',
        'google.oauth2.credentials',
        'google_auth_oauthlib.flow',
        'googleapiclient.discovery',
        'googleapiclient.http',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'torch',
        'tensorflow',
        'whisper',
    ],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YTShortClipper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX not recommended on macOS
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,  # Required for macOS .app bundles
    target_arch=None,  # Use native arch (set to 'universal2' only with universal2 Python from python.org)
    codesign_identity=None,  # Set to your Developer ID for distribution
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='YTShortClipper',
)

app = BUNDLE(
    coll,
    name='YTShortClipper.app',
    icon=icon_path,
    bundle_identifier='org.ytclip.ytshortclipper',
    info_plist={
        'CFBundleName': 'YT Short Clipper',
        'CFBundleDisplayName': 'YT Short Clipper',
        'CFBundleShortVersionString': '0.0.19',
        'CFBundleVersion': '0.0.19',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        'LSMinimumSystemVersion': '10.15',  # macOS Catalina minimum
        'NSMicrophoneUsageDescription': 'YT Short Clipper needs microphone access for audio processing.',
        'NSAppleEventsUsageDescription': 'YT Short Clipper needs automation access.',
    },
)
