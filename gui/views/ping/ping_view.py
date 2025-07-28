"""
Ping测试主视图

整合所有ping测试相关的GUI组件
提供完整的ping测试用户界面
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.ping import PingService, parse_ip_range
from .config_panel import PingConfigPanel, PingParametersPanel
from .result_display import PingResultDisplay
from .stats_panel import PingStatsPanel
from .test_controller import PingTestController
import tkinter.messagebox as mbox
import threading
from datetime import datetime


class PingFrame(tb.Frame):
    """Ping测试主框架"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.ping_service = PingService()
        self.setup_ui()
        self.setup_callbacks()
        
    def setup_ui(self):
        """设置Ping测试界面"""
        # 标题
        title = tb.Label(
            self, 
            text="Ping 网络测试",
            font=('微软雅黑', ui_helper.scale_size(16), 'bold'),
            bootstyle=SUCCESS
        )
        title.pack(pady=(0, ui_helper.get_padding(20)))
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 左侧配置区域
        left_frame = tb.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, ui_helper.get_padding(10)))
        
        # 配置面板
        self.config_panel = PingConfigPanel(left_frame)
        self.config_panel.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        # 参数配置面板
        self.params_panel = PingParametersPanel(left_frame)
        self.params_panel.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        # 测试控制面板
        self.controller = PingTestController(left_frame)
        self.controller.pack(fill=X)
        
        # 右侧结果显示区域
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # 统计信息面板
        self.stats_panel = PingStatsPanel(right_frame)
        self.stats_panel.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        # 结果显示面板
        self.result_display = PingResultDisplay(right_frame)
        self.result_display.pack(fill=BOTH, expand=True)
    
    def setup_callbacks(self):
        """设置回调函数"""
        # 注册测试控制回调
        self.controller.register_callback('single', self.single_ping)
        self.controller.register_callback('batch', self.range_ping)
        self.controller.register_callback('continuous', self.start_continuous_ping)
        self.controller.register_callback('stop', self.stop_ping)
        
        # 设置结果显示的CSV导出回调
        self.result_display.export_csv = self.export_csv_results
    
    def single_ping(self):
        """单次ping测试"""
        target = self.config_panel.get_target()
        if not target:
            mbox.showwarning("输入错误", "请输入目标地址")
            return
            
        params = self.params_panel.get_parameters()
        
        self.result_display.append_result(
            f"\n开始单次测试 {target} (数据包数: {params['count']}, 超时: {params['timeout']}ms)...\n"
        )
        self.result_display.append_result("-" * 60 + "\n")
        
        try:
            result = self.ping_service.ping_with_stats(target, params['count'], params['timeout'])
            
            # 更新统计面板
            self.stats_panel.update_stats({
                'current_host': target,
                'total_hosts': 1
            })
            
            # 显示结果
            self.result_display.show_ping_result(result['stats'])
            
            # 更新控制器进度
            self.controller.update_progress(100, "单次测试完成")
            
        except Exception as e:
            self.result_display.append_result(f"测试出错: {str(e)}\n", "error")
            self.controller.update_progress(0, "测试失败")
    
    def range_ping(self):
        """批量/范围ping测试"""
        target = self.config_panel.get_target()
        if not target:
            mbox.showwarning("输入错误", "请输入目标地址或范围")
            return
            
        params = self.params_panel.get_parameters()
        
        self.result_display.append_result(f"\n开始批量/范围测试: {target}\n")
        self.result_display.append_result(
            f"参数: 数据包数={params['count']}, 超时={params['timeout']}ms, 并发数={params['concurrent']}\n"
        )
        self.result_display.append_result("-" * 60 + "\n")
        
        # 重置统计
        self.stats_panel.reset_stats()
        
        try:
            self.ping_service.ping_ip_range(
                target, 
                params['count'], 
                params['timeout'], 
                params['concurrent'],
                self.on_range_ping_result
            )
        except Exception as e:
            self.result_display.append_result(f"范围测试出错: {str(e)}\n", "error")
            self.controller.update_progress(0, "测试失败")
    
    def start_continuous_ping(self):
        """开始连续ping测试"""
        target = self.config_panel.get_target()
        if not target:
            mbox.showwarning("输入错误", "请输入目标地址")
            return False
            
        if self.ping_service.is_running():
            mbox.showwarning("测试进行中", "请先停止当前测试")
            return False
            
        # 连续测试只支持单个目标
        try:
            ips = parse_ip_range(target)
            if len(ips) > 1:
                mbox.showwarning("输入错误", "连续测试只支持单个目标地址")
                return False
            target = ips[0]
        except:
            pass  # 如果解析失败，使用原始输入（可能是主机名）
            
        params = self.params_panel.get_parameters()
        
        self.result_display.append_result(
            f"\n开始连续测试 {target} (间隔: {params['interval']}s, 超时: {params['timeout']}ms)...\n"
        )
        self.result_display.append_result("-" * 60 + "\n")
        
        # 重置统计
        self.stats_panel.reset_stats()
        self.stats_panel.update_stats({'current_host': target})
        self.stats_panel.update_connection_status(False, True)
        
        # 启动连续ping
        success = self.ping_service.start_continuous_ping(
            target, 
            params['interval'], 
            params['timeout'], 
            self.on_continuous_ping_result
        )
        
        if not success:
            self.stats_panel.update_connection_status(False, False)
            return False
            
        return True
    
    def stop_ping(self):
        """停止ping测试"""
        if self.ping_service.is_running():
            self.ping_service.stop_ping()
            self.result_display.append_result("\n测试已停止\n", "warning")
            self.stats_panel.update_connection_status(False, False)
        else:
            self.result_display.append_result("当前没有正在运行的测试\n", "info")
    
    def on_range_ping_result(self, data):
        """范围ping结果回调"""
        # 在主线程中更新UI
        self.after(0, lambda: self.update_range_ping_ui(data))
    
    def update_range_ping_ui(self, data):
        """更新范围ping的UI"""
        if data['type'] == 'info':
            self.result_display.append_result(f"{data['message']}\n", "info")
            # 更新统计面板
            if "个IP地址" in data['message']:
                try:
                    count = int(data['message'].split()[1])
                    self.stats_panel.update_stats({'total_hosts': count})
                except:
                    pass
                    
        elif data['type'] == 'error':
            self.result_display.append_result(f"❌ {data['message']}\n", "error")
            self.controller.update_progress(0, "测试失败")
            
        elif data['type'] == 'progress':
            # 更新进度
            progress = (data['completed'] / data['total']) * 100
            self.controller.update_progress(progress, f"测试进度: {data['completed']}/{data['total']}")
            
        elif data['type'] == 'results':
            self.show_range_results(data['results'], data['total_count'])
            self.controller.update_progress(100, "批量测试完成")
    
    def on_continuous_ping_result(self, ping_stats, total_stats):
        """连续ping结果回调"""
        # 在主线程中更新UI
        self.after(0, lambda: self.update_continuous_ping_ui(ping_stats, total_stats))
    
    def update_continuous_ping_ui(self, ping_stats, total_stats):
        """更新连续ping的UI"""
        # 更新统计面板
        self.stats_panel.update_stats(total_stats)
        self.stats_panel.update_connection_status(ping_stats['success'], True)
        
        # 显示单次结果
        timestamp = datetime.fromtimestamp(ping_stats.get('timestamp', datetime.now().timestamp())).strftime("%H:%M:%S")
        seq = getattr(ping_stats, 'sequence', total_stats['total_sent'])
        
        if ping_stats['success'] and ping_stats['times']:
            time_ms = ping_stats['times'][0]
            self.result_display.show_continuous_result(seq, timestamp, True, time_ms)
        else:
            self.result_display.show_continuous_result(seq, timestamp, False)
    
    def show_range_results(self, results, total_count):
        """显示范围测试结果"""
        self.result_display.append_result(f"批量测试完成，共测试 {total_count} 个目标\n\n", "info")
        
        success_count = 0
        total_avg_time = 0
        valid_times = 0
        
        for host, data in results.items():
            stats = data['stats']
            if stats['success']:
                success_count += 1
                self.result_display.append_result(
                    f"✓ {host}: 平均 {stats['avg_time']}ms, 丢包率 {stats['packet_loss']:.1f}%\n", 
                    "success"
                )
                if stats['avg_time'] and stats['avg_time'] > 0:
                    total_avg_time += stats['avg_time']
                    valid_times += 1
            else:
                self.result_display.append_result(f"✗ {host}: 无法访问\n", "error")
        
        # 更新统计信息
        success_rate = (success_count / total_count) * 100
        overall_avg = total_avg_time / valid_times if valid_times > 0 else 0
        
        self.stats_panel.update_stats({
            'total_hosts': total_count,
            'success_rate': success_rate,
            'avg_time': overall_avg
        })
        
        self.result_display.append_result(
            f"\n总结: {success_count}/{total_count} 个目标可达 ({success_rate:.1f}%)\n\n", 
            "success" if success_rate >= 80 else "warning" if success_rate >= 50 else "error"
        )
        
        # 显示测试摘要
        duration = self.ping_service.get_stats_manager().get_overall_stats().get('runtime', 0)
        self.controller.show_test_result_summary(success_count, total_count, duration)
    
    def export_csv_results(self):
        """导出CSV格式的结果"""
        try:
            csv_data = self.ping_service.export_results_csv()
            
            if not csv_data or csv_data.count('\n') <= 1:
                mbox.showwarning("警告", "没有可导出的数据")
                return
            
            import tkinter.filedialog as fd
            filename = fd.asksaveasfilename(
                title="导出CSV结果",
                defaultextension=".csv",
                filetypes=[
                    ("CSV文件", "*.csv"),
                    ("所有文件", "*.*")
                ]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8-sig') as f:  # 使用UTF-8-BOM编码以便Excel正确显示
                    f.write(csv_data)
                mbox.showinfo("成功", f"CSV数据已导出到: {filename}")
                
        except Exception as e:
            mbox.showerror("错误", f"导出失败: {str(e)}")
    
    def get_test_summary(self):
        """获取测试摘要信息"""
        return {
            'service_stats': self.ping_service.get_stats_manager().get_overall_stats(),
            'ui_stats': self.stats_panel.get_current_stats(),
            'test_options': self.controller.get_test_options(),
            'parameters': self.params_panel.get_parameters(),
            'target': self.config_panel.get_target()
        }
    
    def reset_all(self):
        """重置所有组件状态"""
        self.config_panel.clear_target()
        self.params_panel.reset_to_defaults()
        self.stats_panel.reset_stats()
        self.result_display.clear_results()
        self.controller.set_testing_state(False)
        self.ping_service.stop_ping()
    
    def load_test_config(self, config):
        """加载测试配置"""
        if 'target' in config:
            self.config_panel.set_target(config['target'])
        if 'parameters' in config:
            self.params_panel.set_parameters(config['parameters'])
        if 'test_options' in config:
            self.controller.set_test_options(config['test_options']) 