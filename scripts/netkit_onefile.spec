# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 分析主程序
a = Analysis(
    ['start_netkit.py'],  # 使用start_netkit.py作为入口点
    pathex=[],
    binaries=[],
    datas=[
        # 包含GUI相关的资源文件
        ('gui', 'gui'),
        ('netkit', 'netkit'),
    ],
    hiddenimports=[
        'ttkbootstrap',
        'psutil',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
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
    name='NETKit-Py',
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