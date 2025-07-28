"""
扫描控制器组件

负责ping扫描的控制逻辑、状态管理和结果处理
"""

import threading
from netkit.services.ping import PingService


class ScanController:
    """扫描控制器"""
    
    def __init__(self, view):
        self.view = view
        self.ping_service = PingService()
        self.scan_thread = None
        self.is_scanning = False
        
        # 统计数据
        self.stats = {
            'online_count': 0,
            'offline_count': 0,
            'total_count': 254
        }
    
    def start_scan(self, network_prefix):
        """开始扫描"""
        if self.is_scanning:
            return False
            
        self.network_prefix = network_prefix
        self.is_scanning = True
        
        # 重置统计
        self.reset_stats()
        
        # 启动扫描线程
        self.scan_thread = threading.Thread(target=self.scan_network, daemon=True)
        self.scan_thread.start()
        
        return True
    
    def stop_scan(self):
        """停止扫描"""
        self.is_scanning = False
        self.ping_service.stop_ping()
    
    def reset_stats(self):
        """重置统计数据"""
        self.stats = {
            'online_count': 0,
            'offline_count': 0,
            'total_count': 254
        }
    
    def scan_network(self):
        """扫描网络（在后台线程中运行）"""
        try:
            # 生成IP列表
            ip_list = []
            for i in range(1, 255):  # 1-254
                ip = f"{self.network_prefix}.{i}"
                ip_list.append(ip)
            
            # 使用ping服务进行批量扫描
            def on_progress(host, result, stats, completed, total):
                if not self.is_scanning:
                    return
                    
                # 提取IP后缀
                ip_suffix = int(host.split('.')[-1])
                
                # 在主线程中更新UI
                self.view.after(0, lambda: self.update_cell_result(ip_suffix, result, stats))
            
            # 执行批量ping
            self.ping_service.batch_ping(
                ip_list,
                count=1,  # 每个IP只ping一次
                timeout=1000,  # 1秒超时
                max_workers=25,  # 25个并发
                progress_callback=on_progress
            )
            
        except Exception as e:
            self.view.after(0, lambda: self.view.show_error(f"扫描过程中出现错误: {str(e)}"))
        finally:
            if self.is_scanning:
                self.view.after(0, self.scan_completed)
    
    def update_cell_result(self, ip_suffix, result, stats):
        """更新方格扫描结果"""
        # 通知视图更新方格状态
        self.view.update_cell_scanning(ip_suffix)
        
        # 延迟显示结果，让用户看到扫描过程
        def show_result():
            if stats['success']:
                self.view.update_cell_online(ip_suffix, stats)
                self.stats['online_count'] += 1
            else:
                self.view.update_cell_offline(ip_suffix, stats)
                self.stats['offline_count'] += 1
            
            # 更新统计显示
            self.view.update_stats(self.stats)
        
        # 延迟500ms显示结果
        self.view.after(500, show_result)
    
    def scan_completed(self):
        """扫描完成"""
        self.is_scanning = False
        
        # 通知视图扫描完成
        self.view.on_scan_completed(self.stats)
    
    def ping_single_ip(self, network_prefix, ip_suffix):
        """单独ping某个IP"""
        ip_address = f"{network_prefix}.{ip_suffix}"
        
        def do_ping():
            try:
                result = self.ping_service.ping_with_stats(ip_address, count=4, timeout=1000)
                
                # 在主线程中显示结果
                self.view.after(0, lambda: self.view.show_single_ping_result(ip_address, result))
                
            except Exception as e:
                self.view.after(0, lambda: self.view.show_error(f"Ping {ip_address} 失败: {str(e)}"))
        
        # 在后台线程中执行ping
        threading.Thread(target=do_ping, daemon=True).start()
        
        return True 