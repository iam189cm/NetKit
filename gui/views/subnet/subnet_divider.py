"""
子网划分组件
负责子网划分功能的UI实现
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from netkit.utils.ui_helper import ui_helper
from netkit.services.subnet import SubnetCalculator
import tkinter as tk
import pyperclip


class SubnetDivider(tb.LabelFrame):
    """子网划分组件"""
    
    def __init__(self, master, on_divide=None, **kwargs):
        super().__init__(master, text="子网划分", padding=ui_helper.get_padding(15), **kwargs)
        
        self.on_divide = on_divide
        self.calculator = SubnetCalculator()
        
        # 当前网络信息
        self.current_network = None
        self.current_hosts = None
        
        # 划分方式变量
        self.divide_mode = tk.StringVar(value="subnets")  # 默认按子网数量
        
        # 划分参数变量
        self.subnet_count = tk.StringVar(value="4")  # 默认4个子网
        self.hosts_per_subnet = tk.StringVar(value="30")  # 默认每子网30个主机
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        # 当前网络信息显示
        self.info_label = tb.Label(
            self,
            text="当前网络: (未计算)",
            font=ui_helper.get_font(9),
            bootstyle=INFO
        )
        self.info_label.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        # 划分方式选择
        mode_frame = tb.Frame(self)
        mode_frame.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        tb.Label(mode_frame, text="划分方式：", font=ui_helper.get_font(9)).pack(side=LEFT)
        
        # 按子网数量
        subnet_radio_frame = tb.Frame(mode_frame)
        subnet_radio_frame.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        tb.Radiobutton(
            subnet_radio_frame,
            text="按子网数量",
            variable=self.divide_mode,
            value="subnets",
            command=self.on_mode_change,
            bootstyle="primary-toolbutton"
        ).pack(side=LEFT)
        
        tb.Label(subnet_radio_frame, text="需要", font=ui_helper.get_font(9)).pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(5)))
        
        self.subnet_count_spinbox = tb.Spinbox(
            subnet_radio_frame,
            from_=2, to=256,
            textvariable=self.subnet_count,
            width=ui_helper.scale_size(6),
            font=ui_helper.get_font(9)
        )
        self.subnet_count_spinbox.pack(side=LEFT)
        
        tb.Label(subnet_radio_frame, text="个子网", font=ui_helper.get_font(9)).pack(side=LEFT, padx=(ui_helper.get_padding(5), 0))
        
        # 按主机数量
        host_radio_frame = tb.Frame(mode_frame)
        host_radio_frame.pack(side=LEFT, padx=(ui_helper.get_padding(30), 0))
        
        tb.Radiobutton(
            host_radio_frame,
            text="按主机数量",
            variable=self.divide_mode,
            value="hosts",
            command=self.on_mode_change,
            bootstyle="primary-toolbutton"
        ).pack(side=LEFT)
        
        tb.Label(host_radio_frame, text="每个子网需要", font=ui_helper.get_font(9)).pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(5)))
        
        self.hosts_spinbox = tb.Spinbox(
            host_radio_frame,
            from_=1, to=65534,
            textvariable=self.hosts_per_subnet,
            width=ui_helper.scale_size(8),
            font=ui_helper.get_font(9)
        )
        self.hosts_spinbox.pack(side=LEFT)
        
        tb.Label(host_radio_frame, text="台主机", font=ui_helper.get_font(9)).pack(side=LEFT, padx=(ui_helper.get_padding(5), 0))
        
        # 初始状态设置
        self.on_mode_change()
        
        # 按钮
        button_frame = tb.Frame(self)
        button_frame.pack(fill=X, pady=(ui_helper.get_padding(10), ui_helper.get_padding(10)))
        
        self.divide_button = tb.Button(
            button_frame,
            text="开始划分",
            command=self.divide_subnet,
            bootstyle=PRIMARY,
            width=ui_helper.scale_size(12),
            state=DISABLED  # 初始禁用
        )
        self.divide_button.pack(side=LEFT)
        
        # 错误信息标签
        self.error_label = tb.Label(
            button_frame,
            text="",
            font=ui_helper.get_font(8),
            bootstyle=DANGER
        )
        self.error_label.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # 分隔线
        tb.Separator(self, orient=HORIZONTAL).pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        # 划分结果标签
        tb.Label(self, text="划分结果：", font=ui_helper.get_font(9, "bold")).pack(anchor=W)
        
        # 结果显示容器
        result_container = tb.Frame(self)
        result_container.pack(fill=BOTH, expand=True, pady=(ui_helper.get_padding(5), 0))
        
        # 创建Text组件显示结果（表格格式）
        self.result_text = tb.Text(
            result_container,
            height=8,  # 设置固定高度8行
            wrap=NONE,  # 不自动换行，保持表格格式
            state=DISABLED,
            relief=FLAT,
            borderwidth=ui_helper.scale_size(1),
            background='#f8f9fa',
            selectbackground='#0078d4',
            selectforeground='white',
            font=('Consolas', 9)  # 使用等宽字体确保对齐
        )
        
        # 添加垂直滚动条
        v_scrollbar = tb.Scrollbar(result_container, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=v_scrollbar.set)
        
        # 添加水平滚动条（因为不自动换行）
        h_scrollbar = tb.Scrollbar(result_container, orient=HORIZONTAL, command=self.result_text.xview)
        self.result_text.configure(xscrollcommand=h_scrollbar.set)
        
        # 布局
        self.result_text.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # 配置grid权重
        result_container.grid_rowconfigure(0, weight=1)
        result_container.grid_columnconfigure(0, weight=1)
        
        # 添加右键菜单
        self.context_menu = tb.Menu(self, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_selected_text)
        self.context_menu.add_command(label="全选", command=self.select_all_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制所有结果", command=self.copy_all_results)
        
        # 绑定右键菜单
        self.result_text.bind("<Button-3>", self.show_context_menu)
    
    def on_mode_change(self):
        """划分方式改变"""
        if self.divide_mode.get() == "subnets":
            self.subnet_count_spinbox.config(state=NORMAL)
            self.hosts_spinbox.config(state=DISABLED)
        else:
            self.subnet_count_spinbox.config(state=DISABLED)
            self.hosts_spinbox.config(state=NORMAL)
    
    def update_network_info(self, network_str: str, hosts_count: str):
        """更新当前网络信息"""
        self.current_network = network_str
        self.current_hosts = hosts_count
        self.info_label.config(text=f"当前网络: {network_str} (可用主机: {hosts_count})")
        self.divide_button.config(state=NORMAL)
        self.clear_error()
    
    def clear_error(self):
        """清空错误信息"""
        self.error_label.config(text="")
    
    def show_error(self, message: str):
        """显示错误信息"""
        self.error_label.config(text=f"⚠ {message}")
    
    def divide_subnet(self):
        """执行子网划分"""
        self.clear_error()
        
        if not self.current_network:
            self.show_error("请先进行基础计算")
            return
        
        try:
            # 解析当前网络
            if '/' in self.current_network:
                parts = self.current_network.split('/')
                ip_str = parts[0]
                cidr_bits = parts[1]
            else:
                self.show_error("网络信息格式错误")
                return
            
            # 获取划分参数
            if self.divide_mode.get() == "subnets":
                try:
                    subnet_count = int(self.subnet_count.get())
                    if subnet_count < 2:
                        self.show_error("子网数量至少为2")
                        return
                    results = self.calculator.divide_subnet(ip_str, cidr_bits, 'subnets', subnet_count)
                except ValueError:
                    self.show_error("请输入有效的子网数量")
                    return
            else:
                try:
                    hosts_count = int(self.hosts_per_subnet.get())
                    if hosts_count < 1:
                        self.show_error("主机数量至少为1")
                        return
                    results = self.calculator.divide_subnet(ip_str, cidr_bits, 'hosts', hosts_count)
                except ValueError:
                    self.show_error("请输入有效的主机数量")
                    return
            
            # 显示结果
            self.display_results(results)
            
            # 调用回调
            if self.on_divide:
                self.on_divide(results)
                
        except Exception as e:
            self.show_error(str(e))
    
    def display_results(self, results: list):
        """显示划分结果"""
        if not results:
            self._update_text_display("暂无划分结果")
            return
        
        # 构建表格格式的文本
        lines = []
        
        # 表头
        header = f"{'序号':<4} {'子网地址':<18} {'可用主机范围':<32} {'主机数':>6}"
        lines.append(header)
        lines.append("-" * len(header))  # 分隔线
        
        # 数据行
        for i, subnet in enumerate(results, 1):
            # 使用正确的英文字段名
            network_addr = subnet['network_address']
            host_range = subnet['host_range']
            host_count = subnet['host_count']
            
            line = f"{i:<4} {network_addr:<18} {host_range:<32} {host_count:>6}"
            lines.append(line)
        
        content = '\n'.join(lines)
        self._update_text_display(content)
    
    def clear_results(self):
        """清空结果"""
        # 清空文本显示
        self._update_text_display("")
        
        # 重置网络信息
        self.current_network = None
        self.current_hosts = None
        self.info_label.config(text="当前网络: (未计算)")
        self.divide_button.config(state=DISABLED)
        self.clear_error()
    
    def _update_text_display(self, content):
        """更新文本显示内容"""
        self.result_text.config(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", content)
        self.result_text.config(state=DISABLED)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            # 检查是否有选中的文本
            if self.result_text.selection_get():
                self.context_menu.entryconfig("复制", state=NORMAL)
            else:
                self.context_menu.entryconfig("复制", state=DISABLED)
        except:
            self.context_menu.entryconfig("复制", state=DISABLED)
        
        self.context_menu.post(event.x_root, event.y_root)
    
    def copy_selected_text(self):
        """复制选中的文本"""
        try:
            selected_text = self.result_text.selection_get()
            if selected_text:
                pyperclip.copy(selected_text)
        except:
            pass
    
    def select_all_text(self):
        """全选文本"""
        self.result_text.tag_add(SEL, "1.0", END)
        self.result_text.mark_set(INSERT, "1.0")
        self.result_text.see(INSERT)
    
    def copy_all_results(self):
        """复制所有划分结果"""
        try:
            # 获取所有文本内容
            all_text = self.result_text.get("1.0", END).strip()
            if all_text:
                pyperclip.copy(all_text)
        except Exception as e:
            pass
    
