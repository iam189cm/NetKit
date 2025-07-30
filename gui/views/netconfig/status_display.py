"""
状态显示UI组件
负责显示操作状态和日志信息
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper


class StatusDisplayWidget(tb.LabelFrame):
    """状态显示组件"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="状态", padding=ui_helper.get_padding(15), **kwargs)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 状态文本框（固定合理高度，不使用DPI缩放）
        self.status_text = tb.Text(
            self,
            height=3,  # 固定3行，确保状态栏可见但不占用过多空间
            state=DISABLED,
            wrap=WORD,
        )
        
        # 滚动条
        scrollbar = tb.Scrollbar(self, orient=VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 初始化状态信息
        self.append_status("=== NetKit 网卡配置工具 ===\n")
        self.append_status("请选择网卡查看当前配置信息\n")
    
    def append_status(self, text):
        """向状态框追加文本"""
        self.status_text.configure(state=NORMAL)
        self.status_text.insert(END, text)
        self.status_text.configure(state=DISABLED)
        self.status_text.see(END)
    
    def clear_status(self):
        """清空状态信息"""
        self.status_text.configure(state=NORMAL)
        self.status_text.delete(1.0, END)
        self.status_text.configure(state=DISABLED)
    
    def get_status_text(self):
        """获取状态文本内容"""
        return self.status_text.get(1.0, END)
    
    def set_status_text(self, text):
        """设置状态文本内容"""
        self.status_text.configure(state=NORMAL)
        self.status_text.delete(1.0, END)
        self.status_text.insert(1.0, text)
        self.status_text.configure(state=DISABLED)
        self.status_text.see(END) 