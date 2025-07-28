"""
可视化Ping测试主界面

采用16x16方格布局，直观显示网段内所有IP的ping状态
设计简洁，交互友好，适合快速网络扫描
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from .grid_cell import IPGridCell
from .scan_controller import ScanController
from .ui_components import IPDetailWindow, IPContextMenu, ScanResultDialog


class VisualPingView(tb.Frame):
    """可视化Ping测试主界面"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.network_prefix = "192.168.1"  # 默认网段
        self.grid_cells = {}  # IP后缀 -> IPGridCell
        self.scan_controller = ScanController(self)
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        # 标题
        title = tb.Label(
            self, 
            text="网络扫描 - 可视化Ping测试",
            font=('微软雅黑', ui_helper.scale_size(16), 'bold'),
            bootstyle=SUCCESS
        )
        title.pack(pady=(0, ui_helper.get_padding(15)))
        
        # 上部分 - 设置区域
        self.setup_control_panel()
        
        # 中部分 - 16x16方格显示区域
        self.setup_grid_area()
        
        # 下部分 - 统计信息
        self.setup_stats_panel()
    
    def setup_control_panel(self):
        """设置控制面板"""
        control_frame = tb.LabelFrame(self, text="扫描设置", padding=ui_helper.get_padding(15))
        control_frame.pack(fill=X, pady=(0, ui_helper.get_padding(15)))
        
        # IP范围输入
        input_frame = tb.Frame(control_frame)
        input_frame.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        tb.Label(input_frame, text="网段:").pack(side=LEFT)
        
        self.network_entry = tb.Entry(input_frame, width=15)
        self.network_entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        self.network_entry.insert(0, self.network_prefix)
        
        tb.Label(input_frame, text="/24", bootstyle=SECONDARY).pack(side=LEFT, padx=(ui_helper.get_padding(5), 0))
        
        # 参数说明
        param_label = tb.Label(
            input_frame, 
            text="(超时: 1000ms, 并发: 25个)",
            font=('微软雅黑', ui_helper.scale_size(8)),
            bootstyle=SECONDARY
        )
        param_label.pack(side=LEFT, padx=(ui_helper.get_padding(20), 0))
        
        # 控制按钮
        button_frame = tb.Frame(control_frame)
        button_frame.pack(fill=X)
        
        self.start_btn = tb.Button(
            button_frame,
            text="开始扫描",
            bootstyle=SUCCESS,
            width=ui_helper.scale_size(12),
            command=self.start_scan
        )
        self.start_btn.pack(side=LEFT, padx=(0, ui_helper.get_padding(10)))
        
        self.stop_btn = tb.Button(
            button_frame,
            text="停止扫描", 
            bootstyle=DANGER,
            width=ui_helper.scale_size(12),
            command=self.stop_scan,
            state=DISABLED
        )
        self.stop_btn.pack(side=LEFT)
    
    def setup_grid_area(self):
        """设置方格显示区域"""
        grid_frame = tb.LabelFrame(self, text="网络状态 (16x16)", padding=ui_helper.get_padding(10))
        grid_frame.pack(fill=BOTH, expand=True, pady=(0, ui_helper.get_padding(15)))
        
        # 创建网格容器
        self.grid_container = tb.Frame(grid_frame)
        self.grid_container.pack(fill=BOTH, expand=True)
        
        # 计算方格大小
        cell_size = ui_helper.scale_size(25)
        
        # 创建16x16网格
        for row in range(16):
            for col in range(16):
                ip_suffix = row * 16 + col + 1
                
                # 跳过大于254的IP
                if ip_suffix > 254:
                    continue
                    
                cell = IPGridCell(self.grid_container, ip_suffix, size=cell_size)
                cell.grid(row=row, column=col, padx=1, pady=1)
                
                self.grid_cells[ip_suffix] = cell
        
        # 为网格容器添加回调方法
        self.grid_container.show_ip_details = self.show_ip_details
        self.grid_container.ping_single_ip = self.ping_single_ip
        self.grid_container.show_context_menu = self.show_context_menu
    
    def setup_stats_panel(self):
        """设置统计面板"""
        stats_frame = tb.LabelFrame(self, text="扫描统计", padding=ui_helper.get_padding(15))
        stats_frame.pack(fill=X)
        
        # 统计标签
        stats_grid = tb.Frame(stats_frame)
        stats_grid.pack(fill=X)
        
        # 在线数量
        tb.Label(stats_grid, text="在线:").grid(row=0, column=0, sticky=W, padx=(0, ui_helper.get_padding(5)))
        self.online_label = tb.Label(stats_grid, text="0", bootstyle=SUCCESS, font=('微软雅黑', ui_helper.scale_size(12), 'bold'))
        self.online_label.grid(row=0, column=1, sticky=W, padx=(0, ui_helper.get_padding(20)))
        
        # 离线数量  
        tb.Label(stats_grid, text="离线:").grid(row=0, column=2, sticky=W, padx=(0, ui_helper.get_padding(5)))
        self.offline_label = tb.Label(stats_grid, text="0", bootstyle=DANGER, font=('微软雅黑', ui_helper.scale_size(12), 'bold'))
        self.offline_label.grid(row=0, column=3, sticky=W, padx=(0, ui_helper.get_padding(20)))
        
        # 总数
        tb.Label(stats_grid, text="总数:").grid(row=0, column=4, sticky=W, padx=(0, ui_helper.get_padding(5)))
        self.total_label = tb.Label(stats_grid, text="254", bootstyle=INFO, font=('微软雅黑', ui_helper.scale_size(12), 'bold'))
        self.total_label.grid(row=0, column=5, sticky=W)
        
        # 扫描状态
        self.status_label = tb.Label(
            stats_frame, 
            text="就绪", 
            bootstyle=SECONDARY,
            font=('微软雅黑', ui_helper.scale_size(10))
        )
        self.status_label.pack(pady=(ui_helper.get_padding(10), 0))
    
    def start_scan(self):
        """开始扫描"""
        # 验证输入
        network_prefix = self.network_entry.get().strip()
        if not self.validate_network_input(network_prefix):
            return
            
        self.network_prefix = network_prefix
        
        # 更新按钮状态
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        
        # 重置方格状态
        self.reset_grid_state()
        
        # 更新状态
        self.status_label.config(text="正在扫描...", bootstyle=WARNING)
        
        # 启动扫描
        self.scan_controller.start_scan(network_prefix)
    
    def stop_scan(self):
        """停止扫描"""
        # 停止扫描控制器
        self.scan_controller.stop_scan()
        
        # 更新按钮状态
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        
        # 停止所有闪烁
        for cell in self.grid_cells.values():
            cell.stop_blinking()
        
        # 更新状态
        self.status_label.config(text="扫描已停止", bootstyle=SECONDARY)
    
    def validate_network_input(self, network_prefix):
        """验证网络输入"""
        if not network_prefix:
            ScanResultDialog.show_validation_error(self, "请输入网段前缀")
            return False
            
        # 验证IP格式
        parts = network_prefix.split('.')
        if len(parts) != 3:
            ScanResultDialog.show_validation_error(self, "请输入正确的网段格式，如: 192.168.1")
            return False
            
        try:
            for part in parts:
                if not (0 <= int(part) <= 255):
                    raise ValueError()
        except ValueError:
            ScanResultDialog.show_validation_error(self, "IP地址格式不正确")
            return False
        
        return True
    
    def reset_grid_state(self):
        """重置方格状态"""
        for cell in self.grid_cells.values():
            cell.set_state(IPGridCell.STATE_INITIAL)
        
        # 重置统计显示
        self.online_label.config(text="0")
        self.offline_label.config(text="0")
    
    # 扫描控制器回调方法
    def update_cell_scanning(self, ip_suffix):
        """更新方格为扫描中状态"""
        if ip_suffix in self.grid_cells:
            self.grid_cells[ip_suffix].set_state(IPGridCell.STATE_SCANNING)
    
    def update_cell_online(self, ip_suffix, stats):
        """更新方格为在线状态"""
        if ip_suffix in self.grid_cells:
            self.grid_cells[ip_suffix].set_state(IPGridCell.STATE_ONLINE, stats)
    
    def update_cell_offline(self, ip_suffix, stats):
        """更新方格为离线状态"""
        if ip_suffix in self.grid_cells:
            self.grid_cells[ip_suffix].set_state(IPGridCell.STATE_OFFLINE, stats)
    
    def update_stats(self, stats):
        """更新统计显示"""
        self.online_label.config(text=str(stats['online_count']))
        self.offline_label.config(text=str(stats['offline_count']))
    
    def on_scan_completed(self, stats):
        """扫描完成回调"""
        # 更新按钮状态
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        
        # 更新状态
        self.status_label.config(text="扫描完成", bootstyle=SUCCESS)
        
        # 显示完成对话框
        ScanResultDialog.show_scan_completed(self, self.network_prefix, stats)
    
    # 方格交互回调方法
    def show_ip_details(self, ip_suffix, event):
        """显示IP详细信息弹窗"""
        if ip_suffix not in self.grid_cells:
            return
            
        cell = self.grid_cells[ip_suffix]
        ip_address = f"{self.network_prefix}.{ip_suffix}"
        
        # 创建详细信息弹窗
        IPDetailWindow(self, ip_address, cell, event)
    
    def ping_single_ip(self, ip_suffix):
        """单独ping某个IP"""
        ip_address = f"{self.network_prefix}.{ip_suffix}"
        
        # 显示正在ping的提示
        ScanResultDialog.show_ping_in_progress(self, ip_address)
        
        # 执行ping
        self.scan_controller.ping_single_ip(self.network_prefix, ip_suffix)
    
    def show_context_menu(self, ip_suffix, event):
        """显示右键菜单"""
        ip_address = f"{self.network_prefix}.{ip_suffix}"
        
        # 创建右键菜单
        IPContextMenu(
            self, ip_address, ip_suffix, event,
            self.ping_single_ip, 
            lambda suffix: self.show_ip_details(suffix, event)
        )
    
    # UI组件回调方法
    def show_single_ping_result(self, ip_address, result):
        """显示单独ping的结果"""
        ScanResultDialog.show_single_ping_result(self, ip_address, result)
    
    def show_error(self, message):
        """显示错误信息"""
        ScanResultDialog.show_error(self, message) 