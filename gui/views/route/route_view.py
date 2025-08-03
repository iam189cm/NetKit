import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.route.route import RouteService
import tkinter.messagebox as mbox
import threading
from tkinter import ttk

# 导入拆分后的UI组件
from .route_table_widget import RouteTableWidget
from .route_form_widget import RouteFormWidget
from .action_buttons_widget import ActionButtonsWidget
from .result_display_widget import ResultDisplayWidget


class RouteFrame(tb.Frame):
    """静态路由主视图 - 组件协调器"""
    
    def __init__(self, master, readonly_mode=False, **kwargs):
        super().__init__(master, **kwargs)
        self.readonly_mode = readonly_mode
        self.route_service = RouteService()
        self.selected_route = None
        
        # UI组件引用
        self.route_table = None
        self.route_form = None
        self.action_buttons = None
        self.result_display = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置静态路由界面 - 组件协调模式"""
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 创建路由表组件
        self.route_table = RouteTableWidget(
            main_frame, 
            on_route_selected=self.on_route_selected
        )
        self.route_table.pack(fill=BOTH, expand=True, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        # 创建路由表单组件
        self.route_form = RouteFormWidget(
            main_frame,
            readonly_mode=self.readonly_mode
        )
        
        # 创建操作按钮组件
        callbacks = {
            'add_route': self.add_route,
            'delete_route': self.delete_selected_route,
            'refresh_routes': self.refresh_routes
        }
        self.action_buttons = ActionButtonsWidget(
            self.route_form,
            callbacks=callbacks,
            readonly_mode=self.readonly_mode
        )
        
        # 将按钮组件添加到表单组件中
        self.action_buttons.pack(fill=X)
        
        # 表单组件包装
        self.route_form.pack(fill=X)
        
        # 创建结果显示组件
        self.result_display = ResultDisplayWidget(main_frame)
        self.result_display.pack(fill=X, pady=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        # 初始化时刷新路由表
        self.refresh_routes()
        
    def on_route_selected(self, route_data):
        """路由选择事件协调"""
        self.selected_route = route_data
        
    def refresh_routes(self):
        """刷新路由表"""
        self.result_display.append_info("正在获取路由表...\n")
        
        def do_refresh():
            try:
                result = self.route_service.get_route_table()
                self.after(0, lambda: self.update_route_table(result))
            except Exception as e:
                self.after(0, lambda: self.result_display.append_error(f"获取路由表出错: {str(e)}\n"))
        
        threading.Thread(target=do_refresh, daemon=True).start()
        
    def update_route_table(self, result):
        """更新路由表显示"""
        if result['success']:
            routes_data = result['routes']
            self.route_table.update_routes(routes_data)
            self.result_display.append_success(f"路由表刷新成功，共 {len(routes_data)} 条路由\n")
        else:
            self.result_display.append_error(f"获取路由表失败: {result['error']}\n")
            

            

            
    def add_route(self):
        """添加路由"""
        try:
            # 从表单组件获取数据
            is_valid, route_data = self.route_form.validate_input()
            if not is_valid:
                mbox.showerror("输入错误", route_data)
                return
                
            dest = route_data['destination']
            mask = route_data['netmask']
            gateway = route_data['gateway']
            metric = route_data['metric']
            
            self.result_display.append_info(f"\n正在添加路由: {dest} mask {mask} gateway {gateway} metric {metric}\n")
            
            def do_add_route():
                try:
                    result = self.route_service.add_route(dest, mask, gateway, metric)
                    self.after(0, lambda: self.handle_add_route_result(result))
                except Exception as e:
                    self.after(0, lambda: self.result_display.append_error(f"添加路由出错: {str(e)}\n"))
            
            threading.Thread(target=do_add_route, daemon=True).start()
            
        except Exception as e:
            mbox.showerror("操作错误", str(e))
        
    def handle_add_route_result(self, result):
        """处理添加路由结果"""
        if result['success']:
            self.result_display.append_success(f"{result['message']}\n")
            # 清空表单
            self.route_form.clear_form()
            # 自动刷新路由表
            self.refresh_routes()
        else:
            self.result_display.append_error(f"{result['error']}\n")
            
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
            
        self.result_display.append_info(f"\n正在删除路由: {dest} mask {mask} gateway {gateway}\n")
        
        def do_delete_route():
            try:
                result = self.route_service.delete_route(dest, mask, gateway)
                self.after(0, lambda: self.handle_delete_route_result(result))
            except Exception as e:
                self.after(0, lambda: self.result_display.append_error(f"删除路由出错: {str(e)}\n"))
        
        threading.Thread(target=do_delete_route, daemon=True).start()
        
    def handle_delete_route_result(self, result):
        """处理删除路由结果"""
        if result['success']:
            self.result_display.append_success(f"{result['message']}\n")
            self.selected_route = None
            self.route_table.clear_selection()
            # 自动刷新路由表
            self.refresh_routes()
        else:
            self.result_display.append_error(f"{result['error']}\n")
            
            
        
    # 兼容性方法，委托给结果显示组件
    def append_result(self, text):
        """向结果框追加文本（兼容性接口）"""
        if self.result_display:
            self.result_display.append_result(text) 