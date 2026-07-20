# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for YT Short Clipper Desktop App

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect OpenCV data (haar cascades)
opencv_data = collect_data_files('cv2')

# Icon path
icon_path = 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[
        # Bundle yt-dlp executable
        (r'C:\Users\jipra\AppData\Local\Programs\Python\Python313\Scripts\yt-dlp.exe', '.'),
        
        # Bundle Deno executable (required for yt-dlp --remote-components)
        # Download from: https://github.com/denoland/deno/releases
        # Windows: deno-x86_64-pc-windows-msvc.zip
        # Extract deno.exe and place in project root, then uncomment line below:
        # ('deno.exe', 'bin'),
    ],
    datas=[
        *opencv_data,
        ('assets', 'assets'),  # Bundle assets folder
        ('clipper_core.py', '.'),  # Bundle core module
        ('youtube_uploader.py', '.'),  # Bundle YouTube module
    ],
    hiddenimports=[
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
        'whisper',  # We use API now, not local
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YTShortClipper',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
