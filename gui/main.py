
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.admin_check import ensure_admin, check_admin_without_exit, auto_elevate
from netkit.utils.network_monitor import start_network_monitoring, stop_network_monitoring
from netkit.utils.ui_helper import ui_helper
from gui.views.netconfig.netconfig_view import NetConfigView
from gui.views.ping import VisualPingView
from gui.views.route.route_view import RouteFrame
from datetime import datetime


class MainWindow:
    def __init__(self, admin_status=None):
        self.app = tb.Window(themename='darkly')
        self.app.title('NetKit v2.0.1')
        
        # 权限状态管理
        if admin_status is None:
            self.is_admin = check_admin_without_exit()
        else:
            self.is_admin = admin_status
        
        # 权限相关UI组件引用
        self.admin_label = None
        self.elevate_button = None
        self.nav_buttons = []
        self.nav_button_configs = []  # 保存按钮配置信息
        
        # 初始化 DPI 缩放
        ui_helper.initialize_scaling(self.app)
        
        # 设置自适应窗口大小（进一步调整高度，确保完全适配2880x1800分辨率）
        ui_helper.center_window(self.app, 1300, 800)
        
        # 允许窗口大小调整（适应不同 DPI）
        self.app.resizable(True, True)
        
        # 设置最小窗口大小
        min_width, min_height = ui_helper.get_window_size(800, 600)
        self.app.minsize(min_width, min_height)
        
        # 当前显示的内容框架
        self.current_frame = None
        
        # 视图实例缓存（防止扫描期间实例被销毁）
        self.cached_views = {}
        
        # 状态栏变量已删除
        
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
        
        # 清理缓存的视图
        if hasattr(self, 'cached_views'):
            for view in self.cached_views.values():
                if hasattr(view, 'cleanup'):
                    view.cleanup()
                try:
                    view.destroy()
                except:
                    pass  # 忽略已销毁的控件错误
        
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
        
        # 底部状态栏已删除
        
        # 默认显示IP切换功能
        self.show_ip_switcher()
        
    def setup_sidebar(self, parent):
        """设置左侧导航栏"""
        # 根据DPI动态调整导航栏宽度
        base_width = 180 if ui_helper.get_scaling_factor() >= 1.5 else 200
        sidebar_width = ui_helper.scale_size(base_width)
        sidebar = tb.Frame(parent, width=sidebar_width)
        sidebar.pack(side=LEFT, fill=Y, padx=(0, ui_helper.get_padding(10)))
        sidebar.pack_propagate(False)
        
        # 标题
        title_label = tb.Label(
            sidebar, 
            text="NetKit", 
            font=ui_helper.get_font(18, "bold"),  # 稍微增大标题字体
            bootstyle=INFO
        )
        title_label.pack(pady=(0, ui_helper.get_padding(8)))
        
        # 版本信息
        version_label = tb.Label(
            sidebar,
            text="v2.0.1",  # 更新版本号
            font=ui_helper.get_font(10),  # 稍微增大版本字体
            bootstyle=SECONDARY
        )
        version_label.pack(pady=(0, ui_helper.get_padding(25)))  # 增加与按钮区域的间距
        
        # 导航按钮
        nav_button_configs = [
            ("网卡配置", self.show_ip_switcher, PRIMARY, "快速切换网络配置", True),  # 需要管理员权限
            ("Ping测试", self.show_ping, SUCCESS, "网络连通性测试", False),      # 不需要管理员权限
            ("静态路由", self.show_route, DANGER, "管理静态路由", True),         # 需要管理员权限
            ("关于", self.show_about_page, INFO, "关于NetKit", False),          # 不需要管理员权限
        ]
        
        # 保存按钮配置
        self.nav_button_configs = nav_button_configs
        
        for text, command, style, tooltip, requires_admin in nav_button_configs:
            btn = tb.Button(
                sidebar,
                text=text,
                command=command,
                bootstyle=style,  # 使用实心样式，更现代化
                width=ui_helper.scale_size(20)  # 稍微增加宽度
            )
            btn.pack(pady=ui_helper.get_padding(8), padx=ui_helper.get_padding(5), fill=X)  # 增加垂直间距
            
            # 保存按钮引用
            self.nav_buttons.append(btn)
            
            # 添加工具提示（简单实现）
            self.create_tooltip(btn, tooltip)
            
        # 分隔线
        separator = tb.Separator(sidebar, orient=HORIZONTAL)
        separator.pack(fill=X, pady=ui_helper.get_padding(20))
        
        # 权限模式
        info_frame = tb.LabelFrame(
            sidebar, 
            text="权限模式", 
            padding=ui_helper.get_padding(10),
            bootstyle=SECONDARY  # 添加样式
        )
        info_frame.pack(fill=X, padx=ui_helper.get_padding(5))
        
        # 权限状态显示
        self.admin_label = tb.Label(
            info_frame,
            text="",
            font=ui_helper.get_font(9),  # 稍微增大字体
            bootstyle=SUCCESS
        )
        self.admin_label.pack(anchor=W, pady=ui_helper.get_padding(2))
        
        # 权限提升按钮（仅在受限模式下显示）
        self.elevate_button = tb.Button(
            info_frame,
            text="使用管理员方式运行",
            command=self.request_admin_elevation,
            bootstyle="primary-outline",
            width=ui_helper.scale_size(18)
        )
        
        # 初始化权限状态显示
        self.update_permission_ui()
            
    def setup_content_area(self, parent):
        """设置右侧内容区域"""
        self.content_area = tb.Frame(parent)
        self.content_area.pack(side=RIGHT, fill=BOTH, expand=True)
        
    # setup_status_bar 方法已删除
        
    # update_time 方法已删除
        
    def create_tooltip(self, widget, text):
        """创建简单的工具提示（状态栏已删除，暂时保留空实现）"""
        # 原本用于在状态栏显示提示信息，现在状态栏已删除
        pass
        
    def set_status(self, message, show_progress=False):
        """设置状态栏消息（状态栏已删除，保留空实现以保持兼容性）"""
        # 原本用于设置底部状态栏消息，现在状态栏已删除
        pass
            
    def clear_content_area(self):
        """清空内容区域"""
        if self.current_frame:
            # 检查是否是正在扫描的VisualPingView
            if self._is_scanning_ping_view():
                # 隐藏而不是销毁正在扫描的ping实例
                self.current_frame.pack_forget()
                self.cached_views['ping'] = self.current_frame
            else:
                # 正常清理其他实例
                if hasattr(self.current_frame, 'cleanup'):
                    self.current_frame.cleanup()
                self.current_frame.destroy()
            
            self.current_frame = None
            
    def _is_scanning_ping_view(self):
        """检查当前是否是正在扫描的VisualPingView"""
        # 检查是否是VisualPingView实例
        if not hasattr(self.current_frame, 'scan_controller'):
            return False
        
        # 检查缓存保护时间戳（3秒保护期）
        if hasattr(self.current_frame, '_from_cache_timestamp'):
            import time
            current_time = time.time()
            time_since_cache = current_time - self.current_frame._from_cache_timestamp
            if time_since_cache < 3.0:  # 3秒保护期
                return True
            
        # 检查扫描状态
        try:
            is_scanning = (hasattr(self.current_frame.scan_controller, 'is_scanning') and 
                          self.current_frame.scan_controller.is_scanning)
            return is_scanning
        except (AttributeError, Exception):
            return False
            
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
            
            # 创建界面，传递权限状态
            self.current_frame = NetConfigView(
                self.content_area, 
                readonly_mode=not self.is_admin
            )
            self.current_frame.pack(fill=BOTH, expand=True)
            
            if not self.is_admin:
                self.set_status("IP地址切换功能已加载（只读模式）")
            else:
                self.set_status("IP地址切换功能已加载")
        except Exception as e:
            self.set_status(f"加载IP切换功能失败: {str(e)}")
        
    def show_ping(self):
        """显示Ping测试功能"""
        self.clear_content_area()
        self.set_status("正在加载Ping测试功能...")
        
        try:
            # 优先使用缓存的实例
            if 'ping' in self.cached_views:
                self.current_frame = self.cached_views['ping']
                del self.cached_views['ping']  # 从缓存中移除
                
                # 标记为从缓存恢复，短时间内保护不被清理
                import time
                self.current_frame._from_cache_timestamp = time.time()
            else:
                self.current_frame = VisualPingView(self.content_area)
            
            self.current_frame.pack(fill=BOTH, expand=True)
            self.set_status("Ping测试功能已加载")
        except Exception as e:
            self.set_status(f"加载Ping测试功能失败: {str(e)}")
        
    def show_route(self):
        """显示静态路由功能"""
        self.clear_content_area()
        self.set_status("正在加载静态路由管理功能...")
        
        try:
            # 创建路由管理界面，传递权限状态
            self.current_frame = RouteFrame(
                self.content_area,
                readonly_mode=not self.is_admin
            )
            self.current_frame.pack(fill=BOTH, expand=True)
            
            if not self.is_admin:
                self.set_status("静态路由管理功能已加载（只读模式）")
            else:
                self.set_status("静态路由管理功能已加载")
        except Exception as e:
            self.set_status(f"加载静态路由管理功能失败: {str(e)}")
    
    def update_permission_ui(self):
        """更新权限状态显示"""
        if self.is_admin:
            # 管理员模式
            self.admin_label.config(
                text="✅ 管理员模式",
                bootstyle=SUCCESS
            )
            # 隐藏权限提升按钮
            self.elevate_button.pack_forget()
        else:
            # 受限模式
            self.admin_label.config(
                text="⚠️ 受限模式",
                bootstyle=WARNING
            )
            # 显示权限提升按钮
            self.elevate_button.pack(pady=ui_helper.get_padding(5), fill=X)
        
        # 更新导航按钮状态
        self.update_nav_buttons_state()
    
    def update_nav_buttons_state(self):
        """根据权限状态更新导航按钮"""
        for i, (btn, (text, command, style, tooltip, requires_admin)) in enumerate(zip(self.nav_buttons, self.nav_button_configs)):
            if requires_admin and not self.is_admin:
                # 需要管理员权限但当前是受限模式 - 变灰但可点击进入只读模式
                btn.config(
                    bootstyle="secondary",  # 灰色样式
                    state="normal"  # 保持可点击
                )
            else:
                # 恢复正常样式
                btn.config(
                    bootstyle=style,
                    state="normal"
                )
    
    def request_admin_elevation(self):
        """请求管理员权限提升"""
        try:
            # 更新按钮文字为提示状态
            self.elevate_button.config(text="正在请求权限...")
            self.elevate_button.update()
            
            # 尝试自动提升权限
            success = auto_elevate()
            
            if success:
                # 成功触发UAC，程序会重启，这里实际不会执行到
                sys.exit(0)
            else:
                # 提升失败（用户取消或系统限制）
                self.show_elevation_failure()
                
        except Exception as e:
            # 发生异常
            self.show_elevation_failure(f"权限提升异常: {str(e)}")
    
    def show_elevation_failure(self, error_msg=None):
        """显示权限提升失败的反馈"""
        # 在权限标签上显示失败信息
        original_text = self.admin_label.cget("text")
        
        if error_msg:
            self.admin_label.config(
                text="❌ 权限获取失败",
                bootstyle=DANGER
            )
        else:
            self.admin_label.config(
                text="❌ 权限获取失败",
                bootstyle=DANGER
            )
        
        # 更新按钮文字
        self.elevate_button.config(text="重试获取权限")
        
        # 3秒后恢复正常状态
        def restore_normal_state():
            self.admin_label.config(
                text="⚠️ 受限模式",
                bootstyle=WARNING
            )
            self.elevate_button.config(text="使用管理员方式运行")
        
        self.app.after(3000, restore_normal_state)
        
    def show_about_page(self):
        """显示关于页面"""
        import webbrowser
        
        self.clear_content_area()
        
        # 创建关于页面的主框架
        about_frame = tb.Frame(self.content_area)
        about_frame.pack(fill=BOTH, expand=True, padx=ui_helper.get_padding(30), pady=ui_helper.get_padding(30))
        
        # 主标题（左对齐）
        main_title = tb.Label(
            about_frame,
            text="NetKit",
            font=ui_helper.get_font(24, "bold"),
            bootstyle=PRIMARY
        )
        main_title.pack(anchor=W, pady=(0, ui_helper.get_padding(5)))
        
        # 副标题（左对齐）
        sub_title = tb.Label(
            about_frame,
            text="网络工程师工具箱",
            font=ui_helper.get_font(14),
            bootstyle=SECONDARY
        )
        sub_title.pack(anchor=W, pady=(0, ui_helper.get_padding(30)))
        
        # 功能标题
        features_title = tb.Label(
            about_frame,
            text="🔧 主要功能",
            font=ui_helper.get_font(16, "bold"),
            bootstyle=SUCCESS
        )
        features_title.pack(anchor=W, pady=(0, ui_helper.get_padding(10)))
        
        # 功能列表
        features = [
            "• 网络配置管理",
            "• Ping连通性测试",
            "• 静态路由管理"
        ]
        
        for feature in features:
            feature_label = tb.Label(
                about_frame,
                text=feature,
                font=ui_helper.get_font(11),
                bootstyle=SECONDARY
            )
            feature_label.pack(anchor=W, pady=ui_helper.get_padding(2), padx=(ui_helper.get_padding(20), 0))
        
        # 相关链接标题
        links_title = tb.Label(
            about_frame,
            text="🔗 相关链接",
            font=ui_helper.get_font(16, "bold"),
            bootstyle=INFO
        )
        links_title.pack(anchor=W, pady=(ui_helper.get_padding(30), ui_helper.get_padding(10)))
        
        # GitHub链接文本
        github_label = tb.Label(
            about_frame,
            text="GitHub：https://github.com/iam189cm/NetKit",
            font=ui_helper.get_font(11, "underline"),
            bootstyle="primary",
            cursor='hand2'
        )
        github_label.pack(anchor=W, pady=ui_helper.get_padding(2), padx=(ui_helper.get_padding(20), 0))
        
        # 绑定GitHub链接点击事件
        def open_github(event):
            webbrowser.open("https://github.com/iam189cm/NetKit")
        github_label.bind("<Button-1>", open_github)
        
        # 官网链接文本
        website_label = tb.Label(
            about_frame,
            text="主页：https://netkit.189cm.com/",
            font=ui_helper.get_font(11, "underline"),
            bootstyle="info",
            cursor='hand2'
        )
        website_label.pack(anchor=W, pady=ui_helper.get_padding(2), padx=(ui_helper.get_padding(20), 0))
        
        # 绑定官网链接点击事件
        def open_website(event):
            webbrowser.open("https://netkit.189cm.com/")
        website_label.bind("<Button-1>", open_website)
        
        # 版本信息标题
        version_title = tb.Label(
            about_frame,
            text="📊 版本信息",
            font=ui_helper.get_font(16, "bold"),
            bootstyle=SECONDARY
        )
        version_title.pack(anchor=W, pady=(ui_helper.get_padding(30), ui_helper.get_padding(10)))
        
        # 版本号
        version_label = tb.Label(
            about_frame,
            text="版本：v2.0.1",
            font=ui_helper.get_font(11),
            bootstyle=SECONDARY
        )
        version_label.pack(anchor=W, padx=(ui_helper.get_padding(20), 0))
        
        # 保存当前框架引用
        self.current_frame = about_frame
    
    def run(self):
        """运行应用程序"""
        self.set_status("NetKit 启动完成，欢迎使用！")
        self.app.mainloop()


def main():
    # 检查管理员权限但不强制退出
    admin_status = check_admin_without_exit()
    app = MainWindow(admin_status)
    app.run()


if __name__ == '__main__':
    main()
