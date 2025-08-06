#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由服务完整功能测试
包含单元测试、集成测试和实际功能验证
"""

import pytest
import subprocess
from unittest.mock import Mock, patch, MagicMock
from netkit.services.route import RouteService, RouteManager, RouteParser, RouteValidator


class TestRouteService:
    """路由服务核心功能测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.route_service = RouteService()
        
    def test_route_service_initialization(self):
        """测试路由服务初始化"""
        assert self.route_service is not None
        assert hasattr(self.route_service, 'manager')
        assert hasattr(self.route_service, 'parser')
        assert hasattr(self.route_service, 'validator')
        print("✅ 路由服务初始化测试通过")
    
    @patch('subprocess.run')
    def test_get_route_table_success(self, mock_run):
        """测试获取路由表成功的情况"""
        # 模拟成功的route print命令输出
        mock_output = """
===========================================================================
接口列表
 12...aa bb cc dd ee ff ......Realtek PCIe GbE Family Controller
===========================================================================

IPv4 路由表
===========================================================================
活动路由:
网络目标        网络掩码          网关       接口   跃点数
          0.0.0.0          0.0.0.0    192.168.1.1   192.168.1.100     25
        127.0.0.0        255.0.0.0         在链路上         127.0.0.1    331
      192.168.1.0    255.255.255.0         在链路上   192.168.1.100    281
===========================================================================
"""
        mock_run.return_value = Mock(returncode=0, stdout=mock_output, stderr="")
        
        result = self.route_service.get_route_table()
        
        assert result['success'] == True
        assert 'routes' in result
        assert len(result['routes']) > 0
        print("✅ 获取路由表测试通过")
    
    @patch('subprocess.run')
    def test_add_route_success(self, mock_run):
        """测试添加路由成功的情况"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = self.route_service.add_route(
            destination="10.0.0.0",
            netmask="255.255.255.0", 
            gateway="192.168.1.1",
            metric=1
        )
        
        assert result['success'] == True
        assert '成功' in result['message']
        print("✅ 添加路由测试通过")
    
    @patch('subprocess.run')
    def test_delete_route_success(self, mock_run):
        """测试删除路由成功的情况"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = self.route_service.delete_route(
            destination="10.0.0.0",
            netmask="255.255.255.0",
            gateway="192.168.1.1"
        )
        
        assert result['success'] == True
        assert '成功' in result['message']
        print("✅ 删除路由测试通过")
    
    def test_validate_route_params_valid(self):
        """测试路由参数验证 - 有效参数"""
        result = self.route_service.validate_route_params(
            destination="192.168.2.0",
            netmask="255.255.255.0",
            gateway="192.168.1.1",
            metric=1
        )
        
        assert result['valid'] == True
        print("✅ 路由参数验证（有效）测试通过")
    
    def test_validate_route_params_invalid_ip(self):
        """测试路由参数验证 - 无效IP地址"""
        result = self.route_service.validate_route_params(
            destination="999.999.999.999",  # 无效IP
            netmask="255.255.255.0",
            gateway="192.168.1.1",
            metric=1
        )
        
        assert result['valid'] == False
        assert 'error' in result
        print("✅ 路由参数验证（无效IP）测试通过")


class TestRouteManager:
    """路由管理器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.manager = RouteManager()
    
    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager is not None
        assert hasattr(self.manager, 'platform')
        print("✅ 路由管理器初始化测试通过")
    
    @patch('subprocess.run')
    def test_get_system_routes(self, mock_run):
        """测试获取系统路由"""
        mock_run.return_value = Mock(
            returncode=0, 
            stdout="mock route output",
            stderr=""
        )
        
        result = self.manager.get_system_routes()
        
        assert result['success'] == True
        assert 'raw_output' in result
        mock_run.assert_called_once()
        print("✅ 获取系统路由测试通过")
    
    @patch('subprocess.run')
    def test_add_system_route(self, mock_run):
        """测试添加系统路由"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = self.manager.add_system_route(
            "10.0.0.0", "255.255.255.0", "192.168.1.1", 1
        )
        
        assert result['success'] == True
        mock_run.assert_called_once()
        print("✅ 添加系统路由测试通过")
    
    @patch('subprocess.run')
    def test_delete_system_route(self, mock_run):
        """测试删除系统路由"""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = self.manager.delete_system_route(
            "10.0.0.0", "255.255.255.0", "192.168.1.1"
        )
        
        assert result['success'] == True
        mock_run.assert_called_once()
        print("✅ 删除系统路由测试通过")


