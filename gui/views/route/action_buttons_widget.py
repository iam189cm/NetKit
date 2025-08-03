"""
操作按钮组件
职责：按钮管理、状态控制、事件分发
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper


class ActionButtonsWidget(tb.Frame):
    """操作按钮组件"""
    
    def __init__(self, master, callbacks=None, readonly_mode=False, **kwargs):
        super().__init__(master, **kwargs)
        
        self.callbacks = callbacks or {}
        self.readonly_mode = readonly_mode
        self.buttons = {}
        
        self.setup_buttons()
        
    def setup_buttons(self):
        """设置按钮"""
        # 操作按钮
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, pady=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        # 添加路由按钮
        self.buttons['add'] = tb.Button(
            btn_frame,
            text="添加路由",
            bootstyle=SUCCESS,
            command=self._on_add_route,
            width=ui_helper.scale_size(12)
        )
        self.buttons['add'].pack(side=LEFT, padx=ui_helper.get_padding(5))
        
        # 删除选中按钮
        self.buttons['delete'] = tb.Button(
            btn_frame,
            text="删除选中",
            bootstyle=DANGER,
            command=self._on_delete_route,
            width=ui_helper.scale_size(12)
        )
        self.buttons['delete'].pack(side=LEFT, padx=ui_helper.get_padding(5))
        
        # 刷新路由表按钮
        self.buttons['refresh'] = tb.Button(
            btn_frame,
            text="刷新路由表",
            bootstyle=INFO,
            command=self._on_refresh_routes,
            width=ui_helper.scale_size(12)
        )
        self.buttons['refresh'].pack(side=LEFT, padx=ui_helper.get_padding(5))
        
        # 在只读模式下禁用操作按钮
        if self.readonly_mode:
            self.set_readonly_mode(True)
            
    def _on_add_route(self):
        """添加路由按钮点击"""
        if 'add_route' in self.callbacks:
            self.callbacks['add_route']()
            
    def _on_delete_route(self):
        """删除路由按钮点击"""
        if 'delete_route' in self.callbacks:
            self.callbacks['delete_route']()
            
    def _on_refresh_routes(self):
        """刷新路由表按钮点击"""
        if 'refresh_routes' in self.callbacks:
            self.callbacks['refresh_routes']()
            
    def set_button_state(self, button_name, enabled):
        """设置按钮状态"""
        if button_name in self.buttons:
            state = NORMAL if enabled else DISABLED
            self.buttons[button_name].config(state=state)
            
    def set_readonly_mode(self, readonly):
        """设置只读模式"""
        self.readonly_mode = readonly
        
        # 在只读模式下禁用添加和删除按钮
        if readonly:
            self.set_button_state('add', False)
            self.set_button_state('delete', False)
        else:
            self.set_button_state('add', True)
            self.set_button_state('delete', True)
            
    def get_button(self, button_name):
        """获取按钮对象"""
        return self.buttons.get(button_name)