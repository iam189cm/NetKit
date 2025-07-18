import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.subnet import SubnetCalculator, calculate_subnet_details, vlsm_subnetting
import tkinter.messagebox as mbox
import threading


class SubnetFrame(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.calculator = SubnetCalculator()
        self.setup_ui()
        
    def setup_ui(self):
        """设置子网计算界面"""
        # 标题
        title = tb.Label(
            self, 
            text="子网与VLSM计算器",            bootstyle=INFO
        )
        title.pack(pady=(ui_helper.get_padding(0), ui_helper.get_padding(20)))
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 左侧功能区域
        left_frame = tb.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        # 创建notebook来组织不同功能
        self.notebook = tb.Notebook(left_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # 子网信息查询标签页
        self.setup_subnet_info_tab()
        
        # VLSM计算标签页
        self.setup_vlsm_tab()
        
        # 格式转换标签页
        self.setup_conversion_tab()
        
        # 右侧结果显示区域
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        result_frame = tb.LabelFrame(right_frame, text="计算结果", padding=ui_helper.get_padding(15))
        result_frame.pack(fill=BOTH, expand=True)
        
        # 结果文本框
        self.result_text = tb.Text(
            result_frame,
            height=ui_helper.scale_size(25),
            state=DISABLED,
            wrap=WORD,
            font=('Consolas', ui_helper.scale_size(10))
        )
        
        # 滚动条
        scrollbar = tb.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 清空结果按钮
        clear_btn_frame = tb.Frame(result_frame)
        clear_btn_frame.pack(fill=X, pady=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        tb.Button(
            clear_btn_frame,
            text="清空结果",
            bootstyle=LIGHT,
            command=self.clear_result,
            width=ui_helper.scale_size(12)
        ).pack(side=RIGHT)
        
        # 初始化
        self.append_result("=== Netkit 子网与VLSM计算器 ===\n")
        self.append_result("选择左侧标签页进行不同类型的计算\n\n")
    
    def setup_subnet_info_tab(self):
        """设置子网信息查询标签页"""
        subnet_info_frame = tb.Frame(self.notebook)
        self.notebook.add(subnet_info_frame, text="子网信息")
        
        # 网络地址输入
        input_frame = tb.LabelFrame(subnet_info_frame, text="网络地址", padding=ui_helper.get_padding(15))
        input_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(input_frame, text="网络地址 (CIDR):").pack(anchor=W, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        self.network_entry = tb.Entry(input_frame, width=ui_helper.scale_size(30), font=('Consolas', ui_helper.scale_size(11)))
        self.network_entry.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        self.network_entry.insert(0, "192.168.1.0/24")
        
        # 示例说明
        example_frame = tb.Frame(input_frame)
        example_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(
            example_frame, 
            text="示例: 192.168.1.0/24 或 10.0.0.0/8",            bootstyle=SECONDARY
        ).pack(side=LEFT)
        
        # 计算按钮
        tb.Button(
            input_frame,
            text="计算子网信息",
            bootstyle=INFO,
            command=self.calculate_subnet_info,
            width=ui_helper.scale_size(20)
        ).pack(pady=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        # 常用子网快速选择
        quick_frame = tb.LabelFrame(subnet_info_frame, text="常用子网", padding=ui_helper.get_padding(10))
        quick_frame.pack(fill=X)
        
        common_networks = [
            "192.168.1.0/24", "192.168.0.0/16", "10.0.0.0/8",
            "172.16.0.0/12", "192.168.1.0/28", "192.168.1.0/30"
        ]
        
        for i, network in enumerate(common_networks):
            row = i // 2
            col = i % 2
            
            tb.Button(
                quick_frame,
                text=network,
                bootstyle=OUTLINE,
                command=lambda net=network: self.set_network_address(net),
                width=ui_helper.scale_size(18)
            ).grid(row=row, column=col, padx=ui_helper.get_padding(5), pady=ui_helper.get_padding(3), sticky=W)
    
    def setup_vlsm_tab(self):
        """设置VLSM计算标签页"""
        vlsm_frame = tb.Frame(self.notebook)
        self.notebook.add(vlsm_frame, text="VLSM划分")
        
        # 基础网络输入
        base_frame = tb.LabelFrame(vlsm_frame, text="基础网络", padding=ui_helper.get_padding(15))
        base_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(base_frame, text="基础网络 (CIDR):").pack(anchor=W, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        self.base_network_entry = tb.Entry(base_frame, width=ui_helper.scale_size(30), font=('Consolas', ui_helper.scale_size(11)))
        self.base_network_entry.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        self.base_network_entry.insert(0, "192.168.1.0/24")
        
        # 子网需求输入
        requirements_frame = tb.LabelFrame(vlsm_frame, text="子网需求", padding=ui_helper.get_padding(15))
        requirements_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(requirements_frame, text="主机数需求 (每行一个数字):").pack(anchor=W, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        self.requirements_text = tb.Text(
            requirements_frame,
            height=ui_helper.scale_size(8),
            width=ui_helper.scale_size(25),
            wrap=WORD,
            font=('Consolas', ui_helper.scale_size(11))
        )
        
        req_scrollbar = tb.Scrollbar(requirements_frame, orient=VERTICAL, command=self.requirements_text.yview)
        self.requirements_text.configure(yscrollcommand=req_scrollbar.set)
        
        text_frame = tb.Frame(requirements_frame)
        text_frame.pack(fill=BOTH, expand=True, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        self.requirements_text.pack(side=LEFT, fill=BOTH, expand=True)
        req_scrollbar.pack(side=RIGHT, fill=Y)
        
        # 默认需求示例
        default_requirements = "50\n25\n10\n5"
        self.requirements_text.insert("1.0", default_requirements)
        
        # VLSM计算按钮
        tb.Button(
            requirements_frame,
            text="计算VLSM划分",
            bootstyle=WARNING,
            command=self.calculate_vlsm,
            width=ui_helper.scale_size(20)
        ).pack(pady=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        # 快速模板
        template_frame = tb.LabelFrame(vlsm_frame, text="快速模板", padding=ui_helper.get_padding(10))
        template_frame.pack(fill=X)
        
        templates = [
            ("办公网络", "100\n50\n20\n10"),
            ("校园网络", "500\n200\n100\n30"),
            ("小型企业", "50\n25\n10\n5"),
            ("数据中心", "1000\n500\n100\n50")
        ]
        
        for i, (name, template) in enumerate(templates):
            row = i // 2
            col = i % 2
            
            tb.Button(
                template_frame,
                text=name,
                bootstyle=OUTLINE,
                command=lambda t=template: self.set_requirements_template(t),
                width=ui_helper.scale_size(12)
            ).grid(row=row, column=col, padx=ui_helper.get_padding(5), pady=ui_helper.get_padding(3))
    
    def setup_conversion_tab(self):
        """设置格式转换标签页"""
        conversion_frame = tb.Frame(self.notebook)
        self.notebook.add(conversion_frame, text="格式转换")
        
        # CIDR转点分十进制
        cidr_frame = tb.LabelFrame(conversion_frame, text="CIDR → 点分十进制", padding=ui_helper.get_padding(15))
        cidr_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(cidr_frame, text="CIDR地址:").pack(anchor=W, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        self.cidr_entry = tb.Entry(cidr_frame, width=ui_helper.scale_size(25), font=('Consolas', ui_helper.scale_size(11)))
        self.cidr_entry.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        self.cidr_entry.insert(0, "192.168.1.0/24")
        
        tb.Button(
            cidr_frame,
            text="转换为点分十进制",
            bootstyle=INFO,
            command=self.convert_cidr_to_dotted,
            width=ui_helper.scale_size(20)
        ).pack()
        
        # 点分十进制转CIDR
        dotted_frame = tb.LabelFrame(conversion_frame, text="点分十进制 → CIDR", padding=ui_helper.get_padding(15))
        dotted_frame.pack(fill=X)
        
        # IP地址
        ip_input_frame = tb.Frame(dotted_frame)
        ip_input_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        tb.Label(ip_input_frame, text="IP地址:").pack(side=LEFT)
        self.ip_entry = tb.Entry(ip_input_frame, width=ui_helper.scale_size(15), font=('Consolas', ui_helper.scale_size(11)))
        self.ip_entry.pack(side=RIGHT)
        self.ip_entry.insert(0, "192.168.1.1")
        
        # 子网掩码
        mask_input_frame = tb.Frame(dotted_frame)
        mask_input_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(mask_input_frame, text="子网掩码:").pack(side=LEFT)
        self.mask_entry = tb.Entry(mask_input_frame, width=ui_helper.scale_size(15), font=('Consolas', ui_helper.scale_size(11)))
        self.mask_entry.pack(side=RIGHT)
        self.mask_entry.insert(0, "255.255.255.0")
        
        tb.Button(
            dotted_frame,
            text="转换为CIDR",
            bootstyle=SUCCESS,
            command=self.convert_dotted_to_cidr,
            width=ui_helper.scale_size(20)
        ).pack()
    
    def set_network_address(self, network):
        """设置网络地址"""
        self.network_entry.delete(0, END)
        self.network_entry.insert(0, network)
        
    def set_requirements_template(self, template):
        """设置需求模板"""
        self.requirements_text.delete("1.0", END)
        self.requirements_text.insert("1.0", template)
    
    def calculate_subnet_info(self):
        """计算子网信息"""
        network = self.network_entry.get().strip()
        if not network:
            mbox.showwarning("输入错误", "请输入网络地址")
            return
        
        self.append_result(f"\n正在计算子网 {network} 的详细信息...\n")
        self.append_result("=" * 50 + "\n")
        
        def do_calculation():
            try:
                result = calculate_subnet_details(network)
                self.after(0, lambda: self.show_subnet_info_result(result))
            except Exception as e:
                self.after(0, lambda: self.append_result(f"计算出错: {str(e)}\n"))
        
        threading.Thread(target=do_calculation, daemon=True).start()
    
    def calculate_vlsm(self):
        """计算VLSM划分"""
        base_network = self.base_network_entry.get().strip()
        requirements_text = self.requirements_text.get("1.0", END).strip()
        
        if not base_network:
            mbox.showwarning("输入错误", "请输入基础网络地址")
            return
            
        if not requirements_text:
            mbox.showwarning("输入错误", "请输入主机数需求")
            return
        
        # 解析需求
        try:
            requirements = []
            for line in requirements_text.split('\n'):
                line = line.strip()
                if line and line.isdigit():
                    requirements.append(int(line))
            
            if not requirements:
                mbox.showwarning("输入错误", "未发现有效的主机数需求")
                return
                
        except ValueError:
            mbox.showwarning("输入错误", "主机数需求必须是数字")
            return
        
        self.append_result(f"\n正在计算 {base_network} 的VLSM划分...\n")
        self.append_result(f"子网需求: {requirements}\n")
        self.append_result("=" * 60 + "\n")
        
        def do_vlsm():
            try:
                result = vlsm_subnetting(base_network, requirements)
                self.after(0, lambda: self.show_vlsm_result(result))
            except Exception as e:
                self.after(0, lambda: self.append_result(f"VLSM计算出错: {str(e)}\n"))
        
        threading.Thread(target=do_vlsm, daemon=True).start()
    
    def convert_cidr_to_dotted(self):
        """CIDR转点分十进制"""
        cidr = self.cidr_entry.get().strip()
        if not cidr:
            mbox.showwarning("输入错误", "请输入CIDR地址")
            return
        
        self.append_result(f"\n转换 {cidr} 为点分十进制格式...\n")
        self.append_result("-" * 40 + "\n")
        
        result = self.calculator.cidr_to_dotted(cidr)
        if result['success']:
            self.append_result(f"CIDR地址: {result['cidr']}\n")
            self.append_result(f"子网掩码: {result['dotted_mask']}\n")
            self.append_result(f"通配符掩码: {result['wildcard']}\n")
            self.append_result(f"前缀长度: /{result['prefix_length']}\n")
        else:
            self.append_result(f"转换失败: {result['error']}\n")
        
        self.append_result("\n")
    
    def convert_dotted_to_cidr(self):
        """点分十进制转CIDR"""
        ip = self.ip_entry.get().strip()
        mask = self.mask_entry.get().strip()
        
        if not ip or not mask:
            mbox.showwarning("输入错误", "请输入IP地址和子网掩码")
            return
        
        self.append_result(f"\n转换 {ip} / {mask} 为CIDR格式...\n")
        self.append_result("-" * 40 + "\n")
        
        result = self.calculator.dotted_to_cidr(ip, mask)
        if result['success']:
            self.append_result(f"IP地址: {result['ip']}\n")
            self.append_result(f"子网掩码: {result['mask']}\n")
            self.append_result(f"CIDR格式: {result['cidr']}\n")
            self.append_result(f"网络地址: {result['network_address']}\n")
            self.append_result(f"前缀长度: /{result['prefix_length']}\n")
        else:
            self.append_result(f"转换失败: {result['error']}\n")
        
        self.append_result("\n")
    
    def show_subnet_info_result(self, result):
        """显示子网信息结果"""
        if result['success']:
            self.append_result(f"网络地址: {result['network_address']}\n")
            self.append_result(f"广播地址: {result['broadcast_address']}\n")
            self.append_result(f"子网掩码: {result['netmask']}\n")
            self.append_result(f"通配符掩码: {result['wildcard']}\n")
            self.append_result(f"前缀长度: /{result['prefix_length']}\n")
            self.append_result(f"子网类别: {result['subnet_class']}\n")
            self.append_result(f"总地址数: {result['total_addresses']}\n")
            self.append_result(f"可用主机数: {result['usable_hosts']}\n")
            self.append_result(f"第一个可用IP: {result['first_usable']}\n")
            self.append_result(f"最后一个可用IP: {result['last_usable']}\n")
            self.append_result("✓ 计算完成\n")
        else:
            self.append_result(f"✗ 计算失败: {result['error']}\n")
        
        self.append_result("\n")
    
    def show_vlsm_result(self, result):
        """显示VLSM结果"""
        if result['success']:
            self.append_result(f"基础网络: {result['base_network']}\n")
            self.append_result(f"子网数量: {len(result['subnets'])}\n")
            self.append_result(f"地址利用率: {result['utilization']:.1f}%\n\n")
            
            for i, subnet in enumerate(result['subnets'], 1):
                self.append_result(f"子网 {i} (需求 {subnet['hosts_required']} 主机):\n")
                self.append_result(f"  网络地址: {subnet['network_address']}/{subnet['prefix_length']}\n")
                self.append_result(f"  广播地址: {subnet['broadcast_address']}\n")
                self.append_result(f"  子网掩码: {subnet['netmask']}\n")
                self.append_result(f"  可用主机: {subnet['usable_hosts']}\n")
                self.append_result(f"  IP范围: {subnet['first_usable']} - {subnet['last_usable']}\n")
                self.append_result("\n")
            
            if result['remaining_networks']:
                self.append_result("剩余可用网络段:\n")
                for net in result['remaining_networks']:
                    self.append_result(f"  {net}\n")
                self.append_result("\n")
            
            self.append_result("✓ VLSM计算完成\n")
        else:
            self.append_result(f"✗ VLSM计算失败: {result['error']}\n")
        
        self.append_result("\n")
    
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