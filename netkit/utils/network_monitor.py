#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络监听服务
使用WMI事件监听网络适配器变化
"""

import threading
import time
import subprocess
import logging
from typing import Callable, Optional


class NetworkMonitor:
    """网络适配器监听器"""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        self.last_event_time = 0
        self.event_debounce_interval = 1.0  # 事件防抖间隔1秒
        
    def add_callback(self, callback: Callable):
        """添加网络变化回调函数"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """移除网络变化回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_monitoring(self):
        """开始监听网络适配器变化"""
        if self.is_monitoring:
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止监听"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def _monitor_loop(self):
        """监听循环"""
        try:
            # 尝试使用WMI事件监听
            if self._try_wmi_monitoring():
                return
        except Exception as e:
            print(f"WMI监听失败，切换到轮询模式: {e}")
        
        # 如果WMI失败，使用轮询模式
        self._polling_monitoring()
    
    def _try_wmi_monitoring(self):
        """尝试使用WMI事件监听"""
        try:
            import wmi
            import pythoncom
            
            # 初始化COM环境
            pythoncom.CoInitialize()
            
            try:
                # 创建WMI连接
                c = wmi.WMI()
                
                # 监听网络适配器配置变化事件
                adapter_watcher = c.Win32_NetworkAdapterConfiguration.watch_for(
                    notification_type="modification"
                )
                
                # 监听网络适配器状态变化事件
                status_watcher = c.Win32_NetworkAdapter.watch_for(
                    notification_type="modification"
                )
                
                print("WMI网络监听已启动")
                
                while self.is_monitoring:
                    try:
                        # 检查配置变化事件（超时1秒）
                        if adapter_watcher(timeout_ms=1000):
                            self._trigger_callbacks("网络适配器配置变化")
                        
                        # 检查状态变化事件（超时1秒）
                        if status_watcher(timeout_ms=1000):
                            self._trigger_callbacks("网络适配器状态变化")
                            
                    except Exception as e:
                        if self.is_monitoring:
                            print(f"WMI事件监听错误: {e}")
                            time.sleep(1)
                
                return True
                
            finally:
                # 清理COM环境
                pythoncom.CoUninitialize()
            
        except ImportError:
            print("WMI模块未安装，使用轮询模式")
            return False
        except Exception as e:
            print(f"WMI监听初始化失败: {e}")
            return False
    
    def _polling_monitoring(self):
        """轮询模式监听"""
        print("使用轮询模式监听网络变化")
        
        # 获取初始网络状态
        previous_state = self._get_network_state()
        
        while self.is_monitoring:
            try:
                time.sleep(2)  # 每2秒检查一次
                
                current_state = self._get_network_state()
                
                # 比较状态变化
                if current_state != previous_state:
                    self._trigger_callbacks("网络状态变化（轮询检测）")
                    previous_state = current_state
                    
            except Exception as e:
                if self.is_monitoring:
                    print(f"轮询监听错误: {e}")
                    time.sleep(5)
    
    def _get_network_state(self):
        """获取当前网络状态（用于轮询比较）"""
        try:
            # 获取网络接口状态
            cmd = ['netsh', 'interface', 'show', 'interface']
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', timeout=10)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return ""
                
        except Exception:
            return ""
    
    def _trigger_callbacks(self, event_type: str):
        """触发回调函数（带防抖）"""
        current_time = time.time()
        
        # 事件防抖
        if (current_time - self.last_event_time) < self.event_debounce_interval:
            return
            
        self.last_event_time = current_time
        
        # 调用所有回调函数
        for callback in self.callbacks:
            try:
                callback(event_type)
            except Exception as e:
                print(f"回调函数执行错误: {e}")


# 全局网络监听器实例
_network_monitor = None


def get_network_monitor() -> NetworkMonitor:
    """获取全局网络监听器实例"""
    global _network_monitor
    if _network_monitor is None:
        _network_monitor = NetworkMonitor()
    return _network_monitor


def start_network_monitoring():
    """启动网络监听"""
    monitor = get_network_monitor()
    monitor.start_monitoring()


def stop_network_monitoring():
    """停止网络监听"""
    monitor = get_network_monitor()
    monitor.stop_monitoring()


def add_network_change_callback(callback: Callable):
    """添加网络变化回调"""
    monitor = get_network_monitor()
    monitor.add_callback(callback)


def remove_network_change_callback(callback: Callable):
    """移除网络变化回调"""
    monitor = get_network_monitor()
    monitor.remove_callback(callback) 