"""
网卡选择器UI组件
负责网卡选择、刷新等交互功能
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.services.netconfig.interface_manager import (
    get_network_interfaces_with_details,
    extract_interface_name_from_display
)
from netkit.utils.network_monitor import add_network_change_callback, remove_network_change_callback
import threading
import time


class InterfaceSelectorWidget(tb.Frame):
    """网卡选择器组件"""
    
    def __init__(self, master, on_interface_selected=None, on_status_update=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # 回调函数
        self.on_interface_selected = on_interface_selected
        self.on_status_update = on_status_update
        
        # 刷新控制变量
        self.last_refresh_time = 0
        self.min_refresh_interval = 2.0  # 最小刷新间隔2秒
        self.is_refreshing = False
        self.refresh_retry_count = 0
        self.max_refresh_retries = 1
        
        self.setup_ui()
        
        # 延迟加载网络接口，避免阻塞界面显示
        self.after(100, lambda: self.refresh_interfaces(force=True))
        
        # 注册网络变化回调
        add_network_change_callback(self.on_network_change)
    
    def setup_ui(self):
        """设置UI组件"""
        # 网卡选择行
        select_frame = tb.Frame(self)
        select_frame.pack(fill=X)
        
        # 左侧：网卡选择标签和下拉框
        tb.Label(select_frame, text="网卡选择:", font=('Microsoft YaHei', 10)).pack(side=LEFT)
        
        self.interface_var = tb.StringVar()
        self.interface_combo = tb.Combobox(
            select_frame,
            textvariable=self.interface_var,
            state="readonly",
            width=55,  # 调整为55以确保网卡名称完整显示
            font=('Microsoft YaHei', 9)
        )
        self.interface_combo.pack(side=LEFT, padx=(10, 20))
        self.interface_combo.bind('<<ComboboxSelected>>', self._on_interface_selected)
        
        # 中间：显示所有网卡选项
        self.show_all_var = tb.BooleanVar()
        tb.Checkbutton(
            select_frame,
            text="显示所有网卡",
            variable=self.show_all_var,
            command=lambda: self.refresh_interfaces(force=True)
        ).pack(side=LEFT, padx=(0, 20))
        
        # 右侧：刷新按钮
        self.refresh_button = tb.Button(
            select_frame,
            text="刷新网卡",
            bootstyle=INFO,
            command=lambda: self.refresh_interfaces(force=True),
            width=12
        )
        self.refresh_button.pack(side=RIGHT)
    
    def _on_interface_selected(self, event=None):
        """内部接口选择处理"""
        if self.on_interface_selected:
            display_name = self.interface_var.get().strip()
            if display_name:
                interface_name = extract_interface_name_from_display(display_name)
                self.on_interface_selected(interface_name, display_name)
    
    def _append_status(self, text):
        """追加状态信息"""
        if self.on_status_update:
            self.on_status_update(text)
    
    def can_refresh(self):
        """检查是否可以刷新（频率控制）"""
        current_time = time.time()
        return (current_time - self.last_refresh_time) >= self.min_refresh_interval
    
    def refresh_interfaces(self, force=False):
        """刷新网络接口列表
        
        Args:
            force (bool): 是否强制刷新，忽略频率限制
        """
        # 频率控制
        if not force and not self.can_refresh():
            return
            
        # 防止重复刷新
        if self.is_refreshing:
            return
            
        # 手动刷新时显示按钮状态
        if force:
            self.set_refresh_button_loading(True)
        
        # 在后台线程中执行刷新
        def refresh_thread():
            try:
                self.is_refreshing = True
                self.last_refresh_time = time.time()
                
                # 保存当前选择的网卡（提取原始接口名称）
                current_display = self.interface_var.get()
                current_selection = extract_interface_name_from_display(current_display) if current_display else ""
                
                # 获取"显示所有网卡"选项的状态
                show_all = self.show_all_var.get()
                interfaces_with_details = get_network_interfaces_with_details(show_all=show_all)
                
                # 在主线程中更新UI
                self.after(0, lambda: self.update_interface_list(interfaces_with_details, current_selection, show_all))
                
            except Exception as e:
                # 在主线程中显示错误
                self.after(0, lambda: self.handle_refresh_error(e))
        
        # 启动后台刷新线程
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_interface_list(self, interfaces_with_details, current_selection, show_all):
        """在主线程中更新界面列表"""
        try:
            if interfaces_with_details:
                # 提取显示名称和原始名称
                display_names = [item[0] for item in interfaces_with_details]
                original_names = [item[1] for item in interfaces_with_details]
                
                self.interface_combo['values'] = display_names
                
                interface_type = "所有网络接口" if show_all else "物理网络接口"
                self._append_status(f"已获取 {len(interfaces_with_details)} 个{interface_type}\n")
                
                # 尝试恢复之前的选择
                if current_selection and current_selection in original_names:
                    # 之前选择的网卡仍然存在，恢复选择
                    index = original_names.index(current_selection)
                    self.interface_var.set(display_names[index])
                    self.after(100, self._on_interface_selected)
                elif current_selection:
                    # 之前选择的网卡消失了，清空选择
                    self.interface_var.set("")
                    self._append_status(f"之前选择的网卡 '{current_selection}' 已不可用\n")
                else:
                    # 首次加载或没有之前的选择，选择第一个网卡
                    self.interface_combo.current(0)
                    self.after(100, self._on_interface_selected)
            else:
                interface_type = "网络接口" if show_all else "物理网络接口"
                self._append_status(f"未找到可用的{interface_type}\n")
                self.interface_var.set("")
                
            self.refresh_retry_count = 0  # 重置重试计数
            
        except Exception as e:
            self.handle_refresh_error(e)
        finally:
            self.is_refreshing = False
            self.set_refresh_button_loading(False)
    
    def handle_refresh_error(self, error):
        """处理刷新错误"""
        self.refresh_retry_count += 1
        
        if self.refresh_retry_count <= self.max_refresh_retries:
            # 重试一次
            self._append_status(f"网卡刷新失败，正在重试... ({self.refresh_retry_count}/{self.max_refresh_retries})\n")
            self.after(1000, lambda: self.refresh_interfaces(force=True))
        else:
            # 重试失败，显示错误
            self._append_status(f"网卡刷新失败: {str(error)}\n")
            self.refresh_retry_count = 0
            self.is_refreshing = False
            self.set_refresh_button_loading(False)
    
    def on_network_change(self, event_type):
        """网络变化回调"""
        # 在主线程中执行刷新
        self.after(0, lambda: self.refresh_interfaces())
        self.after(0, lambda: self._append_status(f"检测到网络变化: {event_type}\n"))
    
    def set_refresh_button_loading(self, loading):
        """设置刷新按钮的加载状态"""
        if loading:
            self.refresh_button.config(text="刷新中...", state=DISABLED)
        else:
            self.refresh_button.config(text="刷新网卡", state=NORMAL)
    
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
        # 移除网络变化回调
        remove_network_change_callback(self.on_network_change) 