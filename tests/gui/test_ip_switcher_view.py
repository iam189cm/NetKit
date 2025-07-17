#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网卡配置界面GUI自动化测试
测试 gui.views.ip_switcher_view 模块的界面组件和用户交互
"""

import pytest
import tkinter as tk
import ttkbootstrap as tb
import unittest.mock as mock
import threading
import time
from unittest.mock import patch, MagicMock

# 设置测试环境
import os
os.environ['NETKIT_TEST_MODE'] = '1'

# 导入测试目标
from gui.views.ip_switcher_view import IPSwitcherFrame

# 导入测试数据
from tests.test_data import (
    VALID_IP_CONFIGS,
    INVALID_IP_CONFIGS,
    MOCK_NETWORK_INTERFACES,
    MOCK_NETWORK_CARD_INFO,
    GUI_TEST_DATA
)


class TestIPSwitcherFrameInitialization:
    """测试IPSwitcherFrame初始化"""
    
    @pytest.fixture
    def root_window(self):
        """创建测试用的根窗口"""
        root = tb.Window(themename='darkly')
        root.withdraw()  # 隐藏窗口
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        """创建IPSwitcherFrame实例"""
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.gui
    def test_frame_initialization(self, ip_switcher_frame):
        """测试界面初始化"""
        assert ip_switcher_frame is not None
        assert hasattr(ip_switcher_frame, 'interface_var')
        assert hasattr(ip_switcher_frame, 'interface_combo')
        assert hasattr(ip_switcher_frame, 'dhcp_var')
        assert hasattr(ip_switcher_frame, 'status_text')
    
    @pytest.mark.gui
    def test_ui_components_exist(self, ip_switcher_frame):
        """测试UI组件是否存在"""
        # 测试输入框
        assert hasattr(ip_switcher_frame, 'ip_entry')
        assert hasattr(ip_switcher_frame, 'mask_entry')
        assert hasattr(ip_switcher_frame, 'gateway_entry')
        assert hasattr(ip_switcher_frame, 'dns1_entry')
        assert hasattr(ip_switcher_frame, 'dns2_entry')
        
        # 测试标签
        assert hasattr(ip_switcher_frame, 'name_label')
        assert hasattr(ip_switcher_frame, 'ip_label')
        assert hasattr(ip_switcher_frame, 'gateway_label')
        
        # 测试按钮和复选框
        assert hasattr(ip_switcher_frame, 'dhcp_check')
        assert hasattr(ip_switcher_frame, 'show_all_var')
    
    @pytest.mark.gui
    def test_initial_values(self, ip_switcher_frame):
        """测试初始值"""
        assert ip_switcher_frame.dhcp_var.get() is False
        assert ip_switcher_frame.show_all_var.get() is False
        assert ip_switcher_frame.interface_var.get() == ""


class TestNetworkInterfaceSelection:
    """测试网络接口选择功能"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.gui
    def test_refresh_interfaces_success(self, ip_switcher_frame):
        """测试刷新网络接口成功"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES
            
            ip_switcher_frame.refresh_interfaces()
            
            # 验证下拉框内容
            assert ip_switcher_frame.interface_combo['values'] == tuple(MOCK_NETWORK_INTERFACES)
            assert ip_switcher_frame.interface_combo.current() == 0
    
    @pytest.mark.gui
    def test_refresh_interfaces_empty(self, ip_switcher_frame):
        """测试刷新网络接口为空"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = []
            
            ip_switcher_frame.refresh_interfaces()
            
            assert ip_switcher_frame.interface_combo['values'] == ()
    
    @pytest.mark.gui
    def test_refresh_interfaces_exception(self, ip_switcher_frame):
        """测试刷新网络接口异常"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.side_effect = Exception("Network error")
            
            ip_switcher_frame.refresh_interfaces()
            
            # 应该不会崩溃，只是在状态栏显示错误
            status_content = ip_switcher_frame.status_text.get('1.0', tk.END)
            assert "失败" in status_content
    
    @pytest.mark.gui
    def test_interface_selection_change(self, ip_switcher_frame):
        """测试网络接口选择变化"""
        with patch('netkit.services.ip_switcher.get_network_card_info') as mock_get_info:
            mock_get_info.return_value = MOCK_NETWORK_CARD_INFO["以太网"]
            
            # 模拟选择接口
            ip_switcher_frame.interface_var.set("以太网")
            ip_switcher_frame.on_interface_selected()
            
            # 验证信息显示更新
            assert ip_switcher_frame.name_label.cget('text') == "以太网"
            assert ip_switcher_frame.ip_label.cget('text') == "192.168.1.100"
            assert ip_switcher_frame.gateway_label.cget('text') == "192.168.1.1"
    
    @pytest.mark.gui
    def test_show_all_interfaces_toggle(self, ip_switcher_frame):
        """测试显示所有网卡选项切换"""
        # 模拟网卡数据
        physical_interfaces = ["以太网", "Wi-Fi"]
        all_interfaces = ["以太网", "Wi-Fi", "VMware Network Adapter VMnet1", "VirtualBox Host-Only Network"]
        
        with patch('gui.views.ip_switcher_view.get_network_interfaces') as mock_get_interfaces:
            # 测试默认状态（不显示虚拟网卡）
            mock_get_interfaces.return_value = physical_interfaces
            ip_switcher_frame.show_all_var.set(False)
            ip_switcher_frame.refresh_interfaces()
            
            # 验证调用参数
            mock_get_interfaces.assert_called_with(show_all=False)
            assert ip_switcher_frame.interface_combo['values'] == tuple(physical_interfaces)
            
            # 测试勾选显示所有网卡
            mock_get_interfaces.return_value = all_interfaces
            ip_switcher_frame.show_all_var.set(True)
            ip_switcher_frame.refresh_interfaces()
            
            # 验证调用参数
            mock_get_interfaces.assert_called_with(show_all=True)
            assert ip_switcher_frame.interface_combo['values'] == tuple(all_interfaces)
            
            # 验证状态栏消息
            status_content = ip_switcher_frame.status_text.get('1.0', tk.END)
            assert "所有网络接口" in status_content
    
    @pytest.mark.gui
    def test_show_all_interfaces_default_state(self, ip_switcher_frame):
        """测试显示所有网卡复选框默认状态"""
        # 验证默认状态为不勾选
        assert ip_switcher_frame.show_all_var.get() == False


class TestUserInput:
    """测试用户输入功能"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.gui
    def test_entry_focus_in_out(self, ip_switcher_frame):
        """测试输入框焦点事件"""
        entry = ip_switcher_frame.ip_entry
        placeholder = "例如: 192.168.1.100"
        
        # 初始状态应该有占位符
        assert entry.get() == placeholder
        
        # 模拟获得焦点
        event = MagicMock()
        event.widget = entry
        ip_switcher_frame.on_entry_focus_in(event, placeholder)
        
        # 占位符应该被清除
        assert entry.get() == ""
        
        # 模拟失去焦点（无内容）
        ip_switcher_frame.on_entry_focus_out(event, placeholder)
        
        # 占位符应该恢复
        assert entry.get() == placeholder
    
    @pytest.mark.gui
    def test_dhcp_toggle(self, ip_switcher_frame):
        """测试DHCP切换"""
        # 初始状态：静态IP模式
        assert ip_switcher_frame.dhcp_var.get() is False
        assert ip_switcher_frame.ip_entry.cget('state') == 'normal'
        
        # 切换到DHCP模式
        ip_switcher_frame.dhcp_var.set(True)
        ip_switcher_frame.on_dhcp_changed()
        
        # 输入框应该被禁用
        assert ip_switcher_frame.ip_entry.cget('state') == 'disabled'
        assert ip_switcher_frame.mask_entry.cget('state') == 'disabled'
        assert ip_switcher_frame.gateway_entry.cget('state') == 'disabled'
        
        # 切换回静态IP模式
        ip_switcher_frame.dhcp_var.set(False)
        ip_switcher_frame.on_dhcp_changed()
        
        # 输入框应该被启用
        assert ip_switcher_frame.ip_entry.cget('state') == 'normal'
        assert ip_switcher_frame.mask_entry.cget('state') == 'normal'
        assert ip_switcher_frame.gateway_entry.cget('state') == 'normal'
    
    @pytest.mark.gui
    def test_get_entry_value(self, ip_switcher_frame):
        """测试获取输入框值"""
        entry = ip_switcher_frame.ip_entry
        placeholder = "例如: 192.168.1.100"
        
        # 测试占位符情况
        entry.delete(0, tk.END)
        entry.insert(0, placeholder)
        value = ip_switcher_frame.get_entry_value(entry, placeholder)
        assert value == ""
        
        # 测试实际值
        entry.delete(0, tk.END)
        entry.insert(0, "192.168.1.100")
        value = ip_switcher_frame.get_entry_value(entry, placeholder)
        assert value == "192.168.1.100"
        
        # 测试空值
        entry.delete(0, tk.END)
        value = ip_switcher_frame.get_entry_value(entry, placeholder)
        assert value == ""


