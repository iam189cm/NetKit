"""
异步网卡数据管理器
提供异步、预加载、智能缓存的网卡信息管理
"""

import threading
import time
import os
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from .wmi_engine import get_wmi_engine, NetworkAdapterInfo
import logging

@dataclass
class LoadingState:
    """加载状态"""
    is_loading: bool = False
    progress: float = 0.0
    message: str = ""
    error: Optional[str] = None

class AsyncNetworkDataManager:
    """异步网卡数据管理器"""
    
    def __init__(self):
        self.wmi_engine = get_wmi_engine()
        self.loading_state = LoadingState()
        self.callbacks = []
        self.logger = logging.getLogger(__name__)
        
        # 预加载标志
        self.preload_completed = False
        self.preload_thread = None
        
        # 数据缓存
        self.adapters_cache = {}
        self.last_full_refresh = 0
        
        # 加载锁
        self.loading_lock = threading.Lock()
        
    def add_callback(self, callback: Callable):
        """添加数据更新回调"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """移除数据更新回调"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start_preload(self):
        """启动预加载"""
        with self.loading_lock:
            if self.preload_thread and self.preload_thread.is_alive():
                return
            
            self.preload_thread = threading.Thread(target=self._preload_worker, daemon=True)
            self.preload_thread.start()
    
    def _preload_worker(self):
        """预加载工作线程"""
        try:
            # CI环境检测 - 如果是CI环境，跳过预加载避免COM冲突
            is_ci = os.getenv('CI', '').lower() == 'true' or os.getenv('GITHUB_ACTIONS', '').lower() == 'true'
            if is_ci:
                self.logger.warning("检测到CI环境，跳过异步预加载")
                self.preload_completed = True
                return
            
            self.loading_state.is_loading = True
            self.loading_state.error = None
            self.loading_state.message = "正在预加载网卡信息..."
            self._notify_callbacks("loading_started")
            
            # 阶段1：加载基本网卡列表
            self.loading_state.progress = 0.1
            self.loading_state.message = "获取网卡列表..."
            self._notify_callbacks("loading_progress")
            
            # 获取所有网卡信息（包括虚拟网卡用于完整缓存）
            adapters = self.wmi_engine.get_all_adapters_info(show_all=True, force_refresh=True)
            
            if not adapters:
                self.loading_state.error = "未找到任何网卡"
                self._notify_callbacks("loading_error")
                return
            
            # 阶段2：批量处理网卡信息
            self.loading_state.progress = 0.3
            self.loading_state.message = f"处理 {len(adapters)} 个网卡信息..."
            self._notify_callbacks("loading_progress")
            
            # 缓存所有适配器信息
            for i, adapter in enumerate(adapters):
                # 更新进度
                progress = 0.3 + (i / len(adapters)) * 0.6
                self.loading_state.progress = progress
                self.loading_state.message = f"处理网卡 {i+1}/{len(adapters)}: {adapter.connection_id}"
                self._notify_callbacks("loading_progress")
                
                # 缓存适配器信息
                self.adapters_cache[adapter.connection_id] = adapter
                
                # 小延迟避免CPU占用过高
                time.sleep(0.005)
            
            # 阶段3：完成预加载
            self.loading_state.progress = 1.0
            self.loading_state.message = f"预加载完成，共 {len(adapters)} 个网卡"
            self.preload_completed = True
            self.last_full_refresh = time.time()
            
            self._notify_callbacks("preload_completed")
            
            # 延迟清除状态信息 (CI环境跳过sleep避免问题)
            if not is_ci:
                time.sleep(2)
            self.loading_state.message = ""
            self._notify_callbacks("loading_message_cleared")
            
        except Exception as e:
            self.loading_state.error = str(e)
            self.logger.error(f"预加载失败: {e}")
            self._notify_callbacks("loading_error")
        finally:
            self.loading_state.is_loading = False
    
    def get_adapter_info_async(self, connection_id: str, callback: Callable[[Optional[NetworkAdapterInfo], Optional[str]], None]):
        """异步获取网卡信息"""
        def worker():
            try:
                # 先检查缓存
                if connection_id in self.adapters_cache:
                    adapter = self.adapters_cache[connection_id]
                    # 检查缓存是否过期（30秒）
                    if time.time() - adapter.last_updated < 30:
                        callback(adapter, None)
                        return
                
                # 从WMI获取最新信息
                adapter = self.wmi_engine.get_adapter_info(connection_id, force_refresh=True)
                if adapter:
                    self.adapters_cache[connection_id] = adapter
                    callback(adapter, None)
                else:
                    callback(None, "网卡不存在")
                    
            except Exception as e:
                callback(None, str(e))
        
        threading.Thread(target=worker, daemon=True).start()
    
    def get_all_adapters_fast(self, show_all=False) -> List[NetworkAdapterInfo]:
        """快速获取所有网卡信息（优先使用缓存）"""
        if not self.preload_completed:
            # 如果预加载未完成，返回空列表并触发预加载
            if not self.loading_state.is_loading:
                self.start_preload()
            return []
        
        # 返回缓存的数据
        adapters = list(self.adapters_cache.values())
        
        # 根据show_all参数过滤
        if not show_all:
            adapters = [a for a in adapters if a.physical_adapter]
        
        return adapters
    
    def get_all_adapters_with_details(self, show_all=False) -> List[tuple]:
        """获取带详细信息的网络接口列表（兼容接口）"""
        adapters = self.get_all_adapters_fast(show_all)
        
        result = []
        for adapter in adapters:
            # 格式化显示名称: [状态] 网卡名称 (制造商 型号) - IP地址
            display_name = self._format_display_name(adapter)
            result.append((display_name, adapter.connection_id))
        
        return result
    
    def _format_display_name(self, adapter: NetworkAdapterInfo) -> str:
        """格式化网卡显示名称"""
        # 格式: [状态] 网卡名称 (制造商 型号) - IP地址
        status = adapter.connection_status
        name = adapter.connection_id
        manufacturer = adapter.manufacturer if adapter.manufacturer != '未知' else ''
        model = adapter.model if adapter.model != '未知' else ''
        ip = adapter.ip_addresses[0] if adapter.ip_addresses else '未配置'
        
        # 简化制造商名称
        if manufacturer:
            if 'Intel' in manufacturer:
                manufacturer = 'Intel'
            elif 'Realtek' in manufacturer:
                manufacturer = 'Realtek'
            elif 'Broadcom' in manufacturer:
                manufacturer = 'Broadcom'
            elif 'Qualcomm' in manufacturer:
                manufacturer = 'Qualcomm'
            elif 'VMware' in manufacturer:
                manufacturer = 'VMware'
            elif 'Microsoft' in manufacturer:
                manufacturer = 'Microsoft'
            elif len(manufacturer) > 15:
                manufacturer = manufacturer[:15] + '...'
        
        # 简化型号显示
        if model:
            if 'Wi-Fi 6E' in model:
                model = model.replace('Wi-Fi 6E ', '')
            elif 'Wi-Fi 6' in model:
                model = model.replace('Wi-Fi 6 ', '')
            elif 'Ethernet' in model:
                model = model.replace('Ethernet ', '')
            elif 'Virtual' in model:
                model = 'Virtual'
        
        # 构建硬件信息部分
        hardware_part = ""
        if manufacturer and model:
            hardware_part = f" ({manufacturer} {model})"
        elif manufacturer:
            hardware_part = f" ({manufacturer})"
        
        return f"[{status}] {name}{hardware_part} - {ip}"
    
    def refresh_adapter(self, connection_id: str):
        """刷新特定网卡信息"""
        def worker():
            try:
                adapter = self.wmi_engine.get_adapter_info(connection_id, force_refresh=True)
                if adapter:
                    self.adapters_cache[connection_id] = adapter
                    self._notify_callbacks("adapter_updated", connection_id)
                else:
                    # 网卡可能已被移除
                    if connection_id in self.adapters_cache:
                        del self.adapters_cache[connection_id]
                    self._notify_callbacks("adapter_removed", connection_id)
            except Exception as e:
                self.logger.error(f"刷新网卡{connection_id}失败: {e}")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def refresh_all_adapters(self):
        """刷新所有网卡信息"""
        def worker():
            try:
                self.loading_state.is_loading = True
                self.loading_state.error = None
                self.loading_state.message = "正在刷新网卡信息..."
                self._notify_callbacks("loading_started")
                
                # 获取最新的网卡信息
                adapters = self.wmi_engine.get_all_adapters_info(show_all=True, force_refresh=True)
                
                # 更新缓存
                new_cache = {}
                for adapter in adapters:
                    new_cache[adapter.connection_id] = adapter
                
                self.adapters_cache = new_cache
                self.last_full_refresh = time.time()
                
                # 先设置加载状态为False，再发送完成事件
                self.loading_state.is_loading = False
                self.loading_state.message = f"刷新完成，共 {len(adapters)} 个网卡"
                self._notify_callbacks("refresh_completed")
                
                # 延迟清除状态信息
                time.sleep(1)
                self.loading_state.message = ""
                self._notify_callbacks("loading_message_cleared")
                
            except Exception as e:
                self.loading_state.error = str(e)
                self.loading_state.is_loading = False
                self.logger.error(f"刷新所有网卡失败: {e}")
                self._notify_callbacks("loading_error")
        
        threading.Thread(target=worker, daemon=True).start()
    
    def get_loading_state(self) -> LoadingState:
        """获取当前加载状态"""
        return self.loading_state
    
    def is_cache_valid(self, max_age_seconds=300) -> bool:
        """检查缓存是否有效"""
        if not self.preload_completed:
            return False
        
        cache_age = time.time() - self.last_full_refresh
        return cache_age < max_age_seconds
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        return {
            'total_adapters': len(self.adapters_cache),
            'physical_adapters': len([a for a in self.adapters_cache.values() if a.physical_adapter]),
            'last_refresh': self.last_full_refresh,
            'cache_age': time.time() - self.last_full_refresh if self.last_full_refresh > 0 else 0,
            'preload_completed': self.preload_completed,
            'is_loading': self.loading_state.is_loading
        }
    
    def clear_cache(self):
        """清空缓存"""
        self.adapters_cache.clear()
        self.preload_completed = False
        self.last_full_refresh = 0
        self.loading_state = LoadingState()
        self._notify_callbacks("cache_cleared")
    
    def invalidate_adapter_cache(self, connection_id: str):
        """立即失效指定网卡的缓存"""
        if connection_id in self.adapters_cache:
            # 将缓存时间设置为很久以前，强制下次获取时刷新
            adapter = self.adapters_cache[connection_id]
            adapter.last_updated = 0
            self.logger.info(f"已失效网卡 {connection_id} 的缓存")
    
    def force_refresh_adapter(self, connection_id: str):
        """强制刷新指定网卡信息并通知回调"""
        def worker():
            try:
                # 强制从WMI获取最新信息
                adapter = self.wmi_engine.get_adapter_info(connection_id, force_refresh=True)
                if adapter:
                    self.adapters_cache[connection_id] = adapter
                    self._notify_callbacks("adapter_force_updated", connection_id)
                    self.logger.info(f"强制刷新网卡 {connection_id} 成功")
                else:
                    self.logger.warning(f"强制刷新网卡 {connection_id} 失败：网卡不存在")
            except Exception as e:
                self.logger.error(f"强制刷新网卡 {connection_id} 失败: {e}")
        
        threading.Thread(target=worker, daemon=True).start()

    def _notify_callbacks(self, event_type: str, data: Any = None):
        """通知回调函数"""
        for callback in self.callbacks:
            try:
                callback(event_type, data)
            except Exception as e:
                self.logger.error(f"回调函数执行失败: {e}")

# 全局异步数据管理器
_async_manager = None

def get_async_manager() -> AsyncNetworkDataManager:
    """获取异步数据管理器实例"""
    global _async_manager
    if _async_manager is None:
        _async_manager = AsyncNetworkDataManager()
    return _async_manager 