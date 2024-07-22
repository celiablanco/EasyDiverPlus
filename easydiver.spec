# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ssailr_gui/easy_diver.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('easydiver.sh', '.'),
        ('modified_counts.py', '.'),
        ('translator.py', '.'),
        ('ssailr_gui/assets/question_icon.png', 'ssailr_gui/assets'),
        ('ssailr_gui/assets/logo.png', 'ssailr_gui/assets'),
        ('ssailr_gui/directory_edit.py', 'ssailr_gui'),
        ('ssailr_gui/file_sorter.py', 'ssailr_gui'),
        ('ssailr_gui/graph_interface.py', 'ssailr_gui'),
        ('ssailr_gui/graphs_generator.py', 'ssailr_gui'),
        ('ssailr_gui/ssailr.py', 'ssailr_gui')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EasyDiver',
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
    entitlements_file=None
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EasyDiver'
)