class TestConfigurationApplication:
    """测试配置应用功能"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.gui
    def test_apply_dhcp_config(self, ip_switcher_frame):
        """测试应用DHCP配置"""
        with patch('netkit.services.ip_switcher.apply_profile') as mock_apply:
            mock_apply.return_value = {'success': True}
            
            # 设置DHCP模式
            ip_switcher_frame.interface_var.set("以太网")
            ip_switcher_frame.dhcp_var.set(True)
            
            ip_switcher_frame.apply_config()
            
            # 验证调用参数
            mock_apply.assert_called_once_with("以太网", "", "", "", "", dhcp=True)
    
    @pytest.mark.gui
    def test_apply_static_config_success(self, ip_switcher_frame):
        """测试应用静态IP配置成功"""
        with patch('netkit.services.ip_switcher.apply_profile') as mock_apply:
            with patch('netkit.services.ip_switcher.validate_ip_config') as mock_validate:
                mock_apply.return_value = {'success': True}
                mock_validate.return_value = {'valid': True}
                
                # 设置静态IP模式和输入值
                ip_switcher_frame.interface_var.set("以太网")
                ip_switcher_frame.dhcp_var.set(False)
                
                # 清除占位符并设置实际值
                for entry, value in [
                    (ip_switcher_frame.ip_entry, "192.168.1.100"),
                    (ip_switcher_frame.mask_entry, "255.255.255.0"),
                    (ip_switcher_frame.gateway_entry, "192.168.1.1"),
                    (ip_switcher_frame.dns1_entry, "8.8.8.8"),
                    (ip_switcher_frame.dns2_entry, "8.8.4.4")
                ]:
                    entry.delete(0, tk.END)
                    entry.insert(0, value)
                
                ip_switcher_frame.apply_config()
                
                # 验证调用参数
                mock_apply.assert_called_once_with(
                    "以太网",
                    "192.168.1.100",
                    "255.255.255.0",
                    "192.168.1.1",
                    "8.8.8.8,8.8.4.4",
                    dhcp=False
                )
    
    @pytest.mark.gui
    def test_apply_config_validation_failure(self, ip_switcher_frame):
        """测试配置验证失败"""
        with patch('netkit.services.ip_switcher.validate_ip_config') as mock_validate:
            mock_validate.return_value = {'valid': False, 'error': '配置无效'}
            
            # 设置静态IP模式和无效输入
            ip_switcher_frame.interface_var.set("以太网")
            ip_switcher_frame.dhcp_var.set(False)
            
            for entry, value in [
                (ip_switcher_frame.ip_entry, "256.256.256.256"),
                (ip_switcher_frame.mask_entry, "255.255.255.0"),
                (ip_switcher_frame.gateway_entry, "192.168.1.1")
            ]:
                entry.delete(0, tk.END)
                entry.insert(0, value)
            
            ip_switcher_frame.apply_config()
            
            # 验证错误消息显示
            status_content = ip_switcher_frame.status_text.get('1.0', tk.END)
            assert "验证失败" in status_content
    
    @pytest.mark.gui
    def test_apply_config_no_interface(self, ip_switcher_frame):
        """测试未选择网络接口"""
        ip_switcher_frame.interface_var.set("")
        ip_switcher_frame.apply_config()
        
        # 验证错误消息
        status_content = ip_switcher_frame.status_text.get('1.0', tk.END)
        assert "请选择网络接口" in status_content
    
    @pytest.mark.gui
    def test_apply_config_incomplete_fields(self, ip_switcher_frame):
        """测试字段不完整"""
        ip_switcher_frame.interface_var.set("以太网")
        ip_switcher_frame.dhcp_var.set(False)
        
        # 只设置部分字段
        ip_switcher_frame.ip_entry.delete(0, tk.END)
        ip_switcher_frame.ip_entry.insert(0, "192.168.1.100")
        
        ip_switcher_frame.apply_config()
        
        # 验证错误消息
        status_content = ip_switcher_frame.status_text.get('1.0', tk.END)
        assert "完整填写" in status_content


class TestStatusDisplay:
    """测试状态显示功能"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.gui
    def test_append_status(self, ip_switcher_frame):
        """测试状态消息追加"""
        initial_content = ip_switcher_frame.status_text.get('1.0', tk.END)
        
        ip_switcher_frame.append_status("测试消息\n")
        
        new_content = ip_switcher_frame.status_text.get('1.0', tk.END)
        assert "测试消息" in new_content
        assert len(new_content) > len(initial_content)
    
    @pytest.mark.gui
    def test_status_text_readonly(self, ip_switcher_frame):
        """测试状态文本框只读"""
        # 状态文本框应该是禁用状态（只读）
        assert ip_switcher_frame.status_text.cget('state') == 'disabled'


