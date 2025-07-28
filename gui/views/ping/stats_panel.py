"""
Ping统计面板模块

显示ping测试的实时统计信息
包括成功率、响应时间、丢包率等关键指标
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from datetime import datetime


class PingStatsPanel(tb.LabelFrame):
    """Ping统计信息面板"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="统计信息", padding=ui_helper.get_padding(10), **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """设置统计面板UI"""
        # 创建统计标签网格
        stats_grid = tb.Frame(self)
        stats_grid.pack(fill=X)
        
        # 统计信息标签定义
        stat_labels = [
            ("当前目标:", "current_target_label", "目标主机地址"),
            ("总IP数:", "total_ips_label", "测试的IP地址总数"),
            ("已发送:", "sent_label", "已发送的数据包数"),
            ("已接收:", "received_label", "已接收的数据包数"),
            ("丢包率:", "loss_label", "数据包丢失百分比"),
            ("成功率:", "success_rate_label", "测试成功百分比"),
            ("平均时间:", "avg_label", "平均响应时间"),
            ("运行时间:", "runtime_label", "测试运行时间")
        ]
        
        # 创建统计标签
        for i, (text, attr_name, tooltip) in enumerate(stat_labels):
            row = i // 2
            col = (i % 2) * 2
            
            # 标签文本
            label = tb.Label(stats_grid, text=text)
            label.grid(row=row, column=col, sticky=W, padx=ui_helper.get_padding(5), pady=ui_helper.get_padding(2))
            
            # 数值标签
            value_label = tb.Label(stats_grid, text="--", bootstyle=INFO)
            value_label.grid(row=row, column=col+1, sticky=W, padx=ui_helper.get_padding(5), pady=ui_helper.get_padding(2))
            setattr(self, attr_name, value_label)
            
            # 添加工具提示
            self._create_tooltip(value_label, tooltip)
        
        # 性能指标面板
        perf_frame = tb.LabelFrame(self, text="性能指标", padding=ui_helper.get_padding(10))
        perf_frame.pack(fill=X, pady=(ui_helper.get_padding(15), 0))
        
        perf_grid = tb.Frame(perf_frame)
        perf_grid.pack(fill=X)
        
        # 性能指标标签
        perf_labels = [
            ("最小时间:", "min_time_label"),
            ("最大时间:", "max_time_label"),
            ("时间抖动:", "jitter_label"),
            ("网络质量:", "quality_label")
        ]
        
        for i, (text, attr_name) in enumerate(perf_labels):
            row = i // 2
            col = (i % 2) * 2
            
            tb.Label(perf_grid, text=text).grid(
                row=row, column=col, sticky=W, 
                padx=ui_helper.get_padding(5), pady=ui_helper.get_padding(2)
            )
            
            value_label = tb.Label(perf_grid, text="--", bootstyle=SECONDARY)
            value_label.grid(
                row=row, column=col+1, sticky=W, 
                padx=ui_helper.get_padding(5), pady=ui_helper.get_padding(2)
            )
            setattr(self, attr_name, value_label)
        
        # 状态指示器
        status_frame = tb.Frame(self)
        status_frame.pack(fill=X, pady=(ui_helper.get_padding(15), 0))
        
        tb.Label(status_frame, text="连接状态:").pack(side=LEFT)
        self.status_indicator = tb.Label(
            status_frame, 
            text="● 未连接", 
            bootstyle=SECONDARY
        )
        self.status_indicator.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # 重置按钮
        tb.Button(
            status_frame,
            text="重置统计",
            bootstyle=OUTLINE,
            width=ui_helper.scale_size(10),
            command=self.reset_stats
        ).pack(side=RIGHT)
        
        # 初始化统计
        self.reset_stats()
    
    def _create_tooltip(self, widget, text):
        """创建工具提示"""
        def show_tooltip(event):
            # 简单的工具提示实现
            pass
        
        def hide_tooltip(event):
            pass
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def update_stats(self, stats_data):
        """
        更新统计信息
        
        Args:
            stats_data (dict): 统计数据
        """
        # 更新基本统计
        if 'current_host' in stats_data:
            self.current_target_label.config(text=str(stats_data['current_host'] or '--'))
        
        if 'total_hosts' in stats_data:
            self.total_ips_label.config(text=str(stats_data['total_hosts']))
        
        if 'total_sent' in stats_data:
            self.sent_label.config(text=str(stats_data['total_sent']))
        
        if 'total_received' in stats_data:
            self.received_label.config(text=str(stats_data['total_received']))
        
        if 'packet_loss' in stats_data:
            loss_rate = stats_data['packet_loss']
            self.loss_label.config(text=f"{loss_rate:.1f}%")
            
            # 根据丢包率设置颜色
            if loss_rate == 0:
                self.loss_label.config(bootstyle=SUCCESS)
            elif loss_rate < 10:
                self.loss_label.config(bootstyle=WARNING)
            else:
                self.loss_label.config(bootstyle=DANGER)
        
        if 'success_rate' in stats_data:
            success_rate = stats_data['success_rate']
            self.success_rate_label.config(text=f"{success_rate:.1f}%")
            
            # 根据成功率设置颜色
            if success_rate >= 95:
                self.success_rate_label.config(bootstyle=SUCCESS)
            elif success_rate >= 80:
                self.success_rate_label.config(bootstyle=WARNING)
            else:
                self.success_rate_label.config(bootstyle=DANGER)
        
        if 'avg_time' in stats_data:
            avg_time = stats_data['avg_time']
            if avg_time > 0:
                self.avg_label.config(text=f"{avg_time}ms")
                
                # 根据响应时间设置颜色
                if avg_time <= 50:
                    self.avg_label.config(bootstyle=SUCCESS)
                elif avg_time <= 100:
                    self.avg_label.config(bootstyle=WARNING)
                else:
                    self.avg_label.config(bootstyle=DANGER)
            else:
                self.avg_label.config(text="--")
        
        if 'runtime_formatted' in stats_data:
            self.runtime_label.config(text=stats_data['runtime_formatted'])
        elif 'runtime' in stats_data:
            runtime = stats_data['runtime']
            self.runtime_label.config(text=f"{runtime:.0f}s")
        
        # 更新性能指标
        if 'min_time' in stats_data:
            min_time = stats_data['min_time']
            self.min_time_label.config(text=f"{min_time}ms" if min_time > 0 else "--")
        
        if 'max_time' in stats_data:
            max_time = stats_data['max_time']
            self.max_time_label.config(text=f"{max_time}ms" if max_time > 0 else "--")
        
        # 计算时间抖动
        if 'min_time' in stats_data and 'max_time' in stats_data:
            min_time = stats_data['min_time']
            max_time = stats_data['max_time']
            if min_time > 0 and max_time > 0:
                jitter = max_time - min_time
                self.jitter_label.config(text=f"{jitter}ms")
            else:
                self.jitter_label.config(text="--")
        
        # 计算网络质量等级
        if 'avg_time' in stats_data and 'packet_loss' in stats_data:
            avg_time = stats_data['avg_time']
            packet_loss = stats_data['packet_loss']
            quality = self._calculate_network_quality(avg_time, packet_loss)
            self.quality_label.config(text=quality)
    
    def update_connection_status(self, is_connected, is_testing=False):
        """
        更新连接状态指示器
        
        Args:
            is_connected (bool): 是否连接成功
            is_testing (bool): 是否正在测试
        """
        if is_testing:
            self.status_indicator.config(text="● 测试中", bootstyle=WARNING)
        elif is_connected:
            self.status_indicator.config(text="● 已连接", bootstyle=SUCCESS)
        else:
            self.status_indicator.config(text="● 未连接", bootstyle=SECONDARY)
    
    def _calculate_network_quality(self, avg_time, packet_loss):
        """
        计算网络质量等级
        
        Args:
            avg_time (int): 平均响应时间
            packet_loss (float): 丢包率
            
        Returns:
            str: 网络质量等级
        """
        if packet_loss >= 20:
            return "很差"
        elif packet_loss >= 10:
            return "较差"
        elif avg_time <= 20 and packet_loss < 1:
            return "优秀"
        elif avg_time <= 50 and packet_loss < 5:
            return "良好"
        elif avg_time <= 100 and packet_loss < 10:
            return "一般"
        else:
            return "较差"
    
    def reset_stats(self):
        """重置所有统计信息显示"""
        # 重置基本统计
        self.current_target_label.config(text="--")
        self.total_ips_label.config(text="--")
        self.sent_label.config(text="0")
        self.received_label.config(text="0")
        self.loss_label.config(text="0%", bootstyle=INFO)
        self.success_rate_label.config(text="--", bootstyle=INFO)
        self.avg_label.config(text="--", bootstyle=INFO)
        self.runtime_label.config(text="0s")
        
        # 重置性能指标
        self.min_time_label.config(text="--")
        self.max_time_label.config(text="--")
        self.jitter_label.config(text="--")
        self.quality_label.config(text="--")
        
        # 重置状态指示器
        self.status_indicator.config(text="● 未连接", bootstyle=SECONDARY)
    
    def get_current_stats(self):
        """
        获取当前显示的统计信息
        
        Returns:
            dict: 当前统计信息
        """
        return {
            'current_target': self.current_target_label.cget('text'),
            'total_ips': self.total_ips_label.cget('text'),
            'sent': self.sent_label.cget('text'),
            'received': self.received_label.cget('text'),
            'loss_rate': self.loss_label.cget('text'),
            'success_rate': self.success_rate_label.cget('text'),
            'avg_time': self.avg_label.cget('text'),
            'runtime': self.runtime_label.cget('text'),
            'min_time': self.min_time_label.cget('text'),
            'max_time': self.max_time_label.cget('text'),
            'jitter': self.jitter_label.cget('text'),
            'quality': self.quality_label.cget('text')
        }
    
    def highlight_stat(self, stat_name, duration=2000):
        """
        高亮显示某个统计项
        
        Args:
            stat_name (str): 统计项名称
            duration (int): 高亮持续时间(毫秒)
        """
        if hasattr(self, f"{stat_name}_label"):
            label = getattr(self, f"{stat_name}_label")
            original_style = label.cget('bootstyle')
            
            # 设置高亮样式
            label.config(bootstyle=WARNING)
            
            # 定时恢复原样式
            self.after(duration, lambda: label.config(bootstyle=original_style)) 