# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['D', '\\freelances\\Tuan\\app_quan_ly_python_qt\\venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('common', 'common'), ('messages', 'messages'), ('models', 'models'), ('presenters', 'presenters'), ('sql_statements', 'sql_statements'), ('ui', 'ui'), ('ui_components', 'ui_components'), ('views', 'views'), ('configs.py', 'configs.py'), ('resources.py', 'resources.py'), ('resources.qrc', 'resources.qrc')],
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
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
