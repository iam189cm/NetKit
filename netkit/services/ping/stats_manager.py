"""
Ping统计管理器模块

负责管理和聚合ping测试的统计数据
支持连续测试的统计信息跟踪
"""

import time
from datetime import datetime
from statistics import mean


class PingStatsManager:
    """Ping统计信息管理器"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """重置所有统计信息"""
        self.start_time = time.time()
        self.total_sent = 0
        self.total_received = 0
        self.total_lost = 0
        self.response_times = []
        self.host_stats = {}
        self.sequence_results = []
        self.current_host = None
    
    def set_target_host(self, host):
        """设置当前目标主机"""
        self.current_host = host
    
    def add_ping_result(self, result, stats):
        """
        添加单次ping结果到统计中
        
        Args:
            result (dict): ping执行结果
            stats (dict): 解析后的统计信息
        """
        # 更新总体统计
        self.total_sent += 1
        
        if stats['success'] and stats['packets_received'] > 0:
            self.total_received += 1
            # 添加响应时间
            if stats['times']:
                self.response_times.extend(stats['times'])
        else:
            self.total_lost += 1
        
        # 记录序列结果（用于连续测试）
        sequence_data = {
            'sequence': getattr(result, 'sequence', len(self.sequence_results) + 1),
            'timestamp': getattr(result, 'timestamp', time.time()),
            'success': stats['success'],
            'response_time': stats['times'][0] if stats['times'] else None,
            'host': stats['host']
        }
        self.sequence_results.append(sequence_data)
        
        # 更新主机统计
        host = stats['host'] or result['host']
        if host not in self.host_stats:
            self.host_stats[host] = {
                'sent': 0,
                'received': 0,
                'lost': 0,
                'times': [],
                'first_seen': time.time(),
                'last_seen': time.time()
            }
        
        host_stat = self.host_stats[host]
        host_stat['sent'] += 1
        host_stat['last_seen'] = time.time()
        
        if stats['success']:
            host_stat['received'] += 1
            if stats['times']:
                host_stat['times'].extend(stats['times'])
        else:
            host_stat['lost'] += 1
    
    def get_overall_stats(self):
        """
        获取总体统计信息
        
        Returns:
            dict: 总体统计信息
        """
        packet_loss = 0
        if self.total_sent > 0:
            packet_loss = (self.total_lost / self.total_sent) * 100
        
        # 计算响应时间统计
        min_time = min(self.response_times) if self.response_times else 0
        max_time = max(self.response_times) if self.response_times else 0
        avg_time = int(mean(self.response_times)) if self.response_times else 0
        
        # 运行时间
        runtime = time.time() - self.start_time
        
        return {
            'total_sent': self.total_sent,
            'total_received': self.total_received,
            'total_lost': self.total_lost,
            'packet_loss': packet_loss,
            'success_rate': (self.total_received / self.total_sent * 100) if self.total_sent > 0 else 0,
            'min_time': min_time,
            'max_time': max_time,
            'avg_time': avg_time,
            'runtime': runtime,
            'runtime_formatted': self._format_duration(runtime),
            'start_time': self.start_time,
            'current_host': self.current_host,
            'total_hosts': len(self.host_stats)
        }
    
    def get_host_stats(self, host=None):
        """
        获取指定主机的统计信息
        
        Args:
            host (str, optional): 主机地址，为None时返回所有主机统计
            
        Returns:
            dict: 主机统计信息
        """
        if host is None:
            return self.host_stats
        
        if host not in self.host_stats:
            return None
        
        host_stat = self.host_stats[host]
        
        # 计算主机特定的统计
        packet_loss = 0
        if host_stat['sent'] > 0:
            packet_loss = (host_stat['lost'] / host_stat['sent']) * 100
        
        min_time = min(host_stat['times']) if host_stat['times'] else 0
        max_time = max(host_stat['times']) if host_stat['times'] else 0
        avg_time = int(mean(host_stat['times'])) if host_stat['times'] else 0
        
        return {
            'host': host,
            'packets_sent': host_stat['sent'],
            'packets_received': host_stat['received'],
            'packets_lost': host_stat['lost'],
            'packet_loss': packet_loss,
            'success_rate': (host_stat['received'] / host_stat['sent'] * 100) if host_stat['sent'] > 0 else 0,
            'min_time': min_time,
            'max_time': max_time,
            'avg_time': avg_time,
            'first_seen': host_stat['first_seen'],
            'last_seen': host_stat['last_seen'],
            'duration': host_stat['last_seen'] - host_stat['first_seen']
        }
    
    def get_recent_results(self, count=10):
        """
        获取最近的ping结果
        
        Args:
            count (int): 返回的结果数量
            
        Returns:
            list: 最近的ping结果列表
        """
        return self.sequence_results[-count:] if self.sequence_results else []
    
    def get_summary_report(self):
        """
        生成汇总报告
        
        Returns:
            str: 格式化的汇总报告
        """
        overall = self.get_overall_stats()
        
        report_lines = [
            "=== Ping测试汇总报告 ===",
            f"测试时间: {self._format_duration(overall['runtime'])}",
            f"目标主机: {overall['current_host'] or '多个主机'}",
            f"总主机数: {overall['total_hosts']}",
            "",
            "=== 数据包统计 ===",
            f"已发送: {overall['total_sent']} 包",
            f"已接收: {overall['total_received']} 包",
            f"丢失: {overall['total_lost']} 包",
            f"丢包率: {overall['packet_loss']:.1f}%",
            f"成功率: {overall['success_rate']:.1f}%",
            "",
            "=== 响应时间统计 ===",
            f"最小时间: {overall['min_time']}ms",
            f"最大时间: {overall['max_time']}ms",
            f"平均时间: {overall['avg_time']}ms",
            ""
        ]
        
        # 添加主机详细统计
        if len(self.host_stats) > 1:
            report_lines.extend([
                "=== 各主机统计 ===",
                ""
            ])
            
            for host in sorted(self.host_stats.keys()):
                host_stat = self.get_host_stats(host)
                report_lines.extend([
                    f"主机: {host}",
                    f"  成功率: {host_stat['success_rate']:.1f}% ({host_stat['packets_received']}/{host_stat['packets_sent']})",
                    f"  平均时间: {host_stat['avg_time']}ms",
                    f"  丢包率: {host_stat['packet_loss']:.1f}%",
                    ""
                ])
        
        return "\n".join(report_lines)
    
    def export_csv_data(self):
        """
        导出CSV格式的数据
        
        Returns:
            str: CSV格式的数据
        """
        if not self.sequence_results:
            return "timestamp,sequence,host,success,response_time\n"
        
        csv_lines = ["timestamp,sequence,host,success,response_time"]
        
        for result in self.sequence_results:
            timestamp = datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            csv_lines.append(
                f"{timestamp},{result['sequence']},{result['host']},"
                f"{result['success']},{result['response_time'] or 'N/A'}"
            )
        
        return "\n".join(csv_lines)
    
    def _format_duration(self, seconds):
        """
        格式化时间间隔
        
        Args:
            seconds (float): 秒数
            
        Returns:
            str: 格式化的时间字符串
        """
        if seconds < 60:
            return f"{seconds:.0f}秒"
        elif seconds < 3600:
            minutes = seconds // 60
            remaining_seconds = seconds % 60
            return f"{minutes:.0f}分{remaining_seconds:.0f}秒"
        else:
            hours = seconds // 3600
            remaining_minutes = (seconds % 3600) // 60
            return f"{hours:.0f}小时{remaining_minutes:.0f}分"
    
    def is_host_healthy(self, host, threshold=80.0):
        """
        判断主机是否健康
        
        Args:
            host (str): 主机地址
            threshold (float): 成功率阈值
            
        Returns:
            bool: 主机是否健康
        """
        host_stat = self.get_host_stats(host)
        if not host_stat:
            return False
        
        return host_stat['success_rate'] >= threshold
    
    def get_performance_grade(self, avg_time):
        """
        根据平均响应时间获取性能等级
        
        Args:
            avg_time (int): 平均响应时间(毫秒)
            
        Returns:
            str: 性能等级
        """
        if avg_time <= 10:
            return "优秀"
        elif avg_time <= 50:
            return "良好"
        elif avg_time <= 100:
            return "一般"
        elif avg_time <= 200:
            return "较差"
        else:
            return "很差" 