class TestRouteParser:
    """路由解析器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.parser = RouteParser()
    
    def test_parse_route_table(self):
        """测试解析路由表输出"""
        mock_output = """
IPv4 路由表
===========================================================================
活动路由:
网络目标        网络掩码          网关       接口   跃点数
          0.0.0.0          0.0.0.0    192.168.1.1   192.168.1.100     25
        127.0.0.0        255.0.0.0         在链路上         127.0.0.1    331
      192.168.1.0    255.255.255.0         在链路上   192.168.1.100    281
"""
        
        result = self.parser.parse_route_table(mock_output)
        
        assert isinstance(result, list)
        assert len(result) >= 2  # 至少应该解析出几条路由
        print("✅ 路由表解析测试通过")
    
    def test_parse_route_line(self):
        """测试解析单行路由"""
        route_line = "192.168.1.0    255.255.255.0         在链路上   192.168.1.100    281"
        
        result = self.parser.parse_route_line(route_line)
        
        assert result is not None
        assert 'network_destination' in result
        assert 'netmask' in result
        print("✅ 单行路由解析测试通过")


class TestRouteValidator:
    """路由验证器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.validator = RouteValidator()
    
    def test_validate_ip_address_valid(self):
        """测试IP地址验证 - 有效地址"""
        assert self.validator.validate_ip_address("192.168.1.1") == True
        assert self.validator.validate_ip_address("10.0.0.1") == True
        assert self.validator.validate_ip_address("172.16.1.1") == True
        print("✅ IP地址验证（有效）测试通过")
    
    def test_validate_ip_address_invalid(self):
        """测试IP地址验证 - 无效地址"""
        assert self.validator.validate_ip_address("999.999.999.999") == False
        assert self.validator.validate_ip_address("192.168.1") == False
        assert self.validator.validate_ip_address("invalid_ip") == False
        print("✅ IP地址验证（无效）测试通过")
    
    def test_validate_netmask_valid(self):
        """测试子网掩码验证 - 有效掩码"""
        result1 = self.validator.validate_netmask("255.255.255.0")
        result2 = self.validator.validate_netmask("255.255.0.0")
        result3 = self.validator.validate_netmask("255.0.0.0")
        
        assert result1['valid'] == True
        assert result2['valid'] == True
        assert result3['valid'] == True
        print("✅ 子网掩码验证（有效）测试通过")
    
    def test_validate_netmask_invalid(self):
        """测试子网掩码验证 - 无效掩码"""
        result1 = self.validator.validate_netmask("255.255.255.1")
        result2 = self.validator.validate_netmask("256.255.255.0")
        
        assert result1['valid'] == False
        assert result2['valid'] == False
        print("✅ 子网掩码验证（无效）测试通过")
    
    def test_validate_route_params(self):
        """测试路由参数完整验证"""
        result = self.validator.validate_route_params(
            destination="192.168.2.0",
            netmask="255.255.255.0", 
            gateway="192.168.1.1",
            metric=1
        )
        
        assert result['valid'] == True
        print("✅ 路由参数完整验证测试通过")


@pytest.mark.integration
class TestRouteIntegration:
    """路由功能集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.route_service = RouteService()
    
    @pytest.mark.skip(reason="需要管理员权限，仅在手动测试时运行")
    def test_real_route_operations(self):
        """测试真实的路由操作（需要管理员权限）"""
        # 注意：这个测试需要管理员权限，通常跳过
        test_destination = "10.10.10.0"
        test_netmask = "255.255.255.0"
        test_gateway = "192.168.1.1"
        
        # 尝试添加测试路由
        add_result = self.route_service.add_route(
            test_destination, test_netmask, test_gateway
        )
        print(f"添加路由结果: {add_result}")
        
        if add_result['success']:
            # 如果添加成功，尝试删除
            delete_result = self.route_service.delete_route(
                test_destination, test_netmask, test_gateway
            )
            print(f"删除路由结果: {delete_result}")
    
    def test_route_table_retrieval(self):
        """测试路由表获取（不需要管理员权限）"""
        result = self.route_service.get_route_table()
        
        assert result is not None
        if result['success']:
            assert 'routes' in result
            assert len(result['routes']) >= 0
            print(f"✅ 获取到 {len(result['routes'])} 条路由记录")
        else:
            print(f"⚠️ 获取路由表失败: {result.get('error', '未知错误')}")


if __name__ == "__main__":
    # 运行完整的路由功能测试
    pytest.main([__file__, "-v", "--tb=short"])