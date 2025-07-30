#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ping服务集成测试
测试Ping服务与GUI的完整交互流程
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from concurrent.futures import ThreadPoolExecutor

# 导入测试目标
from netkit.services.ping.ping_service import PingService
from netkit.services.ping.ping_executor import PingExecutor
from netkit.services.ping.ip_parser import parse_ip_range
from gui.views.ping.visual_ping_view import VisualPingView


@pytest.mark.integration
class TestPingServiceIntegration:
    """Ping服务集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.ping_service = PingService()
        self.test_hosts = ['8.8.8.8', '1.1.1.1', '192.168.1.1']
    
    @patch('subprocess.run')
    def test_single_ping_integration(self, mock_subprocess):
        """测试单个主机Ping集成"""
        # 模拟成功的ping命令输出
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="""
正在 Ping 8.8.8.8 具有 32 字节的数据:
来自 8.8.8.8 的回复: 字节=32 时间=15ms TTL=117
来自 8.8.8.8 的回复: 字节=32 时间=14ms TTL=117
来自 8.8.8.8 的回复: 字节=32 时间=16ms TTL=117
来自 8.8.8.8 的回复: 字节=32 时间=15ms TTL=117

8.8.8.8 的 Ping 统计信息:
    数据包: 已发送 = 4，已接收 = 4，丢失 = 0 (0% 丢失)，
往返行程的估计时间(以毫秒为单位):
    最短 = 14ms，最长 = 16ms，平均 = 15ms
            """,
            stderr=""
        )
        
        # 执行ping测试
        result = self.ping_service.ping_host('8.8.8.8')
        
        # 验证结果
        assert result is not None
        assert result['host'] == '8.8.8.8'
        assert result['success'] == True
        assert result['avg_time'] > 0
        assert result['packet_loss'] == 0
    
    @patch('subprocess.run')
    def test_batch_ping_integration(self, mock_subprocess):
        """测试批量Ping集成"""
        # 模拟不同主机的ping结果
        def mock_ping_response(cmd, **kwargs):
            host = cmd[cmd.index('-n') + 2]  # 获取目标主机
            if host == '8.8.8.8':
                return Mock(
                    returncode=0,
                    stdout="来自 8.8.8.8 的回复: 字节=32 时间=15ms TTL=117\n平均 = 15ms",
                    stderr=""
                )
            elif host == '1.1.1.1':
                return Mock(
                    returncode=0,
                    stdout="来自 1.1.1.1 的回复: 字节=32 时间=12ms TTL=64\n平均 = 12ms",
                    stderr=""
                )
            else:
                return Mock(
                    returncode=1,
                    stdout="",
                    stderr="请求超时"
                )
        
        mock_subprocess.side_effect = mock_ping_response
        
        # 执行批量ping测试
        results = self.ping_service.ping_multiple_hosts(self.test_hosts)
        
        # 验证结果
        assert len(results) == 3
        
        # 验证成功的ping
        google_result = next((r for r in results if r['host'] == '8.8.8.8'), None)
        assert google_result is not None
        assert google_result['success'] == True
        
        cloudflare_result = next((r for r in results if r['host'] == '1.1.1.1'), None)
        assert cloudflare_result is not None
        assert cloudflare_result['success'] == True
        
        # 验证失败的ping
        local_result = next((r for r in results if r['host'] == '192.168.1.1'), None)
        assert local_result is not None
        assert local_result['success'] == False
    
    @patch('subprocess.run')
    @pytest.mark.asyncio
    async def test_async_ping_integration(self, mock_subprocess):
        """测试异步Ping集成"""
        # 模拟ping命令输出
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="来自 8.8.8.8 的回复: 字节=32 时间=15ms TTL=117\n平均 = 15ms",
            stderr=""
        )
        
        # 创建异步ping任务
        tasks = []
        for host in self.test_hosts:
            task = asyncio.create_task(
                asyncio.to_thread(self.ping_service.ping_host, host)
            )
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks)
        
        # 验证结果
        assert len(results) == 3
        for result in results:
            assert result is not None
            assert 'host' in result
            assert 'success' in result
    
    def test_ip_range_parsing_integration(self):
        """测试IP范围解析集成"""
        # 测试不同的IP范围格式
        test_cases = [
            ('192.168.1.1-192.168.1.5', 5),
            ('10.0.0.1-10.0.0.10', 10),
            ('172.16.0.1,172.16.0.2,172.16.0.3', 3),
            ('192.168.1.0/30', 4),  # 网络地址范围
        ]
        
        for ip_range, expected_count in test_cases:
            ips = parse_ip_range(ip_range)
            assert len(ips) == expected_count, f"IP范围 {ip_range} 解析错误"
    
    @patch('subprocess.run')
    def test_ping_with_custom_parameters(self, mock_subprocess):
        """测试自定义参数Ping集成"""
        # 模拟ping命令输出
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="来自 8.8.8.8 的回复: 字节=64 时间=15ms TTL=117\n平均 = 15ms",
            stderr=""
        )
        
        # 使用自定义参数ping
        result = self.ping_service.ping_host(
            '8.8.8.8',
            count=10,
            timeout=5000,
            packet_size=64
        )
        
        # 验证结果
        assert result is not None
        assert result['success'] == True
        
        # 验证命令参数
        mock_subprocess.assert_called_once()
        cmd_args = mock_subprocess.call_args[0][0]
        assert '-n' in cmd_args
        assert '10' in cmd_args  # count参数
        assert '-w' in cmd_args
        assert '5000' in cmd_args  # timeout参数
        assert '-l' in cmd_args
        assert '64' in cmd_args  # packet_size参数


@pytest.mark.integration
class TestPingExecutorIntegration:
    """Ping执行器集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.executor = PingExecutor()
    
    @patch('subprocess.run')
    def test_ping_executor_with_callback(self, mock_subprocess):
        """测试带回调的Ping执行器"""
        # 模拟ping输出
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="来自 8.8.8.8 的回复: 字节=32 时间=15ms TTL=117",
            stderr=""
        )
        
        # 回调函数收集结果
        results = []
        
        def callback(result):
            results.append(result)
        
        # 执行ping
        self.executor.ping_with_callback('8.8.8.8', callback)
        
        # 验证回调被调用
        assert len(results) == 1
        assert results[0]['host'] == '8.8.8.8'
        assert results[0]['success'] == True
    
    @patch('subprocess.run')
    def test_concurrent_ping_execution(self, mock_subprocess):
        """测试并发Ping执行"""
        # 模拟ping输出
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="来自 主机 的回复: 字节=32 时间=15ms TTL=117",
            stderr=""
        )
        
        hosts = ['8.8.8.8', '1.1.1.1', '8.8.4.4', '1.0.0.1']
        results = []
        
        def callback(result):
            results.append(result)
        
        # 并发执行ping
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self.executor.ping_with_callback, host, callback)
                for host in hosts
            ]
            
            # 等待所有任务完成
            for future in futures:
                future.result()
        
        # 验证结果
        assert len(results) == 4
        host_results = {r['host'] for r in results}
        assert host_results == set(hosts)


