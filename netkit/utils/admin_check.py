
import ctypes
import sys
import tkinter.messagebox as mbox
import os

def ensure_admin():
    """Exit the program if not running as admin."""
    # 检查是否设置了测试模式环境变量
    if os.environ.get('NETKIT_TEST_MODE') == '1':
        print("警告: 运行在测试模式下，某些功能可能无法正常工作")
        return
    
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False
    if not is_admin:
        mbox.showwarning(
            "需要管理员权限",
            "检测到当前未以管理员身份运行。请右键本程序图标，选择'以管理员身份运行'后重新启动。"
        )
        sys.exit(1)

def check_admin_status():
    """检查管理员状态但不退出程序"""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return is_admin
    except Exception:
        return False
