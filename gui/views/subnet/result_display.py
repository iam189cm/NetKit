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
        
        # 创建结果表格
        self.create_result_table()
        
    def create_result_table(self):
        """创建结果表格（使用Treeview）"""
        # 创建Treeview
        columns = ['项目', '值']
        
        self.result_tree = tb.Treeview(
            self,
            columns=columns,
            show='tree',  # 不显示表头
            height=8,
            bootstyle=INFO
        )
        
        # 设置列
        self.result_tree.column('#0', width=0, stretch=NO)  # 隐藏树形结构列
        self.result_tree.column('项目', width=ui_helper.scale_size(150), anchor=W)
        self.result_tree.column('值', width=ui_helper.scale_size(350), anchor=W)
        
        # 隐藏表头
        self.result_tree.configure(show='')
        
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
        
        # 创建垂直滚动条
        v_scrollbar = tb.Scrollbar(self, orient=VERTICAL, command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=v_scrollbar.set)
        
        # 布局
        self.result_tree.pack(side=LEFT, fill=BOTH, expand=True)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        
        # 绑定右键菜单
        self.result_tree.bind("<Button-3>", self.show_context_menu)
        
        # 初始化显示空数据
        self.clear_results()
    
    def update_results(self, results: dict):
        """更新结果显示"""
        self.results_data = results
        
        # 清空现有数据
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 映射字典键到字段键
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
        
        # 添加新数据
        for label_text, field_key in self.fields:
            result_key = field_mapping.get(field_key, '')
            if result_key in results:
                value = results[result_key]
                self.result_tree.insert('', 'end', values=(label_text, value))
        
        # 设置行的样式
        for i, item in enumerate(self.result_tree.get_children()):
            if i % 2 == 0:
                self.result_tree.item(item, tags=('evenrow',))
            else:
                self.result_tree.item(item, tags=('oddrow',))
        
        # 配置行样式
        self.result_tree.tag_configure('evenrow', background='#2b3e50')
        self.result_tree.tag_configure('oddrow', background='#1e2a3a')
    
    def clear_results(self):
        """清空结果显示"""
        self.results_data = {}
        
        # 清空所有数据
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        
        # 显示空数据
        for label_text, _ in self.fields:
            self.result_tree.insert('', 'end', values=(label_text, ''))
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        # 创建右键菜单
        context_menu = tk.Menu(self, tearoff=0)
        
        # 获取选中的项
        selection = self.result_tree.selection()
        
        # 复制（选中内容）
        if selection:
            context_menu.add_command(
                label="复制",
                command=lambda: self.copy_selection(selection)
            )
        
        # 全选
        context_menu.add_command(
            label="全选",
            command=self.select_all
        )
        
        # 全部复制
        context_menu.add_command(
            label="全部复制",
            command=self.copy_all
        )
        
        # 显示菜单
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def copy_selection(self, selection):
        """复制选中的内容"""
        if selection:
            item = self.result_tree.item(selection[0])
            values = item['values']
            if len(values) >= 2:
                # 复制"项目: 值"格式
                text = f"{values[0]}: {values[1]}"
                pyperclip.copy(text)
    
    def select_all(self):
        """全选所有项"""
        all_items = self.result_tree.get_children()
        self.result_tree.selection_set(all_items)
    
    def copy_all(self):
        """复制所有结果"""
        if not self.results_data:
            return
        
        # 构建复制内容
        lines = []
        
        # 按顺序添加每个字段
        for item in self.result_tree.get_children():
            values = self.result_tree.item(item)['values']
            if len(values) >= 2 and values[1]:  # 确保有值
                lines.append(f"{values[0]}: {values[1]}")
        
        # 复制到剪贴板
        if lines:
            full_text = '\n'.join(lines)
            pyperclip.copy(full_text)