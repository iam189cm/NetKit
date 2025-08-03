"""
路由操作表单组件
职责：输入表单管理、前端验证、数据收集
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
import tkinter.messagebox as mbox


class RouteFormWidget(tb.LabelFrame):
    """路由操作表单组件"""
    
    def __init__(self, master, readonly_mode=False, **kwargs):
        super().__init__(master, text="路由操作", padding=ui_helper.get_padding(15), **kwargs)
        
        self.readonly_mode = readonly_mode
        self.setup_form()
        
    def setup_form(self):
        """设置表单字段"""
        # 添加路由区域
        add_frame = tb.Frame(self)
        add_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        # 第一行：目标网络和子网掩码
        row1_frame = tb.Frame(add_frame)
        row1_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        tb.Label(row1_frame, text="目标网络:").pack(side=LEFT)
        self.dest_entry = tb.Entry(row1_frame, width=ui_helper.scale_size(15))
        self.dest_entry.pack(side=LEFT, padx=(ui_helper.get_padding(5), ui_helper.get_padding(10)))
        
        tb.Label(row1_frame, text="子网掩码:").pack(side=LEFT)
        self.mask_entry = tb.Entry(row1_frame, width=ui_helper.scale_size(15))
        self.mask_entry.pack(side=LEFT, padx=(ui_helper.get_padding(5), ui_helper.get_padding(10)))
        
        # 第二行：网关和跃点数
        row2_frame = tb.Frame(add_frame)
        row2_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        tb.Label(row2_frame, text="网关地址:").pack(side=LEFT)
        self.gateway_entry = tb.Entry(row2_frame, width=ui_helper.scale_size(15))
        self.gateway_entry.pack(side=LEFT, padx=(ui_helper.get_padding(5), ui_helper.get_padding(10)))
        
        tb.Label(row2_frame, text="跃点数:").pack(side=LEFT)
        self.metric_var = tb.StringVar(value="1")
        self.metric_spinbox = tb.Spinbox(
            row2_frame,
            from_=1, to=9999,
            textvariable=self.metric_var,
            width=ui_helper.scale_size(8)
        )
        self.metric_spinbox.pack(side=LEFT, padx=(ui_helper.get_padding(5), ui_helper.get_padding(10)))
        
        # 在只读模式下禁用输入框
        if self.readonly_mode:
            self.set_readonly(True)
            
    def get_route_data(self):
        """获取表单数据"""
        dest = self.dest_entry.get().strip()
        mask = self.mask_entry.get().strip()
        gateway = self.gateway_entry.get().strip()
        
        try:
            metric = int(self.metric_var.get())
        except ValueError:
            raise ValueError("跃点数必须是数字")
            
        if not all([dest, mask, gateway]):
            raise ValueError("请填写完整的路由信息")
            
        return {
            'destination': dest,
            'netmask': mask,
            'gateway': gateway,
            'metric': metric
        }
        
    def clear_form(self):
        """清空表单"""
        self.dest_entry.delete(0, END)
        self.mask_entry.delete(0, END)
        self.gateway_entry.delete(0, END)
        self.metric_var.set("1")
        
    def validate_input(self):
        """前端输入验证"""
        try:
            route_data = self.get_route_data()
            return True, route_data
        except ValueError as e:
            return False, str(e)
            
    def set_readonly(self, readonly):
        """设置只读状态"""
        self.readonly_mode = readonly
        state = DISABLED if readonly else NORMAL
        
        self.dest_entry.config(state=state)
        self.mask_entry.config(state=state)
        self.gateway_entry.config(state=state)
        self.metric_spinbox.config(state=state)