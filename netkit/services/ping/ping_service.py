"""
Ping服务主类

整合所有ping功能模块，提供统一的服务接口
专为新的可视化ping界面设计
"""

import threading
import concurrent.futures
from .ip_parser import parse_ip_range
from .ping_executor import PingExecutor
from .result_parser import PingResultParser
class PingService:
    """Ping测试服务类"""
    
    def __init__(self):
        self.executor = PingExecutor()
        self.parser = PingResultParser()
        
    def ping_single(self, host, count=4, timeout=3000):
        """
        单次ping测试
        
        Args:
            host (str): 目标主机地址
            count (int): ping次数
            timeout (int): 超时时间(毫秒)
            
        Returns:
            dict: ping执行结果
        """
        return self.executor.ping_single(host, count, timeout)
    
    def ping_with_stats(self, host, count=5, timeout=3000):
        """
        带统计信息的ping测试
        
        Args:
            host (str): 目标主机地址
            count (int): ping次数
            timeout (int): 超时时间(毫秒)
            
        Returns:
            dict: 包含原始输出和统计信息的结果
        """
        result = self.executor.ping_single(host, count, timeout)
        stats = self.parser.parse_ping_result(result['output'])
        
        return {
            'raw_output': result['output'],
            'stats': stats,
            'success': result['success'],
            'error': result['error']
        }
    
    def batch_ping(self, hosts, count=5, timeout=3000, max_workers=25, progress_callback=None):
        """
        批量ping测试
        
        Args:
            hosts (list): 主机地址列表
            count (int): 每个主机的ping次数
            timeout (int): 超时时间(毫秒)
            max_workers (int): 最大并发数
            progress_callback (callable): 进度回调函数
            
        Returns:
            dict: 主机地址到结果的映射
        """
        results = {}
        
        def on_progress(host, result, completed, total):
            # 解析结果并添加统计信息
            stats = self.parser.parse_ping_result(result['output'])
            results[host] = {
                'result': result,
                'stats': stats
            }
            
            # 调用外部进度回调
            if progress_callback:
                progress_callback(host, result, stats, completed, total)
        
        # 执行批量ping
        raw_results = self.executor.batch_ping(
            hosts, count, timeout, max_workers, on_progress
        )
        
        # 如果没有通过进度回调处理，直接处理结果
        if not progress_callback:
            for host, result in raw_results.items():
                if host not in results:
                    stats = self.parser.parse_ping_result(result['output'])
                    results[host] = {
                        'result': result,
                        'stats': stats
                    }
        
        return results
    
    def stop_ping(self):
        """停止ping测试"""
        self.executor.stop_ping()
    
    def is_running(self):
        """检查是否有ping测试正在运行"""
        return self.executor.is_running

 