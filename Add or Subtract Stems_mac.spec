# -*- mode: python ; coding: utf-8 -*-
# macOS build spec file

a = Analysis(
    ['Add or Subtract Stems.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Add or Subtract Stems',
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
    icon=['icon.icns'],  # macOS uses .icns format
)

# Optional: Create a macOS .app bundle
app = BUNDLE(
    exe,
    name='Add or Subtract Stems.app',
    icon='icon.icns',
    bundle_identifier='com.addorsubtractstems.gui',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleName': 'Add or Subtract Stems',
        'NSHighResolutionCapable': True,
    },
)
