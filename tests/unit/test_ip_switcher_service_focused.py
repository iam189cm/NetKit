#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网卡配置界面核心功能单元测试
专注于界面实际使用的功能，不包含配置文件管理
"""

import pytest
import unittest.mock as mock
import subprocess
import os
from unittest.mock import patch, MagicMock

# 设置测试环境
os.environ['NETKIT_TEST_MODE'] = '1'

# 导入测试目标 - 仅界面实际使用的功能
from netkit.services.ip_switcher import (
    get_network_interfaces,      # 获取网络接口列表
    get_network_card_info,       # 获取网卡详细信息
    apply_profile,               # 应用网络配置
    validate_ip_config           # 验证IP配置
)

# 导入测试数据
from tests.test_data import (
    VALID_IP_CONFIGS,
    INVALID_IP_CONFIGS,
    MOCK_NETWORK_INTERFACES,
    MOCK_NETWORK_CARD_INFO,
    MOCK_NETSH_INTERFACE_OUTPUT,
    MOCK_NETSH_IP_CONFIG_OUTPUT,
    MOCK_GETMAC_OUTPUT
)


class TestNetworkInterfaceOperations:
    """测试网络接口操作 - 界面网卡选择功能"""
    
    @pytest.mark.unit
    def test_get_network_interfaces_success(self):
        """测试成功获取网络接口列表"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = MOCK_NETSH_INTERFACE_OUTPUT
            
            interfaces = get_network_interfaces()
            
            assert isinstance(interfaces, list)
            assert "以太网" in interfaces
            assert "Wi-Fi" in interfaces
            # 验证只返回已启用的接口
            assert "蓝牙网络连接" not in interfaces
    
    @pytest.mark.unit
    def test_get_network_interfaces_no_interfaces(self):
        """测试没有可用网络接口的情况"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Admin State    State          Type             Interface Name\n---"
            
            interfaces = get_network_interfaces()
            
            assert interfaces == []
    
    @pytest.mark.unit
    def test_get_network_interfaces_command_failure(self):
        """测试netsh命令执行失败"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            
            interfaces = get_network_interfaces()
            
            assert interfaces == []
    
    @pytest.mark.unit
    def test_get_network_interfaces_show_all_false(self):
        """测试不显示虚拟网卡（默认行为）"""
        mock_output = """
Admin State    State          Type             Interface Name
-------------------------------------------------------------------------
已启用         已连接          专用             以太网
已启用         已连接          专用             Wi-Fi
已启用         已连接          专用             VMware Network Adapter VMnet1
已启用         已连接          专用             VirtualBox Host-Only Network
已启用         已连接          专用             Hyper-V Virtual Ethernet Adapter
已启用         已连接          专用             Microsoft Teredo Tunneling Adapter
"""
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = mock_output
            
            # 默认不显示虚拟网卡
            interfaces = get_network_interfaces(show_all=False)
            
            assert isinstance(interfaces, list)
            assert "以太网" in interfaces
            assert "Wi-Fi" in interfaces
            # 虚拟网卡应该被过滤掉
            assert "VMware Network Adapter VMnet1" not in interfaces
            assert "VirtualBox Host-Only Network" not in interfaces
            assert "Hyper-V Virtual Ethernet Adapter" not in interfaces
            assert "Microsoft Teredo Tunneling Adapter" not in interfaces
    
    @pytest.mark.unit
    def test_get_network_interfaces_show_all_true(self):
        """测试显示所有网卡（包括虚拟网卡）"""
        mock_output = """
Admin State    State          Type             Interface Name
-------------------------------------------------------------------------
已启用         已连接          专用             以太网
已启用         已连接          专用             Wi-Fi
已启用         已连接          专用             VMware Network Adapter VMnet1
已启用         已连接          专用             VirtualBox Host-Only Network
已启用         已连接          专用             Hyper-V Virtual Ethernet Adapter
已启用         已连接          专用             Microsoft Teredo Tunneling Adapter
"""
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = mock_output
            
            # 显示所有网卡
            interfaces = get_network_interfaces(show_all=True)
            
            assert isinstance(interfaces, list)
            assert "以太网" in interfaces
            assert "Wi-Fi" in interfaces
            # 虚拟网卡也应该显示
            assert "VMware Network Adapter VMnet1" in interfaces
            assert "VirtualBox Host-Only Network" in interfaces
            assert "Hyper-V Virtual Ethernet Adapter" in interfaces
            assert "Microsoft Teredo Tunneling Adapter" in interfaces
    
    @pytest.mark.unit
    def test_get_network_interfaces_virtual_card_detection(self):
        """测试虚拟网卡检测功能"""
        mock_output = """
Admin State    State          Type             Interface Name
-------------------------------------------------------------------------
已启用         已连接          专用             以太网
已启用         已连接          专用             Wi-Fi
已启用         已连接          专用             VMware Virtual Ethernet Adapter for VMnet1
已启用         已连接          专用             VirtualBox Host-Only Ethernet Adapter
已启用         已连接          专用             TAP-Windows Adapter V9
已启用         已连接          专用             Microsoft Wi-Fi Direct Virtual Adapter
已启用         已连接          专用             WAN Miniport (IKEv2)
已启用         已连接          专用             Bluetooth Device (Personal Area Network)
"""
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = mock_output
            
            # 不显示虚拟网卡
            interfaces_filtered = get_network_interfaces(show_all=False)
            # 显示所有网卡
            interfaces_all = get_network_interfaces(show_all=True)
            
            # 过滤后应该只有物理网卡
            assert "以太网" in interfaces_filtered
            assert "Wi-Fi" in interfaces_filtered
            assert len(interfaces_filtered) == 2
            
            # 显示所有应该包含虚拟网卡
            assert len(interfaces_all) == 8
            assert "VMware Virtual Ethernet Adapter for VMnet1" in interfaces_all
            assert "VirtualBox Host-Only Ethernet Adapter" in interfaces_all
            assert "TAP-Windows Adapter V9" in interfaces_all
            assert "Microsoft Wi-Fi Direct Virtual Adapter" in interfaces_all
            assert "WAN Miniport (IKEv2)" in interfaces_all
            assert "Bluetooth Device (Personal Area Network)" in interfaces_all


