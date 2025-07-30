#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体缩放测试脚本
用于对比字体缩放开启和关闭的效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper


class FontScalingTestWindow:
    """字体缩放测试窗口"""
    
    def __init__(self):
        self.root = tb.Window(themename='darkly')
        self.root.title('NetKit 字体缩放测试')
        
        # 启用 DPI 感知
        ui_helper.enable_dpi_awareness()
        ui_helper.initialize_scaling(self.root)
        
        # 设置窗口大小和居中
        ui_helper.center_window(self.root, 800, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = tb.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True, padx=ui_helper.get_padding(20), pady=ui_helper.get_padding(20))
        
        # 标题
        title = tb.Label(
            main_frame,
            text="NetKit 字体缩放对比测试",
            font=ui_helper.get_font(16, "bold"),
            bootstyle=PRIMARY
        )
        title.pack(pady=(0, ui_helper.get_padding(20)))
        
        # 控制面板
        control_frame = tb.LabelFrame(main_frame, text="控制面板", padding=ui_helper.get_padding(15))
        control_frame.pack(fill=X, pady=(0, ui_helper.get_padding(20)))
        
        # 字体缩放开关
        self.font_scaling_var = tb.BooleanVar(value=ui_helper.is_font_scaling_enabled())
        font_scaling_check = tb.Checkbutton(
            control_frame,
            text="启用字体DPI缩放",
            variable=self.font_scaling_var,
            command=self.toggle_font_scaling
        )
        font_scaling_check.pack(anchor=W, pady=ui_helper.get_padding(5))
        
        # 当前状态显示
        self.status_label = tb.Label(
            control_frame,
            text=f"当前状态: 字体缩放{'启用' if ui_helper.is_font_scaling_enabled() else '禁用'}",
            font=ui_helper.get_font(10),
            bootstyle=INFO
        )
        self.status_label.pack(anchor=W, pady=ui_helper.get_padding(5))
        
        # 字体大小对比
        comparison_frame = tb.LabelFrame(main_frame, text="字体大小对比", padding=ui_helper.get_padding(15))
        comparison_frame.pack(fill=BOTH, expand=True)
        
        # 创建不同大小的字体示例
        font_sizes = [8, 9, 10, 12, 14, 16, 18, 20]
        
        for size in font_sizes:
            font_frame = tb.Frame(comparison_frame)
            font_frame.pack(fill=X, pady=ui_helper.get_padding(5))
            
            # 字体大小标签
            size_label = tb.Label(
                font_frame,
                text=f"{size}pt:",
                font=ui_helper.get_font(9),
                width=6
            )
            size_label.pack(side=LEFT)
            
            # 示例文本
            sample_text = tb.Label(
                font_frame,
                text=f"这是 {size}pt 字体的示例文本 - Sample Text",
                font=ui_helper.get_font(size),
                bootstyle=SECONDARY
            )
            sample_text.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # DPI信息显示
        info_frame = tb.LabelFrame(main_frame, text="DPI信息", padding=ui_helper.get_padding(15))
        info_frame.pack(fill=X, pady=(ui_helper.get_padding(20), 0))
        
        dpi_info = [
            f"系统缩放因子: {ui_helper.get_scaling_factor():.2f}",
            f"DPI: {ui_helper.get_dpi()}",
            f"屏幕分辨率: {self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}",
            f"基础字体大小: 9pt",
        ]
        
        for info in dpi_info:
            tb.Label(info_frame, text=info, font=ui_helper.get_font(10)).pack(anchor=W, pady=ui_helper.get_padding(2))
        
    def toggle_font_scaling(self):
        """切换字体缩放设置"""
        enabled = self.font_scaling_var.get()
        ui_helper.set_font_scaling(enabled)
        
        # 更新状态显示
        self.status_label.config(text=f"当前状态: 字体缩放{'启用' if enabled else '禁用'}")
        
        # 提示用户重启程序以查看效果
        tb.dialogs.Messagebox.show_info(
            title="设置已更改",
            message="字体缩放设置已更改。\n请重启程序以查看完整效果。",
            parent=self.root
        )
    
    def run(self):
        """运行测试窗口"""
        self.root.mainloop()


def main():
    print("=" * 50)
    print("NetKit 字体缩放测试")
    print("=" * 50)
    
    try:
        test_window = FontScalingTestWindow()
        test_window.run()
    except KeyboardInterrupt:
        print("\n字体缩放测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        print("字体缩放测试完成")


if __name__ == "__main__":
    main()