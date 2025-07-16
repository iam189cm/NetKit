
import subprocess
import concurrent.futures
import threading
import time
import re
from statistics import mean
import ipaddress


def parse_ip_range(ip_range_str):
    """解析IP范围字符串，返回IP地址列表"""
    ips = []
    ip_range_str = ip_range_str.strip()
    
    try:
        # 检查是否是CIDR格式 (如 192.168.1.0/24)
        if '/' in ip_range_str:
            network = ipaddress.IPv4Network(ip_range_str, strict=False)
            ips = [str(ip) for ip in network.hosts()]
        
        # 检查是否是范围格式 (如 192.168.1.1-192.168.1.100)
        elif '-' in ip_range_str:
            start_ip, end_ip = ip_range_str.split('-', 1)
            start_ip = start_ip.strip()
            end_ip = end_ip.strip()
            
            # 验证IP地址格式
            start_addr = ipaddress.IPv4Address(start_ip)
            end_addr = ipaddress.IPv4Address(end_ip)
            
            if start_addr > end_addr:
                raise ValueError("起始IP地址不能大于结束IP地址")
            
            # 生成IP范围
            current = start_addr
            while current <= end_addr:
                ips.append(str(current))
                current += 1
        
        # 单个IP地址或主机名
        else:
            # 尝试验证是否为IP地址
            try:
                ipaddress.IPv4Address(ip_range_str)
                ips = [ip_range_str]
            except:
                # 如果不是IP地址，可能是主机名
                ips = [ip_range_str]
    
    except Exception as e:
        raise ValueError(f"无效的IP范围格式: {str(e)}")
    
    return ips