class TestGUIInteractionSequences:
    """测试GUI交互序列"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.gui
    @pytest.mark.parametrize("sequence", GUI_TEST_DATA["input_sequences"])
    def test_input_sequences(self, ip_switcher_frame, sequence):
        """测试输入序列"""
        for field_name, value in sequence["steps"]:
            if field_name == "dhcp_check":
                ip_switcher_frame.dhcp_var.set(value)
                ip_switcher_frame.on_dhcp_changed()
            elif field_name.endswith("_entry"):
                entry = getattr(ip_switcher_frame, field_name)
                entry.delete(0, tk.END)
                entry.insert(0, str(value))
        
        # 验证输入序列没有导致异常
        assert True
    
    @pytest.mark.gui
    def test_complete_configuration_workflow(self, ip_switcher_frame):
        """测试完整配置工作流"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            with patch('netkit.services.ip_switcher.get_network_card_info') as mock_get_info:
                with patch('netkit.services.ip_switcher.apply_profile') as mock_apply:
                    with patch('netkit.services.ip_switcher.validate_ip_config') as mock_validate:
                        # 设置模拟返回值
                        mock_get_interfaces.return_value = ["以太网"]
                        mock_get_info.return_value = MOCK_NETWORK_CARD_INFO["以太网"]
                        mock_apply.return_value = {'success': True}
                        mock_validate.return_value = {'valid': True}
                        
                        # 1. 刷新网络接口
                        ip_switcher_frame.refresh_interfaces()
                        
                        # 2. 选择网络接口
                        ip_switcher_frame.interface_var.set("以太网")
                        ip_switcher_frame.on_interface_selected()
                        
                        # 3. 配置静态IP
                        ip_switcher_frame.dhcp_var.set(False)
                        ip_switcher_frame.on_dhcp_changed()
                        
                        # 4. 输入配置信息
                        config = VALID_IP_CONFIGS[0]
                        for entry, value in [
                            (ip_switcher_frame.ip_entry, config['ip']),
                            (ip_switcher_frame.mask_entry, config['mask']),
                            (ip_switcher_frame.gateway_entry, config['gateway']),
                            (ip_switcher_frame.dns1_entry, "8.8.8.8"),
                            (ip_switcher_frame.dns2_entry, "8.8.4.4")
                        ]:
                            entry.delete(0, tk.END)
                            entry.insert(0, value)
                        
                        # 5. 应用配置
                        ip_switcher_frame.apply_config()
                        
                        # 验证所有步骤都执行成功
                        mock_get_interfaces.assert_called()
                        mock_get_info.assert_called()
                        mock_validate.assert_called()
                        mock_apply.assert_called()


