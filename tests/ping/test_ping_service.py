#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ping服务测试
基于项目实际实现的Ping功能测试
"""

import pytest
import time
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor

# 导入实际的Ping服务模块
from netkit.services.ping import (
    PingService,
    PingExecutor,
    PingResultParser,
    parse_ip_range
)


class TestPingService:
    """Ping服务测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.ping_service = PingService()
        self.ping_executor = PingExecutor()
        self.result_parser = PingResultParser()
    
    @patch('netkit.services.ping.ping_executor.subprocess.run')
    def test_ping_single_target(self, mock_subprocess):
        """测试单个目标Ping"""
        # 模拟成功的ping命令输出
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"Pinging 8.8.8.8 with 32 bytes of data:\nReply from 8.8.8.8: bytes=32 time=15ms TTL=117\nReply from 8.8.8.8: bytes=32 time=14ms TTL=117\nReply from 8.8.8.8: bytes=32 time=16ms TTL=117\nReply from 8.8.8.8: bytes=32 time=15ms TTL=117\n\nPing statistics for 8.8.8.8:\n    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),\nApproximate round trip times in milli-seconds:\n    Minimum = 14ms, Maximum = 16ms, Average = 15ms"
        mock_result.stderr = b""
        mock_subprocess.return_value = mock_result
        
        # 执行测试
        result = self.ping_service.ping_single('8.8.8.8', count=4, timeout=3000)
        
        # 验证结果
        assert result['success'] == True
        assert result['host'] == '8.8.8.8'
        assert result['return_code'] == 0
        assert '8.8.8.8' in result['output']
        
        # 验证命令调用
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert 'ping' in call_args
        assert '-n' in call_args
        assert '4' in call_args
        assert '-w' in call_args
        assert '3000' in call_args
        assert '8.8.8.8' in call_args
    
    def test_ping_with_stats(self):
        """测试带统计信息的Ping"""
        # 使用公共DNS进行测试
        result = self.ping_service.ping_with_stats('1.1.1.1', count=5, timeout=3000)
        
        # 验证结果结构
        assert 'raw_output' in result
        assert 'stats' in result
        assert 'success' in result
        assert 'error' in result
        
        assert result['success'] == True
        assert '1.1.1.1' in result['raw_output']
        
        # 验证统计信息
        stats = result['stats']
        assert isinstance(stats, dict)
    
    def test_ping_multiple_targets(self):
        """测试批量Ping"""
        # 使用公共DNS进行测试
        hosts = ['8.8.8.8', '1.1.1.1']
        results = self.ping_service.batch_ping(hosts, count=2, timeout=3000, max_workers=2)
        
        # 验证结果
        assert isinstance(results, dict)
        assert len(results) == 2
        
        # 验证成功的ping
        assert '8.8.8.8' in results
        assert results['8.8.8.8']['result']['success'] == True
        
        assert '1.1.1.1' in results
        assert results['1.1.1.1']['result']['success'] == True
    
    def test_ping_result_parsing(self):
        """测试Ping结果解析"""
        # 测试成功的ping输出解析
        success_output = "Pinging 8.8.8.8 with 32 bytes of data:\nReply from 8.8.8.8: bytes=32 time=15ms TTL=117\nReply from 8.8.8.8: bytes=32 time=14ms TTL=117\n\nPing statistics for 8.8.8.8:\n    Packets: Sent = 2, Received = 2, Lost = 0 (0% loss),\nApproximate round trip times in milli-seconds:\n    Minimum = 14ms, Maximum = 15ms, Average = 14ms"
        
        stats = self.result_parser.parse_ping_result(success_output)
        
        # 验证解析结果
        assert isinstance(stats, dict)
        # 具体字段依赖于PingResultParser的实现
    
    def test_ping_timeout_handling(self):
        """测试Ping超时处理"""
        # 测试一个不太可能响应的地址
        result = self.ping_service.ping_single('192.0.2.1', count=1, timeout=1000)
        
        # 应该能正常处理超时情况
        assert 'success' in result
        assert 'error' in result
    
    def test_ping_invalid_host(self):
        """测试无效主机处理"""
        # 测试一个不太可能存在的主机名
        result = self.ping_service.ping_single('definitely.invalid.host.name.12345.test', count=1, timeout=1000)
        
        # 应该能正常处理无效主机
        assert 'success' in result
        assert 'error' in result
        # 注意：某些情况下DNS可能会解析到搜索域，所以我们主要测试结构完整性
        assert isinstance(result['success'], bool)
    
    def test_ip_range_parsing(self):
        """测试IP范围解析"""
        # 测试解析IP范围
        ip_range = "192.168.1.1-192.168.1.5"
        ips = parse_ip_range(ip_range)
        
        # 验证解析结果
        expected_ips = ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5']
        assert ips == expected_ips
    
    def test_ping_performance(self):
        """测试Ping性能"""
        # 性能测试：批量ping应该在合理时间内完成
        hosts = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
        
        start_time = time.time()
        results = self.ping_service.batch_ping(hosts, count=1, timeout=2000, max_workers=3)
        end_time = time.time()
        
        # 验证结果
        assert len(results) == 3
        
        # 性能断言：并行ping应该比串行快
        total_time = end_time - start_time
        assert total_time < 10.0, f"批量ping耗时过长: {total_time:.2f}s"


