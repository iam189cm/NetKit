#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI Helper 模块
提供 DPI 感知、字体管理和界面尺寸计算功能
"""

import sys
import ctypes
import tkinter as tk
from typing import Tuple, Dict, Any


class UIHelper:
    """UI 辅助类，提供 DPI 适配和字体管理功能"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UIHelper, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._scaling_factor = 1.0
            self._dpi = 96
            self._base_font_size = 9
            self._font_family = "Microsoft YaHei"
            self._font_cache = {}
            self._initialized = True
    
    def enable_dpi_awareness(self) -> bool:
        """
        启用 Windows 高 DPI 感知
        
        Returns:
            bool: 是否成功启用 DPI 感知
        """
        if sys.platform != "win32":
            return True
        
        try:
            # 方法1: 尝试使用 Windows 10 及以上的 Per-Monitor DPI Aware V2
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
            return True
        except (AttributeError, OSError):
            try:
                # 方法2: 尝试使用 Windows 8.1 及以上的 Per-Monitor DPI Aware
                ctypes.windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_PER_MONITOR_DPI_AWARE
                return True
            except (AttributeError, OSError):
                try:
                    # 方法3: 回退到 Windows Vista 及以上的 System DPI Aware
                    ctypes.windll.user32.SetProcessDPIAware()
                    return True
                except (AttributeError, OSError):
                    print("警告: 无法设置 DPI 感知，在高分屏上界面可能模糊")
                    return False
    
    def initialize_scaling(self, root: tk.Tk) -> None:
        """
        初始化缩放因子
        
        Args:
            root: Tkinter 根窗口
        """
        # 获取系统DPI设置
        system_scaling_factor = self._get_system_dpi_scaling()
        
        # 固定缩放因子为 1.0
        self._scaling_factor = 1.0
        
        # 计算 DPI（默认 DPI 为 96）
        self._dpi = int(96 * self._scaling_factor)
        
        print(f"DPI 适配信息:")
        print(f"  系统缩放因子: {system_scaling_factor:.2f}")
        print(f"  实际使用缩放因子: {self._scaling_factor:.2f}")
        print(f"  DPI: {self._dpi}")
        print(f"  基础字体大小: {self._base_font_size}")
    
    def _get_system_dpi_scaling(self) -> float:
        """
        获取系统DPI缩放因子
        
        Returns:
            float: 系统DPI缩放因子
        """
        if sys.platform != "win32":
            return 1.0
        
        try:
            # 方法1: 使用 GetDpiForSystem (Windows 10+)
            try:
                system_dpi = ctypes.windll.user32.GetDpiForSystem()
                scaling_factor = system_dpi / 96.0
                print(f"  使用 GetDpiForSystem: {system_dpi} DPI")
                return scaling_factor
            except (AttributeError, OSError):
                pass
            
            # 方法2: 使用 GetDeviceCaps (Windows 7+)
            try:
                hdc = ctypes.windll.user32.GetDC(0)
                if hdc:
                    dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
                    ctypes.windll.user32.ReleaseDC(0, hdc)
                    scaling_factor = dpi_x / 96.0
                    print(f"  使用 GetDeviceCaps: {dpi_x} DPI")
                    return scaling_factor
            except (AttributeError, OSError):
                pass
            
            # 方法3: 使用注册表获取DPI设置
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Control Panel\Desktop\WindowMetrics")
                try:
                    # 获取 AppliedDPI 值
                    applied_dpi, _ = winreg.QueryValueEx(key, "AppliedDPI")
                    scaling_factor = applied_dpi / 96.0
                    print(f"  使用注册表 AppliedDPI: {applied_dpi} DPI")
                    return scaling_factor
                except FileNotFoundError:
                    pass
                finally:
                    winreg.CloseKey(key)
            except (ImportError, OSError):
                pass
            
            print("  警告: 无法获取系统DPI设置，使用默认值")
            return 1.0
            
        except Exception as e:
            print(f"  警告: 获取系统DPI失败: {e}")
            return 1.0
    
    def get_scaling_factor(self) -> float:
        """获取当前缩放因子"""
        return self._scaling_factor
    
    def get_dpi(self) -> int:
        """获取当前 DPI"""
        return self._dpi
    
    def scale_size(self, size: int) -> int:
        """
        根据缩放因子调整尺寸
        
        Args:
            size: 基础尺寸
            
        Returns:
            int: 调整后的尺寸
        """
        return max(1, int(size * self._scaling_factor))
    
    def get_font(self, size: int = None, weight: str = "normal", family: str = None) -> Tuple[str, int, str]:
        """
        获取适配 DPI 的字体
        
        Args:
            size: 字体大小（如果为 None，使用基础字体大小）
            weight: 字体粗细 ("normal", "bold")
            family: 字体族（如果为 None，使用默认字体）
            
        Returns:
            Tuple[str, int, str]: (字体族, 字体大小, 字体粗细)
        """
        if size is None:
            size = self._base_font_size
        if family is None:
            family = self._font_family
        
        # 缓存键
        cache_key = (family, size, weight)
        
        if cache_key not in self._font_cache:
            scaled_size = self.scale_size(size)
            self._font_cache[cache_key] = (family, scaled_size, weight)
        
        return self._font_cache[cache_key]
    
    def get_window_size(self, base_width: int, base_height: int) -> Tuple[int, int]:
        """
        获取适配 DPI 的窗口大小
        
        Args:
            base_width: 基础宽度
            base_height: 基础高度
            
        Returns:
            Tuple[int, int]: (宽度, 高度)
        """
        # 对于窗口大小，使用稍微保守的缩放策略
        # 避免在高 DPI 下窗口过大
        conservative_factor = min(self._scaling_factor, 1.5)
        
        width = int(base_width * conservative_factor)
        height = int(base_height * conservative_factor)
        
        return width, height
    
    def get_widget_config(self, widget_type: str) -> Dict[str, Any]:
        """
        获取特定控件的配置参数
        
        Args:
            widget_type: 控件类型
            
        Returns:
            Dict[str, Any]: 控件配置字典
        """
        configs = {
            "title": {
                "font": self.get_font(18, "bold"),
                "pady": self.scale_size(20)
            },
            "subtitle": {
                "font": self.get_font(14, "bold"),
                "pady": self.scale_size(15)
            },
            "label": {
                "font": self.get_font(10),
                "pady": self.scale_size(5)
            },
            "text": {
                "font": self.get_font(9),
                "pady": self.scale_size(5)
            },
            "entry": {
                "font": self.get_font(9),
                "width": self.scale_size(25)
            },
            "button": {
                "font": self.get_font(9),
                "width": self.scale_size(12),
                "pady": self.scale_size(5)
            },
            "status": {
                "font": self.get_font(8),
                "pady": self.scale_size(2)
            },
            "code": {
                "font": ("Consolas", self.scale_size(9)),
                "pady": self.scale_size(5)
            }
        }
        
        return configs.get(widget_type, {})
    
    def configure_widget_dpi(self, widget: tk.Widget, widget_type: str) -> None:
        """
        为控件配置 DPI 适配参数
        
        Args:
            widget: Tkinter 控件
            widget_type: 控件类型
        """
        config = self.get_widget_config(widget_type)
        if config:
            try:
                widget.configure(**config)
            except Exception as e:
                print(f"警告: 无法配置控件 {widget_type}: {e}")
    
    def get_padding(self, size: int) -> int:
        """获取适配 DPI 的内边距"""
        return self.scale_size(size)
    
    def get_geometry_string(self, width: int, height: int, x: int = None, y: int = None) -> str:
        """
        获取适配 DPI 的窗口几何字符串
        
        Args:
            width: 窗口宽度
            height: 窗口高度
            x: 窗口 x 坐标（可选）
            y: 窗口 y 坐标（可选）
            
        Returns:
            str: 几何字符串
        """
        scaled_width, scaled_height = self.get_window_size(width, height)
        
        if x is not None and y is not None:
            scaled_x = self.scale_size(x)
            scaled_y = self.scale_size(y)
            return f"{scaled_width}x{scaled_height}+{scaled_x}+{scaled_y}"
        else:
            return f"{scaled_width}x{scaled_height}"
    
    def center_window(self, window: tk.Tk, width: int, height: int) -> None:
        """
        将窗口居中显示
        
        Args:
            window: Tkinter 窗口
            width: 窗口宽度
            height: 窗口高度
        """
        scaled_width, scaled_height = self.get_window_size(width, height)
        
        # 获取屏幕尺寸
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - scaled_width) // 2
        y = (screen_height - scaled_height) // 2
        
        window.geometry(f"{scaled_width}x{scaled_height}+{x}+{y}")


# 全局实例
ui_helper = UIHelper() 