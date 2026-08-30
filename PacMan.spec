# -*- mode: python ; coding: utf-8 -*-

import os
import mlx

# mlx/mlx.py loads libmlx.so via ctypes.CDLL at runtime (not a normal
# import), so PyInstaller's static analysis never discovers it on its
# own - it has to be added to `binaries` explicitly.
_mlx_dir = os.path.dirname(mlx.__file__)

a = Analysis(
    ['pac-man.py'],
    pathex=[],
    binaries=[
        (os.path.join(_mlx_dir, 'libmlx.so'), 'mlx'),
    ],
    datas=[('assets', 'assets'), ('config.json', '.')],
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
    [],
    exclude_binaries=True,
    name='PacMan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # The game loads assets/config.json via paths relative to the
    # executable's own directory (e.g. "assets/menu/..."). PyInstaller
    # 6+ defaults to hiding all bundled data inside an "_internal"
    # subfolder instead of placing it next to the exe, which breaks
    # those relative paths. "." restores the old flat layout.
    # (COLLECT() below actually reads this value off the EXE object,
    # not from its own kwargs, so it has to be set here.)
    contents_directory='.',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PacMan',
)
