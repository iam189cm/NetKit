"""
子网计算输入表单组件
负责处理用户输入和验证
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.subnet import SubnetCalculator, IPValidator, CIDRConverter
import tkinter as tk


class SubnetInputForm(tb.LabelFrame):
    """子网计算输入表单"""
    
    def __init__(self, master, on_calculate=None, on_clear=None, **kwargs):
        super().__init__(master, text="基础计算", padding=ui_helper.get_padding(15), **kwargs)
        
        self.on_calculate = on_calculate
        self.on_clear = on_clear
        
        # 服务实例
        self.calculator = SubnetCalculator()
        self.validator = IPValidator()
        self.converter = CIDRConverter()
        
        # 输入模式变量
        self.input_mode = tk.StringVar(value="cidr")  # 默认CIDR方式
        
        # 错误信息标签引用
        self.error_labels = {}
        
        self.setup_form()
        
    def setup_form(self):
        """设置表单"""
        # 输入方式选择
        mode_frame = tb.Frame(self)
        mode_frame.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        tb.Label(mode_frame, text="输入方式：", font=ui_helper.get_font(9)).pack(side=LEFT)
        
        tb.Radiobutton(
            mode_frame,
            text="传统方式",
            variable=self.input_mode,
            value="traditional",
            command=self.on_mode_change,
            bootstyle="primary-toolbutton"
        ).pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(5)))
        
        tb.Radiobutton(
            mode_frame,
            text="CIDR方式",
            variable=self.input_mode,
            value="cidr",
            command=self.on_mode_change,
            bootstyle="primary-toolbutton"
        ).pack(side=LEFT, padx=(0, ui_helper.get_padding(10)))
        
        # 输入区域容器
        self.input_container = tb.Frame(self)
        self.input_container.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        # 创建两种输入界面
        self.create_cidr_input()
        self.create_traditional_input()
        
        # 默认显示CIDR输入
        self.show_cidr_input()
        
        # 按钮区域
        button_frame = tb.Frame(self)
        button_frame.pack(fill=X)
        
        tb.Button(
            button_frame,
            text="计算",
            command=self.calculate,
            bootstyle=PRIMARY,
            width=ui_helper.scale_size(10)
        ).pack(side=LEFT, padx=(0, ui_helper.get_padding(10)))
        
        tb.Button(
            button_frame,
            text="清空",
            command=self.clear,
            bootstyle=SECONDARY,
            width=ui_helper.scale_size(10)
        ).pack(side=LEFT)
    
    def create_cidr_input(self):
        """创建CIDR输入界面"""
        self.cidr_frame = tb.Frame(self.input_container)
        
        # CIDR输入行
        input_row = tb.Frame(self.cidr_frame)
        input_row.pack(fill=X)
        
        tb.Label(input_row, text="IP地址/掩码：", font=ui_helper.get_font(9)).pack(side=LEFT)
        
        self.cidr_entry = tb.Entry(input_row, width=ui_helper.scale_size(25))
        self.cidr_entry.pack(side=LEFT, padx=(ui_helper.get_padding(5), 0))
        self.cidr_entry.insert(0, "192.168.1.0/24")  # 默认值
        
        # 错误信息标签
        error_frame = tb.Frame(self.cidr_frame)
        error_frame.pack(fill=X, pady=(ui_helper.get_padding(2), 0))
        
        self.error_labels['cidr'] = tb.Label(
            error_frame,
            text="",
            font=ui_helper.get_font(8),
            bootstyle=DANGER
        )
        self.error_labels['cidr'].pack(side=LEFT, padx=(ui_helper.get_padding(120), 0))
    
    def create_traditional_input(self):
        """创建传统输入界面"""
        self.traditional_frame = tb.Frame(self.input_container)
        
        # IP地址和子网掩码在同一行
        input_row = tb.Frame(self.traditional_frame)
        input_row.pack(fill=X, pady=(0, ui_helper.get_padding(5)))
        
        # IP地址
        tb.Label(input_row, text="IP地址：", font=ui_helper.get_font(9)).pack(side=LEFT)
        
        self.ip_entry = tb.Entry(input_row, width=ui_helper.scale_size(18))
        self.ip_entry.pack(side=LEFT, padx=(ui_helper.get_padding(5), ui_helper.get_padding(15)))
        self.ip_entry.insert(0, "192.168.1.0")  # 默认值
        
        # 子网掩码
        tb.Label(input_row, text="子网掩码：", font=ui_helper.get_font(9)).pack(side=LEFT)
        
        self.mask_entry = tb.Entry(input_row, width=ui_helper.scale_size(18))
        self.mask_entry.pack(side=LEFT, padx=(ui_helper.get_padding(5), ui_helper.get_padding(10)))
        self.mask_entry.insert(0, "255.255.255.0")  # 默认值
        
        # 提示信息
        tb.Label(
            input_row,
            text="支持输入: 255.255.255.0 或 /24",
            font=ui_helper.get_font(8),
            bootstyle=SECONDARY
        ).pack(side=LEFT)
        
        # 错误信息行
        error_frame = tb.Frame(self.traditional_frame)
        error_frame.pack(fill=X, pady=(ui_helper.get_padding(2), 0))
        
        # IP地址错误信息
        self.error_labels['ip'] = tb.Label(
            error_frame,
            text="",
            font=ui_helper.get_font(8),
            bootstyle=DANGER
        )
        self.error_labels['ip'].pack(side=LEFT, padx=(ui_helper.get_padding(80), 0))
        
        # 子网掩码错误信息
        self.error_labels['mask'] = tb.Label(
            error_frame,
            text="",
            font=ui_helper.get_font(8),
            bootstyle=DANGER
        )
        self.error_labels['mask'].pack(side=LEFT, padx=(ui_helper.get_padding(20), 0))
    
    def on_mode_change(self):
        """输入模式切换"""
        if self.input_mode.get() == "cidr":
            self.show_cidr_input()
            # 尝试从传统输入转换到CIDR
            self.convert_to_cidr()
        else:
            self.show_traditional_input()
            # 尝试从CIDR转换到传统输入
            self.convert_to_traditional()
        
        # 清空所有错误信息
        self.clear_errors()
    
    def show_cidr_input(self):
        """显示CIDR输入界面"""
        self.traditional_frame.pack_forget()
        self.cidr_frame.pack(fill=X)
    
    def show_traditional_input(self):
        """显示传统输入界面"""
        self.cidr_frame.pack_forget()
        self.traditional_frame.pack(fill=X)
    
    def convert_to_cidr(self):
        """从传统输入转换到CIDR格式"""
        try:
            ip = self.ip_entry.get().strip()
            mask = self.mask_entry.get().strip()
            
            if ip and mask:
                # 如果掩码是CIDR格式
                if mask.startswith('/') or mask.isdigit():
                    cidr_bits = mask.strip('/')
                    self.cidr_entry.delete(0, END)
                    self.cidr_entry.insert(0, f"{ip}/{cidr_bits}")
                else:
                    # 转换子网掩码到CIDR
                    cidr_bits = self.converter.mask_to_cidr(mask)
                    if cidr_bits is not None:
                        self.cidr_entry.delete(0, END)
                        self.cidr_entry.insert(0, f"{ip}/{cidr_bits}")
        except:
            pass
    
    def convert_to_traditional(self):
        """从CIDR格式转换到传统输入"""
        try:
            cidr_str = self.cidr_entry.get().strip()
            if '/' in cidr_str:
                parts = cidr_str.split('/')
                if len(parts) == 2:
                    ip = parts[0]
                    cidr_bits = int(parts[1])
                    mask = self.converter.cidr_to_mask(cidr_bits)
                    
                    if mask:
                        self.ip_entry.delete(0, END)
                        self.ip_entry.insert(0, ip)
                        self.mask_entry.delete(0, END)
                        self.mask_entry.insert(0, mask)
        except:
            pass
    
    def clear_errors(self):
        """清空所有错误信息"""
        for label in self.error_labels.values():
            label.config(text="")
    
    def show_error(self, field: str, message: str):
        """显示错误信息"""
        if field in self.error_labels:
            self.error_labels[field].config(text=f"⚠ {message}")
    
    def calculate(self):
        """执行计算"""
        self.clear_errors()
        
        try:
            if self.input_mode.get() == "cidr":
                # CIDR模式
                cidr_str = self.cidr_entry.get().strip()
                if not cidr_str:
                    self.show_error('cidr', "请输入IP地址和CIDR")
                    return
                
                # 验证CIDR格式
                valid, error, parsed = self.validator.validate_cidr_notation(cidr_str)
                if not valid:
                    self.show_error('cidr', error)
                    return
                
                ip_str, cidr_bits = parsed
                network_info = self.calculator.calculate_subnet_info(ip_str, str(cidr_bits))
                
            else:
                # 传统模式
                ip_str = self.ip_entry.get().strip()
                mask_str = self.mask_entry.get().strip()
                
                if not ip_str:
                    self.show_error('ip', "请输入IP地址")
                    return
                
                if not mask_str:
                    self.show_error('mask', "请输入子网掩码")
                    return
                
                # 验证IP地址
                valid, error = self.validator.validate_ip_address(ip_str)
                if not valid:
                    self.show_error('ip', error)
                    return
                
                # 处理掩码输入（支持CIDR格式）
                if mask_str.startswith('/') or mask_str.isdigit():
                    # CIDR格式
                    if mask_str.startswith('/'):
                        cidr_bits = int(mask_str[1:])
                    else:
                        cidr_bits = int(mask_str)
                    
                    valid, error = self.validator.validate_cidr(cidr_bits)
                    if not valid:
                        self.show_error('mask', error)
                        return
                    
                    network_info = self.calculator.calculate_subnet_info(ip_str, str(cidr_bits))
                else:
                    # 子网掩码格式
                    valid, error = self.validator.validate_subnet_mask(mask_str)
                    if not valid:
                        self.show_error('mask', error)
                        return
                    
                    network_info = self.calculator.calculate_subnet_info(ip_str, mask_str)
            
            # 调用回调
            if self.on_calculate:
                self.on_calculate(network_info)
                
        except Exception as e:
            # 根据当前模式显示错误
            if self.input_mode.get() == "cidr":
                self.show_error('cidr', str(e))
            else:
                self.show_error('ip', str(e))
    
    def clear(self):
        """清空表单"""
        # 清空输入
        self.cidr_entry.delete(0, END)
        self.cidr_entry.insert(0, "192.168.1.0/24")
        
        self.ip_entry.delete(0, END)
        self.ip_entry.insert(0, "192.168.1.0")
        
        self.mask_entry.delete(0, END)
        self.mask_entry.insert(0, "255.255.255.0")
        
        # 清空错误信息
        self.clear_errors()
        
        # 调用回调
        if self.on_clear:
            self.on_clear()