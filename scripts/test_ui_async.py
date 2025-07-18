#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI异步加载测试脚本
测试新的异步UI组件是否正常工作
"""

import sys
import os
import time
import tkinter as tk

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as tb
from gui.views.netconfig.interface_selector import InterfaceSelectorWidget

class TestApp:
    def __init__(self):
        self.root = tb.Window(themename='darkly')
        self.root.title("UI异步加载测试")
        self.root.geometry("800x600")
        
        # 创建主框架
        main_frame = tb.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tb.Label(main_frame, text="网卡选择器异步加载测试", font=('Microsoft YaHei', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # 网卡选择器
        self.interface_selector = InterfaceSelectorWidget(
            main_frame,
            on_interface_selected=self.on_interface_selected,
            on_status_update=self.on_status_update
        )
        self.interface_selector.pack(fill=tk.X, pady=(0, 20))
        
        # 状态显示区域
        status_frame = tb.Frame(main_frame)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        tb.Label(status_frame, text="状态信息:", font=('Microsoft YaHei', 12)).pack(anchor=tk.W)
        
        self.status_text = tb.Text(status_frame, height=20, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tb.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # 初始状态
        self.append_status("应用程序启动完成\n")
        self.append_status("正在等待网卡信息加载...\n")
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_interface_selected(self, interface_name, display_name):
        """网卡选择回调"""
        self.append_status(f"选择了网卡: {interface_name}\n")
        self.append_status(f"显示名称: {display_name}\n")
        self.append_status("-" * 50 + "\n")
    
    def on_status_update(self, text):
        """状态更新回调"""
        self.append_status(text)
    
    def append_status(self, text):
        """追加状态文本"""
        self.status_text.insert(tk.END, text)
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def on_closing(self):
        """关闭应用程序"""
        self.interface_selector.cleanup()
        self.root.destroy()
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

def main():
    """主函数"""
    print("启动UI异步加载测试...")
    app = TestApp()
    app.run()

if __name__ == "__main__":
    main() 