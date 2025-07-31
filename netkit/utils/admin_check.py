
import ctypes
import sys
import tkinter.messagebox as mbox
import os
import subprocess

def check_admin_status():
    """检查管理员状态但不退出程序"""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        return is_admin
    except Exception:
        return False

def auto_elevate():
    """自动请求管理员权限提升，返回是否成功触发提升"""
    try:
        # 使用ShellExecuteW重新启动程序
        # 参数说明：hwnd, operation, file, parameters, directory, show_cmd
        result = ctypes.windll.shell32.ShellExecuteW(
            None,                    # hwnd
            "runas",                 # operation (以管理员身份运行)
            sys.executable,          # file (Python解释器路径)
            " ".join(sys.argv),      # parameters (命令行参数)
            None,                    # directory
            1                        # show_cmd (SW_SHOWNORMAL)
        )
        
        # ShellExecuteW返回值大于32表示成功
        if result > 32:
            # 成功触发UAC提升，当前进程可以退出
            return True
        else:
            # 提升失败（用户取消、系统限制等）
            return False
            
    except Exception as e:
        # 发生异常，提升失败
        print(f"权限提升异常: {e}")
        return False

def check_admin_without_exit():
    """检查管理员权限但不退出程序，返回权限状态"""
    # 在测试模式下，我们仍然检查真实的管理员权限状态
    # 但不会因为权限不足而退出程序
    return check_admin_status()

def ensure_admin(allow_limited_mode=False):
    """检查管理员权限，支持受限模式"""
    # 检查是否设置了测试模式环境变量
    if os.environ.get('NETKIT_TEST_MODE') == '1':
        print("警告: 运行在测试模式下，某些功能可能无法正常工作")
        if allow_limited_mode:
            return check_admin_status()
        return
    
    is_admin = check_admin_status()
    
    if not is_admin:
        if allow_limited_mode:
            # 允许受限模式，返回权限状态
            return False
        else:
            # 传统模式，显示警告并退出
            mbox.showwarning(
                "需要管理员权限",
                "检测到当前未以管理员身份运行。请右键本程序图标，选择'以管理员身份运行'后重新启动。"
            )
            sys.exit(1)
    
    return True
