"""
可视化Ping测试主界面

采用智能动态布局，根据窗口大小自动调整行列数，直观显示网段内所有IP的ping状态
设计简洁，交互友好，适合快速网络扫描
"""

import math
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
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
        
        # 布局缓存和性能优化
        self.layout_cache = {}  # 容器尺寸 -> 布局参数
        self.last_layout = None  # 上次使用的布局
        self._last_cell_size = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""        
        # 上部分 - 设置区域
        self.setup_control_panel()
        
        # 中部分 - 智能动态方格显示区域
        self.setup_grid_area()
        
        # 下部分 - 统计信息
        self.setup_stats_panel()
    
    def setup_control_panel(self):
        """设置控制面板"""
        control_frame = tb.LabelFrame(self, text="扫描设置", padding=ui_helper.get_padding(15))
        control_frame.pack(fill=X, pady=(0, ui_helper.get_padding(15)))
        
        # 主控制行 - 包含网段输入和按钮
        main_control_frame = tb.Frame(control_frame)
        main_control_frame.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        # 左侧：网段输入区域
        input_section = tb.Frame(main_control_frame)
        input_section.pack(side=LEFT, fill=X, expand=True)
        
        tb.Label(input_section, text="网段:").pack(side=LEFT)
        
        self.network_entry = tb.Entry(input_section, width=15)
        self.network_entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        self.network_entry.insert(0, self.network_prefix)
        
        tb.Label(input_section, text="/24", bootstyle=SECONDARY).pack(side=LEFT, padx=(ui_helper.get_padding(5), 0))
        
        # 右侧：控制按钮
        button_section = tb.Frame(main_control_frame)
        button_section.pack(side=RIGHT)
        
        self.start_btn = tb.Button(
            button_section,
            text="开始扫描",
            bootstyle=SUCCESS,
            width=ui_helper.scale_size(12),
            command=self.start_scan
        )
        self.start_btn.pack(side=LEFT, padx=(0, ui_helper.get_padding(10)))
        
        self.stop_btn = tb.Button(
            button_section,
            text="停止扫描", 
            bootstyle=DANGER,
            width=ui_helper.scale_size(12),
            command=self.stop_scan,
            state=DISABLED
        )
        self.stop_btn.pack(side=LEFT)
    
    def setup_grid_area(self):
        """设置方格显示区域"""
        grid_frame = tb.LabelFrame(self, text="网络状态", padding=ui_helper.get_padding(10))
        grid_frame.pack(fill=BOTH, expand=True, pady=(0, ui_helper.get_padding(15)))
        
        # 创建滚动框架容器
        self.scrolled_frame = ScrolledFrame(grid_frame, autohide=True)
        self.scrolled_frame.pack(fill=BOTH, expand=True)
        
        # 获取滚动框架内的实际容器
        self.grid_container = self.scrolled_frame
        
        # 初始化网格，延迟到窗口显示后再创建
        self.grid_cells = {}
        self.grid_frame = grid_frame
        
        # 绑定容器大小变化事件（绑定到外层容器）
        grid_frame.bind('<Configure>', self.on_grid_container_configure)
        
        # 为网格容器添加回调方法
        self.grid_container.ping_single_ip = self.ping_single_ip
        self.grid_container.show_context_menu = self.show_context_menu
        
        # 延迟创建网格（确保容器已经有实际尺寸）
        self.after(100, self.create_adaptive_grid)
    
    def on_grid_container_configure(self, event):
        """响应容器大小变化"""
        # 只响应外层框架的配置事件，避免子控件事件干扰
        if event.widget == self.grid_frame:
            # 扫描期间阻止网格重建
            if hasattr(self, 'scan_controller') and self.scan_controller.is_scanning:
                return
                
            # 延迟调整，避免频繁触发
            if hasattr(self, '_resize_job'):
                self.after_cancel(self._resize_job)
            self._resize_job = self.after(50, self.create_adaptive_grid)
    
    def calculate_adaptive_cell_size(self):
        """固定返回44px的方格大小（适配DPI）"""
        return ui_helper.scale_size(44)
    
    def calculate_optimal_grid_layout(self, container_width, container_height):
        """计算最优的网格布局"""
        # 使用缓存避免重复计算
        cache_key = f"{container_width}x{container_height}"
        if cache_key in self.layout_cache:
            return self.layout_cache[cache_key]
        
        cell_size = ui_helper.scale_size(44)  # 固定44px方格
        spacing = 2  # padx=1, pady=1，总间距2px
        padding = ui_helper.get_padding(10) * 2  # 左右内边距
        total_ips = 254
        
        # 计算可用空间
        available_width = max(0, container_width - padding)
        available_height = max(0, container_height - padding)
        
        # 计算理想列数（12-30列限制）
        if available_width <= 0:
            cols = 12  # 最小列数
        else:
            ideal_cols = (available_width + spacing) // (cell_size + spacing)
            cols = max(12, min(30, ideal_cols))
        
        # 计算所需行数
        rows = math.ceil(total_ips / cols)
        
        # 计算网格总高度
        total_height = rows * cell_size + (rows - 1) * spacing
        
        layout = {
            'cols': cols,
            'rows': rows, 
            'cell_size': cell_size,
            'total_height': total_height,
            'available_width': available_width,
            'available_height': available_height
        }
        
        # 缓存结果
        self.layout_cache[cache_key] = layout
        return layout
    
    def create_adaptive_grid(self):
        """创建智能动态布局的网格"""
        print(f"DEBUG: create_adaptive_grid被调用，当前网格数量：{len(self.grid_cells)}")
        try:
            # 获取容器的实际尺寸
            container_width = self.grid_frame.winfo_width()
            container_height = self.grid_frame.winfo_height()
            print(f"DEBUG: 容器尺寸 {container_width}x{container_height}")
            
            # 如果容器还没有实际尺寸，延迟执行
            if container_width <= 1 or container_height <= 1:
                self.after(50, self.create_adaptive_grid)
                return
            
            # 扫描保护机制：如果正在扫描，不允许重建网格
            if hasattr(self, 'scan_controller') and self.scan_controller and self.scan_controller.is_scanning:
                print("DEBUG: 扫描正在进行，跳过网格重建")
                return
                
            # 时间戳保护机制
            import time
            current_time = time.time()
            protection_timestamp = getattr(self, '_grid_protection_timestamp', 0)
            if current_time - protection_timestamp < 5.0:  # 5秒保护期
                print(f"DEBUG: 保护期内({current_time - protection_timestamp:.1f}s)，跳过网格重建")
                return
            
            # 计算最优布局
            layout = self.calculate_optimal_grid_layout(container_width, container_height)
            
            # 性能优化：检查布局是否真正改变
            if (self.last_layout and 
                self.last_layout['cols'] == layout['cols'] and 
                self.last_layout['rows'] == layout['rows'] and
                self.grid_cells):
                print("DEBUG: 布局未变，跳过重建")
                return  # 布局未变，跳过重建
            
            # 如果有现有网格且只是重新排列，智能调整
            if (self.grid_cells and self.last_layout and 
                len(self.grid_cells) == 254):  # 现有cell数量正确
                self._rearrange_existing_grid(layout)
            else:
                self._create_new_grid(layout)
            
            # ScrolledFrame会自动管理滚动区域，无需手动设置scrollregion
            
            # 记录当前布局
            self.last_layout = layout
            
        except Exception as e:
            # 异常情况下强制重建
            print(f"DEBUG: 网格创建异常: {e}")
            self.force_rebuild_grid()
    
    def _rearrange_existing_grid(self, layout):
        """重新排列现有网格cell的位置"""
        cols = layout['cols']
        cell_size = layout['cell_size']
        
        # 重新排列所有cell
        for ip_suffix, cell in self.grid_cells.items():
            row = (ip_suffix - 1) // cols
            col = (ip_suffix - 1) % cols
            
            # 更新方格大小和位置
            cell.configure(width=cell_size, height=cell_size)
            cell.grid(row=row, column=col, padx=1, pady=1)
    
    def _create_new_grid(self, layout):
        """创建全新的网格"""
        print("DEBUG: ===== 开始销毁现有网格 =====")
        # 清除现有网格
        for cell in self.grid_cells.values():
            cell.destroy()
        self.grid_cells.clear()
        print("DEBUG: ===== 网格销毁完成 =====")
        
        cols = layout['cols']
        rows = layout['rows']
        cell_size = layout['cell_size']
        
        # 创建新网格：动态行列数
        for ip_suffix in range(1, 255):  # IP 1-254
            row = (ip_suffix - 1) // cols
            col = (ip_suffix - 1) % cols
            
            cell = IPGridCell(self.grid_container, ip_suffix, size=cell_size)
            cell.grid(row=row, column=col, padx=1, pady=1)
            
            self.grid_cells[ip_suffix] = cell
        
        print("DEBUG: 网格创建完成")
    
    def force_rebuild_grid(self):
        """强制重建网格（用于异常情况）"""
        # 清除现有网格
        for cell in self.grid_cells.values():
            cell.destroy()
        self.grid_cells.clear()
        
        # 清除缓存
        self.layout_cache.clear()
        self.last_layout = None
        if hasattr(self, '_last_cell_size'):
            delattr(self, '_last_cell_size')
        
        # 重新创建
        self.create_adaptive_grid()
    
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
        
        # 清理缓存保护时间戳，允许正常清理
        if hasattr(self, '_from_cache_timestamp'):
            delattr(self, '_from_cache_timestamp')
        

    
    # 方格交互回调方法
    
    def ping_single_ip(self, ip_suffix):
        """单独ping某个IP"""
        ip_address = f"{self.network_prefix}.{ip_suffix}"
        
        # 直接执行ping，不显示提示窗口
        self.scan_controller.ping_single_ip(self.network_prefix, ip_suffix)
    
    def show_context_menu(self, ip_suffix, event):
        """显示右键菜单（只有单独ping功能）"""
        ip_address = f"{self.network_prefix}.{ip_suffix}"
        
        # 创建简化的右键菜单
        IPContextMenu(
            self, ip_address, ip_suffix, event,
            self.ping_single_ip
        )
    
    # UI组件回调方法
    def show_single_ping_result(self, ip_address, result):
        """显示单独ping的结果"""
        ScanResultDialog.show_single_ping_result(self, ip_address, result)
    
    def show_error(self, message):
        """显示错误信息"""
        ScanResultDialog.show_error(self, message)
    
    def cleanup(self):
        """清理资源，停止正在进行的扫描"""
        if self.scan_controller:
            self.scan_controller.stop_scan()
        
        # 停止所有闪烁效果
        for cell in self.grid_cells.values():
            try:
                cell.stop_blinking()
            except:
                pass  # 忽略已销毁的控件错误 