"""
结果显示组件
职责：操作结果展示、消息管理、格式化显示
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from datetime import datetime


class ResultDisplayWidget(tb.LabelFrame):
    """结果显示组件"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="操作结果", padding=ui_helper.get_padding(10), **kwargs)
        
        self.setup_display()
        self.initialize_display()
        
    def setup_display(self):
        """设置显示区域"""
        self.result_text = tb.Text(
            self,
            height=ui_helper.scale_size(6),
            state=DISABLED,
            wrap=WORD,
            font=ui_helper.get_font()
        )
        
        result_scrollbar = tb.Scrollbar(self, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        self.result_text.pack(side=LEFT, fill=BOTH, expand=True)
        result_scrollbar.pack(side=RIGHT, fill=Y)
        
    def initialize_display(self):
        """初始化显示内容"""
        self.append_result("=== Netkit 静态路由管理工具 ===\n")
        self.append_result("点击'刷新路由表'按钮获取当前路由信息\n\n")
        
    def append_result(self, message, msg_type='info'):
        """追加结果消息"""
        self.result_text.configure(state=NORMAL)
        
        # 格式化消息（可以根据类型添加不同的前缀或样式）
        formatted_message = self._format_message(message, msg_type)
        
        self.result_text.insert(END, formatted_message)
        self.result_text.configure(state=DISABLED)
        self.result_text.see(END)
        
    def _format_message(self, message, msg_type):
        """格式化消息"""
        # 根据消息类型添加不同的标识
        if msg_type == 'success':
            return f"✓ {message}"
        elif msg_type == 'error':
            return f"✗ {message}"
        elif msg_type == 'warning':
            return f"⚠ {message}"
        else:
            return message
            
    def append_success(self, message):
        """追加成功消息"""
        self.append_result(message, 'success')
        
    def append_error(self, message):
        """追加错误消息"""
        self.append_result(message, 'error')
        
    def append_warning(self, message):
        """追加警告消息"""
        self.append_result(message, 'warning')
        
    def append_info(self, message):
        """追加信息消息"""
        self.append_result(message, 'info')
        
    def clear_results(self):
        """清空结果显示"""
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.configure(state=DISABLED)
        self.initialize_display()
        
    def get_text_widget(self):
        """获取文本组件（用于直接操作）"""
        return self.result_text