@pytest.mark.performance
class TestGUIPerformance:
    """GUI性能测试"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.benchmark
    def test_frame_creation_performance(self, benchmark, root_window):
        """测试界面创建性能"""
        def create_frame():
            frame = IPSwitcherFrame(root_window)
            return frame
        
        frame = benchmark(create_frame)
        assert frame is not None
    
    @pytest.mark.benchmark
    def test_interface_refresh_performance(self, benchmark, ip_switcher_frame):
        """测试接口刷新性能"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = MOCK_NETWORK_INTERFACES * 10  # 模拟大量接口
            
            def refresh_interfaces():
                ip_switcher_frame.refresh_interfaces()
            
            benchmark(refresh_interfaces)
    
    @pytest.mark.slow
    def test_gui_responsiveness(self, ip_switcher_frame):
        """测试GUI响应性"""
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            # 模拟慢速网络调用
            def slow_get_interfaces():
                time.sleep(0.1)  # 模拟100ms延迟
                return MOCK_NETWORK_INTERFACES
            
            mock_get_interfaces.side_effect = slow_get_interfaces
            
            start_time = time.time()
            ip_switcher_frame.refresh_interfaces()
            end_time = time.time()
            
            # 验证操作在合理时间内完成
            assert end_time - start_time < 1.0  # 1秒内完成


@pytest.mark.windows
class TestWindowsSpecific:
    """Windows特定测试"""
    
    @pytest.fixture
    def root_window(self):
        root = tb.Window(themename='darkly')
        root.withdraw()
        yield root
        root.destroy()
    
    @pytest.fixture
    def ip_switcher_frame(self, root_window):
        frame = IPSwitcherFrame(root_window)
        return frame
    
    @pytest.mark.gui
    def test_chinese_interface_names(self, ip_switcher_frame):
        """测试中文网络接口名称"""
        chinese_interfaces = ["以太网", "无线网络连接", "本地连接"]
        
        with patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.return_value = chinese_interfaces
            
            ip_switcher_frame.refresh_interfaces()
            
            # 验证中文接口名称正确显示
            assert ip_switcher_frame.interface_combo['values'] == tuple(chinese_interfaces)
    
    @pytest.mark.gui
    def test_font_rendering(self, ip_switcher_frame):
        """测试字体渲染"""
        # 验证使用了Microsoft YaHei字体
        title_font = ip_switcher_frame.winfo_children()[0].cget('font')
        assert 'Microsoft YaHei' in str(title_font)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 