class PingService:
    """Ping测试服务类"""
    
    def __init__(self):
        self.is_running = False
        self.executor = None
        self.stop_event = threading.Event()
        
    def ping_single(self, host, count=4, timeout=3000):
        """单次ping测试"""
        try:
            cmd = ['ping', '-n', str(count), '-w', str(timeout), host]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'host': host
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'host': host
            }
    
    def parse_ping_result(self, ping_output):
        """解析ping结果"""
        stats = {
            'host': '',
            'packets_sent': 0,
            'packets_received': 0,
            'packet_loss': 0,
            'times': [],
            'min_time': 0,
            'max_time': 0,
            'avg_time': 0,
            'success': False
        }
        
        if not ping_output:
            return stats
            
        lines = ping_output.split('\n')
        
        # 提取主机名
        for line in lines:
            if 'Pinging' in line or '正在 Ping' in line:
                # 匹配IP地址或主机名
                ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'
                ip_match = re.search(ip_pattern, line)
                if ip_match:
                    stats['host'] = ip_match.group(1)
                break
        
        # 提取ping时间
        time_pattern = r'time[<=](\d+)ms|时间[<=](\d+)ms'
        for line in lines:
            time_match = re.search(time_pattern, line)
            if time_match:
                time_value = int(time_match.group(1) or time_match.group(2))
                stats['times'].append(time_value)
        
        # 提取统计信息
        for line in lines:
            # 发送和接收包数量
            if 'Packets:' in line or '数据包:' in line:
                sent_pattern = r'Sent = (\d+)|已发送 = (\d+)'
                received_pattern = r'Received = (\d+)|已接收 = (\d+)'
                loss_pattern = r'Lost = (\d+)|丢失 = (\d+)'
                
                sent_match = re.search(sent_pattern, line)
                received_match = re.search(received_pattern, line)
                loss_match = re.search(loss_pattern, line)
                
                if sent_match:
                    stats['packets_sent'] = int(sent_match.group(1) or sent_match.group(2))
                if received_match:
                    stats['packets_received'] = int(received_match.group(1) or received_match.group(2))
                if loss_match:
                    lost_packets = int(loss_match.group(1) or loss_match.group(2))
                    if stats['packets_sent'] > 0:
                        stats['packet_loss'] = (lost_packets / stats['packets_sent']) * 100
            
            # 时间统计
            if 'Minimum' in line or '最短' in line:
                min_pattern = r'Minimum = (\d+)ms|最短 = (\d+)ms'
                max_pattern = r'Maximum = (\d+)ms|最长 = (\d+)ms'
                avg_pattern = r'Average = (\d+)ms|平均 = (\d+)ms'
                
                min_match = re.search(min_pattern, line)
                max_match = re.search(max_pattern, line)
                avg_match = re.search(avg_pattern, line)
                
                if min_match:
                    stats['min_time'] = int(min_match.group(1) or min_match.group(2))
                if max_match:
                    stats['max_time'] = int(max_match.group(1) or max_match.group(2))
                if avg_match:
                    stats['avg_time'] = int(avg_match.group(1) or avg_match.group(2))
        
        # 如果没有从Windows ping输出中提取到统计信息，自己计算
        if stats['times'] and stats['packets_sent'] == 0:
            stats['packets_sent'] = len(stats['times'])
            stats['packets_received'] = len(stats['times'])
            stats['packet_loss'] = 0
            stats['min_time'] = min(stats['times'])
            stats['max_time'] = max(stats['times'])
            stats['avg_time'] = int(mean(stats['times']))
        
        stats['success'] = stats['packets_received'] > 0
        return stats
    
    def continuous_ping(self, host, interval=1, timeout=300, callback=None):
        """连续ping测试"""
        self.is_running = True
        self.stop_event.clear()
        
        count = 0
        total_stats = {
            'host': host,
            'total_sent': 0,
            'total_received': 0,
            'total_lost': 0,
            'times': [],
            'start_time': time.time()
        }
        
        while self.is_running and not self.stop_event.is_set():
            count += 1
            
            # 单次ping
            result = self.ping_single(host, count=1, timeout=timeout)
            
            if callback:
                ping_stats = self.parse_ping_result(result['output'])
                ping_stats['sequence'] = count
                ping_stats['timestamp'] = time.time()
                
                # 更新总体统计
                total_stats['total_sent'] += 1
                if ping_stats['success']:
                    total_stats['total_received'] += 1
                    if ping_stats['times']:
                        total_stats['times'].extend(ping_stats['times'])
                else:
                    total_stats['total_lost'] += 1
                
                # 计算总体统计
                total_stats['packet_loss'] = (total_stats['total_lost'] / total_stats['total_sent']) * 100
                if total_stats['times']:
                    total_stats['min_time'] = min(total_stats['times'])
                    total_stats['max_time'] = max(total_stats['times'])
                    total_stats['avg_time'] = int(mean(total_stats['times']))
                
                # 调用回调函数
                callback(ping_stats, total_stats)
            
            # 等待间隔时间
            if not self.stop_event.wait(interval):
                continue
            else:
                break
    
    def batch_ping(self, hosts, count=5, timeout=300, max_workers=25):
        """批量ping测试"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有ping任务
            future_to_host = {
                executor.submit(self.ping_single, host, count, timeout): host 
                for host in hosts
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    result = future.result()
                    stats = self.parse_ping_result(result['output'])
                    results[host] = {
                        'result': result,
                        'stats': stats
                    }
                except Exception as e:
                    results[host] = {
                        'result': {'success': False, 'error': str(e), 'host': host},
                        'stats': {'success': False, 'host': host}
                    }
        
        return results
    
    def ping_ip_range(self, ip_range_str, count=5, timeout=300, max_workers=25, callback=None):
        """Ping IP范围"""
        try:
            # 解析IP范围
            ips = parse_ip_range(ip_range_str)
            
            if callback:
                callback({
                    'type': 'info',
                    'message': f"解析到 {len(ips)} 个IP地址，开始批量ping测试..."
                })
            
            # 批量ping
            results = self.batch_ping(ips, count, timeout, max_workers)
            
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
    
    def start_continuous_ping(self, host, interval=1, timeout=300, callback=None):
        """启动连续ping测试（在后台线程中运行）"""
        if self.is_running:
            return False
            
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = self.executor.submit(self.continuous_ping, host, interval, timeout, callback)
        return True
    
    def stop_ping(self):
        """停止ping测试"""
        self.is_running = False
        self.stop_event.set()
        
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None


# 向后兼容的简单函数
def ping(host, count=4):
    """简单的ping函数（向后兼容）"""
    service = PingService()
    result = service.ping_single(host, count)
    return result['output']


def ping_with_stats(host, count=5, timeout=300):
    """带统计信息的ping函数"""
    service = PingService()
    result = service.ping_single(host, count, timeout)
    stats = service.parse_ping_result(result['output'])
    return {
        'raw_output': result['output'],
        'stats': stats,
        'success': result['success'],
        'error': result['error']
    }
