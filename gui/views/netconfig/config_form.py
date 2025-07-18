"""
IP配置表单UI组件
负责IP配置的输入和应用
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.netconfig.ip_configurator import apply_profile, validate_ip_config


class ConfigFormWidget(tb.LabelFrame):
    """IP配置表单组件"""
    
    def __init__(self, master, on_config_applied=None, on_status_update=None, **kwargs):
        super().__init__(master, text="网络配置", padding=ui_helper.get_padding(20), **kwargs)
        
        # 回调函数
        self.on_config_applied = on_config_applied
        self.on_status_update = on_status_update
        
        # 当前选择的网卡
        self.current_interface = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 配置字段（DNS分为两个输入框）
        self.config_fields = [
            ("IP地址:", "ip_entry", "例如: 192.168.1.100"),
            ("子网掩码:", "mask_entry", "例如: 255.255.255.0 或 24"),
            ("默认网关:", "gateway_entry", "例如: 192.168.1.1"),
            ("DNS服务器1:", "dns1_entry", "例如: 8.8.8.8"),
            ("DNS服务器2:", "dns2_entry", "例如: 8.8.4.4")
        ]
        
        # 创建配置输入字段
        for i, (label_text, entry_name, placeholder) in enumerate(self.config_fields):
            field_frame = tb.Frame(self)
            field_frame.pack(fill=X, pady=ui_helper.get_padding(5))
            
            # 标签
            tb.Label(field_frame, text=label_text, font=ui_helper.get_font(10), width=ui_helper.scale_size(12)).pack(side=LEFT)
            
            # 输入框
            entry = tb.Entry(field_frame, font=ui_helper.get_font(9), width=ui_helper.scale_size(40))
            entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
            entry.insert(0, placeholder)
            entry.bind('<FocusIn>', lambda e, ph=placeholder: self.on_entry_focus_in(e, ph))
            entry.bind('<FocusOut>', lambda e, ph=placeholder: self.on_entry_focus_out(e, ph))
            setattr(self, entry_name, entry)
            
            # DHCP复选框（只在IP地址行显示）
            if entry_name == "ip_entry":
                self.dhcp_var = tb.BooleanVar()
                self.dhcp_check = tb.Checkbutton(
                    field_frame,
                    text="DHCP",
                    variable=self.dhcp_var,
                    command=self.on_dhcp_changed
                )
                self.dhcp_check.pack(side=RIGHT, padx=(ui_helper.get_padding(20), 0))
        
        # 应用配置按钮
        button_frame = tb.Frame(self)
        button_frame.pack(fill=X, pady=(ui_helper.get_padding(20), 0))
        
        tb.Button(
            button_frame,
            text="应用配置",
            bootstyle=SUCCESS,
            command=self.apply_config,
            width=ui_helper.scale_size(15),        ).pack(anchor=CENTER)
    
    def _append_status(self, text):
        """追加状态信息"""
        if self.on_status_update:
            self.on_status_update(text)
    
    def on_entry_focus_in(self, event, placeholder):
        """输入框获得焦点时清除占位符"""
        if event.widget.get() == placeholder:
            event.widget.delete(0, END)
            event.widget.config(foreground='white')
    
    def on_entry_focus_out(self, event, placeholder):
        """输入框失去焦点时恢复占位符"""
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(foreground='gray')
    
    def on_dhcp_changed(self):
        """DHCP选项改变时的处理"""
        is_dhcp = self.dhcp_var.get()
        
        # 禁用或启用相关输入框
        state = DISABLED if is_dhcp else NORMAL
        self.ip_entry.config(state=state)
        self.mask_entry.config(state=state)
        self.gateway_entry.config(state=state)
        
        if is_dhcp:
            self._append_status("已启用DHCP模式\n")
        else:
            self._append_status("已禁用DHCP模式，请手动配置IP信息\n")
    
    def get_entry_value(self, entry, placeholder):
        """获取输入框的实际值（排除占位符）"""
        value = entry.get().strip()
        return "" if value == placeholder else value
    
    def set_current_interface(self, interface_name):
        """设置当前选择的网卡"""
        self.current_interface = interface_name
    
    def apply_config(self):
        """应用网络配置"""
        if not self.current_interface:
            self._append_status("错误: 请选择网络接口\n")
            return
        
        is_dhcp = self.dhcp_var.get()
        
        if is_dhcp:
            # DHCP模式
            self._append_status(f"\n正在为接口 '{self.current_interface}' 启用DHCP...\n")
            self._append_status("-" * 50 + "\n")
            
            try:
                result = apply_profile(self.current_interface, "", "", "", "", dhcp=True)
                if result['success']:
                    self._append_status("✓ DHCP配置应用成功!\n\n")
                    # 通知配置已应用
                    if self.on_config_applied:
                        self.on_config_applied(self.current_interface)
                else:
                    self._append_status(f"✗ DHCP配置失败: {result['error']}\n\n")
            except Exception as e:
                self._append_status(f"✗ 执行出错: {str(e)}\n\n")
        else:
            # 静态IP模式
            ip = self.get_entry_value(self.ip_entry, "例如: 192.168.1.100")
            mask = self.get_entry_value(self.mask_entry, "例如: 255.255.255.0 或 24")
            gateway = self.get_entry_value(self.gateway_entry, "例如: 192.168.1.1")
            dns1 = self.get_entry_value(self.dns1_entry, "例如: 8.8.8.8")
            dns2 = self.get_entry_value(self.dns2_entry, "例如: 8.8.4.4")
            
            # 验证必填字段
            if not all([ip, mask, gateway]):
                self._append_status("错误: 请完整填写IP地址、子网掩码和默认网关\n")
                return
            
            # 验证配置
            validation = validate_ip_config(ip, mask, gateway, f"{dns1},{dns2}")
            if not validation['valid']:
                self._append_status(f"配置验证失败: {validation['error']}\n")
                return
            
            # 应用配置
            self._append_status(f"\n正在应用静态IP配置到接口 '{self.current_interface}'...\n")
            self._append_status(f"IP地址: {ip}\n")
            self._append_status(f"子网掩码: {mask}\n")
            self._append_status(f"默认网关: {gateway}\n")
            if dns1 or dns2:
                self._append_status(f"DNS服务器: {dns1}, {dns2}\n")
            self._append_status("-" * 50 + "\n")
            
            try:
                result = apply_profile(self.current_interface, ip, mask, gateway, f"{dns1},{dns2}", dhcp=False)
                if result['success']:
                    self._append_status("✓ 静态IP配置应用成功!\n\n")
                    # 通知配置已应用
                    if self.on_config_applied:
                        self.on_config_applied(self.current_interface)
                else:
                    self._append_status(f"✗ 静态IP配置失败: {result['error']}\n\n")
            except Exception as e:
                self._append_status(f"✗ 执行出错: {str(e)}\n\n")
    
    def get_current_config(self):
        """获取当前配置"""
        return {
            'dhcp': self.dhcp_var.get(),
            'ip': self.get_entry_value(self.ip_entry, "例如: 192.168.1.100"),
            'mask': self.get_entry_value(self.mask_entry, "例如: 255.255.255.0 或 24"),
            'gateway': self.get_entry_value(self.gateway_entry, "例如: 192.168.1.1"),
            'dns1': self.get_entry_value(self.dns1_entry, "例如: 8.8.8.8"),
            'dns2': self.get_entry_value(self.dns2_entry, "例如: 8.8.4.4")
        }
    
    def reset_form(self):
        """重置表单"""
        # 重置DHCP选项
        self.dhcp_var.set(False)
        self.on_dhcp_changed()
        
        # 重置所有输入框
        for _, entry_name, placeholder in self.config_fields:
            entry = getattr(self, entry_name)
            entry.delete(0, END)
            entry.insert(0, placeholder)
            entry.config(foreground='gray') 