"""
网卡选择器UI组件 - 异步优化版本
提供流畅的异步加载体验
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.netconfig.async_manager import get_async_manager
from netkit.services.netconfig.interface_manager import extract_interface_name_from_display, start_preload
from netkit.utils.network_monitor import add_network_change_callback, remove_network_change_callback
import threading
import time

class InterfaceSelectorWidget(tb.Frame):
    """网卡选择器组件 - 异步优化版本"""
    
    def __init__(self, master, on_interface_selected=None, on_status_update=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # 回调函数
        self.on_interface_selected = on_interface_selected
        self.on_status_update = on_status_update
        
        # 异步管理器
        self.async_manager = get_async_manager()
        self.async_manager.add_callback(self._on_async_event)
        
        # UI状态
        self.is_loading = False
        self.current_selection = None
        
        # 错误处理和超时管理
        self.loading_timeout_id = None
        self.loading_start_time = None
        self.max_loading_timeout = 30000  # 30秒超时
        
        # 定期状态检查
        self.state_check_interval = 5000  # 5秒检查一次
        self.state_check_id = None
        
        self.setup_ui()
        
        # 启动异步加载
        self.start_async_loading()
        
        # 启动定期状态检查
        self._start_state_check()
        
        # 注册网络变化回调
        add_network_change_callback(self.on_network_change)
    
    def setup_ui(self):
        """设置UI组件"""
        # 主容器
        main_frame = tb.Frame(self)
        main_frame.pack(fill=X)
        
        # 左侧：网卡选择
        left_frame = tb.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=X, expand=True)
        
        tb.Label(left_frame, text="网卡选择:", font=ui_helper.get_font(10)).pack(side=LEFT)
        
        self.interface_var = tb.StringVar()
        self.interface_combo = tb.Combobox(
            left_frame,
            textvariable=self.interface_var,
            state="readonly",
            width=ui_helper.scale_size(55),
            font=ui_helper.get_font(9)
        )
        self.interface_combo.pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(20)))
        self.interface_combo.bind('<<ComboboxSelected>>', self._on_interface_selected)
        
        # 中间：选项
        middle_frame = tb.Frame(main_frame)
        middle_frame.pack(side=LEFT)
        
        self.show_all_var = tb.BooleanVar()
        tb.Checkbutton(
            middle_frame,
            text="显示所有网卡",
            variable=self.show_all_var,
            command=self.on_show_all_changed
        ).pack(side=LEFT, padx=(0, ui_helper.get_padding(20)))
        
        # 右侧：刷新按钮和进度
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=RIGHT)
        
        self.refresh_button = tb.Button(
            right_frame,
            text="刷新网卡",
            bootstyle=INFO,
            command=self.manual_refresh,
            width=ui_helper.scale_size(12)
        )
        self.refresh_button.pack(side=RIGHT)
        
        # 进度条（初始隐藏）
        self.progress_bar = tb.Progressbar(
            right_frame,
            mode='determinate',
            length=ui_helper.scale_size(100)
        )
        
        # 状态标签
        self.status_label = tb.Label(
            main_frame,
            text="正在加载网卡信息...",
            font=ui_helper.get_font(8),
            foreground="gray"
        )
        self.status_label.pack(fill=X, pady=(ui_helper.get_padding(5), 0))
    
    def start_async_loading(self):
        """启动异步加载"""
        # 验证并同步状态
        self._validate_and_sync_state()
        
        # 检查预加载状态
        if self.async_manager.preload_completed:
            # 预加载已完成，直接更新界面
            self.is_loading = False
            self.refresh_button.config(state=NORMAL)
            self.interface_combo.config(state="readonly")
            self.update_interface_list()
            self.status_label.config(text="网卡信息已就绪")
            # 3秒后隐藏状态标签
            self.after(3000, lambda: self.status_label.config(text=""))
            return
        
        # 检查是否正在加载
        if self.async_manager.loading_state.is_loading:
            # 正在加载中，更新UI状态但不重新启动预加载
            self.is_loading = True
            self.refresh_button.config(state=DISABLED)
            self.interface_combo.config(state=DISABLED)
            
            # 显示进度条
            self.progress_bar.pack(side=RIGHT, padx=(ui_helper.get_padding(10), 0))
            self.progress_bar.start()
            
            # 更新当前状态
            current_message = self.async_manager.loading_state.message
            if current_message:
                self.status_label.config(text=current_message)
            else:
                self.status_label.config(text="正在加载网卡信息...")
            return
        
        # 需要启动新的预加载
        self.is_loading = True
        self.refresh_button.config(state=DISABLED)
        self.interface_combo.config(state=DISABLED)
        
        # 显示进度条
        self.progress_bar.pack(side=RIGHT, padx=(ui_helper.get_padding(10), 0))
        self.progress_bar.start()
        
        # 启动超时检测
        self._start_loading_timeout()
        
        # 启动预加载
        start_preload()
    
    def _on_async_event(self, event_type: str, data=None):
        """异步事件处理"""
        # 确保在主线程中执行UI更新
        self.after(0, lambda: self._handle_async_event(event_type, data))
    
    def _handle_async_event(self, event_type: str, data=None):
        """处理异步事件（在主线程中）"""
        try:
            if event_type == "loading_started":
                self.status_label.config(text="正在加载网卡信息...")
                
            elif event_type == "loading_progress":
                progress = self.async_manager.loading_state.progress * 100
                message = self.async_manager.loading_state.message
                
                self.progress_bar.config(value=progress)
                self.status_label.config(text=message)
                
            elif event_type == "preload_completed":
                self._on_preload_completed()
                
            elif event_type == "refresh_completed":
                self._on_refresh_completed()
                
            elif event_type == "loading_error":
                error = self.async_manager.loading_state.error
                self.status_label.config(text=f"加载失败: {error}")
                self._append_status(f"加载失败: {error}\n")
                self._reset_loading_state()
                
            elif event_type == "adapter_updated":
                self._on_adapter_updated(data)
                
            elif event_type == "loading_message_cleared":
                # 只有在没有其他状态消息时才清除
                if self.status_label.cget("text").startswith(("预加载完成", "刷新完成")):
                    self.status_label.config(text="")
                    
        except Exception as e:
            # 异常处理，避免事件处理失败导致界面卡死
            self.status_label.config(text=f"事件处理失败: {str(e)}")
            self._append_status(f"事件处理失败: {str(e)}\n")
            # 确保在异常情况下也能重置状态
            if self.is_loading:
                self._reset_loading_state()
    
    def _on_preload_completed(self):
        """预加载完成处理"""
        self.is_loading = False
        
        # 隐藏进度条
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        
        # 启用控件
        self.refresh_button.config(state=NORMAL)
        self.interface_combo.config(state="readonly")
        
        # 更新网卡列表
        self.update_interface_list()
        
        self.status_label.config(text="网卡信息加载完成")
        
        # 3秒后隐藏状态标签
        self.after(3000, lambda: self.status_label.config(text=""))
        
        # 清除超时检测
        self._clear_loading_timeout()
    
    def _on_refresh_completed(self):
        """手动刷新完成处理"""
        self.is_loading = False
        
        # 隐藏进度条
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        
        # 启用控件
        self.refresh_button.config(state=NORMAL)
        self.interface_combo.config(state="readonly")
        
        # 更新网卡列表
        self.update_interface_list()
        
        self.status_label.config(text="网卡信息刷新完成")
        
        # 3秒后隐藏状态标签
        self.after(3000, lambda: self.status_label.config(text=""))
        
        # 清除超时检测
        self._clear_loading_timeout()
    
    def update_interface_list(self):
        """更新网卡列表"""
        try:
            show_all = self.show_all_var.get()
            interfaces_with_details = self.async_manager.get_all_adapters_with_details(show_all)
            
            if not interfaces_with_details:
                self.interface_combo['values'] = []
                self.status_label.config(text="未找到可用网卡")
                return
            
            # 提取显示名称
            display_names = [item[0] for item in interfaces_with_details]
            original_names = [item[1] for item in interfaces_with_details]
            
            self.interface_combo['values'] = display_names
            
            # 尝试恢复之前的选择
            if self.current_selection:
                for i, original_name in enumerate(original_names):
                    if original_name == self.current_selection:
                        self.interface_combo.current(i)
                        break
            elif display_names:
                # 选择第一个网卡
                self.interface_combo.current(0)
                self.after(100, self._on_interface_selected)
            
            interface_type = "所有网络接口" if show_all else "物理网络接口"
            self._append_status(f"已获取 {len(interfaces_with_details)} 个{interface_type}\n")
            
        except Exception as e:
            self.status_label.config(text=f"更新网卡列表失败: {str(e)}")
    
    def manual_refresh(self):
        """手动刷新"""
        if self.is_loading:
            return
        
        self.is_loading = True
        self.refresh_button.config(state=DISABLED)
        
        # 显示进度条
        self.progress_bar.pack(side=RIGHT, padx=(ui_helper.get_padding(10), 0))
        self.progress_bar.start()
        
        # 启动超时检测
        self._start_loading_timeout()
        
        # 触发异步刷新
        self.async_manager.refresh_all_adapters()
        
        self._append_status("手动刷新网卡信息...\n")
    
    def on_show_all_changed(self):
        """显示所有网卡选项改变"""
        if not self.is_loading and self.async_manager.preload_completed:
            self.update_interface_list()
    
    def _on_interface_selected(self, event=None):
        """网卡选择事件处理"""
        if self.on_interface_selected:
            display_name = self.interface_var.get().strip()
            if display_name:
                interface_name = extract_interface_name_from_display(display_name)
                self.current_selection = interface_name
                self.on_interface_selected(interface_name, display_name)
    
    def _on_adapter_updated(self, connection_id):
        """网卡更新事件处理"""
        if connection_id == self.current_selection:
            # 当前选择的网卡信息更新了，重新触发选择事件
            self.after(100, self._on_interface_selected)
        
        # 更新网卡列表
        self.update_interface_list()
    
    def _reset_loading_state(self):
        """重置加载状态"""
        self.is_loading = False
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.refresh_button.config(state=NORMAL)
        self.interface_combo.config(state="readonly")
        
        # 清除超时检测
        self._clear_loading_timeout()
    
    def _start_loading_timeout(self):
        """启动加载超时检测"""
        self._clear_loading_timeout()
        self.loading_start_time = time.time()
        self.loading_timeout_id = self.after(self.max_loading_timeout, self._on_loading_timeout)
    
    def _clear_loading_timeout(self):
        """清除加载超时检测"""
        if self.loading_timeout_id:
            self.after_cancel(self.loading_timeout_id)
            self.loading_timeout_id = None
        self.loading_start_time = None
    
    def _on_loading_timeout(self):
        """加载超时处理"""
        if self.is_loading:
            self.status_label.config(text="加载超时，正在重试...")
            self._append_status("网卡信息加载超时，正在重试...\n")
            
            # 重置状态
            self._reset_loading_state()
            
            # 延迟重试
            self.after(1000, self._retry_loading)
    
    def _retry_loading(self):
        """重试加载"""
        try:
            self.status_label.config(text="正在重试加载网卡信息...")
            self._append_status("开始重试加载网卡信息...\n")
            
            # 清除异步管理器的缓存，强制重新加载
            self.async_manager.clear_cache()
            
            # 重新启动加载
            self.start_async_loading()
            
        except Exception as e:
            self.status_label.config(text=f"重试失败: {str(e)}")
            self._append_status(f"重试加载失败: {str(e)}\n")
            self._reset_loading_state()
    
    def _validate_and_sync_state(self):
        """验证并同步UI状态与异步管理器状态"""
        try:
            # 检查异步管理器状态
            async_loading = self.async_manager.loading_state.is_loading
            async_completed = self.async_manager.preload_completed
            
            # 如果异步管理器显示未在加载，但UI显示正在加载，需要同步
            if not async_loading and self.is_loading:
                if async_completed:
                    # 预加载已完成，更新UI
                    self._on_preload_completed()
                else:
                    # 异步加载可能失败了，重置UI状态
                    self._reset_loading_state()
                    self.status_label.config(text="状态同步：加载已停止")
                    
            # 如果异步管理器显示正在加载，但UI显示未在加载，需要同步
            elif async_loading and not self.is_loading:
                self.is_loading = True
                self.refresh_button.config(state=DISABLED)
                self.interface_combo.config(state=DISABLED)
                
                # 显示进度条
                self.progress_bar.pack(side=RIGHT, padx=(ui_helper.get_padding(10), 0))
                self.progress_bar.start()
                
                # 启动超时检测
                self._start_loading_timeout()
                
                current_message = self.async_manager.loading_state.message
                if current_message:
                    self.status_label.config(text=current_message)
                else:
                    self.status_label.config(text="状态同步：正在加载...")
                    
        except Exception as e:
            self._append_status(f"状态同步失败: {str(e)}\n")
    
    def _start_state_check(self):
        """启动定期状态检查"""
        self._stop_state_check()
        self.state_check_id = self.after(self.state_check_interval, self._periodic_state_check)
    
    def _stop_state_check(self):
        """停止定期状态检查"""
        if self.state_check_id:
            self.after_cancel(self.state_check_id)
            self.state_check_id = None
    
    def _periodic_state_check(self):
        """定期状态检查"""
        try:
            # 执行状态验证和同步
            self._validate_and_sync_state()
            
            # 继续下一次检查
            self.state_check_id = self.after(self.state_check_interval, self._periodic_state_check)
            
        except Exception as e:
            self._append_status(f"定期状态检查失败: {str(e)}\n")
            # 即使检查失败，也要继续下一次检查
            self.state_check_id = self.after(self.state_check_interval, self._periodic_state_check)
    
    def _append_status(self, text):
        """追加状态信息"""
        if self.on_status_update:
            self.on_status_update(text)
    
    def on_network_change(self, event_type):
        """网络变化回调"""
        # 在主线程中执行刷新
        self.after(0, lambda: self.refresh_network_change(event_type))
    
    def refresh_network_change(self, event_type):
        """处理网络变化（在主线程中）"""
        if not self.is_loading:
            # 触发异步刷新
            self.async_manager.refresh_all_adapters()
            self._append_status(f"检测到网络变化: {event_type}\n")
    
    def get_selected_interface(self):
        """获取当前选择的网卡"""
        display_name = self.interface_var.get().strip()
        if display_name:
            return extract_interface_name_from_display(display_name)
        return None
    
    def get_selected_display_name(self):
        """获取当前选择的显示名称"""
        return self.interface_var.get().strip()
    
    def cleanup(self):
        """清理资源"""
        # 停止定期状态检查
        self._stop_state_check()
        
        # 清除超时检测
        self._clear_loading_timeout()
        
        # 清理异步管理器回调
        self.async_manager.remove_callback(self._on_async_event)
        
        # 清理网络变化回调
        remove_network_change_callback(self.on_network_change) 