"""
Ping服务主类

整合所有ping功能模块，提供统一的服务接口
"""

import threading
import concurrent.futures
from .ip_parser import parse_ip_range
from .ping_executor import PingExecutor
from .result_parser import PingResultParser
from .stats_manager import PingStatsManager


class PingService:
    """Ping测试服务类"""
    
    def __init__(self):
        self.executor = PingExecutor()
        self.parser = PingResultParser()
        self.stats_manager = PingStatsManager()
        self.background_executor = None
        
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
    
    def ping_ip_range(self, ip_range_str, count=5, timeout=3000, max_workers=25, callback=None):
        """
        Ping IP范围
        
        Args:
            ip_range_str (str): IP范围字符串
            count (int): ping次数
            timeout (int): 超时时间(毫秒)
            max_workers (int): 最大并发数
            callback (callable): 结果回调函数
            
        Returns:
            dict: 测试结果
        """
        try:
            # 解析IP范围
            ips = parse_ip_range(ip_range_str)
            
            if callback:
                callback({
                    'type': 'info',
                    'message': f"解析到 {len(ips)} 个IP地址，开始批量ping测试..."
                })
            
            # 批量ping
            def on_progress(host, result, stats, completed, total):
                if callback:
                    callback({
                        'type': 'progress',
                        'host': host,
                        'result': result,
                        'stats': stats,
                        'completed': completed,
                        'total': total
                    })
            
            results = self.batch_ping(ips, count, timeout, max_workers, on_progress)
            
            if callback:
                callback({
                    'type': 'results',
                    'results': results,
                    'total_count': len(ips)
                })
            
            return results
            
        except Exception as e:
            error_msg = f"IP范围ping失败: {str(e)}"
            if callback:
                callback({
                    'type': 'error',
                    'message': error_msg
                })
            return {'error': error_msg}
    
    def start_continuous_ping(self, host, interval=1, timeout=3000, callback=None):
        """
        启动连续ping测试
        
        Args:
            host (str): 目标主机地址
            interval (int): ping间隔时间(秒)
            timeout (int): 超时时间(毫秒)
            callback (callable): 结果回调函数
            
        Returns:
            bool: 是否成功启动
        """
        if self.executor.is_running:
            return False
        
        # 重置统计管理器
        self.stats_manager.reset()
        self.stats_manager.set_target_host(host)
        
        def on_ping_result(result):
            # 解析结果
            stats = self.parser.parse_ping_result(result['output'])
            
            # 添加到统计管理器
            self.stats_manager.add_ping_result(result, stats)
            
            # 获取总体统计
            overall_stats = self.stats_manager.get_overall_stats()
            
            # 调用外部回调
            if callback:
                callback(stats, overall_stats)
        
        # 启动连续ping
        return self.executor.start_continuous_ping(
            host, interval, timeout, on_ping_result
        )
    
    def stop_ping(self):
        """停止ping测试"""
        self.executor.stop_ping()
    
    def is_running(self):
        """检查是否有ping测试正在运行"""
        return self.executor.is_running
    
    def get_stats_manager(self):
        """获取统计管理器实例"""
        return self.stats_manager
    
    def generate_report(self):
        """生成测试报告"""
        return self.stats_manager.get_summary_report()
    
    def export_results_csv(self):
        """导出结果为CSV格式"""
        return self.stats_manager.export_csv_data()


# 向后兼容的简单函数
def ping(host, count=4):
    """
    简单的ping函数（向后兼容）
    
    Args:
        host (str): 目标主机地址
        count (int): ping次数
        
    Returns:
        str: ping输出结果
    """
    service = PingService()
    result = service.ping_single(host, count)
    return result['output']


def ping_with_stats(host, count=5, timeout=3000):
    """
    带统计信息的ping函数
    
    Args:
        host (str): 目标主机地址
        count (int): ping次数
        timeout (int): 超时时间(毫秒)
        
    Returns:
        dict: 包含原始输出和统计信息的结果
    """
    service = PingService()
    return service.ping_with_stats(host, count, timeout) 