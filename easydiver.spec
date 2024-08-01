# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ssailr_gui/easy_diver_2_main.py'],
    pathex=[],
    binaries=[(
        '/usr/local/bin/pandaseq', '.'
    )],
    datas=[
        ('easydiver.sh', '.'),
        ('translator.py', '.'),
        ('seq_names_and_bootstrap.py','.'),
        ('ssailr_gui/assets/question_icon.png', 'ssailr_gui/assets/'),
        ('ssailr_gui/easy_diver.py', 'ssailr_gui/'),
        ('ssailr_gui/modified_counts.py', 'ssailr_gui/'),
        ('ssailr_gui/assets/logo.png', 'ssailr_gui/assets/'),
        ('ssailr_gui/directory_edit.py', 'ssailr_gui/'),
        ('ssailr_gui/file_sorter.py', 'ssailr_gui/'),
        ('ssailr_gui/graph_interface.py', 'ssailr_gui/'),
        ('ssailr_gui/graphs_generator.py', 'ssailr_gui/')
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
    name='EasyDiver2',
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
