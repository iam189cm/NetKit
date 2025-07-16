
import subprocess
import threading
import time
import re
import socket
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


class TracerouteService:
    """路由追踪服务类"""
    
    def __init__(self):
        self.is_running = False
        self.stop_event = threading.Event()
        self.process = None
        
    def start_traceroute(self, target, max_hops=30, timeout=5000, callback=None):
        """开始路由追踪"""
        if self.is_running:
            return False
            
        self.is_running = True
        self.stop_event.clear()
        
        # 在后台线程中执行traceroute
        def run_traceroute():
            try:
                # 使用Windows的tracert命令
                cmd = ['tracert', '-d', '-h', str(max_hops), '-w', str(timeout), target]
                
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='gbk',
                    bufsize=1,
                    universal_newlines=True
                )
                
                hop_number = 0
                
                # 实时读取输出
                for line in iter(self.process.stdout.readline, ''):
                    if self.stop_event.is_set():
                        break
                        
                    if line.strip():
                        parsed_hop = self.parse_tracert_line(line.strip(), hop_number)
                        if parsed_hop:
                            hop_number = parsed_hop['hop']
                            # 异步解析主机名
                            if parsed_hop['ip'] and parsed_hop['ip'] != '*':
                                self.resolve_hostname_async(parsed_hop, callback)
                            else:
                                if callback:
                                    callback(parsed_hop)
                
                # 等待进程结束
                self.process.wait()
                
            except Exception as e:
                if callback:
                    callback({
                        'error': True,
                        'message': f"路由追踪出错: {str(e)}"
                    })
            finally:
                self.is_running = False
                self.process = None
        
        # 启动后台线程
        thread = threading.Thread(target=run_traceroute, daemon=True)
        thread.start()
        return True
    
    def stop_traceroute(self):
        """停止路由追踪"""
        self.stop_event.set()
        self.is_running = False
        
        if self.process:
            try:
                self.process.terminate()
                # 等待进程结束，最多等待3秒
                self.process.wait(timeout=3)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            finally:
                self.process = None
    
    def parse_tracert_line(self, line, current_hop):
        """解析tracert输出行"""
        # 跳过标题行和空行
        if not line or 'Tracing route to' in line or 'over a maximum of' in line:
            return None
        
        # 匹配跳数行的模式
        # 例如: "  1    <1 ms    <1 ms    <1 ms  192.168.1.1"
        # 或者: "  2     *        *        *     Request timed out."
        hop_pattern = r'^\s*(\d+)\s+'
        hop_match = re.match(hop_pattern, line)
        
        if not hop_match:
            return None
            
        hop_number = int(hop_match.group(1))
        remaining_line = line[hop_match.end():]
        
        # 检查是否是超时行
        if 'Request timed out' in line or '*' in remaining_line:
            return {
                'hop': hop_number,
                'ip': '*',
                'hostname': '*',
                'times': ['*', '*', '*'],
                'avg_time': '*',
                'timeout': True
            }
        
        # 解析时间和IP地址
        # 匹配时间模式 (例如: "<1 ms", "12 ms", "*")
        time_pattern = r'(?:(\d+)\s*ms|(<1)\s*ms|\*)'
        times = re.findall(time_pattern, remaining_line)
        
        # 提取IP地址
        ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'
        ip_match = re.search(ip_pattern, remaining_line)
        ip_address = ip_match.group(1) if ip_match else '*'
        
        # 处理时间数据
        parsed_times = []
        numeric_times = []
        
        for time_match in times:
            if time_match[0]:  # 普通数字时间
                time_val = int(time_match[0])
                parsed_times.append(f"{time_val} ms")
                numeric_times.append(time_val)
            elif time_match[1]:  # <1 ms的情况
                parsed_times.append("<1 ms")
                numeric_times.append(0)
            else:  # * 的情况
                parsed_times.append("*")
        
        # 计算平均时间
        if numeric_times:
            avg_time = sum(numeric_times) / len(numeric_times)
            avg_time_str = f"{avg_time:.0f} ms" if avg_time >= 1 else "<1 ms"
        else:
            avg_time_str = "*"
        
        return {
            'hop': hop_number,
            'ip': ip_address,
            'hostname': '',  # 稍后异步解析
            'times': parsed_times,
            'avg_time': avg_time_str,
            'timeout': False
        }
    
    def resolve_hostname_async(self, hop_data, callback):
        """异步解析主机名"""
        def resolve():
            try:
                if hop_data['ip'] and hop_data['ip'] != '*':
                    # 尝试反向DNS解析
                    hostname = socket.gethostbyaddr(hop_data['ip'])[0]
                    hop_data['hostname'] = hostname
                else:
                    hop_data['hostname'] = '*'
            except:
                hop_data['hostname'] = hop_data['ip']  # 解析失败时使用IP
            
            if callback:
                callback(hop_data)
        
        # 使用线程池进行异步解析
        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(resolve)


# 向后兼容的简单函数
def traceroute(host, max_hops=30):
    """简单的traceroute函数（向后兼容）"""
    try:
        cmd = ['tracert', '-d', '-h', str(max_hops), host]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk')
        return result.stdout
    except Exception as e:
        return f"Traceroute error: {str(e)}"


def traceroute_with_callback(host, max_hops=30, timeout=300, callback=None):
    """带回调的traceroute函数"""
    service = TracerouteService()
    return service.start_traceroute(host, max_hops, timeout, callback)
