# -*- mode: python ; coding: utf-8 -*-
import os
import sys

# 获取项目根目录（scripts目录的上级目录）
# 在PyInstaller中，__file__不可用，使用SPECPATH代替
root_dir = os.path.dirname(SPECPATH)

block_cipher = None

# 分析主程序
a = Analysis(
    [os.path.join(root_dir, 'scripts', 'start.py')],  # 使用绝对路径
    pathex=[root_dir],
    binaries=[],
    datas=[
        # 包含GUI相关的资源文件
        (os.path.join(root_dir, 'gui'), 'gui'),
        (os.path.join(root_dir, 'netkit'), 'netkit'),
        # 包含assets目录（如果有样式文件）
        (os.path.join(root_dir, 'gui', 'assets'), 'gui/assets'),
    ],
    hiddenimports=[
        # GUI框架相关
        'ttkbootstrap',
        'ttkbootstrap.constants',
        'ttkbootstrap.themes',
        'ttkbootstrap.style',
        'ttkbootstrap.scrolled',
        'ttkbootstrap.tooltip',
        'ttkbootstrap.dialogs',
        'ttkbootstrap.tableview',
        
        # 系统相关
        'psutil',
        'psutil._common',
        'psutil._pswindows',
        
        # 标准库
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        'tkinter.font',
        
        # 网络和系统
        'threading',
        'subprocess',
        'json',
        'ipaddress',
        'socket',
        'platform',
        'time',
        'sys',
        'os',
        're',
        'datetime',
        'traceback',
        'collections',
        'functools',
        'itertools',
        'math',
        'random',
        'string',
        'uuid',
        'pathlib',
        'shutil',
        'tempfile',
        'logging',
        'warnings',
        
        # 项目模块
        'gui',
        'gui.main',
        'gui.views',
        'gui.views.netconfig',
        'gui.views.ping',
        'gui.views.route.route_view',
        'netkit',
        'netkit.services',
        'netkit.services.netconfig',
        'netkit.services.ping',
        'netkit.services.route',
        'netkit.utils',
        'netkit.utils.admin_check',
        'netkit.utils.network_monitor',
        'netkit.utils.ui_helper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'jupyter',
        'IPython',
        'notebook',
        'sphinx',
        'pytest',
        'setuptools',
        'wheel',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建PYZ文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 创建单个exe文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NetKit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以在这里添加图标文件路径
) 