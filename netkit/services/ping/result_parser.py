"""
Ping结果解析模块

负责解析Windows ping命令的输出结果
提取统计信息如丢包率、响应时间等
"""

import re
from statistics import mean


class PingResultParser:
    """Ping结果解析器"""
    
    @staticmethod
    def parse_ping_result(ping_output):
        """
        解析ping命令输出结果
        
        Args:
            ping_output (str): ping命令的输出文本
            
        Returns:
            dict: 解析后的统计信息
        """
        stats = {
            'host': '',
            'packets_sent': 0,
            'packets_received': 0,
            'packet_loss': 0,
            'times': [],
            'min_time': 0,
            'max_time': 0,
            'avg_time': 0,
            'success': False,
            'raw_output': ping_output
        }
        
        if not ping_output:
            return stats
            
        lines = ping_output.split('\n')
        
        # 提取主机名/IP地址
        stats['host'] = PingResultParser._extract_host(lines)
        
        # 提取ping响应时间
        stats['times'] = PingResultParser._extract_response_times(lines)
        
        # 提取统计信息
        packet_stats = PingResultParser._extract_packet_statistics(lines)
        stats.update(packet_stats)
        
        # 提取时间统计
        time_stats = PingResultParser._extract_time_statistics(lines)
        stats.update(time_stats)
        
        # 如果没有从Windows ping输出中提取到统计信息，自己计算
        if stats['times'] and stats['packets_sent'] == 0:
            stats['packets_sent'] = len(stats['times'])
            stats['packets_received'] = len(stats['times'])
            stats['packet_loss'] = 0
            if stats['times']:
                stats['min_time'] = min(stats['times'])
                stats['max_time'] = max(stats['times'])
                stats['avg_time'] = int(mean(stats['times']))
        
        stats['success'] = stats['packets_received'] > 0
        return stats
    
    @staticmethod
    def _extract_host(lines):
        """从ping输出中提取主机名或IP地址"""
        for line in lines:
            if 'Pinging' in line or '正在 Ping' in line:
                # 匹配IP地址或主机名
                ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'
                ip_match = re.search(ip_pattern, line)
                if ip_match:
                    return ip_match.group(1)
                
                # 如果没有找到IP，尝试提取主机名
                host_pattern = r'Pinging\s+([^\s\[]+)|正在 Ping\s+([^\s\[]+)'
                host_match = re.search(host_pattern, line)
                if host_match:
                    return host_match.group(1) or host_match.group(2)
        return ''
    
    @staticmethod
    def _extract_response_times(lines):
        """从ping输出中提取响应时间列表"""
        times = []
        
        # 匹配各种时间格式
        time_patterns = [
            r'time[<=](\d+)ms',
            r'时间[<=](\d+)ms',
            r'time=(\d+)ms',
            r'时间=(\d+)ms'
        ]
        
        for line in lines:
            for pattern in time_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    try:
                        times.append(int(match))
                    except ValueError:
                        continue
        
        return times
    
    @staticmethod
    def _extract_packet_statistics(lines):
        """从ping输出中提取数据包统计信息"""
        stats = {
            'packets_sent': 0,
            'packets_received': 0,
            'packet_loss': 0
        }
        
        for line in lines:
            # 匹配数据包统计行
            if 'Packets:' in line or '数据包:' in line:
                # 英文版本
                sent_pattern = r'Sent = (\d+)'
                received_pattern = r'Received = (\d+)'
                lost_pattern = r'Lost = (\d+)'
                
                # 中文版本  
                sent_pattern_cn = r'已发送 = (\d+)'
                received_pattern_cn = r'已接收 = (\d+)'
                lost_pattern_cn = r'丢失 = (\d+)'
                
                patterns = [
                    (sent_pattern, sent_pattern_cn, 'packets_sent'),
                    (received_pattern, received_pattern_cn, 'packets_received'),
                    (lost_pattern, lost_pattern_cn, 'packets_lost')
                ]
                
                for en_pattern, cn_pattern, key in patterns:
                    match = re.search(en_pattern, line) or re.search(cn_pattern, line)
                    if match:
                        value = int(match.group(1))
                        if key == 'packets_lost':
                            # 计算丢包率
                            if stats['packets_sent'] > 0:
                                stats['packet_loss'] = (value / stats['packets_sent']) * 100
                        else:
                            stats[key] = value
                
                break
        
        return stats
    
    @staticmethod
    def _extract_time_statistics(lines):
        """从ping输出中提取时间统计信息"""
        stats = {
            'min_time': 0,
            'max_time': 0,
            'avg_time': 0
        }
        
        for line in lines:
            # 匹配时间统计行
            if 'Minimum' in line or '最短' in line:
                # 英文版本
                min_pattern = r'Minimum = (\d+)ms'
                max_pattern = r'Maximum = (\d+)ms'
                avg_pattern = r'Average = (\d+)ms'
                
                # 中文版本
                min_pattern_cn = r'最短 = (\d+)ms'
                max_pattern_cn = r'最长 = (\d+)ms'
                avg_pattern_cn = r'平均 = (\d+)ms'
                
                patterns = [
                    (min_pattern, min_pattern_cn, 'min_time'),
                    (max_pattern, max_pattern_cn, 'max_time'),
                    (avg_pattern, avg_pattern_cn, 'avg_time')
                ]
                
                for en_pattern, cn_pattern, key in patterns:
                    match = re.search(en_pattern, line) or re.search(cn_pattern, line)
                    if match:
                        stats[key] = int(match.group(1))
                
                break
        
        return stats
    
    @staticmethod
    def format_result_summary(stats):
        """
        格式化ping结果摘要
        
        Args:
            stats (dict): ping统计信息
            
        Returns:
            str: 格式化的结果摘要
        """
        if not stats['success']:
            return f"❌ {stats['host']}: 无法访问"
        
        summary_parts = [
            f"✅ {stats['host']}",
            f"平均: {stats['avg_time']}ms",
            f"丢包率: {stats['packet_loss']:.1f}%"
        ]
        
        if stats['min_time'] and stats['max_time']:
            summary_parts.append(f"范围: {stats['min_time']}-{stats['max_time']}ms")
        
        return " | ".join(summary_parts)
    
    @staticmethod
    def is_host_reachable(stats):
        """
        判断主机是否可达
        
        Args:
            stats (dict): ping统计信息
            
        Returns:
            bool: 主机是否可达
        """
        return stats['success'] and stats['packets_received'] > 0 