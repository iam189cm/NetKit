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
        # 创建主要配置区域的水平布局框架
        config_main_frame = tb.Frame(self)
        config_main_frame.pack(fill=BOTH, expand=True, pady=(0, ui_helper.get_padding(15)))
        
        # IP地址配置分组（左侧）
        self.setup_ip_config_group(config_main_frame)
        
        # DNS服务器配置分组（右侧）
        self.setup_dns_config_group(config_main_frame)
        
        # 应用配置按钮
        self.setup_apply_button()
    
    def setup_ip_config_group(self, parent):
        """设置IP地址配置分组"""
        # IP地址配置分组框（左侧，平分水平空间）
        ip_group = tb.LabelFrame(parent, text="IP地址配置", padding=ui_helper.get_padding(15))
        ip_group.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, ui_helper.get_padding(5)))
        
        # IP配置模式选择变量
        self.ip_mode_var = tb.StringVar(value="manual")  # 默认选择手动配置
        
        # 自动获得IP地址单选按钮
        self.ip_auto_radio = tb.Radiobutton(
            ip_group,
            text="自动获得IP地址(DHCP)",
            variable=self.ip_mode_var,
            value="auto",
            command=self.on_ip_mode_changed
        )
        self.ip_auto_radio.pack(anchor=W, pady=ui_helper.get_padding(5))
        
        # 使用下面的IP地址单选按钮
        self.ip_manual_radio = tb.Radiobutton(
            ip_group,
            text="使用下面的IP地址",
            variable=self.ip_mode_var,
            value="manual",
            command=self.on_ip_mode_changed
        )
        self.ip_manual_radio.pack(anchor=W, pady=ui_helper.get_padding(5))
        
        # IP配置输入区域
        ip_input_frame = tb.Frame(ip_group)
        ip_input_frame.pack(fill=X, padx=(ui_helper.get_padding(25), 0), pady=ui_helper.get_padding(10))
        
        # IP地址输入
        ip_frame = tb.Frame(ip_input_frame)
        ip_frame.pack(fill=X, pady=ui_helper.get_padding(5))
        tb.Label(ip_frame, text="IP地址:", font=ui_helper.get_font(10), width=ui_helper.scale_size(12)).pack(side=LEFT)
        self.ip_entry = tb.Entry(ip_frame, font=ui_helper.get_font(9), width=ui_helper.scale_size(25))
        self.ip_entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # 子网掩码输入
        mask_frame = tb.Frame(ip_input_frame)
        mask_frame.pack(fill=X, pady=ui_helper.get_padding(5))
        tb.Label(mask_frame, text="子网掩码:", font=ui_helper.get_font(10), width=ui_helper.scale_size(12)).pack(side=LEFT)
        self.mask_entry = tb.Entry(mask_frame, font=ui_helper.get_font(9), width=ui_helper.scale_size(25))
        self.mask_entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # 默认网关输入
        gateway_frame = tb.Frame(ip_input_frame)
        gateway_frame.pack(fill=X, pady=ui_helper.get_padding(5))
        tb.Label(gateway_frame, text="默认网关:", font=ui_helper.get_font(10), width=ui_helper.scale_size(12)).pack(side=LEFT)
        self.gateway_entry = tb.Entry(gateway_frame, font=ui_helper.get_font(9), width=ui_helper.scale_size(25))
        self.gateway_entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
    
    def setup_dns_config_group(self, parent):
        """设置DNS服务器配置分组"""
        # DNS服务器配置分组框（右侧，平分水平空间）
        dns_group = tb.LabelFrame(parent, text="DNS服务器配置", padding=ui_helper.get_padding(15))
        dns_group.pack(side=LEFT, fill=BOTH, expand=True, padx=(ui_helper.get_padding(5), 0))
        
        # DNS配置模式选择变量
        self.dns_mode_var = tb.StringVar(value="manual")  # 默认选择手动配置
        
        # 自动获取DNS服务器地址单选按钮
        self.dns_auto_radio = tb.Radiobutton(
            dns_group,
            text="自动获取DNS服务器地址",
            variable=self.dns_mode_var,
            value="auto",
            command=self.on_dns_mode_changed
        )
        self.dns_auto_radio.pack(anchor=W, pady=ui_helper.get_padding(5))
        
        # 使用下面的DNS服务器地址单选按钮
        self.dns_manual_radio = tb.Radiobutton(
            dns_group,
            text="使用下面的DNS服务器地址",
            variable=self.dns_mode_var,
            value="manual",
            command=self.on_dns_mode_changed
        )
        self.dns_manual_radio.pack(anchor=W, pady=ui_helper.get_padding(5))
        
        # DNS配置输入区域
        dns_input_frame = tb.Frame(dns_group)
        dns_input_frame.pack(fill=X, padx=(ui_helper.get_padding(25), 0), pady=ui_helper.get_padding(10))
        
        # 首选DNS服务器输入
        dns1_frame = tb.Frame(dns_input_frame)
        dns1_frame.pack(fill=X, pady=ui_helper.get_padding(5))
        tb.Label(dns1_frame, text="首选DNS服务器:", font=ui_helper.get_font(10), width=ui_helper.scale_size(15)).pack(side=LEFT)
        self.dns1_entry = tb.Entry(dns1_frame, font=ui_helper.get_font(9), width=ui_helper.scale_size(25))
        self.dns1_entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # 备用DNS服务器输入
        dns2_frame = tb.Frame(dns_input_frame)
        dns2_frame.pack(fill=X, pady=ui_helper.get_padding(5))
        tb.Label(dns2_frame, text="备用DNS服务器:", font=ui_helper.get_font(10), width=ui_helper.scale_size(15)).pack(side=LEFT)
        self.dns2_entry = tb.Entry(dns2_frame, font=ui_helper.get_font(9), width=ui_helper.scale_size(25))
        self.dns2_entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
    
    def setup_apply_button(self):
        """设置应用配置按钮"""
        button_frame = tb.Frame(self)
        button_frame.pack(fill=X, pady=(ui_helper.get_padding(20), 0))
        
        tb.Button(
            button_frame,
            text="应用配置",
            bootstyle=SUCCESS,
            command=self.apply_config,
            width=ui_helper.scale_size(15)
        ).pack(anchor=CENTER)
    
    def on_ip_mode_changed(self):
        """IP配置模式改变时的处理"""
        is_manual = self.ip_mode_var.get() == "manual"
        state = NORMAL if is_manual else DISABLED
        
        # 设置IP相关输入框的状态
        self.ip_entry.config(state=state)
        self.mask_entry.config(state=state)
        self.gateway_entry.config(state=state)
        
        # 根据状态调整外观
        if is_manual:
            # 手动模式：恢复正常外观
            self.ip_entry.config(background='white', foreground='black')
            self.mask_entry.config(background='white', foreground='black')
            self.gateway_entry.config(background='white', foreground='black')
        else:
            # 自动模式：设置为禁用外观
            self.ip_entry.config(background='#f0f0f0', foreground='gray')
            self.mask_entry.config(background='#f0f0f0', foreground='gray')
            self.gateway_entry.config(background='#f0f0f0', foreground='gray')
        
        # 状态提示
        if is_manual:
            self._append_status("已选择手动配置IP地址\n")
        else:
            self._append_status("已选择自动获得IP地址(DHCP)\n")
    
    def on_dns_mode_changed(self):
        """DNS配置模式改变时的处理"""
        is_manual = self.dns_mode_var.get() == "manual"
        state = NORMAL if is_manual else DISABLED
        
        # 设置DNS相关输入框的状态
        self.dns1_entry.config(state=state)
        self.dns2_entry.config(state=state)
        
        # 根据状态调整外观
        if is_manual:
            # 手动模式：恢复正常外观
            self.dns1_entry.config(background='white', foreground='black')
            self.dns2_entry.config(background='white', foreground='black')
        else:
            # 自动模式：设置为禁用外观
            self.dns1_entry.config(background='#f0f0f0', foreground='gray')
            self.dns2_entry.config(background='#f0f0f0', foreground='gray')
        
        # 状态提示
        if is_manual:
            self._append_status("已选择手动配置DNS服务器地址\n")
        else:
            self._append_status("已选择自动获取DNS服务器地址\n")
    
    def _append_status(self, text):
        """追加状态信息"""
        if self.on_status_update:
            self.on_status_update(text)
    
    def get_entry_value(self, entry):
        """获取输入框的实际值"""
        return entry.get().strip()
    
    def set_current_interface(self, interface_name):
        """设置当前选择的网卡"""
        self.current_interface = interface_name
    
    def apply_config(self):
        """应用网络配置"""
        if not self.current_interface:
            self._append_status("错误: 请选择网络接口\n")
            return
        
        # 获取配置模式
        ip_mode = self.ip_mode_var.get()  # 'auto' 或 'manual'
        dns_mode = self.dns_mode_var.get()  # 'auto' 或 'manual'
        
        # 获取配置参数
        ip_config = {
            'ip': self.get_entry_value(self.ip_entry),
            'mask': self.get_entry_value(self.mask_entry),
            'gateway': self.get_entry_value(self.gateway_entry)
        }
        
        dns_config = {
            'dns1': self.get_entry_value(self.dns1_entry),
            'dns2': self.get_entry_value(self.dns2_entry)
        }
        
        # 验证配置
        if not self._validate_config(ip_mode, dns_mode, ip_config, dns_config):
            return
        
        # 应用配置
        self._apply_network_config(ip_mode, dns_mode, ip_config, dns_config)
    
    def _validate_config(self, ip_mode, dns_mode, ip_config, dns_config):
        """验证网络配置"""
        # 手动IP模式下的验证
        if ip_mode == "manual":
            if not all([ip_config['ip'], ip_config['mask']]):
                self._append_status("错误: 手动配置IP时，IP地址和子网掩码为必填项\n")
                return False
            
            # 验证IP配置的有效性
            validation = validate_ip_config(
                ip_config['ip'], 
                ip_config['mask'], 
                ip_config['gateway'], 
                f"{dns_config['dns1']},{dns_config['dns2']}"
            )
            if not validation['valid']:
                self._append_status(f"IP配置验证失败: {validation['error']}\n")
                return False
        
        # 手动DNS模式下的验证
        if dns_mode == "manual":
            # DNS服务器是可选的，但如果填写了就要验证格式
            for dns_name, dns_value in [("首选DNS", dns_config['dns1']), ("备用DNS", dns_config['dns2'])]:
                if dns_value:
                    try:
                        import ipaddress
                        ipaddress.IPv4Address(dns_value)
                    except ValueError:
                        self._append_status(f"错误: {dns_name}服务器地址格式无效: {dns_value}\n")
                        return False
        
        return True
    
    def _apply_network_config(self, ip_mode, dns_mode, ip_config, dns_config):
        """应用网络配置"""
        self._append_status(f"\n正在应用网络配置到接口 '{self.current_interface}'...\n")
        
        # 显示配置信息
        if ip_mode == "auto":
            self._append_status("IP配置: 自动获得IP地址(DHCP)\n")
        else:
            self._append_status(f"IP配置: 手动配置\n")
            self._append_status(f"  IP地址: {ip_config['ip']}\n")
            self._append_status(f"  子网掩码: {ip_config['mask']}\n")
            if ip_config['gateway']:
                self._append_status(f"  默认网关: {ip_config['gateway']}\n")
            else:
                self._append_status("  默认网关: 未设置\n")
        
        if dns_mode == "auto":
            self._append_status("DNS配置: 自动获取DNS服务器地址\n")
        else:
            self._append_status("DNS配置: 手动配置\n")
            if dns_config['dns1']:
                self._append_status(f"  首选DNS: {dns_config['dns1']}\n")
            if dns_config['dns2']:
                self._append_status(f"  备用DNS: {dns_config['dns2']}\n")
        
        self._append_status("-" * 50 + "\n")
        
        try:
            # 调用新的配置应用函数
            result = apply_profile(
                self.current_interface, 
                ip_mode, 
                dns_mode, 
                ip_config, 
                dns_config
            )
            
            if result['success']:
                self._append_status("✓ 网络配置应用成功!\n\n")
                # 通知配置已应用
                if self.on_config_applied:
                    self.on_config_applied(self.current_interface)
            else:
                self._append_status(f"✗ 网络配置失败: {result['error']}\n\n")
        except Exception as e:
            self._append_status(f"✗ 执行出错: {str(e)}\n\n")
    
    def get_current_config(self):
        """获取当前配置"""
        return {
            'ip_mode': self.ip_mode_var.get(),
            'dns_mode': self.dns_mode_var.get(),
            'ip': self.get_entry_value(self.ip_entry),
            'mask': self.get_entry_value(self.mask_entry),
            'gateway': self.get_entry_value(self.gateway_entry),
            'dns1': self.get_entry_value(self.dns1_entry),
            'dns2': self.get_entry_value(self.dns2_entry)
        }
    
    def reset_form(self):
        """重置表单"""
        # 重置配置模式为手动
        self.ip_mode_var.set("manual")
        self.dns_mode_var.set("manual")
        
        # 触发模式改变事件
        self.on_ip_mode_changed()
        self.on_dns_mode_changed()
        
        # 清空所有输入框
        self.ip_entry.delete(0, END)
        self.mask_entry.delete(0, END)
        self.gateway_entry.delete(0, END)
        self.dns1_entry.delete(0, END)
        self.dns2_entry.delete(0, END) 