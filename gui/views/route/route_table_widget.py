"""
路由表显示组件
职责：TreeView管理、数据显示、选择事件处理
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from tkinter import ttk


class RouteTableWidget(tb.LabelFrame):
    """路由表显示组件"""
    
    def __init__(self, master, on_route_selected=None, **kwargs):
        super().__init__(master, text="当前路由表", padding=ui_helper.get_padding(10), **kwargs)
        
        self.on_route_selected = on_route_selected
        self.routes_data = []
        self.selected_route = None
        
        self.setup_table()
        
    def setup_table(self):
        """设置路由表TreeView"""
        # 创建TreeView
        columns = ("destination", "netmask", "gateway", "interface", "metric", "type")
        self.route_tree = ttk.Treeview(self, columns=columns, show="headings", height=ui_helper.scale_size(12))
        
        # 设置列标题和宽度（统一左对齐）
        self.route_tree.heading("destination", text="目标网络", anchor=W)
        self.route_tree.heading("netmask", text="子网掩码", anchor=W)
        self.route_tree.heading("gateway", text="网关", anchor=W)
        self.route_tree.heading("interface", text="接口", anchor=W)
        self.route_tree.heading("metric", text="跃点数", anchor=W)
        self.route_tree.heading("type", text="路由类型", anchor=W)
        
        self.route_tree.column("destination", width=ui_helper.scale_size(120), anchor=W)
        self.route_tree.column("netmask", width=ui_helper.scale_size(120), anchor=W)
        self.route_tree.column("gateway", width=ui_helper.scale_size(120), anchor=W)
        self.route_tree.column("interface", width=ui_helper.scale_size(120), anchor=W)
        self.route_tree.column("metric", width=ui_helper.scale_size(80), anchor=W)
        self.route_tree.column("type", width=ui_helper.scale_size(100), anchor=W)
        
        # 绑定选择事件
        self.route_tree.bind('<<TreeviewSelect>>', self._on_route_select)
        
        # 布局
        self.route_tree.pack(fill=BOTH, expand=True)
        
    def update_routes(self, routes_data):
        """更新路由数据显示"""
        self.routes_data = routes_data
        self.populate_route_tree()
        
    def populate_route_tree(self):
        """填充路由表TreeView"""
        # 清空现有数据
        for item in self.route_tree.get_children():
            self.route_tree.delete(item)
        
        # 添加路由数据
        for route in self.routes_data:
            self.route_tree.insert('', 'end', values=(
                route['network_destination'],
                route['netmask'],
                route['gateway'],
                route['interface'],
                route['metric'],
                route['route_type']
            ))
            
    def _on_route_select(self, event):
        """路由选择事件处理"""
        selection = self.route_tree.selection()
        if selection:
            item = self.route_tree.item(selection[0])
            values = item['values']
            
            # 找到对应的路由数据
            for route in self.routes_data:
                if (route['network_destination'] == values[0] and 
                    route['netmask'] == values[1] and 
                    route['gateway'] == values[2]):
                    self.selected_route = route
                    break
            
            # 通知父组件
            if self.on_route_selected and self.selected_route:
                self.on_route_selected(self.selected_route)
                
    def get_selected_route(self):
        """获取选中的路由"""
        return self.selected_route
        
    def clear_selection(self):
        """清除选择状态"""
        self.selected_route = None
        selection = self.route_tree.selection()
        if selection:
            self.route_tree.selection_remove(selection[0])