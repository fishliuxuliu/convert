# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[Path('.')],
    binaries=[],
    datas=[
        # 收集 Qt6 翻译文件（可选，减少体积可注释掉）
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PyQt6.sip',
        'docx',
        'docx.oxml',
        'docx.table',
        'docx.text',
        'docx.opc',
        'lxml',
        'pdfplumber',
        'pdfplumber.pdf',
        'pdfplumber.page',
        'pdfplumber.utils',
        'PIL',
        'PIL._imaging',
        'chardet',
    ],
    hookspath=[],
    hooksconfig={},
    cipher=block_cipher,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

# 收集所有 DLL 和依赖
def collect_pandas_binaries():
    binaries = []
    return binaries

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,
    name='DocMarkdownConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # 可指定 .ico 文件路径
    version=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='DocMarkdownConverter',
)
