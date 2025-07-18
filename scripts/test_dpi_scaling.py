#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DPI 缩放测试脚本
用于验证不同 DPI 设置下的界面显示效果
"""

import sys
import os
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from netkit.utils.ui_helper import ui_helper


class DPITestWindow:
    """DPI 测试窗口"""
    
    def __init__(self):
        self.root = tb.Window(themename='darkly')
        self.root.title('NetKit DPI 缩放测试')
        
        # 启用 DPI 感知
        ui_helper.enable_dpi_awareness()
        ui_helper.initialize_scaling(self.root)
        
        # 设置窗口尺寸和居中
        ui_helper.center_window(self.root, 800, 600)
        self.root.resizable(True, True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置测试界面"""
        # 主容器
        main_frame = tb.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=ui_helper.get_padding(20), pady=ui_helper.get_padding(20))
        
        # 标题
        title = tb.Label(
            main_frame,
            text="NetKit DPI 缩放测试",
            font=ui_helper.get_font(20, "bold"),
            bootstyle=PRIMARY
        )
        title.pack(pady=(0, ui_helper.get_padding(20)))
        
        # DPI 信息显示
        info_frame = tb.LabelFrame(main_frame, text="DPI 信息", padding=ui_helper.get_padding(15))
        info_frame.pack(fill=X, pady=(0, ui_helper.get_padding(20)))
        
        # DPI 详细信息
        dpi_info = [
            f"缩放因子: {ui_helper.get_scaling_factor():.2f}",
            f"DPI: {ui_helper.get_dpi()}",
            f"屏幕分辨率: {self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}",
            f"基础字体: {ui_helper.get_font()}",
            f"标题字体: {ui_helper.get_font(18, 'bold')}",
        ]
        
        for info in dpi_info:
            tb.Label(info_frame, text=info, font=ui_helper.get_font(10)).pack(anchor=W, pady=ui_helper.get_padding(2))
        
        # 字体测试区域
        font_frame = tb.LabelFrame(main_frame, text="字体测试", padding=ui_helper.get_padding(15))
        font_frame.pack(fill=X, pady=(0, ui_helper.get_padding(20)))
        
        font_sizes = [8, 9, 10, 12, 14, 16, 18, 20]
        for size in font_sizes:
            tb.Label(
                font_frame,
                text=f"字体大小 {size}px - 中文测试 ABC 123",
                font=ui_helper.get_font(size)
            ).pack(anchor=W, pady=ui_helper.get_padding(2))
        
        # 控件测试区域
        widget_frame = tb.LabelFrame(main_frame, text="控件测试", padding=ui_helper.get_padding(15))
        widget_frame.pack(fill=BOTH, expand=True, pady=(0, ui_helper.get_padding(20)))
        
        # 按钮测试
        button_frame = tb.Frame(widget_frame)
        button_frame.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        tb.Label(button_frame, text="按钮测试:", font=ui_helper.get_font(10, "bold")).pack(side=LEFT)
        
        for i, (text, style) in enumerate([("主要", PRIMARY), ("成功", SUCCESS), ("警告", WARNING), ("危险", DANGER)]):
            tb.Button(
                button_frame,
                text=text,
                bootstyle=style,
                width=ui_helper.scale_size(10)
            ).pack(side=LEFT, padx=ui_helper.get_padding(5))
        
        # 输入框测试
        entry_frame = tb.Frame(widget_frame)
        entry_frame.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        tb.Label(entry_frame, text="输入框测试:", font=ui_helper.get_font(10, "bold")).pack(side=LEFT)
        
        test_entry = tb.Entry(
            entry_frame,
            font=ui_helper.get_font(9),
            width=ui_helper.scale_size(30)
        )
        test_entry.pack(side=LEFT, padx=ui_helper.get_padding(10))
        test_entry.insert(0, "测试输入框 - Test Entry")
        
        # 文本框测试
        text_frame = tb.Frame(widget_frame)
        text_frame.pack(fill=BOTH, expand=True)
        
        tb.Label(text_frame, text="文本框测试:", font=ui_helper.get_font(10, "bold")).pack(anchor=W)
        
        test_text = tb.Text(
            text_frame,
            height=ui_helper.scale_size(8),
            font=ui_helper.get_font(9),
            wrap=WORD
        )
        test_text.pack(fill=BOTH, expand=True, pady=ui_helper.get_padding(5))
        
        # 添加测试文本
        test_content = """这是一个 DPI 缩放测试文本框。
        
当前 DPI 设置:
- 缩放因子: {:.2f}
- DPI: {}
- 屏幕分辨率: {}x{}

测试内容:
1. 中文字符显示测试
2. English character display test
3. 数字和符号: 123456789 !@#$%^&*()
4. 特殊字符: αβγδε ∑∏∫∆∇

如果您看到这些文字清晰显示，说明 DPI 适配工作正常。
""".format(
            ui_helper.get_scaling_factor(),
            ui_helper.get_dpi(),
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight()
        )
        
        test_text.insert(1.0, test_content)
        
        # 滚动条
        scrollbar = tb.Scrollbar(text_frame, orient=VERTICAL, command=test_text.yview)
        test_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 底部状态栏
        status_frame = tb.Frame(main_frame)
        status_frame.pack(fill=X, pady=(ui_helper.get_padding(10), 0))
        
        tb.Label(
            status_frame,
            text=f"NetKit DPI 测试 - 缩放因子: {ui_helper.get_scaling_factor():.2f} | DPI: {ui_helper.get_dpi()}",
            font=ui_helper.get_font(8),
            bootstyle=SECONDARY
        ).pack(side=LEFT)
        
        # 退出按钮
        tb.Button(
            status_frame,
            text="退出",
            bootstyle=DANGER,
            command=self.root.quit,
            width=ui_helper.scale_size(8)
        ).pack(side=RIGHT)
        
    def run(self):
        """运行测试窗口"""
        print("DPI 缩放测试窗口启动中...")
        print(f"当前 DPI 设置: 缩放因子 {ui_helper.get_scaling_factor():.2f}, DPI {ui_helper.get_dpi()}")
        print("请检查窗口中的字体、控件大小是否合适")
        print("按 Ctrl+C 或点击退出按钮关闭测试窗口")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\n测试被用户中断")
        
        print("DPI 缩放测试完成")


def main():
    """主函数"""
    print("=" * 50)
    print("NetKit DPI 缩放测试")
    print("=" * 50)
    
    # 创建并运行测试窗口
    test_window = DPITestWindow()
    test_window.run()


if __name__ == '__main__':
    main() 