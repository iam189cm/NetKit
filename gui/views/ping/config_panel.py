"""
Ping配置面板模块

负责用户输入和参数设置的GUI组件
包括目标地址输入、测试参数配置等
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper


class PingConfigPanel(tb.LabelFrame):
    """Ping配置面板"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="目标设置", padding=ui_helper.get_padding(15), **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """设置配置面板UI"""
        # 目标地址/范围输入
        target_frame = tb.Frame(self)
        target_frame.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        tb.Label(target_frame, text="目标地址/范围:").pack(anchor=W, pady=(0, ui_helper.get_padding(5)))
        self.target_entry = tb.Entry(target_frame, width=ui_helper.scale_size(30))
        self.target_entry.pack(fill=X)
        
        # 添加说明文本
        help_text = tb.Label(
            target_frame,
            text="支持格式: 单个IP、IP范围(1.1.1.1-1.1.1.100)、CIDR(192.168.1.0/24)、主机名",
            font=('微软雅黑', ui_helper.scale_size(8)),
            bootstyle=SECONDARY
        )
        help_text.pack(anchor=W, pady=(ui_helper.get_padding(5), 0))
        
        # 预设目标按钮
        preset_frame = tb.Frame(target_frame)
        preset_frame.pack(fill=X, pady=(ui_helper.get_padding(10), 0))
        
        preset_targets = [
            ("百度", "www.baidu.com"),
            ("谷歌DNS", "8.8.8.8"),
            ("本地网关", "192.168.1.1"),
            ("本机回环", "127.0.0.1")
        ]
        
        for i, (name, target) in enumerate(preset_targets):
            btn = tb.Button(
                preset_frame,
                text=name,
                bootstyle=OUTLINE,
                width=ui_helper.scale_size(8),
                command=lambda t=target: self.set_target(t)
            )
            btn.grid(row=0, column=i, padx=ui_helper.get_padding(2), sticky=W)
    
    def set_target(self, target):
        """设置目标地址"""
        self.target_entry.delete(0, END)
        self.target_entry.insert(0, target)
    
    def get_target(self):
        """获取目标地址"""
        return self.target_entry.get().strip()
    
    def clear_target(self):
        """清空目标地址"""
        self.target_entry.delete(0, END)


class PingParametersPanel(tb.LabelFrame):
    """Ping参数配置面板"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="测试参数", padding=ui_helper.get_padding(15), **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """设置参数配置UI"""
        # 参数网格布局
        params_grid = tb.Frame(self)
        params_grid.pack(fill=X)
        
        # Ping次数
        tb.Label(params_grid, text="Ping次数:").grid(
            row=0, column=0, sticky=W, pady=ui_helper.get_padding(5)
        )
        self.count_var = tb.StringVar(value="5")
        count_spinbox = tb.Spinbox(
            params_grid, 
            from_=1, to=100, 
            textvariable=self.count_var,
            width=ui_helper.scale_size(10)
        )
        count_spinbox.grid(
            row=0, column=1, 
            padx=(ui_helper.get_padding(10), 0), 
            pady=ui_helper.get_padding(5), 
            sticky=W
        )
        
        # 超时时间
        tb.Label(params_grid, text="超时时间(ms):").grid(
            row=1, column=0, sticky=W, pady=ui_helper.get_padding(5)
        )
        self.timeout_var = tb.StringVar(value="3000")
        timeout_spinbox = tb.Spinbox(
            params_grid, 
            from_=100, to=10000, 
            increment=100,
            textvariable=self.timeout_var,
            width=ui_helper.scale_size(10)
        )
        timeout_spinbox.grid(
            row=1, column=1, 
            padx=(ui_helper.get_padding(10), 0), 
            pady=ui_helper.get_padding(5), 
            sticky=W
        )
        
        # 并发数
        tb.Label(params_grid, text="并发数:").grid(
            row=2, column=0, sticky=W, pady=ui_helper.get_padding(5)
        )
        self.concurrent_var = tb.StringVar(value="25")
        concurrent_spinbox = tb.Spinbox(
            params_grid, 
            from_=1, to=100, 
            textvariable=self.concurrent_var,
            width=ui_helper.scale_size(10)
        )
        concurrent_spinbox.grid(
            row=2, column=1, 
            padx=(ui_helper.get_padding(10), 0), 
            pady=ui_helper.get_padding(5), 
            sticky=W
        )
        
        # 连续测试间隔
        tb.Label(params_grid, text="连续间隔(s):").grid(
            row=3, column=0, sticky=W, pady=ui_helper.get_padding(5)
        )
        self.interval_var = tb.StringVar(value="1")
        interval_spinbox = tb.Spinbox(
            params_grid, 
            from_=1, to=60, 
            textvariable=self.interval_var,
            width=ui_helper.scale_size(10)
        )
        interval_spinbox.grid(
            row=3, column=1, 
            padx=(ui_helper.get_padding(10), 0), 
            pady=ui_helper.get_padding(5), 
            sticky=W
        )
        
        # 参数预设
        preset_frame = tb.LabelFrame(self, text="参数预设", padding=ui_helper.get_padding(10))
        preset_frame.pack(fill=X, pady=(ui_helper.get_padding(15), 0))
        
        presets_grid = tb.Frame(preset_frame)
        presets_grid.pack(fill=X)
        
        presets = [
            ("快速", {"count": "3", "timeout": "1000", "concurrent": "50", "interval": "1"}),
            ("标准", {"count": "5", "timeout": "3000", "concurrent": "25", "interval": "1"}),
            ("详细", {"count": "10", "timeout": "5000", "concurrent": "10", "interval": "2"}),
            ("保守", {"count": "3", "timeout": "10000", "concurrent": "5", "interval": "3"})
        ]
        
        for i, (name, params) in enumerate(presets):
            btn = tb.Button(
                presets_grid,
                text=name,
                bootstyle=OUTLINE,
                width=ui_helper.scale_size(8),
                command=lambda p=params: self.apply_preset(p)
            )
            btn.grid(row=0, column=i, padx=ui_helper.get_padding(2))
    
    def apply_preset(self, params):
        """应用参数预设"""
        self.count_var.set(params["count"])
        self.timeout_var.set(params["timeout"])
        self.concurrent_var.set(params["concurrent"])
        self.interval_var.set(params["interval"])
    
    def get_parameters(self):
        """获取当前参数设置"""
        return {
            'count': int(self.count_var.get()),
            'timeout': int(self.timeout_var.get()),
            'concurrent': int(self.concurrent_var.get()),
            'interval': int(self.interval_var.get())
        }
    
    def set_parameters(self, params):
        """设置参数"""
        if 'count' in params:
            self.count_var.set(str(params['count']))
        if 'timeout' in params:
            self.timeout_var.set(str(params['timeout']))
        if 'concurrent' in params:
            self.concurrent_var.set(str(params['concurrent']))
        if 'interval' in params:
            self.interval_var.set(str(params['interval']))
    
    def reset_to_defaults(self):
        """重置为默认参数"""
        self.apply_preset({
            "count": "5",
            "timeout": "3000", 
            "concurrent": "25",
            "interval": "1"
        }) 