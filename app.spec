# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=['D:\\QT_app\\qt_project\\venv\\Lib\\site-packages'],
    binaries=[],
    datas=[('README.md', 'README.md'), ('common', 'common'), ('messages', 'messages'), ('models', 'models'), ('presenters', 'presenters'), ('sql_statements', 'sql_statements'), ('ui', 'ui'), ('ui_components', 'ui_components'), ('views', 'views'), ('configs.py', 'configs.py'), ('icon.ico', 'icon.ico'), ('resources.py', 'resources.py'), ('resources.qrc', 'resources.qrc')],
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
    icon=['icon.ico'],
)
