"""
网络配置主视图
整合所有网络配置相关的UI组件
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from .interface_selector import InterfaceSelectorWidget
from .info_display import InfoDisplayWidget
from .config_form import ConfigFormWidget
from .status_display import StatusDisplayWidget


class NetConfigView(tb.Frame):
    """网络配置主视图"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 标题
        title = tb.Label(
            self, 
            text="网卡配置", 
            font=('Microsoft YaHei', 18, 'bold'),
            bootstyle=PRIMARY
        )
        title.pack(pady=(0, 20))
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # 创建状态显示组件（先创建，因为其他组件需要引用）
        self.status_display = StatusDisplayWidget(main_frame)
        
        # 创建网卡选择器
        self.interface_selector = InterfaceSelectorWidget(
            main_frame,
            on_interface_selected=self.on_interface_selected,
            on_status_update=self.status_display.append_status
        )
        self.interface_selector.pack(fill=X, pady=(0, 15))
        
        # 创建网卡信息显示
        self.info_display = InfoDisplayWidget(
            main_frame,
            on_status_update=self.status_display.append_status
        )
        self.info_display.pack(fill=X, pady=(0, 15))
        
        # 创建配置表单
        self.config_form = ConfigFormWidget(
            main_frame,
            on_config_applied=self.on_config_applied,
            on_status_update=self.status_display.append_status
        )
        self.config_form.pack(fill=X, pady=(0, 15))
        
        # 状态显示区域
        self.status_display.pack(fill=BOTH, expand=True)
    
    def on_interface_selected(self, interface_name, display_name):
        """网卡选择事件处理"""
        # 更新信息显示
        self.info_display.update_interface_info(interface_name)
        
        # 更新配置表单的当前网卡
        self.config_form.set_current_interface(interface_name)
    
    def on_config_applied(self, interface_name):
        """配置应用完成事件处理"""
        # 刷新网卡信息显示
        self.info_display.after(1000, lambda: self.info_display.update_interface_info(interface_name))
        
        # 触发网卡列表刷新
        self.interface_selector.after(2000, lambda: self.interface_selector.refresh_interfaces())
    
    def cleanup(self):
        """清理资源"""
        # 清理网卡选择器资源
        self.interface_selector.cleanup()
    
    def get_selected_interface(self):
        """获取当前选择的网卡"""
        return self.interface_selector.get_selected_interface()
    
    def get_current_config(self):
        """获取当前配置"""
        return self.config_form.get_current_config()
    
    def append_status(self, text):
        """追加状态信息"""
        self.status_display.append_status(text) 