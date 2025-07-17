
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.services.ip_switcher import (
    get_network_interfaces, apply_profile, set_dhcp, validate_ip_config
)
import tkinter.messagebox as mbox
import threading

class IPSwitcherFrame(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.interfaces = []
        self.setup_ui()
        self.refresh_interfaces()

    def setup_ui(self):
        """设置网卡配置界面"""
        # --- 网卡选择 ---
        selection_frame = tb.LabelFrame(self, text="网卡选择", padding=15)
        selection_frame.pack(fill=X, padx=10, pady=10)

        tb.Label(selection_frame, text="选择网卡:").pack(side=LEFT, padx=(0, 10))
        self.interface_var = tb.StringVar()
        self.interface_combo = tb.Combobox(selection_frame, textvariable=self.interface_var, state="readonly", width=40)
        self.interface_combo.pack(side=LEFT, padx=(0, 10))
        self.interface_combo.bind("<<ComboboxSelected>>", self.on_interface_selected)

        self.show_all_var = tb.BooleanVar()
        tb.Checkbutton(selection_frame, text="显示所有网卡", variable=self.show_all_var, command=self.refresh_interfaces).pack(side=LEFT, padx=10)
        tb.Button(selection_frame, text="刷新网卡", command=self.refresh_interfaces, bootstyle=INFO).pack(side=LEFT)

        # --- 当前网卡信息 ---
        info_frame = tb.LabelFrame(self, text="当前网卡信息", padding=15)
        info_frame.pack(fill=X, padx=10, pady=(0, 10))

        self.info_text = tb.Text(info_frame, height=8, width=80, state=DISABLED, wrap=WORD, font=('Consolas', 10))
        self.info_text.pack(fill=BOTH, expand=True)

        # --- IP配置 ---
        config_frame = tb.LabelFrame(self, text="IP 配置", padding=15)
        config_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        self.dhcp_var = tb.BooleanVar(value=False)
        self.dhcp_check = tb.Checkbutton(config_frame, text="DHCP", variable=self.dhcp_var, command=self.toggle_dhcp)
        
        self.ip_entry = self.create_config_entry(config_frame, "IP地址:", "例如: 192.168.1.100")
        self.dhcp_check.grid(row=0, column=2, sticky='e', padx=5)
        self.mask_entry = self.create_config_entry(config_frame, "子网掩码:", "例如: 255.255.255.0 或 24")
        self.gateway_entry = self.create_config_entry(config_frame, "默认网关:", "例如: 192.168.1.1")
        self.dns1_entry = self.create_config_entry(config_frame, "DNS服务器1:", "首选DNS服务器")
        self.dns2_entry = self.create_config_entry(config_frame, "DNS服务器2:", "备用DNS服务器")

        # --- 应用按钮 ---
        apply_button = tb.Button(self, text="应用配置", command=self.apply_config, bootstyle=SUCCESS, width=20)
        apply_button.pack(pady=20)

    def create_config_entry(self, parent, label_text, placeholder_text):
        row = len(parent.grid_slaves(row=None))
        label = tb.Label(parent, text=label_text, width=12)
        label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
        entry = tb.Entry(parent, width=50)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky='we')
        entry.insert(0, placeholder_text)
        entry.config(foreground="grey")
        entry.bind("<FocusIn>", lambda e: self.on_entry_focus_in(e, placeholder_text))
        entry.bind("<FocusOut>", lambda e: self.on_entry_focus_out(e, placeholder_text))
        parent.grid_columnconfigure(1, weight=1)
        return entry
    
    def on_entry_focus_in(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, "end")
            event.widget.config(foreground='white')

    def on_entry_focus_out(self, event, placeholder):
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(foreground='grey')

    def refresh_interfaces(self):
        """刷新网络接口列表"""
        def _task():
            try:
                self.interfaces = get_network_interfaces(self.show_all_var.get())
                interface_names = [f"{iface['name']} ({iface['description']})" for iface in self.interfaces]
                
                self.interface_combo['values'] = interface_names
                if interface_names:
                    self.interface_combo.current(0)
                    self.on_interface_selected()
                else:
                    self.clear_info()
            except Exception as e:
                mbox.showerror("错误", f"获取网络接口失败: {e}")

        threading.Thread(target=_task).start()

    def on_interface_selected(self, event=None):
        """当用户选择一个网卡时"""
        try:
            selected_index = self.interface_combo.current()
            if selected_index < 0: return

            interface = self.interfaces[selected_index]
            self.display_interface_info(interface)
            self.populate_config_fields(interface)
        except (IndexError, KeyError) as e:
             self.clear_info()
             print(f"选择接口时出错: {e}")
             
    def display_interface_info(self, interface):
        """显示选定接口的详细信息"""
        info = (
            f"网卡名称: {interface.get('name', 'N/A')}\n"
            f"描述    : {interface.get('description', 'N/A')}\n"
            f"状态    : {interface.get('status', 'N/A')}\n"
            f"物理地址: {interface.get('mac', 'N/A')}\n"
            f"DHCP    : {'是' if interface.get('dhcp_enabled') else '否'}\n"
            f"IP地址  : {interface.get('ip', 'N/A')}\n"
            f"子网掩码: {interface.get('mask', 'N/A')}\n"
            f"默认网关: {interface.get('gateway', 'N/A')}\n"
            f"DNS服务器: {', '.join(interface.get('dns_servers', []))}"
        )
        self.info_text.config(state=NORMAL)
        self.info_text.delete("1.0", END)
        self.info_text.insert(END, info)
        self.info_text.config(state=DISABLED)

    def populate_config_fields(self, interface):
        """用接口信息填充配置字段"""
        self.dhcp_var.set(interface.get('dhcp_enabled', False))

        self.ip_entry.delete(0, END)
        self.ip_entry.insert(0, interface.get('ip', ''))
        self.mask_entry.delete(0, END)
        self.mask_entry.insert(0, interface.get('mask', ''))
        self.gateway_entry.delete(0, END)
        self.gateway_entry.insert(0, interface.get('gateway', ''))

        dns_servers = interface.get('dns_servers', [])
        self.dns1_entry.delete(0, END)
        self.dns1_entry.insert(0, dns_servers[0] if len(dns_servers) > 0 else '')
        self.dns2_entry.delete(0, END)
        self.dns2_entry.insert(0, dns_servers[1] if len(dns_servers) > 1 else '')
        self.toggle_dhcp()

    def clear_info(self):
        self.info_text.config(state=NORMAL)
        self.info_text.delete("1.0", END)
        self.info_text.config(state=DISABLED)
        self.interface_var.set('')
        self.interface_combo['values'] = []
        # Clear entry fields
        for entry in [self.ip_entry, self.mask_entry, self.gateway_entry, self.dns1_entry, self.dns2_entry]:
            entry.delete(0, END)

    def toggle_dhcp(self):
        """切换DHCP状态"""
        is_dhcp = self.dhcp_var.get()
        state = DISABLED if is_dhcp else NORMAL
        for entry in [self.ip_entry, self.mask_entry, self.gateway_entry, self.dns1_entry, self.dns2_entry]:
            entry.config(state=state)

    def apply_config(self):
        """应用网络配置"""
        selected_index = self.interface_combo.current()
        if selected_index < 0:
            mbox.showerror("错误", "请选择一个网络接口。")
            return
        
        interface_name = self.interfaces[selected_index]['name']
        is_dhcp = self.dhcp_var.get()

        def _task():
            try:
                if is_dhcp:
                    result = set_dhcp(interface_name)
                else:
                    ip = self.ip_entry.get().strip()
                    mask = self.mask_entry.get().strip()
                    gateway = self.gateway_entry.get().strip()
                    dns1 = self.dns1_entry.get().strip()
                    dns2 = self.dns2_entry.get().strip()

                    if not all([ip, mask, gateway]):
                        mbox.showerror("输入错误", "IP地址、子网掩码和默认网关不能为空。")
                        return

                    validation = validate_ip_config(ip, mask, gateway, f"{dns1},{dns2}" if dns1 or dns2 else "")
                    if not validation['valid']:
                        mbox.showerror("配置错误", f"配置验证失败: {validation['error']}")
                        return
                    
                    result = apply_profile(interface_name, ip, mask, gateway, dns1, dns2)

                if result['success']:
                    mbox.showinfo("成功", result['message'])
                    self.refresh_interfaces()
                else:
                    mbox.showerror("失败", result['error'])
            except Exception as e:
                mbox.showerror("应用配置时出错", str(e))
        
        threading.Thread(target=_task).start()
