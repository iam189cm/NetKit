"""
子网计算输入表单组件
负责处理用户输入和验证
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.subnet import SubnetCalculator, IPValidator
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
        
        # 错误信息标签引用
        self.error_labels = {}
        
        self.setup_form()
        
    def setup_form(self):
        """设置表单"""
        # 直接创建传统输入界面
        self.create_traditional_input()
        
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
    

    
    def create_traditional_input(self):
        """创建输入界面"""
        # IP地址和子网掩码在同一行
        input_row = tb.Frame(self)
        input_row.pack(fill=X, pady=(0, ui_helper.get_padding(5)))
        
        # IP地址
        tb.Label(input_row, text="IP地址：", font=ui_helper.get_font(9)).pack(side=LEFT)
        
        self.ip_entry = tb.Entry(input_row, width=ui_helper.scale_size(18))
        self.ip_entry.pack(side=LEFT, padx=(ui_helper.get_padding(5), ui_helper.get_padding(15)))
        
        # 子网掩码
        tb.Label(input_row, text="子网掩码：", font=ui_helper.get_font(9)).pack(side=LEFT)
        
        self.mask_entry = tb.Entry(input_row, width=ui_helper.scale_size(18))
        self.mask_entry.pack(side=LEFT, padx=(ui_helper.get_padding(5), ui_helper.get_padding(10)))
        
        # 提示信息
        tb.Label(
            input_row,
            text="支持输入: 255.255.255.0 或 /24",
            font=ui_helper.get_font(8),
            bootstyle=SECONDARY
        ).pack(side=LEFT)
        
        # 错误信息行
        error_frame = tb.Frame(self)
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
            # 获取输入数据
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
            self.show_error('ip', str(e))
    
    def clear(self):
        """清空表单"""
        # 真正清空所有输入
        self.ip_entry.delete(0, END)
        self.mask_entry.delete(0, END)
        
        # 清空错误信息
        self.clear_errors()
        
        # 调用回调
        if self.on_clear:
            self.on_clear()