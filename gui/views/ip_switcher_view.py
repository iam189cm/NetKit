
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
        
        # 上半部分：网卡选择 + 信息显示 + 配置输入
        top_frame = tb.Frame(self)
        top_frame.pack(fill=BOTH, expand=True, pady=(0, 10))
        
        # 网卡选择区域
        self.setup_network_selection(top_frame)
        
        # 当前网卡信息显示区域
        self.setup_network_info_display(top_frame)
        
        # 网络配置输入区域
        self.setup_network_config(top_frame)
        
        # 下半部分：执行结果区域
        self.setup_result_area()
        
        # 初始化
        self.refresh_interfaces()
        self.append_result("=== NetKit 网卡配置工具 ===\n")
        self.append_result("请选择网卡查看当前配置信息\n\n")
        
    def setup_network_selection(self, parent):
        """设置网卡选择区域"""
        select_frame = tb.LabelFrame(parent, text="网卡选择", padding=15)
        select_frame.pack(fill=X, pady=(0, 10))
        
        # 创建水平布局容器
        content_frame = tb.Frame(select_frame)
        content_frame.pack(fill=X)
        
        # 左侧：网卡选择
        left_frame = tb.Frame(content_frame)
        left_frame.pack(side=LEFT, fill=X, expand=True)
        
        tb.Label(left_frame, text="网卡选择:").pack(anchor=W, pady=(0, 5))
        self.interface_var = tb.StringVar()
        self.interface_combo = tb.Combobox(
            left_frame, 
            textvariable=self.interface_var,
            state="readonly",
            width=50
        )
        self.interface_combo.pack(fill=X, pady=(0, 10))
        self.interface_combo.bind('<<ComboboxSelected>>', self.on_interface_selected)
        
        # 右侧：按钮和选项
        right_frame = tb.Frame(content_frame)
        right_frame.pack(side=RIGHT, padx=(20, 0))
        
        # 刷新按钮
        tb.Button(
            right_frame,
            text="刷新网卡",
            bootstyle=INFO,
            command=self.refresh_interfaces,
            width=15
        ).pack(pady=(0, 10))
        
        # 显示所有网卡选项
        self.show_all_var = tb.BooleanVar()
        tb.Checkbutton(
            right_frame,
            text="显示所有网卡",
            variable=self.show_all_var,
            command=self.refresh_interfaces
        ).pack()
        
    def setup_network_info_display(self, parent):
        """设置当前网卡信息显示区域"""
        info_frame = tb.LabelFrame(parent, text="当前网卡信息", padding=15)
        info_frame.pack(fill=X, pady=(0, 10))
        
        # 创建两列布局
        columns_frame = tb.Frame(info_frame)
        columns_frame.pack(fill=X)
        
        # 左列
        left_column = tb.Frame(columns_frame)
        left_column.pack(side=LEFT, fill=X, expand=True)
        
        # 右列
        right_column = tb.Frame(columns_frame)
        right_column.pack(side=RIGHT, fill=X, expand=True, padx=(20, 0))
        
        # 创建信息显示标签
        info_fields = [
            ("网卡名称:", "name_label"),
            ("描述:", "desc_label"),
            ("状态:", "status_label"),
            ("物理地址:", "mac_label"),
            ("速度:", "speed_label"),
            ("IP地址:", "ip_label"),
            ("子网掩码:", "mask_label"),
            ("网关:", "gateway_label"),
            ("DNS服务器1:", "dns1_label"),
            ("DNS服务器2:", "dns2_label")
        ]
        
        # 分配字段到两列
        for i, (label_text, attr_name) in enumerate(info_fields):
            parent_column = left_column if i < 5 else right_column
            
            field_frame = tb.Frame(parent_column)
            field_frame.pack(fill=X, pady=2)
            
            tb.Label(field_frame, text=label_text, width=12).pack(side=LEFT)
            label = tb.Label(field_frame, text="未选择", bootstyle=SECONDARY)
            label.pack(side=LEFT, padx=(10, 0))
            setattr(self, attr_name, label)
            
    def setup_network_config(self, parent):
        """设置网络配置输入区域"""
        config_frame = tb.LabelFrame(parent, text="网络配置", padding=15)
        config_frame.pack(fill=X, pady=(0, 10))
        
        # 创建水平布局容器
        content_frame = tb.Frame(config_frame)
        content_frame.pack(fill=X)
        
        # 左侧：配置输入
        left_frame = tb.Frame(content_frame)
        left_frame.pack(side=LEFT, fill=X, expand=True)
        
        # DHCP选项
        dhcp_frame = tb.Frame(left_frame)
        dhcp_frame.pack(fill=X, pady=(0, 15))
        
        self.dhcp_var = tb.BooleanVar()
        self.dhcp_check = tb.Checkbutton(
            dhcp_frame,
            text="DHCP",
            variable=self.dhcp_var,
            command=self.on_dhcp_changed
        )
        self.dhcp_check.pack(anchor=W)
        
        # 配置输入字段（两列布局）
        fields_frame = tb.Frame(left_frame)
        fields_frame.pack(fill=X)
        
        # 左列字段
        left_fields_frame = tb.Frame(fields_frame)
        left_fields_frame.pack(side=LEFT, fill=X, expand=True)
        
        # 右列字段
        right_fields_frame = tb.Frame(fields_frame)
        right_fields_frame.pack(side=RIGHT, fill=X, expand=True, padx=(20, 0))
        
        config_fields = [
            ("IP地址:", "ip_entry", "例如: 192.168.1.100"),
            ("子网掩码:", "mask_entry", "例如: 255.255.255.0 或 24"),
            ("默认网关:", "gateway_entry", "例如: 192.168.1.1"),
            ("DNS服务器1:", "dns1_entry", "例如: 8.8.8.8"),
            ("DNS服务器2:", "dns2_entry", "例如: 8.8.4.4")
        ]
        
        for i, (label_text, entry_name, placeholder) in enumerate(config_fields):
            parent_frame = left_fields_frame if i < 3 else right_fields_frame
            
            field_frame = tb.Frame(parent_frame)
            field_frame.pack(fill=X, pady=3)
            
            tb.Label(field_frame, text=label_text, width=12).pack(anchor=W)
            entry = tb.Entry(field_frame, width=25)
            entry.pack(fill=X, pady=(2, 0))
            entry.insert(0, placeholder)
            entry.bind('<FocusIn>', lambda e, placeholder=placeholder: self.on_entry_focus_in(e, placeholder))
            entry.bind('<FocusOut>', lambda e, placeholder=placeholder: self.on_entry_focus_out(e, placeholder))
            setattr(self, entry_name, entry)
        
        # 右侧：应用配置按钮
        right_frame = tb.Frame(content_frame)
        right_frame.pack(side=RIGHT, padx=(20, 0))
        
        tb.Button(
            right_frame,
            text="应用配置",
            bootstyle=SUCCESS,
            command=self.apply_config,
            width=20,
            height=3
        ).pack(anchor=CENTER, pady=(30, 0))
        
    def setup_result_area(self):
        """设置执行结果区域"""
        result_frame = tb.LabelFrame(self, text="执行结果", padding=15)
        result_frame.pack(fill=BOTH, expand=True, pady=(10, 0))
        
        # 结果文本框和滚动条
        text_frame = tb.Frame(result_frame)
        text_frame.pack(fill=BOTH, expand=True)
        
        self.result_text = tb.Text(
            text_frame,
            height=8,
            state=DISABLED,
            wrap=WORD,
            font=('Consolas', 10)
        )
        
        scrollbar = tb.Scrollbar(text_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 清空结果按钮
        clear_btn_frame = tb.Frame(result_frame)
        clear_btn_frame.pack(fill=X, pady=(10, 0))
        
        tb.Button(
            clear_btn_frame,
            text="清空结果",
            bootstyle=LIGHT,
            command=self.clear_result,
            width=12
        ).pack(side=RIGHT)
        
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
            self.append_result("已启用DHCP模式\n")
        else:
            self.append_result("已禁用DHCP模式，请手动配置IP信息\n")
    
    def refresh_interfaces(self):
        """刷新网络接口列表"""
        try:
            interfaces = get_network_interfaces()
            self.interface_combo['values'] = interfaces
            if interfaces:
                self.interface_combo.current(0)
                self.on_interface_selected()
                self.append_result(f"已获取 {len(interfaces)} 个网络接口\n")
            else:
                self.append_result("未找到可用的网络接口\n")
        except Exception as e:
            self.append_result(f"获取网络接口失败: {str(e)}\n")
    
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
            self.dns1_label.config(text=info.get('dns1', '未配置'))
            self.dns2_label.config(text=info.get('dns2', '未配置'))
            
            self.append_result(f"已选择网卡: {info.get('name', interface)}\n")
            
        except Exception as e:
            self.append_result(f"获取网卡信息失败: {str(e)}\n")
            # 重置信息显示
            for label in [self.name_label, self.desc_label, self.status_label, 
                         self.mac_label, self.speed_label, self.ip_label, 
                         self.mask_label, self.gateway_label, self.dns1_label, self.dns2_label]:
                label.config(text="获取失败")
    
    def get_entry_value(self, entry, placeholder):
        """获取输入框的实际值（排除占位符）"""
        value = entry.get().strip()
        return "" if value == placeholder else value
    
    def apply_config(self):
        """应用网络配置"""
        interface = self.interface_var.get().strip()
        if not interface:
            self.append_result("错误: 请选择网络接口\n")
            return
        
        is_dhcp = self.dhcp_var.get()
        
        if is_dhcp:
            # DHCP模式
            self.append_result(f"\n正在为接口 '{interface}' 启用DHCP...\n")
            self.append_result("-" * 40 + "\n")
            
            try:
                # 这里需要实现DHCP配置逻辑
                result = apply_profile(interface, "", "", "", "", dhcp=True)
                if result['success']:
                    self.append_result("✓ DHCP配置应用成功!\n\n")
                    # 刷新网卡信息显示
                    self.on_interface_selected()
                else:
                    self.append_result(f"✗ DHCP配置失败: {result['error']}\n\n")
            except Exception as e:
                self.append_result(f"✗ 执行出错: {str(e)}\n\n")
        else:
            # 静态IP模式
            ip = self.get_entry_value(self.ip_entry, "例如: 192.168.1.100")
            mask = self.get_entry_value(self.mask_entry, "例如: 255.255.255.0 或 24")
            gateway = self.get_entry_value(self.gateway_entry, "例如: 192.168.1.1")
            dns1 = self.get_entry_value(self.dns1_entry, "例如: 8.8.8.8")
            dns2 = self.get_entry_value(self.dns2_entry, "例如: 8.8.4.4")
            
            # 验证必填字段
            if not all([ip, mask, gateway]):
                self.append_result("错误: 请完整填写IP地址、子网掩码和默认网关\n")
                return
            
            # 合并DNS服务器
            dns = dns1
            if dns2:
                dns = f"{dns1},{dns2}" if dns1 else dns2
            
            # 验证配置
            validation = validate_ip_config(ip, mask, gateway, dns)
            if not validation['valid']:
                self.append_result(f"配置验证失败: {validation['error']}\n")
                return
            
            # 应用配置
            self.append_result(f"\n正在应用静态IP配置到接口 '{interface}'...\n")
            self.append_result(f"IP地址: {ip}\n")
            self.append_result(f"子网掩码: {mask}\n")
            self.append_result(f"默认网关: {gateway}\n")
            if dns1:
                self.append_result(f"DNS服务器1: {dns1}\n")
            if dns2:
                self.append_result(f"DNS服务器2: {dns2}\n")
            self.append_result("-" * 40 + "\n")
            
            try:
                result = apply_profile(interface, ip, mask, gateway, dns, dhcp=False)
                if result['success']:
                    self.append_result("✓ 静态IP配置应用成功!\n\n")
                    # 刷新网卡信息显示
                    self.on_interface_selected()
                else:
                    self.append_result(f"✗ 静态IP配置失败: {result['error']}\n\n")
            except Exception as e:
                self.append_result(f"✗ 执行出错: {str(e)}\n\n")
    
    def clear_result(self):
        """清空结果框"""
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.configure(state=DISABLED)
        self.append_result("=== 结果已清空 ===\n\n")
            
    def append_result(self, text):
        """向结果框追加文本"""
        self.result_text.configure(state=NORMAL)
        self.result_text.insert(END, text)
        self.result_text.configure(state=DISABLED)
        self.result_text.see(END)
