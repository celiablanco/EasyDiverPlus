# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['easy_diver_plus_gui/easy_diver_plus_main.py'],
    pathex=[],
    binaries=[
        ('_pandaseq_macos_x86_64/pandaseq', '.'),
        ('_pandaseq_macos_x86_64/libpandaseq.7.dylib', '.'),
        ('_pandaseq_macos_x86_64/libpandaseq.dylib', '.')
    ],
    datas=[
        ('easydiver.sh', '.'),
        ('translator.py', '.'),
        ('seq_names_and_bootstrap.py','.'),
        ('easy_diver_plus_gui/assets/question_icon.png', 'easy_diver_plus_gui/assets/'),
        ('easy_diver_plus_gui/easy_diver.py', 'easy_diver_plus_gui/'),
        ('easy_diver_plus_gui/analysis_output.py', 'easy_diver_plus_gui/'),
        ('easy_diver_plus_gui/assets/logo.png', 'easy_diver_plus_gui/assets/'),
        ('easy_diver_plus_gui/directory_edit.py', 'easy_diver_plus_gui/'),
        ('easy_diver_plus_gui/file_sorter.py', 'easy_diver_plus_gui/'),
        ('easy_diver_plus_gui/graph_interface.py', 'easy_diver_plus_gui/'),
        ('easy_diver_plus_gui/graphs_generator.py', 'easy_diver_plus_gui/')
    ],
    hiddenimports=['plotly','plotly.graph_objs','plotly.subplots','plotly.io.orca', 'plotly.io.kaleido', 'webbrowser'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    imports=True,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher = block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EasyDiverPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True
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
