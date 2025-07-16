
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.admin_check import ensure_admin
from gui.views.ip_switcher_view import IPSwitcherFrame
from gui.views.ping_view import PingFrame
from gui.views.subnet_view import SubnetFrame
from gui.views.traceroute_view import TracerouteFrame
from gui.views.route_view import RouteFrame
from datetime import datetime


class MainWindow:
    def __init__(self):
        self.app = tb.Window(themename='darkly')
        self.app.title('NetKit v0.2.9 - 网络工程师工具箱')
        self.app.geometry('1200x800')
        self.app.minsize(1000, 600)
        
        # 当前显示的内容框架
        self.current_frame = None
        
        # 状态栏变量
        self.status_var = tb.StringVar()
        self.status_var.set("就绪")
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置主界面布局"""
        # 创建主容器
        main_container = tb.Frame(self.app)
        main_container.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
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
        sidebar = tb.Frame(parent, width=200)
        sidebar.pack(side=LEFT, fill=Y, padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # 标题
        title_label = tb.Label(
            sidebar, 
                            text="NetKit", 
            font=('Arial', 16, 'bold'),
            bootstyle=INFO
        )
        title_label.pack(pady=(0, 10))
        
        # 版本信息
        version_label = tb.Label(
            sidebar,
            text="v0.1 网络工具箱",
            font=('Arial', 9),
            bootstyle=SECONDARY
        )
        version_label.pack(pady=(0, 20))
        
        # 导航按钮
        nav_buttons = [
            ("IP地址切换", self.show_ip_switcher, PRIMARY, "快速切换网络配置"),
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
                width=18
            )
            btn.pack(pady=5, padx=5, fill=X)
            
            # 添加工具提示（简单实现）
            self.create_tooltip(btn, tooltip)
            
        # 分隔线
        separator = tb.Separator(sidebar, orient=HORIZONTAL)
        separator.pack(fill=X, pady=20)
        
        # 系统信息
        info_frame = tb.LabelFrame(sidebar, text="系统信息", padding=10)
        info_frame.pack(fill=X, padx=5)
        
        # 管理员状态
        admin_status = "已获取管理员权限" if os.environ.get('NETKIT_TEST_MODE') != '1' else "测试模式"
        admin_label = tb.Label(
            info_frame,
            text=f"权限: {admin_status}",
            font=('Arial', 8),
            bootstyle=SUCCESS if admin_status == "已获取管理员权限" else WARNING
        )
        admin_label.pack(anchor=W, pady=2)
        
        # 启动时间
        start_time = datetime.now().strftime("%H:%M:%S")
        time_label = tb.Label(
            info_frame,
            text=f"启动: {start_time}",
            font=('Arial', 8),
            bootstyle=SECONDARY
        )
        time_label.pack(anchor=W, pady=2)
            
    def setup_content_area(self, parent):
        """设置右侧内容区域"""
        self.content_area = tb.Frame(parent)
        self.content_area.pack(side=RIGHT, fill=BOTH, expand=True)
        
    def setup_status_bar(self):
        """设置状态栏"""
        status_frame = tb.Frame(self.app)
        status_frame.pack(side=BOTTOM, fill=X, padx=10, pady=(0, 10))
        
        # 分隔线
        separator = tb.Separator(status_frame, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(0, 5))
        
        # 状态栏内容
        status_content = tb.Frame(status_frame)
        status_content.pack(fill=X)
        
        # 状态文本
        status_label = tb.Label(
            status_content,
            text="状态:",
            font=('Arial', 9),
            bootstyle=SECONDARY
        )
        status_label.pack(side=LEFT)
        
        self.status_display = tb.Label(
            status_content,
            textvariable=self.status_var,
            font=('Arial', 9),
            bootstyle=INFO
        )
        self.status_display.pack(side=LEFT, padx=(5, 0))
        
        # 进度条（初始隐藏）
        self.progress_bar = tb.Progressbar(
            status_content,
            mode='indeterminate',
            length=200
        )
        
        # 当前时间
        self.time_label = tb.Label(
            status_content,
            text="",
            font=('Arial', 9),
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
            self.progress_bar.pack(side=LEFT, padx=(20, 0))
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
            
    def clear_content_area(self):
        """清空内容区域"""
        if self.current_frame:
            self.current_frame.destroy()
            self.current_frame = None
            
    def show_ip_switcher(self):
        """显示IP切换功能"""
        self.clear_content_area()
        self.set_status("正在加载IP地址切换功能...")
        
        try:
            self.current_frame = IPSwitcherFrame(self.content_area)
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
