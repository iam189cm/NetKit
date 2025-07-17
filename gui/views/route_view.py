import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.services.route import RouteService
import tkinter.messagebox as mbox
import threading
from tkinter import ttk


class RouteFrame(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.route_service = RouteService()
        self.routes_data = []
        self.filtered_routes = []
        self.selected_route = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置静态路由管理界面"""
        # 标题
        title = tb.Label(
            self, 
            text="静态路由管理", 
            font=('Microsoft YaHei', 18, 'bold'),
            bootstyle=DANGER
        )
        title.pack(pady=(0, 20))
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 上方路由表显示区域
        table_frame = tb.LabelFrame(main_frame, text="当前路由表", padding=10)
        table_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 筛选控制区域
        filter_frame = tb.Frame(table_frame)
        filter_frame.pack(fill=X, pady=(0, 10))
        
        # 筛选输入框
        tb.Label(filter_frame, text="筛选:").pack(side=LEFT)
        
        self.filter_column_var = tb.StringVar(value="全部")
        filter_column_combo = tb.Combobox(
            filter_frame,
            textvariable=self.filter_column_var,
            values=["全部", "目标网络", "子网掩码", "网关", "接口", "跃点数", "路由类型"],
            state="readonly",
            width=12
        )
        filter_column_combo.pack(side=LEFT, padx=(5, 0))
        
        self.filter_value_var = tb.StringVar()
        self.filter_entry = tb.Entry(filter_frame, textvariable=self.filter_value_var, width=20)
        self.filter_entry.pack(side=LEFT, padx=(5, 0))
        self.filter_entry.bind('<KeyRelease>', self.on_filter_change)
        
        tb.Button(
            filter_frame,
            text="清除筛选",
            bootstyle=LIGHT,
            command=self.clear_filter,
            width=8
        ).pack(side=LEFT, padx=(5, 0))
        
        # 刷新按钮
        tb.Button(
            filter_frame,
            text="刷新路由表",
            bootstyle=INFO,
            command=self.refresh_routes,
            width=12
        ).pack(side=RIGHT)
        
        # 路由表TreeView
        self.setup_route_table(table_frame)
        
        # 下方操作区域
        operation_frame = tb.LabelFrame(main_frame, text="路由操作", padding=15)
        operation_frame.pack(fill=X)
        
        # 添加路由区域
        add_frame = tb.Frame(operation_frame)
        add_frame.pack(fill=X, pady=(0, 10))
        
        # 第一行：目标网络和子网掩码
        row1_frame = tb.Frame(add_frame)
        row1_frame.pack(fill=X, pady=(0, 5))
        
        tb.Label(row1_frame, text="目标网络:").pack(side=LEFT)
        self.dest_entry = tb.Entry(row1_frame, width=15)
        self.dest_entry.pack(side=LEFT, padx=(5, 10))
        self.dest_entry.insert(0, "192.168.2.0")
        
        tb.Label(row1_frame, text="子网掩码:").pack(side=LEFT)
        self.mask_entry = tb.Entry(row1_frame, width=15)
        self.mask_entry.pack(side=LEFT, padx=(5, 10))
        self.mask_entry.insert(0, "255.255.255.0")
        
        # 第二行：网关和跃点数
        row2_frame = tb.Frame(add_frame)
        row2_frame.pack(fill=X, pady=(0, 5))
        
        tb.Label(row2_frame, text="网关地址:").pack(side=LEFT)
        self.gateway_entry = tb.Entry(row2_frame, width=15)
        self.gateway_entry.pack(side=LEFT, padx=(5, 10))
        self.gateway_entry.insert(0, "192.168.1.1")
        
        tb.Label(row2_frame, text="跃点数:").pack(side=LEFT)
        self.metric_var = tb.StringVar(value="1")
        metric_spinbox = tb.Spinbox(
            row2_frame,
            from_=1, to=9999,
            textvariable=self.metric_var,
            width=8
        )
        metric_spinbox.pack(side=LEFT, padx=(5, 10))
        
        # 操作按钮
        btn_frame = tb.Frame(add_frame)
        btn_frame.pack(fill=X, pady=(10, 0))
        
        tb.Button(
            btn_frame,
            text="验证参数",
            bootstyle=WARNING,
            command=self.validate_route_params,
            width=12
        ).pack(side=LEFT, padx=(0, 5))
        
        tb.Button(
            btn_frame,
            text="添加路由",
            bootstyle=SUCCESS,
            command=self.add_route,
            width=12
        ).pack(side=LEFT, padx=5)
        
        tb.Button(
            btn_frame,
            text="删除选中",
            bootstyle=DANGER,
            command=self.delete_selected_route,
            width=12
        ).pack(side=LEFT, padx=5)
        
        # 结果显示区域
        result_frame = tb.LabelFrame(main_frame, text="操作结果", padding=10)
        result_frame.pack(fill=X, pady=(10, 0))
        
        self.result_text = tb.Text(
            result_frame,
            height=6,
            state=DISABLED,
            wrap=WORD,
            font=('Consolas', 9)
        )
        
        result_scrollbar = tb.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side=LEFT, fill=BOTH, expand=True)
        result_scrollbar.pack(side=RIGHT, fill=Y)
        
        # 清空结果按钮
        clear_result_frame = tb.Frame(result_frame)
        clear_result_frame.pack(fill=X, pady=(5, 0))
        
        tb.Button(
            clear_result_frame,
            text="清空结果",
            bootstyle=LIGHT,
            command=self.clear_result,
            width=12
        ).pack(side=RIGHT)
        
        # 初始化
        self.append_result("=== Netkit 静态路由管理工具 ===\n")
        self.append_result("点击'刷新路由表'按钮获取当前路由信息\n\n")
        
        # 初始化时刷新路由表
        self.refresh_routes()
        
    def setup_route_table(self, parent):
        """设置路由表TreeView"""
        # 创建TreeView
        columns = ("destination", "netmask", "gateway", "interface", "metric", "type")
        self.route_tree = ttk.Treeview(parent, columns=columns, show="headings", height=12)
        
        # 设置列标题和宽度
        self.route_tree.heading("destination", text="目标网络")
        self.route_tree.heading("netmask", text="子网掩码")
        self.route_tree.heading("gateway", text="网关")
        self.route_tree.heading("interface", text="接口")
        self.route_tree.heading("metric", text="跃点数")
        self.route_tree.heading("type", text="路由类型")
        
        self.route_tree.column("destination", width=120)
        self.route_tree.column("netmask", width=120)
        self.route_tree.column("gateway", width=120)
        self.route_tree.column("interface", width=120)
        self.route_tree.column("metric", width=80)
        self.route_tree.column("type", width=100)
        
        # 绑定选择事件
        self.route_tree.bind('<<TreeviewSelect>>', self.on_route_select)
        
        # 滚动条
        tree_scrollbar_v = ttk.Scrollbar(parent, orient=VERTICAL, command=self.route_tree.yview)
        tree_scrollbar_h = ttk.Scrollbar(parent, orient=HORIZONTAL, command=self.route_tree.xview)
        self.route_tree.configure(yscrollcommand=tree_scrollbar_v.set, xscrollcommand=tree_scrollbar_h.set)
        
        # 布局
        self.route_tree.pack(side=LEFT, fill=BOTH, expand=True)
        tree_scrollbar_v.pack(side=RIGHT, fill=Y)
        tree_scrollbar_h.pack(side=BOTTOM, fill=X)
        
    def refresh_routes(self):
        """刷新路由表"""
        self.append_result("正在获取路由表...\n")
        
        def do_refresh():
            try:
                result = self.route_service.get_route_table()
                self.after(0, lambda: self.update_route_table(result))
            except Exception as e:
                self.after(0, lambda: self.append_result(f"获取路由表出错: {str(e)}\n"))
        
        threading.Thread(target=do_refresh, daemon=True).start()
        
    def update_route_table(self, result):
        """更新路由表显示"""
        if result['success']:
            self.routes_data = result['routes']
            self.filtered_routes = self.routes_data.copy()
            self.populate_route_tree()
            self.append_result(f"路由表刷新成功，共 {len(self.routes_data)} 条路由\n")
        else:
            self.append_result(f"获取路由表失败: {result['error']}\n")
            
    def populate_route_tree(self):
        """填充路由表TreeView"""
        # 清空现有数据
        for item in self.route_tree.get_children():
            self.route_tree.delete(item)
        
        # 添加路由数据
        for route in self.filtered_routes:
            self.route_tree.insert('', 'end', values=(
                route['network_destination'],
                route['netmask'],
                route['gateway'],
                route['interface'],
                route['metric'],
                route['route_type']
            ))
            
    def on_route_select(self, event):
        """路由选择事件"""
        selection = self.route_tree.selection()
        if selection:
            item = self.route_tree.item(selection[0])
            values = item['values']
            
            # 找到对应的路由数据
            for route in self.filtered_routes:
                if (route['network_destination'] == values[0] and 
                    route['netmask'] == values[1] and 
                    route['gateway'] == values[2]):
                    self.selected_route = route
                    break
                    
    def on_filter_change(self, event=None):
        """筛选变化事件"""
        self.apply_filter()
        
    def apply_filter(self):
        """应用筛选"""
        filter_column = self.filter_column_var.get()
        filter_value = self.filter_value_var.get().lower()
        
        if not filter_value or filter_column == "全部":
            self.filtered_routes = self.routes_data.copy()
        else:
            self.filtered_routes = []
            
            for route in self.routes_data:
                match = False
                
                if filter_column == "目标网络" and filter_value in route['network_destination'].lower():
                    match = True
                elif filter_column == "子网掩码" and filter_value in route['netmask'].lower():
                    match = True
                elif filter_column == "网关" and filter_value in route['gateway'].lower():
                    match = True
                elif filter_column == "接口" and filter_value in route['interface'].lower():
                    match = True
                elif filter_column == "跃点数" and filter_value in str(route['metric']):
                    match = True
                elif filter_column == "路由类型" and filter_value in route['route_type'].lower():
                    match = True
                elif filter_column == "全部":
                    # 搜索所有字段
                    search_text = f"{route['network_destination']} {route['netmask']} {route['gateway']} {route['interface']} {route['metric']} {route['route_type']}".lower()
                    if filter_value in search_text:
                        match = True
                
                if match:
                    self.filtered_routes.append(route)
        
        self.populate_route_tree()
        
    def clear_filter(self):
        """清除筛选"""
        self.filter_value_var.set("")
        self.filter_column_var.set("全部")
        self.apply_filter()
        
    def validate_route_params(self):
        """验证路由参数"""
        dest = self.dest_entry.get().strip()
        mask = self.mask_entry.get().strip()
        gateway = self.gateway_entry.get().strip()
        
        try:
            metric = int(self.metric_var.get())
        except ValueError:
            self.append_result("错误: 跃点数必须是数字\n")
            return
            
        if not all([dest, mask, gateway]):
            self.append_result("错误: 请填写完整的路由信息\n")
            return
            
        self.append_result(f"正在验证路由参数: {dest} mask {mask} gateway {gateway} metric {metric}\n")
        
        # 验证参数
        validation = self.route_service.validate_route_params(dest, mask, gateway, metric)
        if validation['valid']:
            self.append_result("✓ 路由参数验证通过\n")
            
            # 检查路由冲突
            conflict_check = self.route_service.check_route_conflict(dest, mask)
            if conflict_check['conflict']:
                self.append_result(f"⚠ 警告: {conflict_check['message']}\n")
            else:
                self.append_result("✓ 无路由冲突\n")
        else:
            self.append_result(f"✗ 参数验证失败: {validation['error']}\n")
            
    def add_route(self):
        """添加路由"""
        dest = self.dest_entry.get().strip()
        mask = self.mask_entry.get().strip()
        gateway = self.gateway_entry.get().strip()
        
        try:
            metric = int(self.metric_var.get())
        except ValueError:
            mbox.showerror("输入错误", "跃点数必须是数字")
            return
            
        if not all([dest, mask, gateway]):
            mbox.showerror("输入错误", "请填写完整的路由信息")
            return
            
        self.append_result(f"\n正在添加路由: {dest} mask {mask} gateway {gateway} metric {metric}\n")
        
        def do_add_route():
            try:
                result = self.route_service.add_route(dest, mask, gateway, metric)
                self.after(0, lambda: self.handle_add_route_result(result))
            except Exception as e:
                self.after(0, lambda: self.append_result(f"添加路由出错: {str(e)}\n"))
        
        threading.Thread(target=do_add_route, daemon=True).start()
        
    def handle_add_route_result(self, result):
        """处理添加路由结果"""
        if result['success']:
            self.append_result(f"✓ {result['message']}\n")
            # 自动刷新路由表
            self.refresh_routes()
        else:
            self.append_result(f"✗ {result['error']}\n")
            
    def delete_selected_route(self):
        """删除选中的路由"""
        if not self.selected_route:
            mbox.showwarning("选择错误", "请先选择要删除的路由")
            return
            
        route = self.selected_route
        dest = route['network_destination']
        mask = route['netmask']
        gateway = route['gateway']
        
        # 确认删除
        if not mbox.askyesno("确认删除", 
                           f"确定要删除以下路由吗？\n\n"
                           f"目标网络: {dest}\n"
                           f"子网掩码: {mask}\n"
                           f"网关: {gateway}\n"
                           f"跃点数: {route['metric']}"):
            return
            
        self.append_result(f"\n正在删除路由: {dest} mask {mask} gateway {gateway}\n")
        
        def do_delete_route():
            try:
                result = self.route_service.delete_route(dest, mask, gateway)
                self.after(0, lambda: self.handle_delete_route_result(result))
            except Exception as e:
                self.after(0, lambda: self.append_result(f"删除路由出错: {str(e)}\n"))
        
        threading.Thread(target=do_delete_route, daemon=True).start()
        
    def handle_delete_route_result(self, result):
        """处理删除路由结果"""
        if result['success']:
            self.append_result(f"✓ {result['message']}\n")
            self.selected_route = None
            # 自动刷新路由表
            self.refresh_routes()
        else:
            self.append_result(f"✗ {result['error']}\n")
            
    def clear_result(self):
        """清空结果框"""
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.configure(state=DISABLED)
        
    def append_result(self, text):
        """向结果框追加文本"""
        self.result_text.configure(state=NORMAL)
        self.result_text.insert(END, text)
        self.result_text.configure(state=DISABLED)
        self.result_text.see(END) 