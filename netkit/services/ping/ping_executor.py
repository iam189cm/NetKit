"""
Ping执行器模块

负责执行实际的ping命令并返回原始结果
支持Windows系统的ping命令，处理编码问题
"""

import subprocess
import concurrent.futures
import threading
import time


class PingExecutor:
    """Ping命令执行器"""
    
    def __init__(self):
        self.is_running = False
        self.executor = None
        self.stop_event = threading.Event()
        
    def ping_single(self, host, count=4, timeout=3000):
        """
        执行单次ping测试
        
        Args:
            host (str): 目标主机地址
            count (int): ping次数
            timeout (int): 超时时间(毫秒)
            
        Returns:
            dict: 包含执行结果的字典
        """
        try:
            cmd = ['ping', '-n', str(count), '-w', str(timeout), host]
            
            # 处理Windows系统的编码问题
            result = self._run_ping_command(cmd)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'host': host,
                'return_code': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'host': host,
                'return_code': -1
            }
    
    def _run_ping_command(self, cmd):
        """
        运行ping命令，处理编码问题
        
        Args:
            cmd (list): 命令参数列表
            
        Returns:
            subprocess.CompletedProcess: 命令执行结果
        """
        # Windows系统中netsh命令存在编码问题，特别是中文网卡名称会出现乱码
        # 解决方案是使用多种编码尝试机制：先尝试UTF-8，失败后尝试GBK，最后使用系统默认编码
        encodings = ['utf-8', 'gbk', 'cp936', None]
        
        for encoding in encodings:
            try:
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    encoding=encoding,
                    timeout=30  # 防止命令hang住
                )
                return result
            except (UnicodeDecodeError, UnicodeError):
                continue
            except subprocess.TimeoutExpired:
                # 超时情况下返回失败结果
                return subprocess.CompletedProcess(
                    cmd, 1, '', 'Command timeout'
                )
            except Exception as e:
                if encoding is None:  # 最后一次尝试失败
                    return subprocess.CompletedProcess(
                        cmd, 1, '', str(e)
                    )
                continue
        
        # 如果所有编码都失败，返回错误结果
        return subprocess.CompletedProcess(
            cmd, 1, '', 'Encoding error: unable to decode output'
        )
    
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
        completed = 0
        total = len(hosts)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有ping任务
            future_to_host = {
                executor.submit(self.ping_single, host, count, timeout): host 
                for host in hosts
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_host):
                host = future_to_host[future]
                completed += 1
                
                try:
                    result = future.result()
                    results[host] = result
                    
                    # 调用进度回调
                    if progress_callback:
                        progress_callback(host, result, completed, total)
                        
                except Exception as e:
                    error_result = {
                        'success': False, 
                        'error': str(e), 
                        'host': host,
                        'output': '',
                        'return_code': -1
                    }
                    results[host] = error_result
                    
                    if progress_callback:
                        progress_callback(host, error_result, completed, total)
        
        return results
    
    def continuous_ping(self, host, interval=1, timeout=3000, callback=None):
        """
        连续ping测试
        
        Args:
            host (str): 目标主机地址
            interval (int): ping间隔时间(秒)
            timeout (int): 超时时间(毫秒)
            callback (callable): 结果回调函数
        """
        self.is_running = True
        self.stop_event.clear()
        
        sequence = 0
        start_time = time.time()
        
        while self.is_running and not self.stop_event.is_set():
            sequence += 1
            
            # 执行单次ping
            result = self.ping_single(host, count=1, timeout=timeout)
            result['sequence'] = sequence
            result['timestamp'] = time.time()
            result['elapsed_time'] = time.time() - start_time
            
            # 调用回调函数
            if callback:
                callback(result)
            
            # 等待间隔时间
            if not self.stop_event.wait(interval):
                continue
            else:
                break
    
    def start_continuous_ping(self, host, interval=1, timeout=3000, callback=None):
        """
        在后台线程中启动连续ping测试
        
        Args:
            host (str): 目标主机地址
            interval (int): ping间隔时间(秒)
            timeout (int): 超时时间(毫秒)
            callback (callable): 结果回调函数
            
        Returns:
            bool: 是否成功启动
        """
        if self.is_running:
            return False
            
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = self.executor.submit(
            self.continuous_ping, host, interval, timeout, callback
        )
        return True
    
    def stop_ping(self):
        """停止ping测试"""
        self.is_running = False
        self.stop_event.set()
        
        if self.executor:
            self.executor.shutdown(wait=False)
            self.executor = None
    
    def is_ping_running(self):
        """检查是否有ping测试正在运行"""
        return self.is_running 