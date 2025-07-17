#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网卡配置服务单元测试
测试 netkit.services.ip_switcher 模块的所有功能
"""

import pytest
import unittest.mock as mock
import subprocess
import json
import os
from pathlib import Path

# 导入测试目标
from netkit.services.ip_switcher import (
    get_network_interfaces,
    get_network_card_info,
    apply_profile,
    validate_ip_config,
    save_profile,
    load_profiles,
    delete_profile,
    check_network_conflict,
    suggest_ip_config,
    get_interface_config,
    get_config_dir
)

# 导入测试数据
from tests.test_data import (
    VALID_IP_CONFIGS,
    INVALID_IP_CONFIGS,
    MOCK_NETWORK_INTERFACES,
    MOCK_NETSH_INTERFACE_OUTPUT,
    MOCK_NETWORK_CARD_INFO,
    MOCK_NETSH_IP_CONFIG_OUTPUT,
    MOCK_GETMAC_OUTPUT,
    ERROR_SCENARIOS
)


class TestNetworkInterfaceOperations:
    """测试网络接口相关操作"""
    
    @pytest.mark.unit
    def test_get_network_interfaces_success(self):
        """测试成功获取网络接口列表"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = MOCK_NETSH_INTERFACE_OUTPUT
            
            interfaces = get_network_interfaces()
            
            assert isinstance(interfaces, list)
            assert "以太网" in interfaces
            assert "Wi-Fi" in interfaces
            assert "蓝牙网络连接" not in interfaces  # 已禁用的不应该包含
            
            # 验证调用参数
            mock_run.assert_called_once_with(
                ['netsh', 'interface', 'show', 'interface'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
    
    @pytest.mark.unit
    def test_get_network_interfaces_command_failure(self):
        """测试命令执行失败的情况"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            
            interfaces = get_network_interfaces()
            
            assert interfaces == []
    
    @pytest.mark.unit
    def test_get_network_interfaces_empty_output(self):
        """测试空输出的情况"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = ""
            
            interfaces = get_network_interfaces()
            
            assert interfaces == []
    
    @pytest.mark.unit
    def test_get_network_interfaces_exception(self):
        """测试异常情况"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Command failed")
            
            interfaces = get_network_interfaces()
            
            assert interfaces == []


class TestNetworkCardInfo:
    """测试网卡详细信息获取"""
    
    @pytest.mark.unit
    def test_get_network_card_info_success(self):
        """测试成功获取网卡信息"""
        interface_name = "以太网"
        
        with mock.patch('subprocess.run') as mock_run:
            # 模拟三个不同的命令调用
            mock_run.side_effect = [
                # netsh interface show interface
                mock.Mock(returncode=0, stdout="管理状态: 已启用\n类型: 专用"),
                # getmac
                mock.Mock(returncode=0, stdout=MOCK_GETMAC_OUTPUT),
                # netsh interface ip show config
                mock.Mock(returncode=0, stdout=MOCK_NETSH_IP_CONFIG_OUTPUT)
            ]
            
            info = get_network_card_info(interface_name)
            
            assert info['name'] == interface_name
            assert info['status'] == '已启用'
            assert info['ip'] == '192.168.1.100'
            assert info['mask'] == '255.255.255.0'
            assert info['gateway'] == '192.168.1.1'
            assert info['dns1'] == '8.8.8.8'
            assert info['dns2'] == '8.8.4.4'
    
    @pytest.mark.unit
    def test_get_network_card_info_command_failure(self):
        """测试命令执行失败"""
        interface_name = "不存在的网卡"
        
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stdout = ""
            
            info = get_network_card_info(interface_name)
            
            assert info['name'] == interface_name
            assert info['status'] == '获取失败'
            assert info['ip'] == '获取失败'
    
    @pytest.mark.unit
    def test_get_network_card_info_exception(self):
        """测试异常情况"""
        interface_name = "测试网卡"
        
        with mock.patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Command failed")
            
            info = get_network_card_info(interface_name)
            
            assert info['name'] == interface_name
            assert all(value == '获取失败' for key, value in info.items() if key != 'name')


class TestIPConfigValidation:
    """测试IP配置验证"""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("config", VALID_IP_CONFIGS)
    def test_validate_ip_config_valid(self, config):
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
    def test_validate_ip_config_invalid(self, config):
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
    def test_validate_ip_config_with_warnings(self):
        """测试带警告的配置"""
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.252",  # /30 网络，主机数很少
            "192.168.1.101",
            "8.8.8.8"
        )
        
        assert result['valid'] is True
        assert 'warnings' in result
        assert len(result['warnings']) > 0
    
    @pytest.mark.unit
    def test_validate_ip_config_dns_validation(self):
        """测试DNS服务器验证"""
        # 测试无效DNS
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.0",
            "192.168.1.1",
            "256.256.256.256"
        )
        
        assert result['valid'] is False
        assert 'DNS' in result['error']
    
    @pytest.mark.unit
    def test_validate_ip_config_empty_dns(self):
        """测试空DNS配置"""
        result = validate_ip_config(
            "192.168.1.100",
            "255.255.255.0",
            "192.168.1.1",
            ""
        )
        
        assert result['valid'] is True


class TestProfileManagement:
    """测试配置文件管理"""
    
    @pytest.fixture
    def temp_config_dir(self, tmp_path):
        """创建临时配置目录"""
        config_dir = tmp_path / ".netkit_py"
        config_dir.mkdir()
        return config_dir
    
    @pytest.mark.unit
    def test_save_profile_success(self, temp_config_dir):
        """测试保存配置文件成功"""
        with mock.patch('netkit.services.ip_switcher.get_config_dir') as mock_get_config_dir:
            mock_get_config_dir.return_value = temp_config_dir
            
            result = save_profile(
                "测试配置",
                "以太网",
                "192.168.1.100",
                "255.255.255.0",
                "192.168.1.1",
                "8.8.8.8"
            )
            
            assert result['success'] is True
            assert "已保存" in result['message']
            
            # 验证文件是否创建
            profiles_file = temp_config_dir / 'ip_profiles.json'
            assert profiles_file.exists()
            
            # 验证内容
            with open(profiles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert "测试配置" in data
                assert data["测试配置"]["ip"] == "192.168.1.100"
    
    @pytest.mark.unit
    def test_load_profiles_success(self, temp_config_dir):
        """测试加载配置文件成功"""
        # 创建测试配置文件
        profiles_file = temp_config_dir / 'ip_profiles.json'
        test_data = {
            "测试配置": {
                "interface": "以太网",
                "ip": "192.168.1.100",
                "mask": "255.255.255.0",
                "gateway": "192.168.1.1",
                "dns": "8.8.8.8"
            }
        }
        
        with open(profiles_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        with mock.patch('netkit.services.ip_switcher.get_config_dir') as mock_get_config_dir:
            mock_get_config_dir.return_value = temp_config_dir
            
            profiles = load_profiles()
            
            assert "测试配置" in profiles
            assert profiles["测试配置"]["ip"] == "192.168.1.100"
    
    @pytest.mark.unit
    def test_load_profiles_file_not_exists(self, temp_config_dir):
        """测试配置文件不存在的情况"""
        with mock.patch('netkit.services.ip_switcher.get_config_dir') as mock_get_config_dir:
            mock_get_config_dir.return_value = temp_config_dir
            
            profiles = load_profiles()
            
            assert profiles == {}
    
    @pytest.mark.unit
    def test_delete_profile_success(self, temp_config_dir):
        """测试删除配置文件成功"""
        # 创建测试配置文件
        profiles_file = temp_config_dir / 'ip_profiles.json'
        test_data = {
            "测试配置1": {"ip": "192.168.1.100"},
            "测试配置2": {"ip": "192.168.1.101"}
        }
        
        with open(profiles_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        with mock.patch('netkit.services.ip_switcher.get_config_dir') as mock_get_config_dir:
            mock_get_config_dir.return_value = temp_config_dir
            
            result = delete_profile("测试配置1")
            
            assert result['success'] is True
            assert "已删除" in result['message']
            
            # 验证文件内容
            with open(profiles_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert "测试配置1" not in data
                assert "测试配置2" in data
    
    @pytest.mark.unit
    def test_delete_profile_not_exists(self, temp_config_dir):
        """测试删除不存在的配置"""
        profiles_file = temp_config_dir / 'ip_profiles.json'
        test_data = {}
        
        with open(profiles_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        with mock.patch('netkit.services.ip_switcher.get_config_dir') as mock_get_config_dir:
            mock_get_config_dir.return_value = temp_config_dir
            
            result = delete_profile("不存在的配置")
            
            assert result['success'] is False
            assert "不存在" in result['error']


class TestApplyProfile:
    """测试应用配置"""
    
    @pytest.mark.unit
    def test_apply_profile_dhcp_success(self):
        """测试DHCP配置应用成功"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = apply_profile("以太网", "", "", "", "", dhcp=True)
            
            assert result['success'] is True
            assert "DHCP" in result['message']
            
            # 验证调用了正确的命令
            calls = mock_run.call_args_list
            assert len(calls) == 2  # DHCP IP 和 DNS 命令
            
            # 验证第一个命令是设置DHCP
            first_call = calls[0][0][0]
            assert 'netsh' in first_call
            assert 'source=dhcp' in first_call
    
    @pytest.mark.unit
    def test_apply_profile_static_success(self):
        """测试静态IP配置应用成功"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
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
            
            # 验证调用了正确的命令
            calls = mock_run.call_args_list
            assert len(calls) == 3  # IP设置 + 2个DNS设置
    
    @pytest.mark.unit
    def test_apply_profile_command_failure(self):
        """测试命令执行失败"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "参数不正确"
            
            result = apply_profile("以太网", "", "", "", "", dhcp=True)
            
            assert result['success'] is False
            assert "失败" in result['error']
    
    @pytest.mark.unit
    def test_apply_profile_exception(self):
        """测试异常情况"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Command failed")
            
            result = apply_profile("以太网", "", "", "", "", dhcp=True)
            
            assert result['success'] is False
            assert "出错" in result['error']


class TestNetworkConflictCheck:
    """测试网络冲突检查"""
    
    @pytest.mark.unit
    def test_check_network_conflict_no_conflict(self):
        """测试无冲突情况"""
        with mock.patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            with mock.patch('netkit.services.ip_switcher.get_interface_config') as mock_get_config:
                mock_get_interfaces.return_value = ["以太网", "Wi-Fi"]
                mock_get_config.return_value = """
                IP Address: 192.168.1.50
                Default Gateway: 192.168.1.1
                """
                
                result = check_network_conflict("192.168.1.100", "255.255.255.0", "192.168.1.1")
                
                assert result['has_conflict'] is False
                assert len(result['conflicts']) == 0
    
    @pytest.mark.unit
    def test_check_network_conflict_ip_conflict(self):
        """测试IP冲突"""
        with mock.patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            with mock.patch('netkit.services.ip_switcher.get_interface_config') as mock_get_config:
                mock_get_interfaces.return_value = ["以太网"]
                mock_get_config.return_value = """
                IP Address: 192.168.1.100
                Default Gateway: 192.168.1.1
                """
                
                result = check_network_conflict("192.168.1.100", "255.255.255.0", "192.168.1.1")
                
                assert result['has_conflict'] is True
                assert len(result['conflicts']) > 0
                assert "IP地址" in result['conflicts'][0]
    
    @pytest.mark.unit
    def test_check_network_conflict_exception(self):
        """测试异常情况"""
        with mock.patch('netkit.services.ip_switcher.get_network_interfaces') as mock_get_interfaces:
            mock_get_interfaces.side_effect = Exception("Network error")
            
            result = check_network_conflict("192.168.1.100", "255.255.255.0", "192.168.1.1")
            
            assert result['has_conflict'] is False
            assert len(result['conflicts']) > 0
            assert "出错" in result['conflicts'][0]


class TestConfigSuggestions:
    """测试配置建议"""
    
    @pytest.mark.unit
    def test_suggest_ip_config_success(self):
        """测试配置建议成功"""
        with mock.patch('netkit.services.ip_switcher.get_interface_config') as mock_get_config:
            with mock.patch('netkit.services.ip_switcher.validate_ip_config') as mock_validate:
                mock_get_config.return_value = "Interface config"
                mock_validate.return_value = {'valid': True}
                
                result = suggest_ip_config("以太网")
                
                assert result['success'] is True
                assert 'suggestions' in result
                assert len(result['suggestions']) > 0
    
    @pytest.mark.unit
    def test_suggest_ip_config_no_interface(self):
        """测试接口不存在"""
        with mock.patch('netkit.services.ip_switcher.get_interface_config') as mock_get_config:
            mock_get_config.return_value = None
            
            result = suggest_ip_config("不存在的接口")
            
            assert result['success'] is False
            assert "无法获取" in result['error']


class TestUtilityFunctions:
    """测试工具函数"""
    
    @pytest.mark.unit
    def test_get_interface_config_success(self):
        """测试获取接口配置成功"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Interface config output"
            
            result = get_interface_config("以太网")
            
            assert result == "Interface config output"
    
    @pytest.mark.unit
    def test_get_interface_config_failure(self):
        """测试获取接口配置失败"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            
            result = get_interface_config("以太网")
            
            assert result is None
    
    @pytest.mark.unit
    def test_get_config_dir(self):
        """测试获取配置目录"""
        with mock.patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path("/home/user")
            
            config_dir = get_config_dir()
            
            assert config_dir == Path("/home/user/.netkit_py")


@pytest.mark.performance
class TestPerformance:
    """性能测试"""
    
    @pytest.mark.benchmark
    def test_validate_ip_config_performance(self, benchmark):
        """测试IP配置验证性能"""
        def validate_config():
            return validate_ip_config("192.168.1.100", "255.255.255.0", "192.168.1.1", "8.8.8.8")
        
        result = benchmark(validate_config)
        assert result['valid'] is True
    
    @pytest.mark.benchmark
    def test_get_network_interfaces_performance(self, benchmark):
        """测试获取网络接口性能"""
        with mock.patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = MOCK_NETSH_INTERFACE_OUTPUT
            
            def get_interfaces():
                return get_network_interfaces()
            
            result = benchmark(get_interfaces)
            assert isinstance(result, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 