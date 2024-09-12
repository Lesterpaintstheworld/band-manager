# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('C:\\Python312\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Core.dll', 'PyQt5/Qt5/bin'), ('C:\\Python312\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Gui.dll', 'PyQt5/Qt5/bin'), ('C:\\Python312\\Lib\\site-packages\\PyQt5\\Qt5\\bin\\Qt5Widgets.dll', 'PyQt5/Qt5/bin'), ('C:\\Python312\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\platforms\\qwindows.dll', 'PyQt5/Qt5/plugins/platforms')],
    datas=[('C:\\Users\\conta\\synthetic-band-manager/prompts', 'prompts'), ('C:\\Users\\conta\\synthetic-band-manager/*.md', '.'), ('C:\\Users\\conta\\synthetic-band-manager/*.json', '.'), ('C:\\Users\\conta\\synthetic-band-manager/style.css', '.'), ('C:\\Users\\conta\\synthetic-band-manager/spinner.gif', '.'), ('C:\\Users\\conta\\synthetic-band-manager/.env', '.'), ('C:\\Users\\conta\\synthetic-band-manager/splash.png', '.')],
    hiddenimports=['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'openai', 'dotenv'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['transformers', 'torch', 'tensorflow'],
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
    name='BandManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\conta\\synthetic-band-manager\\icon.ico'],
)
