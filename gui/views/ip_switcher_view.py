
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.services.ip_switcher import (
    apply_profile, get_network_interfaces, save_profile, 
    load_profiles, delete_profile, validate_ip_config
)
import tkinter.messagebox as mbox


class IPSwitcherFrame(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.profiles = {}
        self.setup_ui()
        self.load_saved_profiles()
        
    def setup_ui(self):
        """设置IP切换界面"""
        # 标题
        title = tb.Label(
            self, 
            text="IP 地址快速切换", 
            font=('Arial', 18, 'bold'),
            bootstyle=PRIMARY
        )
        title.pack(pady=(0, 20))
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 左侧配置区域
        left_frame = tb.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        
        # 配置文件管理
        profile_frame = tb.LabelFrame(left_frame, text="配置文件管理", padding=15)
        profile_frame.pack(fill=X, pady=(0, 10))
        
        # 配置文件选择
        profile_select_frame = tb.Frame(profile_frame)
        profile_select_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(profile_select_frame, text="选择配置:").pack(side=LEFT)
        self.profile_var = tb.StringVar()
        self.profile_combo = tb.Combobox(
            profile_select_frame,
            textvariable=self.profile_var,
            state="readonly",
            width=20
        )
        self.profile_combo.pack(side=LEFT, padx=(10, 5))
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_selected)
        
        # 配置文件操作按钮
        profile_btn_frame = tb.Frame(profile_select_frame)
        profile_btn_frame.pack(side=RIGHT)
        
        tb.Button(
            profile_btn_frame,
            text="加载",
            bootstyle=INFO,
            command=self.load_selected_profile,
            width=8
        ).pack(side=LEFT, padx=2)
        
        tb.Button(
            profile_btn_frame,
            text="删除",
            bootstyle=DANGER,
            command=self.delete_selected_profile,
            width=8
        ).pack(side=LEFT, padx=2)
        
        # 保存新配置
        save_frame = tb.Frame(profile_frame)
        save_frame.pack(fill=X)
        
        tb.Label(save_frame, text="保存为:").pack(side=LEFT)
        self.profile_name_entry = tb.Entry(save_frame, width=20)
        self.profile_name_entry.pack(side=LEFT, padx=(10, 5))
        
        tb.Button(
            save_frame,
            text="保存配置",
            bootstyle=SUCCESS,
            command=self.save_current_config,
            width=10
        ).pack(side=RIGHT)
        
        # 网络配置输入区域
        config_frame = tb.LabelFrame(left_frame, text="网络配置", padding=15)
        config_frame.pack(fill=X, pady=(0, 10))
        
        # 网络接口选择
        interface_frame = tb.Frame(config_frame)
        interface_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(interface_frame, text="网络接口:").pack(side=LEFT)
        self.interface_var = tb.StringVar()
        self.interface_combo = tb.Combobox(
            interface_frame, 
            textvariable=self.interface_var,
            state="readonly",
            width=25
        )
        self.interface_combo.pack(side=LEFT, padx=(10, 5))
        
        # 刷新接口按钮
        tb.Button(
            interface_frame,
            text="刷新",
            bootstyle=INFO,
            command=self.refresh_interfaces,
            width=8
        ).pack(side=RIGHT)
        
        # IP配置字段
        config_fields = [
            ("IP地址:", "ip_entry", ""),
            ("子网掩码:", "mask_entry", ""),
            ("默认网关:", "gateway_entry", ""),
            ("DNS服务器:", "dns_entry", "")
        ]
        
        for i, (label_text, entry_name, default_value) in enumerate(config_fields):
            field_frame = tb.Frame(config_frame)
            field_frame.pack(fill=X, pady=3)
            
            tb.Label(field_frame, text=label_text, width=12).pack(side=LEFT)
            entry = tb.Entry(field_frame, width=35)
            entry.pack(side=LEFT, padx=(10, 0))
            if default_value:  # 只有非空默认值才插入
                entry.insert(0, default_value)
            setattr(self, entry_name, entry)
        
        # 操作按钮
        btn_frame = tb.Frame(config_frame)
        btn_frame.pack(fill=X, pady=(15, 0))
        
        tb.Button(
            btn_frame,
            text="验证配置",
            bootstyle=WARNING,
            command=self.validate_current_config,
            width=12
        ).pack(side=LEFT, padx=(0, 10))
        
        tb.Button(
            btn_frame,
            text="应用配置",
            bootstyle=SUCCESS,
            command=self.apply_config,
            width=12
        ).pack(side=LEFT)
        
        # 右侧结果显示区域
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        result_frame = tb.LabelFrame(right_frame, text="执行结果", padding=15)
        result_frame.pack(fill=BOTH, expand=True)
        
        # 结果文本框
        self.result_text = tb.Text(
            result_frame,
            height=20,
            state=DISABLED,
            wrap=WORD,
            font=('Consolas', 10)
        )
        
        # 滚动条
        scrollbar = tb.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
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
        
        # 初始化时刷新网络接口
        self.refresh_interfaces()
        self.append_result("=== Netkit IP地址快速切换工具 ===\n")
        self.append_result("请选择网络接口并输入IP配置信息\n\n")
        
    def refresh_interfaces(self):
        """刷新网络接口列表"""
        try:
            interfaces = get_network_interfaces()
            self.interface_combo['values'] = interfaces
            if interfaces:
                self.interface_combo.current(0)
                self.append_result(f"已获取 {len(interfaces)} 个网络接口\n")
            else:
                self.append_result("未找到可用的网络接口\n")
        except Exception as e:
            self.append_result(f"获取网络接口失败: {str(e)}\n")
    
    def validate_current_config(self):
        """验证当前配置"""
        ip = self.ip_entry.get().strip()
        mask = self.mask_entry.get().strip()
        gateway = self.gateway_entry.get().strip()
        dns = self.dns_entry.get().strip()
        
        self.append_result("正在验证IP配置...\n")
        
        result = validate_ip_config(ip, mask, gateway, dns)
        if result['valid']:
            self.append_result("✓ IP配置验证通过\n")
        else:
            self.append_result(f"✗ IP配置验证失败: {result['error']}\n")
            
    def apply_config(self):
        """应用IP配置"""
        interface = self.interface_var.get().strip()
        ip = self.ip_entry.get().strip()
        mask = self.mask_entry.get().strip()
        gateway = self.gateway_entry.get().strip()
        dns = self.dns_entry.get().strip()
        
        # 验证输入
        if not interface:
            self.append_result("错误: 请选择网络接口\n")
            return
            
        if not all([ip, mask, gateway]):
            self.append_result("错误: 请完整填写IP地址、子网掩码和默认网关\n")
            return
        
        # 先验证配置
        validation = validate_ip_config(ip, mask, gateway, dns)
        if not validation['valid']:
            self.append_result(f"配置验证失败: {validation['error']}\n")
            return
            
        # 应用配置
        self.append_result(f"\n正在应用配置到接口 '{interface}'...\n")
        self.append_result(f"IP地址: {ip}\n")
        self.append_result(f"子网掩码: {mask}\n")
        self.append_result(f"默认网关: {gateway}\n")
        if dns:
            self.append_result(f"DNS服务器: {dns}\n")
        self.append_result("-" * 40 + "\n")
        
        try:
            result = apply_profile(interface, ip, mask, gateway, dns)
            if result['success']:
                self.append_result("✓ IP配置应用成功!\n\n")
            else:
                self.append_result(f"✗ IP配置应用失败: {result['error']}\n\n")
        except Exception as e:
            self.append_result(f"✗ 执行出错: {str(e)}\n\n")
    
    def save_current_config(self):
        """保存当前配置"""
        name = self.profile_name_entry.get().strip()
        if not name:
            mbox.showwarning("输入错误", "请输入配置文件名称")
            return
            
        interface = self.interface_var.get().strip()
        ip = self.ip_entry.get().strip()
        mask = self.mask_entry.get().strip()
        gateway = self.gateway_entry.get().strip()
        dns = self.dns_entry.get().strip()
        
        if not all([interface, ip, mask, gateway]):
            mbox.showwarning("输入错误", "请完整填写网络配置信息")
            return
        
        # 验证配置
        validation = validate_ip_config(ip, mask, gateway, dns)
        if not validation['valid']:
            mbox.showerror("配置错误", f"配置验证失败: {validation['error']}")
            return
            
        try:
            result = save_profile(name, interface, ip, mask, gateway, dns)
            if result['success']:
                self.append_result(f"✓ 配置 '{name}' 保存成功\n")
                self.profile_name_entry.delete(0, END)
                self.load_saved_profiles()
            else:
                self.append_result(f"✗ 保存失败: {result['error']}\n")
                mbox.showerror("保存失败", result['error'])
        except Exception as e:
            self.append_result(f"✗ 保存出错: {str(e)}\n")
    
    def load_saved_profiles(self):
        """加载已保存的配置文件"""
        try:
            self.profiles = load_profiles()
            profile_names = list(self.profiles.keys())
            self.profile_combo['values'] = profile_names
            if profile_names:
                self.profile_combo.current(0)
        except Exception as e:
            self.append_result(f"加载配置文件失败: {str(e)}\n")
    
    def on_profile_selected(self, event=None):
        """配置文件选择事件"""
        # 这里可以添加预览配置的逻辑
        pass
    
    def load_selected_profile(self):
        """加载选中的配置文件"""
        profile_name = self.profile_var.get()
        if not profile_name or profile_name not in self.profiles:
            mbox.showwarning("选择错误", "请选择有效的配置文件")
            return
            
        profile = self.profiles[profile_name]
        
        # 更新界面
        self.interface_var.set(profile['interface'])
        self.ip_entry.delete(0, END)
        self.ip_entry.insert(0, profile['ip'])
        self.mask_entry.delete(0, END)
        self.mask_entry.insert(0, profile['mask'])
        self.gateway_entry.delete(0, END)
        self.gateway_entry.insert(0, profile['gateway'])
        self.dns_entry.delete(0, END)
        self.dns_entry.insert(0, profile['dns'])
        
        self.append_result(f"✓ 已加载配置 '{profile_name}'\n")
    
    def delete_selected_profile(self):
        """删除选中的配置文件"""
        profile_name = self.profile_var.get()
        if not profile_name or profile_name not in self.profiles:
            mbox.showwarning("选择错误", "请选择有效的配置文件")
            return
            
        if mbox.askyesno("确认删除", f"确定要删除配置 '{profile_name}' 吗？"):
            try:
                result = delete_profile(profile_name)
                if result['success']:
                    self.append_result(f"✓ 配置 '{profile_name}' 已删除\n")
                    self.load_saved_profiles()
                else:
                    self.append_result(f"✗ 删除失败: {result['error']}\n")
                    mbox.showerror("删除失败", result['error'])
            except Exception as e:
                self.append_result(f"✗ 删除出错: {str(e)}\n")
    
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