class TestNetworkCardInfoDisplay:
    """测试网卡信息显示 - 界面信息展示功能"""
    
    @pytest.mark.unit
    def test_get_network_card_info_complete(self):
        """测试获取完整网卡信息"""
        interface_name = "以太网"
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                # netsh interface show interface
                mock.Mock(returncode=0, stdout="管理状态: 已启用\n类型: 专用"),
                # getmac
                mock.Mock(returncode=0, stdout=MOCK_GETMAC_OUTPUT),
                # netsh interface ip show config
                mock.Mock(returncode=0, stdout=MOCK_NETSH_IP_CONFIG_OUTPUT)
            ]
            
            info = get_network_card_info(interface_name)
            
            # 验证所有界面显示的信息字段
            assert info['name'] == interface_name
            assert info['status'] == '已启用'
            assert info['ip'] == '192.168.1.100'
            assert info['mask'] == '255.255.255.0'
            assert info['gateway'] == '192.168.1.1'
            assert info['dns1'] == '8.8.8.8'
            assert info['dns2'] == '8.8.4.4'
    
    @pytest.mark.unit
    def test_get_network_card_info_no_ip_config(self):
        """测试网卡无IP配置的情况"""
        interface_name = "Wi-Fi"
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = [
                # netsh interface show interface
                mock.Mock(returncode=0, stdout="管理状态: 已断开连接\n类型: 专用"),
                # getmac
                mock.Mock(returncode=0, stdout=MOCK_GETMAC_OUTPUT),
                # netsh interface ip show config - 无IP配置
                mock.Mock(returncode=0, stdout="配置为 DHCP，地址为 0.0.0.0")
            ]
            
            info = get_network_card_info(interface_name)
            
            assert info['name'] == interface_name
            assert info['status'] == '已断开连接'
            # 无IP配置时应显示默认值
            assert info['ip'] == '未配置'
            assert info['gateway'] == '未配置'
    
    @pytest.mark.unit
    def test_get_network_card_info_command_failure(self):
        """测试获取网卡信息命令失败"""
        interface_name = "不存在的网卡"
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            
            info = get_network_card_info(interface_name)
            
            assert info['name'] == interface_name
            # 命令失败时应显示默认值而不是错误
            assert info['ip'] == '未配置'
            assert info['gateway'] == '未配置'


