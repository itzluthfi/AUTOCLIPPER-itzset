# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

opencv_data = collect_data_files('cv2')

icon_path = 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None

a = Analysis(
    ['webview_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        *opencv_data,
        ('assets', 'assets'),
        ('web', 'web'),
        ('clipper_core.py', '.'),
        ('youtube_uploader.py', '.'),
        ('config', 'config'),
        ('utils', 'utils'),
        ('pages', 'pages'),
        ('dialogs', 'dialogs'),
        ('components', 'components'),
    ],
    hiddenimports=[
        'webview',
        'openai',
        'cv2',
        'numpy',
        'PIL',
        'requests',
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
    name='YTShortClipperWeb',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)
