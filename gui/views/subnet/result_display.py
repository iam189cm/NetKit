"""
子网计算结果显示组件
支持文本选择和右键复制功能
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
import tkinter as tk
import pyperclip


class SubnetResultDisplay(tb.LabelFrame):
    """子网计算结果显示"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="计算结果", padding=ui_helper.get_padding(15), **kwargs)
        
        # 结果数据
        self.results_data = {}
        
        # 创建结果显示区域
        self.create_result_display()
        
    def create_result_display(self):
        """创建结果显示区域（使用Text组件）"""
        # 创建可选择的文本显示区域
        self.result_text = tb.Text(
            self,
            height=8,  # 设置固定高度8行
            wrap=WORD,  # 自动换行
            state=DISABLED,
            relief=FLAT,
            borderwidth=ui_helper.scale_size(1),
            background='#f8f9fa',
            selectbackground='#0078d4',
            selectforeground='white'
        )
        self.result_text.pack(fill=BOTH, expand=True)
        
        # 定义要显示的字段
        self.fields = [
            ('网络地址', 'network_address'),
            ('广播地址', 'broadcast_address'),
            ('子网掩码', 'subnet_mask'),
            ('CIDR表示', 'cidr_notation'),
            ('可用主机范围', 'host_range'),
            ('可用主机数', 'host_count'),
            ('网络位/主机位', 'network_host_bits'),
            ('IP地址类型', 'ip_type')
        ]
        
        # 添加右键菜单
        self.context_menu = tb.Menu(self, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_selected_text)
        self.context_menu.add_command(label="全选", command=self.select_all_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制所有结果", command=self.copy_all_results)
        
        # 绑定右键菜单
        self.result_text.bind("<Button-3>", self.show_context_menu)
        
        # 初始化显示空数据
        self.clear_results()
    
    def update_results(self, results: dict):
        """更新结果显示"""
        self.results_data = results
        
        # 直接使用英文字段名映射到中文显示名称
        field_mapping = {
            'network_address': '网络地址',
            'broadcast_address': '广播地址',
            'subnet_mask': '子网掩码',
            'cidr_notation': 'CIDR表示',
            'host_range': '可用主机范围',
            'host_count': '可用主机数',
            'network_host_bits': '网络位/主机位',
            'ip_type': 'IP地址类型'
        }
        
        # 构建显示内容
        content_lines = []
        for label_text, field_key in self.fields:
            if field_key in results:
                value = results[field_key]
                content_lines.append(f"{label_text}: {value}")
            else:
                content_lines.append(f"{label_text}: ")
        
        content = '\n'.join(content_lines)
        self._update_text_display(content)
    
    def clear_results(self):
        """清空结果显示"""
        self.results_data = {}
        
        # 显示空数据
        content_lines = []
        for label_text, _ in self.fields:
            content_lines.append(f"{label_text}: ")
        
        content = '\n'.join(content_lines)
        self._update_text_display(content)
    
    def _update_text_display(self, content):
        """更新文本显示内容"""
        self.result_text.config(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", content)
        self.result_text.config(state=DISABLED)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            # 检查是否有选中的文本
            if self.result_text.selection_get():
                self.context_menu.entryconfig("复制", state=NORMAL)
            else:
                self.context_menu.entryconfig("复制", state=DISABLED)
        except:
            self.context_menu.entryconfig("复制", state=DISABLED)
        
        self.context_menu.post(event.x_root, event.y_root)
    
    def copy_selected_text(self):
        """复制选中的文本"""
        try:
            selected_text = self.result_text.selection_get()
            if selected_text:
                pyperclip.copy(selected_text)
        except:
            pass
    
    def select_all_text(self):
        """全选文本"""
        self.result_text.tag_add(SEL, "1.0", END)
        self.result_text.mark_set(INSERT, "1.0")
        self.result_text.see(INSERT)
    
    def copy_all_results(self):
        """复制所有计算结果"""
        try:
            # 获取所有文本内容
            all_text = self.result_text.get("1.0", END).strip()
            if all_text:
                pyperclip.copy(all_text)
        except Exception as e:
            pass