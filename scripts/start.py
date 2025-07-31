#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netkit 启动脚本
"""

import os
import sys
from pathlib import Path

# 切换到项目根目录
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

# 添加项目根目录到Python路径
sys.path.insert(0, str(project_root))

def main():
    # 在导入 GUI 模块之前设置 DPI 感知
    try:
        from netkit.utils.ui_helper import ui_helper
        ui_helper.enable_dpi_awareness()
    except ImportError as e:
        print(f"警告: 无法导入 UI 辅助模块: {e}")
        # 回退到原始的 DPI 设置
        if sys.platform == "win32":
            import ctypes
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
            except (AttributeError, OSError):
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                except (AttributeError, OSError):
                    print("警告: 无法设置 DPI 感知，在高分屏上界面可能模糊")
        
    # 设置测试模式（开发阶段使用）
    os.environ['NETKIT_TEST_MODE'] = '1'
    
    print("正在启动 Netkit...")
    print("警告: 当前运行在测试模式下")
    print("某些需要管理员权限的功能可能无法正常工作")
    print("-" * 50)
    
    try:
        # 导入并启动主程序
        from gui.main import MainWindow
        
        app = MainWindow()
        print("Netkit 启动成功!")
        print("请在弹出的窗口中使用各项功能")
        
        # 运行主循环
        app.run()
        
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("Netkit 已退出")
    return 0

if __name__ == "__main__":
    sys.exit(main())