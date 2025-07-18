#!/usr/bin/env python3
"""
网卡选择器修复验证脚本
测试手动刷新按钮和界面切换的修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from gui.views.netconfig.interface_selector import InterfaceSelectorWidget
from netkit.services.netconfig.async_manager import get_async_manager
import time

class TestWindow:
    def __init__(self):
        self.root = tb.Window(themename='darkly')
        self.root.title('网卡选择器修复验证')
        
        # 初始化UI助手
        ui_helper.initialize_scaling(self.root)
        ui_helper.center_window(self.root, 800, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置测试界面"""
        # 标题
        title = tb.Label(
            self.root,
            text="网卡选择器修复验证",
            font=ui_helper.get_font(16, "bold"),
            bootstyle=PRIMARY
        )
        title.pack(pady=20)
        
        # 测试按钮区域
        button_frame = tb.Frame(self.root)
        button_frame.pack(pady=10)
        
        # 测试按钮
        tb.Button(
            button_frame,
            text="模拟快速界面切换",
            command=self.test_rapid_switching,
            bootstyle=WARNING
        ).pack(side=LEFT, padx=5)
        
        tb.Button(
            button_frame,
            text="检查异步状态",
            command=self.check_async_status,
            bootstyle=INFO
        ).pack(side=LEFT, padx=5)
        
        tb.Button(
            button_frame,
            text="强制重置状态",
            command=self.force_reset_state,
            bootstyle=DANGER
        ).pack(side=LEFT, padx=5)
        
        # 网卡选择器测试区域
        selector_frame = tb.LabelFrame(self.root, text="网卡选择器测试", padding=20)
        selector_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        # 状态显示
        self.status_text = tb.Text(
            selector_frame,
            height=6,
            state=DISABLED,
            wrap=WORD
        )
        self.status_text.pack(fill=X, pady=(0, 10))
        
        # 创建网卡选择器
        self.interface_selector = InterfaceSelectorWidget(
            selector_frame,
            on_interface_selected=self.on_interface_selected,
            on_status_update=self.append_status
        )
        self.interface_selector.pack(fill=X)
        
        # 初始状态
        self.append_status("=== 网卡选择器修复验证测试 ===\n")
        self.append_status("1. 测试手动刷新按钮是否能正常启用/禁用\n")
        self.append_status("2. 测试快速界面切换是否会导致状态异常\n")
        self.append_status("3. 测试错误恢复和超时处理\n\n")
        
    def on_interface_selected(self, interface_name, display_name):
        """网卡选择回调"""
        self.append_status(f"选择了网卡: {interface_name}\n")
        self.append_status(f"显示名称: {display_name}\n")
        
    def append_status(self, text):
        """追加状态信息"""
        self.status_text.configure(state=NORMAL)
        self.status_text.insert(END, text)
        self.status_text.configure(state=DISABLED)
        self.status_text.see(END)
        
    def test_rapid_switching(self):
        """测试快速界面切换"""
        self.append_status("\n=== 开始快速界面切换测试 ===\n")
        
        # 模拟快速创建和销毁网卡选择器
        for i in range(3):
            self.append_status(f"第 {i+1} 次切换...\n")
            
            # 销毁当前选择器
            if hasattr(self, 'interface_selector'):
                self.interface_selector.cleanup()
                self.interface_selector.destroy()
            
            # 短暂延迟
            self.root.update()
            time.sleep(0.1)
            
            # 重新创建选择器
            selector_frame = self.root.children['!labelframe']
            self.interface_selector = InterfaceSelectorWidget(
                selector_frame,
                on_interface_selected=self.on_interface_selected,
                on_status_update=self.append_status
            )
            self.interface_selector.pack(fill=X)
            
            self.root.update()
            time.sleep(0.5)
            
        self.append_status("快速界面切换测试完成\n\n")
        
    def check_async_status(self):
        """检查异步状态"""
        self.append_status("\n=== 异步状态检查 ===\n")
        
        async_manager = get_async_manager()
        
        # 获取状态信息
        loading_state = async_manager.get_loading_state()
        cache_info = async_manager.get_cache_info()
        
        self.append_status(f"预加载完成: {async_manager.preload_completed}\n")
        self.append_status(f"正在加载: {loading_state.is_loading}\n")
        self.append_status(f"加载进度: {loading_state.progress * 100:.1f}%\n")
        self.append_status(f"当前消息: {loading_state.message}\n")
        self.append_status(f"错误信息: {loading_state.error}\n")
        self.append_status(f"缓存的网卡数量: {cache_info['total_adapters']}\n")
        self.append_status(f"物理网卡数量: {cache_info['physical_adapters']}\n")
        self.append_status(f"缓存年龄: {cache_info['cache_age']:.1f}秒\n")
        
        # 检查UI状态
        if hasattr(self, 'interface_selector'):
            ui_loading = self.interface_selector.is_loading
            button_state = self.interface_selector.refresh_button.cget('state')
            combo_state = self.interface_selector.interface_combo.cget('state')
            
            self.append_status(f"UI加载状态: {ui_loading}\n")
            self.append_status(f"刷新按钮状态: {button_state}\n")
            self.append_status(f"网卡选择框状态: {combo_state}\n")
            
            # 检查状态是否同步
            if loading_state.is_loading != ui_loading:
                self.append_status("⚠️ 警告: 异步状态与UI状态不同步!\n")
            else:
                self.append_status("✅ 状态同步正常\n")
        
        self.append_status("\n")
        
    def force_reset_state(self):
        """强制重置状态"""
        self.append_status("\n=== 强制重置状态 ===\n")
        
        if hasattr(self, 'interface_selector'):
            # 强制重置UI状态
            self.interface_selector._reset_loading_state()
            self.append_status("UI状态已重置\n")
            
            # 验证状态同步
            self.interface_selector._validate_and_sync_state()
            self.append_status("状态同步验证完成\n")
            
        self.append_status("\n")
        
    def run(self):
        """运行测试"""
        self.root.mainloop()

if __name__ == "__main__":
    print("启动网卡选择器修复验证...")
    test_window = TestWindow()
    test_window.run() 