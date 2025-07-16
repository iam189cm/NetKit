#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Netkit 启动脚本
"""

import os
import sys

def main():
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