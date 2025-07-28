"""
IP方格单元格组件

用于可视化ping测试界面的单个IP状态显示
支持状态切换、闪烁动画和鼠标交互
"""

import tkinter as tk


class IPGridCell(tk.Canvas):
    """IP方格单元格"""
    
    # 状态常量
    STATE_INITIAL = "initial"
    STATE_SCANNING = "scanning"  
    STATE_ONLINE = "online"
    STATE_OFFLINE = "offline"
    
    # 颜色方案
    COLORS = {
        STATE_INITIAL: "#CCCCCC",
        STATE_SCANNING: "#FFFF00", 
        STATE_ONLINE: "#00AA00",
        STATE_OFFLINE: "#CC0000"
    }
    
    def __init__(self, master, ip_suffix, size=30, **kwargs):
        super().__init__(master, width=size, height=size, highlightthickness=1, 
                        highlightbackground="#666666", **kwargs)
        
        self.ip_suffix = ip_suffix  # IP最后一段数字
        self.size = size
        self.state = self.STATE_INITIAL
        self.ping_result = None
        self.is_blinking = False
        self.blink_job = None
        
        # 绘制初始状态
        self.draw_cell()
        
        # 绑定鼠标事件
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<Double-Button-1>", self.on_double_click)
        self.bind("<Button-3>", self.on_right_click)
        
    def draw_cell(self):
        """绘制方格"""
        self.delete("all")
        
        # 绘制背景
        color = self.COLORS[self.state]
        self.create_rectangle(2, 2, self.size-2, self.size-2, 
                            fill=color, outline="#333333", width=1)
        
        # 绘制IP后缀数字
        if self.ip_suffix > 0:  # 跳过0和255
            font_size = max(8, self.size // 4)
            self.create_text(self.size//2, self.size//2, 
                           text=str(self.ip_suffix),
                           font=('微软雅黑', font_size, 'bold'),
                           fill="white" if self.state in [self.STATE_ONLINE, self.STATE_OFFLINE] else "black")
    
    def set_state(self, state, ping_result=None):
        """设置方格状态"""
        if state == self.state:
            return
            
        self.state = state
        self.ping_result = ping_result
        
        # 停止闪烁
        if self.blink_job:
            self.after_cancel(self.blink_job)
            self.blink_job = None
            self.is_blinking = False
        
        # 如果是扫描状态，启动闪烁
        if state == self.STATE_SCANNING:
            self.start_blinking()
        else:
            self.draw_cell()
    
    def start_blinking(self):
        """开始闪烁动画（1秒3次）"""
        if not self.is_blinking:
            self.is_blinking = True
            self.blink()
    
    def blink(self):
        """闪烁动画实现"""
        if not self.is_blinking or self.state != self.STATE_SCANNING:
            return
            
        # 切换显示/隐藏
        current_color = self.itemcget(self.find_all()[0], "fill")
        if current_color == self.COLORS[self.STATE_SCANNING]:
            # 切换到暗色
            self.itemconfig(self.find_all()[0], fill="#CCAA00")
        else:
            # 切换到亮色
            self.itemconfig(self.find_all()[0], fill=self.COLORS[self.STATE_SCANNING])
        
        # 继续闪烁（333ms间隔，1秒3次）
        self.blink_job = self.after(333, self.blink)
    
    def stop_blinking(self):
        """停止闪烁"""
        self.is_blinking = False
        if self.blink_job:
            self.after_cancel(self.blink_job)
            self.blink_job = None
    
    def on_left_click(self, event):
        """左键单击 - 显示详细信息"""
        if hasattr(self.master, 'show_ip_details'):
            self.master.show_ip_details(self.ip_suffix, event)
    
    def on_double_click(self, event):
        """双击 - 单独ping该IP"""
        if hasattr(self.master, 'ping_single_ip'):
            self.master.ping_single_ip(self.ip_suffix)
    
    def on_right_click(self, event):
        """右键单击 - 显示菜单"""
        if hasattr(self.master, 'show_context_menu'):
            self.master.show_context_menu(self.ip_suffix, event) 