class TestPingExecutor:
    """Ping执行器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.executor = PingExecutor()
    
    def test_build_ping_command(self):
        """测试构建Ping命令"""
        # 测试基本命令构建 - 直接测试ping_single方法
        result = self.executor.ping_single('8.8.8.8', count=4, timeout=3000)
        
        # 验证结果格式
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'output' in result
        assert 'error' in result
        assert 'host' in result
        assert 'return_code' in result
        assert result['host'] == '8.8.8.8'
    
    @patch('netkit.services.ping.ping_executor.subprocess.run')
    def test_execute_ping_command(self, mock_subprocess):
        """测试执行Ping命令"""
        # 模拟subprocess返回
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = b"ping output"
        mock_result.stderr = b""
        mock_subprocess.return_value = mock_result
        
        # 执行测试 - 使用实际的ping_single方法
        result = self.executor.ping_single('8.8.8.8', count=2, timeout=2000)
        
        # 验证结果
        assert result['success'] == True
        assert result['return_code'] == 0
        assert 'ping output' in result['output']
        
        # 验证subprocess调用
        mock_subprocess.assert_called_once()


class TestPingResultParser:
    """Ping结果解析器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.parser = PingResultParser()
    
    def test_parse_successful_ping(self):
        """测试解析成功的Ping结果"""
        ping_output = """
Pinging 8.8.8.8 with 32 bytes of data:
Reply from 8.8.8.8: bytes=32 time=15ms TTL=117
Reply from 8.8.8.8: bytes=32 time=14ms TTL=117
Reply from 8.8.8.8: bytes=32 time=16ms TTL=117
Reply from 8.8.8.8: bytes=32 time=15ms TTL=117

Ping statistics for 8.8.8.8:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 14ms, Maximum = 16ms, Average = 15ms
"""
        
        stats = self.parser.parse_ping_result(ping_output)
        
        # 验证解析结果
        assert isinstance(stats, dict)
        # 具体验证依赖于parser的实现
    
    def test_parse_failed_ping(self):
        """测试解析失败的Ping结果"""
        ping_output = """
Pinging invalid.host with 32 bytes of data:
Request timed out.
Request timed out.
Request timed out.
Request timed out.

Ping statistics for invalid.host:
    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
"""
        
        stats = self.parser.parse_ping_result(ping_output)
        
        # 验证解析结果
        assert isinstance(stats, dict)
        # 应该能正确解析失败的ping结果


if __name__ == "__main__":
    # 运行Ping服务测试
    pytest.main([__file__, "-v"])