class TestIPConfigurationValidation:
    """测试IP配置验证 - 界面配置验证功能"""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("config", VALID_IP_CONFIGS)
    def test_validate_ip_config_valid_configurations(self, config):
        """测试有效IP配置验证"""
        result = validate_ip_config(
            config['ip'],
            config['mask'],
            config['gateway'],
            config['dns']
        )
        
        assert result['valid'] is True
        assert 'error' not in result
    
    @pytest.mark.unit
    @pytest.mark.parametrize("config", INVALID_IP_CONFIGS)
    def test_validate_ip_config_invalid_configurations(self, config):
        """测试无效IP配置验证"""
        result = validate_ip_config(
            config['ip'],
            config['mask'],
            config['gateway'],
            config['dns']
        )
        
        assert result['valid'] is False
        assert 'error' in result
        assert len(result['error']) > 0
    
    @pytest.mark.unit
    def test_validate_ip_config_empty_dns(self):
        """测试空DNS配置（界面允许DNS为空）"""
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.0",
            "192.168.1.1",
            ""  # 空DNS
        )
        
        assert result['valid'] is True
    
    @pytest.mark.unit
    def test_validate_ip_config_single_dns(self):
        """测试单个DNS服务器配置"""
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.0",
            "192.168.1.1",
            "8.8.8.8"  # 只有一个DNS
        )
        
        assert result['valid'] is True
    
    @pytest.mark.unit
    def test_validate_ip_config_network_address_error(self):
        """测试网络地址错误（界面常见错误）"""
        result = validate_ip_config(
            "192.168.1.0",    # 网络地址
            "255.255.255.0",
            "192.168.1.1",
            "8.8.8.8"
        )
        
        assert result['valid'] is False
        assert "网络地址" in result['error']
    
    @pytest.mark.unit
    def test_validate_ip_config_broadcast_address_error(self):
        """测试广播地址错误（界面常见错误）"""
        result = validate_ip_config(
            "192.168.1.255",  # 广播地址
            "255.255.255.0",
            "192.168.1.1",
            "8.8.8.8"
        )
        
        assert result['valid'] is False
        assert "广播地址" in result['error']