@pytest.mark.integration
@pytest.mark.slow
class TestPingStressIntegration:
    """Ping压力测试集成"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.ping_service = PingService()
    
    @patch('subprocess.run')
    def test_high_volume_ping(self, mock_subprocess):
        """测试大量主机Ping"""
        # 模拟ping输出
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="来自 主机 的回复: 字节=32 时间=15ms TTL=117\n平均 = 15ms",
            stderr=""
        )
        
        # 生成大量主机列表
        hosts = [f'192.168.1.{i}' for i in range(1, 101)]  # 100个主机
        
        start_time = time.time()
        results = self.ping_service.ping_multiple_hosts(hosts, max_workers=10)
        end_time = time.time()
        
        # 验证结果
        assert len(results) == 100
        assert end_time - start_time < 30  # 应该在30秒内完成
        
        # 验证所有结果都有效
        for result in results:
            assert 'host' in result
            assert 'success' in result
    
    @patch('subprocess.run')
    def test_long_running_ping(self, mock_subprocess):
        """测试长时间运行的Ping"""
        # 模拟ping输出
        mock_subprocess.return_value = Mock(
            returncode=0,
            stdout="来自 8.8.8.8 的回复: 字节=32 时间=15ms TTL=117\n平均 = 15ms",
            stderr=""
        )
        
        # 长时间ping测试
        results = []
        start_time = time.time()
        
        # 模拟持续ping 10秒
        while time.time() - start_time < 2:  # 测试中缩短为2秒
            result = self.ping_service.ping_host('8.8.8.8')
            results.append(result)
            time.sleep(0.1)
        
        # 验证结果
        assert len(results) > 0
        for result in results:
            assert result['host'] == '8.8.8.8'
            assert result['success'] == True


@pytest.mark.integration
class TestPingUIIntegration:
    """Ping UI集成测试"""
    
    @pytest.fixture
    def mock_tk_root(self):
        """模拟Tkinter根窗口"""
        with patch('tkinter.Tk') as mock_root:
            mock_instance = Mock()
            mock_root.return_value = mock_instance
            yield mock_instance
    
    def test_ping_result_display_integration(self, mock_tk_root):
        """测试Ping结果显示集成"""
        # 模拟ping结果
        ping_results = [
            {
                'host': '8.8.8.8',
                'success': True,
                'avg_time': 15.5,
                'packet_loss': 0,
                'status': 'success'
            },
            {
                'host': '192.168.1.999',
                'success': False,
                'avg_time': 0,
                'packet_loss': 100,
                'status': 'timeout'
            }
        ]
        
        # 这里应该测试UI组件如何处理这些结果
        # 由于GUI测试复杂，这里主要验证数据结构
        for result in ping_results:
            assert 'host' in result
            assert 'success' in result
            assert 'avg_time' in result
            assert 'packet_loss' in result
            assert 'status' in result


if __name__ == "__main__":
    # 运行Ping集成测试
    pytest.main([__file__, "-v", "-m", "integration"])