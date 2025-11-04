# -*- mode: python ; coding: utf-8 -*-
"""
MaaAgent PyInstaller 配置文件
用于打包 Python Agent 为单可执行文件

使用方法:
    cd 到项目根目录，然后执行:
    pyinstaller tools/MaaAgent.spec
"""

import os

# 获取项目根目录（spec 文件在 tools/ 下，需要返回上一级）
spec_root = os.path.dirname(os.path.abspath(SPECPATH))

block_cipher = None

a = Analysis(
    [os.path.join(spec_root, 'agent/main.py')],
    pathex=[],
    binaries=[],
    datas=[
        (os.path.join(spec_root, 'agent/config'), 'config'),
        (os.path.join(spec_root, 'agent/postmessage'), 'postmessage'),
    ],
    hiddenimports=[
        'win32timezone',
        'win32api',
        'win32con',
        'win32gui',
        'win32com',
        'win32com.shell',
        'win32com.shell.shell',
        'pywintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 收集所有 pywin32 相关的模块
a.binaries = a.binaries + TOC([
    ('pythoncom310.dll', None, 'BINARY'),
    ('pywintypes310.dll', None, 'BINARY'),
])

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MaaAgent',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 保留控制台窗口以显示日志
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可选: 添加图标文件路径
)