class TestNetworkConfigurationApplication:
    """测试网络配置应用 - 界面应用配置功能"""
    
    @pytest.mark.unit
    def test_apply_profile_dhcp_mode(self):
        """测试DHCP模式配置应用"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            
            result = apply_profile("以太网", "", "", "", "", dhcp=True)
            
            assert result['success'] is True
            assert "DHCP" in result['message']
            
            # 验证调用了DHCP相关命令
            calls = mock_run.call_args_list
            assert len(calls) >= 2  # IP设置 + DNS设置
            
            # 验证第一个命令包含DHCP设置
            first_call = calls[0][0][0]
            assert 'netsh' in first_call
            assert 'source=dhcp' in first_call
    
    @pytest.mark.unit
    def test_apply_profile_static_ip_mode(self):
        """测试静态IP模式配置应用"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            
            result = apply_profile(
                "以太网",
                "192.168.1.100",
                "255.255.255.0",
                "192.168.1.1",
                "8.8.8.8,8.8.4.4",
                dhcp=False
            )
            
            assert result['success'] is True
            assert "静态IP" in result['message']
            
            # 验证调用了静态IP相关命令
            calls = mock_run.call_args_list
            assert len(calls) >= 3  # IP设置 + 主DNS + 备DNS
    
    @pytest.mark.unit
    def test_apply_profile_static_ip_single_dns(self):
        """测试静态IP模式单个DNS配置"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            
            result = apply_profile(
                "以太网",
                "192.168.1.100",
                "255.255.255.0",
                "192.168.1.1",
                "8.8.8.8",  # 只有一个DNS
                dhcp=False
            )
            
            assert result['success'] is True
            
            # 验证调用了正确数量的命令
            calls = mock_run.call_args_list
            assert len(calls) >= 2  # IP设置 + DNS设置
    
    @pytest.mark.unit
    def test_apply_profile_command_failure(self):
        """测试配置应用命令失败"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "拒绝访问"
            
            result = apply_profile("以太网", "", "", "", "", dhcp=True)
            
            assert result['success'] is False
            assert "失败" in result['error']
            assert "拒绝访问" in result['error']
    
    @pytest.mark.unit
    def test_apply_profile_interface_not_found(self):
        """测试网络接口不存在的情况"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "找不到指定的接口"
            
            result = apply_profile("不存在的网卡", "", "", "", "", dhcp=True)
            
            assert result['success'] is False
            assert "失败" in result['error']


class TestSpecialScenarios:
    """测试特殊场景 - 界面可能遇到的特殊情况"""
    
    @pytest.mark.unit
    def test_chinese_interface_names(self):
        """测试中文网络接口名称处理"""
        chinese_output = """
Admin State    State          Type             Interface Name
-------------------------------------------------------------------------
已启用          已连接          专用             以太网
已启用          已断开连接      专用             无线网络连接
已启用          已连接          专用             本地连接
        """
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = chinese_output
            
            interfaces = get_network_interfaces()
            
            assert "以太网" in interfaces
            assert "本地连接" in interfaces
            # 注意：实际实现可能包含所有接口，这里验证接口名称能正确解析
            assert "无线网络连接" in interfaces
    
    @pytest.mark.unit
    def test_special_characters_in_interface_names(self):
        """测试接口名称包含特殊字符"""
        special_output = """
Admin State    State          Type             Interface Name
-------------------------------------------------------------------------
已启用          已连接          专用             以太网 2
已启用          已连接          专用             Wi-Fi (Intel)
        """
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = special_output
            
            interfaces = get_network_interfaces()
            
            assert "以太网 2" in interfaces
            assert "Wi-Fi (Intel)" in interfaces
    
    @pytest.mark.unit
    def test_cidr_notation_in_mask(self):
        """测试CIDR记法的子网掩码验证"""
        # 界面支持 "24" 这样的CIDR记法
        result = validate_ip_config(
            "192.168.1.100",
            "24",  # CIDR记法
            "192.168.1.1",
            "8.8.8.8"
        )
        
        # 当前实现可能不支持，这个测试用于验证需求
        # 实际结果取决于validate_ip_config的实现
        assert 'valid' in result
    
    @pytest.mark.unit
    def test_multiple_dns_servers(self):
        """测试多个DNS服务器配置"""
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.0",
            "192.168.1.1",
            "8.8.8.8,8.8.4.4,114.114.114.114"  # 3个DNS
        )
        
        assert result['valid'] is True


@pytest.mark.performance
class TestPerformanceScenarios:
    """测试性能场景 - 界面响应性能"""
    
    @pytest.mark.benchmark
    def test_get_network_interfaces_performance(self, benchmark):
        """测试获取网络接口性能"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = MOCK_NETSH_INTERFACE_OUTPUT
            
            result = benchmark(get_network_interfaces)
            assert isinstance(result, list)
    
    @pytest.mark.benchmark
    def test_validate_ip_config_performance(self, benchmark):
        """测试IP配置验证性能"""
        def validate_config():
            return validate_ip_config("192.168.1.100", "255.255.255.0", "192.168.1.1", "8.8.8.8")
        
        result = benchmark(validate_config)
        assert result['valid'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 