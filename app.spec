# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['D:\\QT_app\\qt_project\\venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('common', 'common'), ('messages', 'messages'), ('models', 'models'), ('presenters', 'presenters'), ('sql_statements', 'sql_statements'), ('ui', 'ui'), ('ui_components', 'ui_components'), ('views', 'views'), ('configs.py', 'configs.py'), ('icon.ico', 'icon.ico'), ('resources.py', 'resources.py'), ('resources.qrc', 'resources.qrc')],
    hiddenimports=['pkg_resources.extern'],
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
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
