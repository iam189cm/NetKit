#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import traceback

# 设置测试模式
os.environ['NETKIT_TEST_MODE'] = '1'

    print("开始测试Netkit GUI...")
print(f"Python版本: {sys.version}")
print(f"当前目录: {os.getcwd()}")

try:
    print("1. 测试基本导入...")
    import tkinter as tk
    print("   ✓ tkinter 导入成功")
    
    import ttkbootstrap as tb
    print("   ✓ ttkbootstrap 导入成功")
    
    print("2. 测试创建基本窗口...")
    root = tk.Tk()
    root.title("测试窗口")
    root.geometry("300x200")
    
    label = tk.Label(root, text="如果你看到这个窗口，说明GUI基本功能正常！")
    label.pack(pady=50)
    
    button = tk.Button(root, text="关闭", command=root.quit)
    button.pack(pady=10)
    
    print("   ✓ 基本窗口创建成功")
    print("3. 启动GUI主循环...")
    
    root.mainloop()
    print("   ✓ GUI正常退出")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    traceback.print_exc()

    print("\n4. 测试Netkit主程序...")
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gui.main import MainWindow
    print("   ✓ MainWindow 导入成功")
    
    app = MainWindow()
    print("   ✓ MainWindow 创建成功")
    print("   启动主程序...")
    app.run()
    
except Exception as e:
    print(f"❌ 主程序错误: {e}")
    traceback.print_exc() 