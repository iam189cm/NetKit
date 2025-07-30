#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础集成测试
测试核心模块的基本集成功能
"""

import pytest
import time
from unittest.mock import Mock, patch

# 导入测试目标
from netkit.services.netconfig import (
    validate_ip_config,
)


@pytest.mark.integration
class TestBasicIntegration:
    """基础集成测试"""
    
    def test_ip_validation_integration(self):
        """测试IP配置验证集成"""
        # 有效配置测试
        result = validate_ip_config(
            ip='192.168.1.100',
            mask='255.255.255.0',
            gateway='192.168.1.1',
            dns='8.8.8.8,8.8.4.4'
        )
        
        assert result['valid'], f"有效配置验证失败: {result.get('error', '')}"
        
        # 无效配置测试
        result = validate_ip_config(
            ip='999.999.999.999',  # 无效IP
            mask='255.255.255.0',
            gateway='192.168.1.1',
            dns='8.8.8.8,8.8.4.4'
        )
        
        assert not result['valid'], "无效配置应该验证失败"
        assert 'error' in result
    
    def test_multiple_validation_integration(self):
        """测试多个配置验证的集成"""
        test_configs = [
            {
                'ip': '192.168.1.100',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns': '8.8.8.8,8.8.4.4',
                'expected': True
            },
            {
                'ip': '10.0.0.100',
                'mask': '255.255.255.0',
                'gateway': '10.0.0.1',
                'dns': '1.1.1.1,1.0.0.1',
                'expected': True
            },
            {
                'ip': 'invalid_ip',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns': '8.8.8.8,8.8.4.4',
                'expected': False
            }
        ]
        
        for i, test_case in enumerate(test_configs):
            result = validate_ip_config(
                ip=test_case['ip'],
                mask=test_case['mask'],
                gateway=test_case['gateway'],
                dns=test_case['dns']
            )
            assert result['valid'] == test_case['expected'], f"测试用例 {i+1} 验证结果不符合预期"
    
    def test_validation_performance_integration(self):
        """测试验证性能集成"""
        # 执行多次验证，测试性能
        start_time = time.time()
        
        for _ in range(100):
            result = validate_ip_config(
                ip='192.168.1.100',
                mask='255.255.255.0',
                gateway='192.168.1.1',
                dns='8.8.8.8,8.8.4.4'
            )
            assert result['valid']
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 性能断言：100次验证应该在1秒内完成
        assert total_time < 1.0, f"验证性能过慢: {total_time:.3f}s"
        
        avg_time = total_time / 100
        assert avg_time < 0.01, f"平均验证时间过慢: {avg_time:.6f}s"


@pytest.mark.integration
class TestModuleImportIntegration:
    """模块导入集成测试"""
    
    def test_core_modules_import(self):
        """测试核心模块导入"""
        # 测试网络配置模块
        from netkit.services.netconfig import (
            get_network_interfaces,
            validate_ip_config,
            apply_profile
        )
        
        # 验证函数可调用
        assert callable(get_network_interfaces)
        assert callable(validate_ip_config)
        assert callable(apply_profile)
    
    def test_service_modules_import(self):
        """测试服务模块导入"""
        try:
            # 测试各个服务模块
            from netkit.services.ping.ping_service import PingService
            from netkit.services.subnet import SubnetCalculator
            from netkit.services.traceroute import TracerouteService
            from netkit.services.route import RouteService
            
            # 验证类可实例化
            ping_service = PingService()
            assert ping_service is not None
            
            subnet_calc = SubnetCalculator()
            assert subnet_calc is not None
            
            traceroute_service = TracerouteService()
            assert traceroute_service is not None
            
            route_service = RouteService()
            assert route_service is not None
            
        except ImportError as e:
            pytest.skip(f"服务模块导入失败，可能未完全实现: {e}")
    
    def test_utils_modules_import(self):
        """测试工具模块导入"""
        from netkit.utils.ui_helper import UIHelper
        
        # 验证工具类可实例化
        ui_helper = UIHelper()
        assert ui_helper is not None


@pytest.mark.integration
@pytest.mark.slow
class TestStressIntegration:
    """压力集成测试"""
    
    def test_validation_stress(self):
        """测试验证压力"""
        configs = []
        
        # 生成大量测试配置（排除网络地址和广播地址）
        for i in range(2, 254):  # 排除1（网关）和255（广播）
            configs.append({
                'ip': f'192.168.1.{i}',
                'mask': '255.255.255.0',
                'gateway': '192.168.1.1',
                'dns1': '8.8.8.8',
                'dns2': '8.8.4.4'
            })
        
        start_time = time.time()
        valid_count = 0
        
        for config in configs:
            result = validate_ip_config(
                ip=config['ip'],
                mask=config['mask'],
                gateway=config['gateway'],
                dns=config['dns1'] + ',' + config['dns2']
            )
            if result['valid']:
                valid_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 验证结果
        assert valid_count == len(configs), f"应该有 {len(configs)} 个有效配置，实际有 {valid_count} 个"
        assert total_time < 5.0, f"压力测试时间过长: {total_time:.3f}s"
        
        print(f"压力测试完成: {valid_count}/{len(configs)} 个配置验证成功，耗时 {total_time:.3f}s")


if __name__ == "__main__":
    # 运行基础集成测试
    pytest.main([__file__, "-v", "-m", "integration"])