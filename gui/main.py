
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.admin_check import ensure_admin
from netkit.utils.network_monitor import start_network_monitoring, stop_network_monitoring
from netkit.utils.ui_helper import ui_helper
from gui.views.netconfig.netconfig_view import NetConfigView
from gui.views.ping_view import PingFrame
from gui.views.subnet_view import SubnetFrame
from gui.views.traceroute_view import TracerouteFrame
from gui.views.route_view import RouteFrame
from datetime import datetime


class MainWindow:
    def __init__(self):
        self.app = tb.Window(themename='darkly')
        self.app.title('NetKit v0.2.9 - 网络工程师工具箱')
        
        # 初始化 DPI 缩放
        ui_helper.initialize_scaling(self.app)
        
        # 设置自适应窗口大小
        ui_helper.center_window(self.app, 1000, 900)
        
        # 允许窗口大小调整（适应不同 DPI）
        self.app.resizable(True, True)
        
        # 设置最小窗口大小
        min_width, min_height = ui_helper.get_window_size(800, 600)
        self.app.minsize(min_width, min_height)
        
        # 当前显示的内容框架
        self.current_frame = None
        
        # 状态栏变量
        self.status_var = tb.StringVar()
        self.status_var.set("就绪")
        
        self.setup_ui()
        
        # 启动网络监听
        start_network_monitoring()
        
        # 启动异步预加载以提升性能
        from netkit.services.netconfig.interface_manager import start_preload
        start_preload()
        
        # 绑定窗口关闭事件
        self.app.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_closing(self):
        """窗口关闭时的清理工作"""
        # 停止网络监听
        stop_network_monitoring()
        
        # 清理当前视图
        if hasattr(self, 'current_frame') and self.current_frame:
            if hasattr(self.current_frame, 'cleanup'):
                self.current_frame.cleanup()
        
        # 关闭窗口
        self.app.destroy()
        
    def setup_ui(self):
        """设置主界面布局"""
        # 创建主容器
        main_container = tb.Frame(self.app)
        padding = ui_helper.get_padding(10)
        main_container.pack(fill=BOTH, expand=True, padx=padding, pady=padding)
        
        # 左侧导航栏
        self.setup_sidebar(main_container)
        
        # 右侧内容区域
        self.setup_content_area(main_container)
        
        # 底部状态栏
        self.setup_status_bar()
        
        # 默认显示IP切换功能
        self.show_ip_switcher()
        
    def setup_sidebar(self, parent):
        """设置左侧导航栏"""
        sidebar_width = ui_helper.scale_size(200)
        sidebar = tb.Frame(parent, width=sidebar_width)
        sidebar.pack(side=LEFT, fill=Y, padx=(0, ui_helper.get_padding(10)))
        sidebar.pack_propagate(False)
        
        # 标题
        title_label = tb.Label(
            sidebar, 
            text="NetKit", 
            font=ui_helper.get_font(16, "bold"),
            bootstyle=INFO
        )
        title_label.pack(pady=(0, ui_helper.get_padding(10)))
        
        # 版本信息
        version_label = tb.Label(
            sidebar,
            text="v0.1 网络工具箱",
            font=ui_helper.get_font(9),
            bootstyle=SECONDARY
        )
        version_label.pack(pady=(0, ui_helper.get_padding(20)))
        
        # 导航按钮
        nav_buttons = [
            ("网卡配置", self.show_ip_switcher, PRIMARY, "快速切换网络配置"),
            ("Ping测试", self.show_ping, SUCCESS, "网络连通性测试"),
            ("子网计算", self.show_subnet, INFO, "子网划分与计算"),
            ("路由追踪", self.show_traceroute, WARNING, "追踪网络路径"),
            ("静态路由", self.show_route, DANGER, "管理静态路由"),
        ]
        
        for text, command, style, tooltip in nav_buttons:
            btn = tb.Button(
                sidebar,
                text=text,
                command=command,
                bootstyle=f"{style}-outline",
                width=ui_helper.scale_size(18)
            )
            btn.pack(pady=ui_helper.get_padding(5), padx=ui_helper.get_padding(5), fill=X)
            
            # 添加工具提示（简单实现）
            self.create_tooltip(btn, tooltip)
            
        # 分隔线
        separator = tb.Separator(sidebar, orient=HORIZONTAL)
        separator.pack(fill=X, pady=ui_helper.get_padding(20))
        
        # 系统信息
        info_frame = tb.LabelFrame(sidebar, text="系统信息", padding=ui_helper.get_padding(10))
        info_frame.pack(fill=X, padx=ui_helper.get_padding(5))
        
        # 管理员状态
        admin_status = "已获取管理员权限" if os.environ.get('NETKIT_TEST_MODE') != '1' else "测试模式"
        admin_label = tb.Label(
            info_frame,
            text=f"权限: {admin_status}",
            font=ui_helper.get_font(8),
            bootstyle=SUCCESS if admin_status == "已获取管理员权限" else WARNING
        )
        admin_label.pack(anchor=W, pady=ui_helper.get_padding(2))
        
        # 启动时间
        start_time = datetime.now().strftime("%H:%M:%S")
        time_label = tb.Label(
            info_frame,
            text=f"启动: {start_time}",
            font=ui_helper.get_font(8),
            bootstyle=SECONDARY
        )
        time_label.pack(anchor=W, pady=ui_helper.get_padding(2))
            
    def setup_content_area(self, parent):
        """设置右侧内容区域"""
        self.content_area = tb.Frame(parent)
        self.content_area.pack(side=RIGHT, fill=BOTH, expand=True)
        
    def setup_status_bar(self):
        """设置状态栏"""
        status_frame = tb.Frame(self.app)
        padding = ui_helper.get_padding(10)
        status_frame.pack(side=BOTTOM, fill=X, padx=padding, pady=(0, padding))
        
        # 分隔线
        separator = tb.Separator(status_frame, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(0, ui_helper.get_padding(5)))
        
        # 状态栏内容
        status_content = tb.Frame(status_frame)
        status_content.pack(fill=X)
        
        # 状态文本
        status_label = tb.Label(
            status_content,
            text="状态:",
            font=ui_helper.get_font(9),
            bootstyle=SECONDARY
        )
        status_label.pack(side=LEFT)
        
        self.status_display = tb.Label(
            status_content,
            textvariable=self.status_var,
            font=ui_helper.get_font(9),
            bootstyle=INFO
        )
        self.status_display.pack(side=LEFT, padx=(ui_helper.get_padding(5), 0))
        
        # 进度条（初始隐藏）
        self.progress_bar = tb.Progressbar(
            status_content,
            mode='indeterminate',
            length=ui_helper.scale_size(200)
        )
        
        # 当前时间
        self.time_label = tb.Label(
            status_content,
            text="",
            font=ui_helper.get_font(9),
            bootstyle=SECONDARY
        )
        self.time_label.pack(side=RIGHT)
        
        # 更新时间
        self.update_time()
        
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        # 每秒更新一次
        self.app.after(1000, self.update_time)
        
    def create_tooltip(self, widget, text):
        """创建简单的工具提示"""
        def on_enter(event):
            self.set_status(text)
        
        def on_leave(event):
            self.set_status("就绪")
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def set_status(self, message, show_progress=False):
        """设置状态栏消息"""
        self.status_var.set(message)
        
        if show_progress:
            self.progress_bar.pack(side=LEFT, padx=(ui_helper.get_padding(20), 0))
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            
    def clear_content_area(self):
        """清空内容区域"""
        if self.current_frame:
            # 如果当前框架有清理方法，先调用清理
            if hasattr(self.current_frame, 'cleanup'):
                self.current_frame.cleanup()
            self.current_frame.destroy()
            self.current_frame = None
            
    def show_ip_switcher(self):
        """显示IP切换功能"""
        self.clear_content_area()
        self.set_status("正在加载IP地址切换功能...")
        
        try:
            # 在创建界面之前就启动预加载，确保数据准备
            from netkit.services.netconfig.interface_manager import start_preload
            from netkit.services.netconfig.async_manager import get_async_manager
            
            # 获取异步管理器实例
            async_manager = get_async_manager()
            
            # 如果预加载未完成，启动预加载
            if not async_manager.preload_completed:
                start_preload()
            
            # 创建界面
            self.current_frame = NetConfigView(self.content_area)
            self.current_frame.pack(fill=BOTH, expand=True)
            self.set_status("IP地址切换功能已加载")
        except Exception as e:
            self.set_status(f"加载IP切换功能失败: {str(e)}")
        
    def show_ping(self):
        """显示Ping测试功能"""
        self.clear_content_area()
        self.set_status("正在加载Ping测试功能...")
        
        try:
            self.current_frame = PingFrame(self.content_area)
            self.current_frame.pack(fill=BOTH, expand=True)
            self.set_status("Ping测试功能已加载")
        except Exception as e:
            self.set_status(f"加载Ping测试功能失败: {str(e)}")
        
    def show_subnet(self):
        """显示子网计算功能"""
        self.clear_content_area()
        self.set_status("正在加载子网计算功能...")
        
        try:
            self.current_frame = SubnetFrame(self.content_area)
            self.current_frame.pack(fill=BOTH, expand=True)
            self.set_status("子网计算功能已加载")
        except Exception as e:
            self.set_status(f"加载子网计算功能失败: {str(e)}")
        
    def show_traceroute(self):
        """显示路由追踪功能"""
        self.clear_content_area()
        self.set_status("正在加载路由追踪功能...")
        
        try:
            self.current_frame = TracerouteFrame(self.content_area)
            self.current_frame.pack(fill=BOTH, expand=True)
            self.set_status("路由追踪功能已加载")
        except Exception as e:
            self.set_status(f"加载路由追踪功能失败: {str(e)}")
        
    def show_route(self):
        """显示静态路由功能"""
        self.clear_content_area()
        self.set_status("正在加载静态路由管理功能...")
        
        try:
            self.current_frame = RouteFrame(self.content_area)
            self.current_frame.pack(fill=BOTH, expand=True)
            self.set_status("静态路由管理功能已加载")
        except Exception as e:
            self.set_status(f"加载静态路由管理功能失败: {str(e)}")
        
    def run(self):
        """运行应用程序"""
        self.set_status("NetKit 启动完成，欢迎使用！")
        self.app.mainloop()


def main():
    ensure_admin()
    app = MainWindow()
    app.run()


if __name__ == '__main__':
    main()
