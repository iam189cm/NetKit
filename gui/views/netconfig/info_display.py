"""
网卡信息显示UI组件
负责显示网卡的详细信息
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.services.netconfig.interface_info import get_network_card_info


class InfoDisplayWidget(tb.LabelFrame):
    """网卡信息显示组件"""
    
    def __init__(self, master, on_status_update=None, **kwargs):
        super().__init__(master, text="当前网卡信息", padding=20, **kwargs)
        
        # 回调函数
        self.on_status_update = on_status_update
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 创建信息显示区域（1列布局）
        info_container = tb.Frame(self)
        info_container.pack(fill=X)
        
        # 信息字段定义（10行显示）
        self.info_fields = [
            ("网卡名称:", "name_label"),
            ("描述:", "desc_label"),
            ("状态:", "status_label"),
            ("物理地址:", "mac_label"),
            ("速度:", "speed_label"),
            ("IP地址:", "ip_label"),
            ("子网掩码:", "mask_label"),
            ("默认网关:", "gateway_label"),
            ("DNS服务器1:", "dns1_label"),
            ("DNS服务器2:", "dns2_label")
        ]
        
        # 创建信息显示标签（每行一个信息）
        for i, (label_text, attr_name) in enumerate(self.info_fields):
            field_frame = tb.Frame(info_container)
            field_frame.pack(fill=X, pady=2)
            
            tb.Label(field_frame, text=label_text, font=('Microsoft YaHei', 9), width=12).pack(side=LEFT)
            label = tb.Label(field_frame, text="未选择", font=('Microsoft YaHei', 9), bootstyle=SECONDARY)
            label.pack(side=LEFT, padx=(10, 0))
            setattr(self, attr_name, label)
    
    def _append_status(self, text):
        """追加状态信息"""
        if self.on_status_update:
            self.on_status_update(text)
    
    def show_no_selection_info(self):
        """显示未选择网卡的状态"""
        # 重置所有信息显示为"未选择网卡"
        for _, attr_name in self.info_fields:
            label = getattr(self, attr_name)
            label.config(text="未选择网卡")
    
    def update_interface_info(self, interface_name):
        """更新网卡信息显示"""
        if not interface_name:
            self.show_no_selection_info()
            return
            
        try:
            # 获取网卡详细信息
            info = get_network_card_info(interface_name)
            
            # 更新信息显示
            self.name_label.config(text=info.get('name', '未知'))
            self.desc_label.config(text=info.get('description', '未知'))
            self.status_label.config(text=info.get('status', '未知'))
            self.mac_label.config(text=info.get('mac', '未知'))
            self.speed_label.config(text=info.get('speed', '未知'))
            self.ip_label.config(text=info.get('ip', '未配置'))
            self.mask_label.config(text=info.get('mask', '未配置'))
            self.gateway_label.config(text=info.get('gateway', '未配置'))
            
            # 分别显示两个DNS服务器
            self.dns1_label.config(text=info.get('dns1', '未配置'))
            self.dns2_label.config(text=info.get('dns2', '未配置'))
            
            self._append_status(f"已选择网卡: {info.get('name', interface_name)}\n")
            
        except Exception as e:
            self._append_status(f"获取网卡信息失败: {str(e)}\n")
            # 重置信息显示
            for _, attr_name in self.info_fields:
                label = getattr(self, attr_name)
                label.config(text="获取失败")
    
    def get_current_info(self):
        """获取当前显示的网卡信息"""
        info = {}
        for label_text, attr_name in self.info_fields:
            label = getattr(self, attr_name)
            field_name = attr_name.replace('_label', '')
            info[field_name] = label.cget('text')
        return info 