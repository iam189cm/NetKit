
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.services.ip_switcher import (
    apply_profile, get_network_interfaces, validate_ip_config,
    get_network_card_info
)
import tkinter.messagebox as mbox


class IPSwitcherFrame(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.setup_ui()
        
    def setup_ui(self):
        """设置网卡配置界面"""
        # 标题
        title = tb.Label(
            self, 
            text="网卡配置", 
            font=('Arial', 18, 'bold'),
            bootstyle=PRIMARY
        )
        title.pack(pady=(0, 20))
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True, padx=20)
        
        # 网卡选择区域
        self.setup_network_selection(main_frame)
        
        # 当前网卡信息显示区域
        self.setup_network_info_display(main_frame)
        
        # 网络配置区域
        self.setup_network_config(main_frame)
        
        # 状态区域
        self.setup_status_area(main_frame)
        
        # 初始化
        self.append_status("=== NetKit 网卡配置工具 ===\n")
        self.append_status("请选择网卡查看当前配置信息\n")
        
        # 延迟加载网络接口，避免阻塞界面显示
        self.after(100, self.refresh_interfaces)
        
    def setup_network_selection(self, parent):
        """设置网卡选择区域"""
        # 网卡选择行
        select_frame = tb.Frame(parent)
        select_frame.pack(fill=X, pady=(0, 15))
        
        # 左侧：网卡选择标签和下拉框
        tb.Label(select_frame, text="网卡选择:", font=('Arial', 10)).pack(side=LEFT)
        
        self.interface_var = tb.StringVar()
        self.interface_combo = tb.Combobox(
            select_frame,
            textvariable=self.interface_var,
            state="readonly",
            width=60,
            font=('Arial', 9)
        )
        self.interface_combo.pack(side=LEFT, padx=(10, 20))
        self.interface_combo.bind('<<ComboboxSelected>>', self.on_interface_selected)
        
        # 中间：显示所有网卡选项
        self.show_all_var = tb.BooleanVar()
        tb.Checkbutton(
            select_frame,
            text="显示所有网卡",
            variable=self.show_all_var,
            command=self.refresh_interfaces
        ).pack(side=LEFT, padx=(0, 20))
        
        # 右侧：刷新按钮
        tb.Button(
            select_frame,
            text="刷新网卡",
            bootstyle=INFO,
            command=self.refresh_interfaces,
            width=12
        ).pack(side=RIGHT)
        
    def setup_network_info_display(self, parent):
        """设置当前网卡信息显示区域"""
        info_frame = tb.LabelFrame(parent, text="当前网卡信息", padding=20)
        info_frame.pack(fill=X, pady=(0, 15))
        
        # 创建信息显示网格
        info_grid = tb.Frame(info_frame)
        info_grid.pack(fill=X)
        
        # 信息字段定义
        info_fields = [
            ("网卡名称:", "name_label"),
            ("描述:", "desc_label"),
            ("状态:", "status_label"),
            ("物理地址:", "mac_label"),
            ("速度:", "speed_label"),
            ("IP地址:", "ip_label"),
            ("子网掩码:", "mask_label"),
            ("默认网关:", "gateway_label"),
            ("DNS服务器:", "dns_label")
        ]
        
        # 创建信息显示标签
        for i, (label_text, attr_name) in enumerate(info_fields):
            row = i // 3  # 每行3个字段
            col = i % 3
            
            field_frame = tb.Frame(info_grid)
            field_frame.grid(row=row, column=col, sticky=W, padx=(0, 40), pady=3)
            
            tb.Label(field_frame, text=label_text, font=('Arial', 9)).pack(side=LEFT)
            label = tb.Label(field_frame, text="未选择", font=('Arial', 9), bootstyle=SECONDARY)
            label.pack(side=LEFT, padx=(5, 0))
            setattr(self, attr_name, label)
        
        # 配置网格权重
        for i in range(3):
            info_grid.columnconfigure(i, weight=1)
            
    def setup_network_config(self, parent):
        """设置网络配置区域"""
        config_frame = tb.LabelFrame(parent, text="网络配置", padding=20)
        config_frame.pack(fill=X, pady=(0, 15))
        
        # 配置字段
        config_fields = [
            ("IP地址:", "ip_entry", "例如: 192.168.1.100"),
            ("子网掩码:", "mask_entry", "例如: 255.255.255.0 或 24"),
            ("默认网关:", "gateway_entry", "例如: 192.168.1.1"),
            ("DNS服务器:", "dns_entry", "例如: 8.8.8.8,8.8.4.4")
        ]
        
        # 创建配置输入字段
        for i, (label_text, entry_name, placeholder) in enumerate(config_fields):
            field_frame = tb.Frame(config_frame)
            field_frame.pack(fill=X, pady=5)
            
            # 标签
            tb.Label(field_frame, text=label_text, font=('Arial', 10), width=12).pack(side=LEFT)
            
            # 输入框
            entry = tb.Entry(field_frame, font=('Arial', 9), width=40)
            entry.pack(side=LEFT, padx=(10, 0))
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
                self.dhcp_check.pack(side=RIGHT, padx=(20, 0))
        
        # 应用配置按钮
        button_frame = tb.Frame(config_frame)
        button_frame.pack(fill=X, pady=(20, 0))
        
        tb.Button(
            button_frame,
            text="应用配置",
            bootstyle=SUCCESS,
            command=self.apply_config,
            width=15
        ).pack(anchor=CENTER)
        
    def setup_status_area(self, parent):
        """设置状态区域"""
        status_frame = tb.LabelFrame(parent, text="状态", padding=15)
        status_frame.pack(fill=BOTH, expand=True, pady=(0, 0))
        
        # 状态文本框
        self.status_text = tb.Text(
            status_frame,
            height=6,
            state=DISABLED,
            wrap=WORD,
            font=('Consolas', 9)
        )
        
        # 滚动条
        scrollbar = tb.Scrollbar(status_frame, orient=VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
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
            self.append_status("已启用DHCP模式\n")
        else:
            self.append_status("已禁用DHCP模式，请手动配置IP信息\n")
    
    def refresh_interfaces(self):
        """刷新网络接口列表"""
        try:
            interfaces = get_network_interfaces()
            self.interface_combo['values'] = interfaces
            if interfaces:
                self.interface_combo.current(0)
                self.append_status(f"已获取 {len(interfaces)} 个网络接口\n")
                # 延迟调用网卡信息获取，避免阻塞
                self.after(100, self.on_interface_selected)
            else:
                self.append_status("未找到可用的网络接口\n")
        except Exception as e:
            self.append_status(f"获取网络接口失败: {str(e)}\n")
    
    def on_interface_selected(self, event=None):
        """网卡选择改变时的处理"""
        interface = self.interface_var.get().strip()
        if not interface:
            return
            
        try:
            # 获取网卡详细信息
            info = get_network_card_info(interface)
            
            # 更新信息显示
            self.name_label.config(text=info.get('name', '未知'))
            self.desc_label.config(text=info.get('description', '未知'))
            self.status_label.config(text=info.get('status', '未知'))
            self.mac_label.config(text=info.get('mac', '未知'))
            self.speed_label.config(text=info.get('speed', '未知'))
            self.ip_label.config(text=info.get('ip', '未配置'))
            self.mask_label.config(text=info.get('mask', '未配置'))
            self.gateway_label.config(text=info.get('gateway', '未配置'))
            
            # 合并DNS服务器显示
            dns1 = info.get('dns1', '')
            dns2 = info.get('dns2', '')
            if dns1 and dns2:
                dns_text = f"{dns1}, {dns2}"
            elif dns1:
                dns_text = dns1
            elif dns2:
                dns_text = dns2
            else:
                dns_text = "未配置"
            self.dns_label.config(text=dns_text)
            
            self.append_status(f"已选择网卡: {info.get('name', interface)}\n")
            
        except Exception as e:
            self.append_status(f"获取网卡信息失败: {str(e)}\n")
            # 重置信息显示
            for label in [self.name_label, self.desc_label, self.status_label, 
                         self.mac_label, self.speed_label, self.ip_label, 
                         self.mask_label, self.gateway_label, self.dns_label]:
                label.config(text="获取失败")
    
    def get_entry_value(self, entry, placeholder):
        """获取输入框的实际值（排除占位符）"""
        value = entry.get().strip()
        return "" if value == placeholder else value
    
    def apply_config(self):
        """应用网络配置"""
        interface = self.interface_var.get().strip()
        if not interface:
            self.append_status("错误: 请选择网络接口\n")
            return
        
        is_dhcp = self.dhcp_var.get()
        
        if is_dhcp:
            # DHCP模式
            self.append_status(f"\n正在为接口 '{interface}' 启用DHCP...\n")
            self.append_status("-" * 50 + "\n")
            
            try:
                result = apply_profile(interface, "", "", "", "", dhcp=True)
                if result['success']:
                    self.append_status("✓ DHCP配置应用成功!\n\n")
                    # 刷新网卡信息显示
                    self.after(1000, self.on_interface_selected)
                else:
                    self.append_status(f"✗ DHCP配置失败: {result['error']}\n\n")
            except Exception as e:
                self.append_status(f"✗ 执行出错: {str(e)}\n\n")
        else:
            # 静态IP模式
            ip = self.get_entry_value(self.ip_entry, "例如: 192.168.1.100")
            mask = self.get_entry_value(self.mask_entry, "例如: 255.255.255.0 或 24")
            gateway = self.get_entry_value(self.gateway_entry, "例如: 192.168.1.1")
            dns = self.get_entry_value(self.dns_entry, "例如: 8.8.8.8,8.8.4.4")
            
            # 验证必填字段
            if not all([ip, mask, gateway]):
                self.append_status("错误: 请完整填写IP地址、子网掩码和默认网关\n")
                return
            
            # 验证配置
            validation = validate_ip_config(ip, mask, gateway, dns)
            if not validation['valid']:
                self.append_status(f"配置验证失败: {validation['error']}\n")
                return
            
            # 应用配置
            self.append_status(f"\n正在应用静态IP配置到接口 '{interface}'...\n")
            self.append_status(f"IP地址: {ip}\n")
            self.append_status(f"子网掩码: {mask}\n")
            self.append_status(f"默认网关: {gateway}\n")
            if dns:
                self.append_status(f"DNS服务器: {dns}\n")
            self.append_status("-" * 50 + "\n")
            
            try:
                result = apply_profile(interface, ip, mask, gateway, dns, dhcp=False)
                if result['success']:
                    self.append_status("✓ 静态IP配置应用成功!\n\n")
                    # 刷新网卡信息显示
                    self.after(1000, self.on_interface_selected)
                else:
                    self.append_status(f"✗ 静态IP配置失败: {result['error']}\n\n")
            except Exception as e:
                self.append_status(f"✗ 执行出错: {str(e)}\n\n")
    
    def append_status(self, text):
        """向状态框追加文本"""
        self.status_text.configure(state=NORMAL)
        self.status_text.insert(END, text)
        self.status_text.configure(state=DISABLED)
        self.status_text.see(END)
