"""
UI组件模块

包含可视化ping界面的各种UI组件
如详细信息弹窗、右键菜单等
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from .grid_cell import IPGridCell


class IPDetailWindow:
    """IP详细信息弹窗"""
    
    def __init__(self, parent, ip_address, cell, event):
        self.parent = parent
        self.ip_address = ip_address
        self.cell = cell
        
        # 创建弹窗
        self.window = tk.Toplevel(parent)
        self.window.title("IP详细信息")
        self.window.geometry("300x150")
        self.window.resizable(False, False)
        
        # 设置弹窗位置（鼠标附近）
        x = event.x_root + 10
        y = event.y_root + 10
        self.window.geometry(f"+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置弹窗UI"""
        # 详细信息内容
        info_frame = tb.Frame(self.window, padding=20)
        info_frame.pack(fill=BOTH, expand=True)
        
        # IP地址
        tb.Label(info_frame, text="IP地址:", font=('微软雅黑', 10, 'bold')).pack(anchor=W)
        tb.Label(info_frame, text=self.ip_address, font=('微软雅黑', 10)).pack(anchor=W, pady=(0, 10))
        
        # 状态
        tb.Label(info_frame, text="状态:", font=('微软雅黑', 10, 'bold')).pack(anchor=W)
        status_text = {
            IPGridCell.STATE_INITIAL: "未扫描",
            IPGridCell.STATE_SCANNING: "扫描中",
            IPGridCell.STATE_ONLINE: "在线",
            IPGridCell.STATE_OFFLINE: "离线"
        }.get(self.cell.state, "未知")
        
        status_color = {
            IPGridCell.STATE_INITIAL: SECONDARY,
            IPGridCell.STATE_SCANNING: WARNING,
            IPGridCell.STATE_ONLINE: SUCCESS,
            IPGridCell.STATE_OFFLINE: DANGER
        }.get(self.cell.state, SECONDARY)
        
        tb.Label(info_frame, text=status_text, font=('微软雅黑', 10), bootstyle=status_color).pack(anchor=W, pady=(0, 10))
        
        # 响应时间
        tb.Label(info_frame, text="响应时间:", font=('微软雅黑', 10, 'bold')).pack(anchor=W)
        if self.cell.ping_result and self.cell.ping_result.get('times'):
            response_time = f"{self.cell.ping_result['times'][0]}ms"
        else:
            response_time = "无数据"
        tb.Label(info_frame, text=response_time, font=('微软雅黑', 10)).pack(anchor=W)
        
        # 关闭按钮
        tb.Button(info_frame, text="关闭", command=self.window.destroy).pack(pady=(15, 0))


class IPContextMenu:
    """IP右键菜单"""
    
    def __init__(self, parent, ip_address, ip_suffix, event, ping_callback):
        self.parent = parent
        self.ip_address = ip_address
        self.ip_suffix = ip_suffix
        self.ping_callback = ping_callback
        
        # 创建右键菜单
        self.menu = tk.Menu(parent, tearoff=0)
        self.setup_menu()
        
        # 显示菜单
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
    
    def setup_menu(self):
        """设置菜单项"""
        self.menu.add_command(
            label=f"单独ping {self.ip_address}",
            command=lambda: self.ping_callback(self.ip_suffix)
        )


class ScanResultDialog:
    """扫描结果对话框"""
    
    @staticmethod
    def show_scan_completed(parent, network_prefix, stats):
        """显示扫描完成对话框"""
        online_count = stats['online_count']
        offline_count = stats['offline_count']
        
        messagebox.showinfo(
            "扫描完成", 
            f"网段 {network_prefix}.0/24 扫描完成\n\n"
            f"在线设备: {online_count}\n"
            f"离线设备: {offline_count}\n"
            f"总计: {online_count + offline_count}"
        )
    
    @staticmethod
    def show_single_ping_result(parent, ip_address, result):
        """显示单独ping的结果"""
        stats = result['stats']
        
        if stats['success']:
            message = (
                f"Ping {ip_address} 成功!\n\n"
                f"数据包: 已发送 {stats['packets_sent']}, 已接收 {stats['packets_received']}\n"
                f"丢包率: {stats['packet_loss']:.1f}%\n"
                f"响应时间: 最小 {stats['min_time']}ms, 最大 {stats['max_time']}ms, 平均 {stats['avg_time']}ms"
            )
            messagebox.showinfo("Ping结果", message)
        else:
            messagebox.showerror("Ping结果", f"Ping {ip_address} 失败\n\n目标主机无响应")
    
    @staticmethod
    def show_ping_in_progress(parent, ip_address):
        """显示正在ping的提示"""
        messagebox.showinfo("正在Ping", f"正在ping {ip_address}，请稍候...")
    
    @staticmethod
    def show_error(parent, message):
        """显示错误信息"""
        messagebox.showerror("错误", message)
    
    @staticmethod
    def show_validation_error(parent, message):
        """显示验证错误"""
        messagebox.showerror("输入错误", message) 