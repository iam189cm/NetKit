"""
子网计算主视图
整合所有子网计算相关的UI组件
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from .input_form import SubnetInputForm
from .result_display import SubnetResultDisplay
from .subnet_divider import SubnetDivider


class SubnetView(tb.Frame):
    """子网计算主视图"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # 当前计算结果
        self.current_network_info = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=ui_helper.get_padding(20))
        
        # 创建输入表单
        self.input_form = SubnetInputForm(
            main_frame,
            on_calculate=self.on_calculate,
            on_clear=self.on_clear
        )
        self.input_form.pack(fill=X, pady=(0, ui_helper.get_padding(15)))
        
        # 创建计算结果显示
        self.result_display = SubnetResultDisplay(main_frame)
        self.result_display.pack(fill=X, pady=(0, ui_helper.get_padding(15)))
        
        # 创建子网划分组件
        self.subnet_divider = SubnetDivider(
            main_frame,
            on_divide=self.on_divide_subnet
        )
        self.subnet_divider.pack(fill=BOTH, expand=True)
        
        # 默认执行一次计算
        self.input_form.calculate()
    
    def on_calculate(self, network_info: dict):
        """处理计算事件"""
        # 保存当前网络信息
        self.current_network_info = network_info
        
        # 更新结果显示
        self.result_display.update_results(network_info)
        
        # 更新子网划分组件的当前网络信息
        network_str = f"{network_info['网络地址']}{network_info['CIDR表示']}"
        hosts_count = network_info['可用主机数']
        self.subnet_divider.update_network_info(network_str, hosts_count)
    
    def on_clear(self):
        """处理清空事件"""
        # 清空结果显示
        self.result_display.clear_results()
        
        # 清空子网划分结果
        self.subnet_divider.clear_results()
        
        # 清空当前网络信息
        self.current_network_info = None
    
    def on_divide_subnet(self, divide_results: list):
        """处理子网划分结果"""
        # 子网划分组件会自己显示结果，这里可以做额外处理
        pass