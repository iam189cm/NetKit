import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.services.ping import PingService, ping_with_stats, parse_ip_range
import tkinter.messagebox as mbox
import threading
from datetime import datetime


class PingFrame(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.ping_service = PingService()
        self.setup_ui()
        
    def setup_ui(self):
        """设置Ping测试界面"""
        # 标题
        title = tb.Label(
            self, 
            text="Ping 网络测试", 
            font=('Arial', 18, 'bold'),
            bootstyle=SUCCESS
        )
        title.pack(pady=(0, 20))
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 左侧配置区域
        left_frame = tb.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(0, 10))
        
        # 目标配置
        target_frame = tb.LabelFrame(left_frame, text="目标设置", padding=15)
        target_frame.pack(fill=X, pady=(0, 10))
        
        # 目标地址/范围
        target_input_frame = tb.Frame(target_frame)
        target_input_frame.pack(fill=X, pady=(0, 10))
        
        tb.Label(target_input_frame, text="目标地址/范围:").pack(anchor=W, pady=(0, 5))
        self.target_entry = tb.Entry(target_input_frame, width=30)
        self.target_entry.pack(fill=X)
        
        # 添加说明文本
        help_text = tb.Label(
            target_input_frame,
            text="支持格式: 单个IP、IP范围(1.1.1.1-1.1.1.100)、CIDR(192.168.1.0/24)、主机名",
            font=('Arial', 8),
            bootstyle=SECONDARY
        )
        help_text.pack(anchor=W, pady=(5, 0))
        
        # 测试参数配置
        params_frame = tb.LabelFrame(left_frame, text="测试参数", padding=15)
        params_frame.pack(fill=X, pady=(0, 10))
        
        # 参数网格布局
        params_grid = tb.Frame(params_frame)
        params_grid.pack(fill=X)
        
        # Ping次数
        tb.Label(params_grid, text="Ping次数:").grid(row=0, column=0, sticky=W, pady=5)
        self.count_var = tb.StringVar(value="5")
        count_spinbox = tb.Spinbox(
            params_grid, 
            from_=1, to=100, 
            textvariable=self.count_var,
            width=10
        )
        count_spinbox.grid(row=0, column=1, padx=(10, 0), pady=5, sticky=W)
        
        # 超时时间
        tb.Label(params_grid, text="超时时间(ms):").grid(row=1, column=0, sticky=W, pady=5)
        self.timeout_var = tb.StringVar(value="300")
        timeout_spinbox = tb.Spinbox(
            params_grid, 
            from_=100, to=5000, 
            increment=100,
            textvariable=self.timeout_var,
            width=10
        )
        timeout_spinbox.grid(row=1, column=1, padx=(10, 0), pady=5, sticky=W)
        
        # 并发数
        tb.Label(params_grid, text="并发数:").grid(row=2, column=0, sticky=W, pady=5)
        self.concurrent_var = tb.StringVar(value="25")
        concurrent_spinbox = tb.Spinbox(
            params_grid, 
            from_=1, to=100, 
            textvariable=self.concurrent_var,
            width=10
        )
        concurrent_spinbox.grid(row=2, column=1, padx=(10, 0), pady=5, sticky=W)
        
        # 连续测试间隔
        tb.Label(params_grid, text="连续间隔(s):").grid(row=3, column=0, sticky=W, pady=5)
        self.interval_var = tb.StringVar(value="1")
        interval_spinbox = tb.Spinbox(
            params_grid, 
            from_=1, to=60, 
            textvariable=self.interval_var,
            width=10
        )
        interval_spinbox.grid(row=3, column=1, padx=(10, 0), pady=5, sticky=W)
        
        # 测试模式选择
        mode_frame = tb.LabelFrame(left_frame, text="测试模式", padding=15)
        mode_frame.pack(fill=X, pady=(0, 10))
        
        # 单次测试按钮
        tb.Button(
            mode_frame,
            text="单次测试",
            bootstyle=INFO,
            command=self.single_ping,
            width=20
        ).pack(fill=X, pady=(0, 5))
        
        # 批量/范围测试按钮
        tb.Button(
            mode_frame,
            text="批量/范围测试",
            bootstyle=SUCCESS,
            command=self.range_ping,
            width=20
        ).pack(fill=X, pady=(0, 5))
        
        # 连续测试按钮
        tb.Button(
            mode_frame,
            text="连续测试",
            bootstyle=WARNING,
            command=self.start_continuous_ping,
            width=20
        ).pack(fill=X, pady=(0, 5))
        
        # 停止测试按钮
        tb.Button(
            mode_frame,
            text="停止测试",
            bootstyle=DANGER,
            command=self.stop_ping,
            width=20
        ).pack(fill=X)
        
        # 右侧结果显示区域
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # 统计信息显示
        stats_frame = tb.LabelFrame(right_frame, text="统计信息", padding=10)
        stats_frame.pack(fill=X, pady=(0, 10))
        
        # 创建统计标签
        stats_grid = tb.Frame(stats_frame)
        stats_grid.pack(fill=X)
        
        # 统计信息标签
        stat_labels = [
            ("当前目标:", "current_target_label"),
            ("总IP数:", "total_ips_label"),
            ("已发送:", "sent_label"),
            ("已接收:", "received_label"),
            ("丢包率:", "loss_label"),
            ("成功率:", "success_rate_label"),
            ("平均时间:", "avg_label"),
            ("运行时间:", "runtime_label")
        ]
        
        for i, (text, attr_name) in enumerate(stat_labels):
            row = i // 2
            col = (i % 2) * 2
            
            tb.Label(stats_grid, text=text).grid(row=row, column=col, sticky=W, padx=5, pady=2)
            label = tb.Label(stats_grid, text="--", bootstyle=INFO)
            label.grid(row=row, column=col+1, sticky=W, padx=5, pady=2)
            setattr(self, attr_name, label)
        
        # 结果显示区域
        result_frame = tb.LabelFrame(right_frame, text="测试结果", padding=10)
        result_frame.pack(fill=BOTH, expand=True)
        
        # 结果文本框
        self.result_text = tb.Text(
            result_frame,
            height=20,
            state=DISABLED,
            wrap=WORD,
            font=('Consolas', 9)
        )
        
        # 滚动条
        scrollbar = tb.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 清空结果按钮
        clear_btn_frame = tb.Frame(result_frame)
        clear_btn_frame.pack(fill=X, pady=(10, 0))
        
        tb.Button(
            clear_btn_frame,
            text="清空结果",
            bootstyle=LIGHT,
            command=self.clear_result,
            width=12
        ).pack(side=RIGHT)
        
        # 初始化
        self.append_result("=== Netkit Ping网络测试工具 ===\n")
        self.append_result("请输入目标地址/范围并选择测试模式\n")
        self.append_result("支持格式: 单个IP、IP范围(1.1.1.1-1.1.1.100)、CIDR(192.168.1.0/24)、主机名\n\n")
        self.reset_stats()
        
    def single_ping(self):
        """单次ping测试"""
        target = self.target_entry.get().strip()
        if not target:
            mbox.showwarning("输入错误", "请输入目标地址")
            return
            
        count = int(self.count_var.get())
        timeout = int(self.timeout_var.get())
        
        self.append_result(f"\n开始单次测试 {target} (数据包数: {count}, 超时: {timeout}ms)...\n")
        self.append_result("-" * 60 + "\n")
        
        # 在后台线程中执行ping
        def do_ping():
            try:
                result = ping_with_stats(target, count, timeout)
                
                # 在主线程中更新UI
                self.after(0, lambda: self.show_ping_result(result))
                
            except Exception as e:
                self.after(0, lambda: self.append_result(f"测试出错: {str(e)}\n"))
        
        threading.Thread(target=do_ping, daemon=True).start()
    
    def range_ping(self):
        """批量/范围ping测试"""
        target = self.target_entry.get().strip()
        if not target:
            mbox.showwarning("输入错误", "请输入目标地址或范围")
            return
            
        count = int(self.count_var.get())
        timeout = int(self.timeout_var.get())
        concurrent = int(self.concurrent_var.get())
        
        self.append_result(f"\n开始批量/范围测试: {target}\n")
        self.append_result(f"参数: 数据包数={count}, 超时={timeout}ms, 并发数={concurrent}\n")
        self.append_result("-" * 60 + "\n")
        
        self.reset_stats()
        
        # 在后台线程中执行ping
        def do_range_ping():
            try:
                self.ping_service.ping_ip_range(
                    target, 
                    count, 
                    timeout, 
                    concurrent,
                    self.on_range_ping_result
                )
                
            except Exception as e:
                self.after(0, lambda: self.append_result(f"范围测试出错: {str(e)}\n"))
        
        threading.Thread(target=do_range_ping, daemon=True).start()
    
    def start_continuous_ping(self):
        """开始连续ping测试"""
        target = self.target_entry.get().strip()
        if not target:
            mbox.showwarning("输入错误", "请输入目标地址")
            return
            
        if self.ping_service.is_running:
            mbox.showwarning("测试进行中", "请先停止当前测试")
            return
            
        # 连续测试只支持单个目标
        try:
            ips = parse_ip_range(target)
            if len(ips) > 1:
                mbox.showwarning("输入错误", "连续测试只支持单个目标地址")
                return
            target = ips[0]
        except:
            pass  # 如果解析失败，使用原始输入（可能是主机名）
            
        interval = int(self.interval_var.get())
        timeout = int(self.timeout_var.get())
        
        self.append_result(f"\n开始连续测试 {target} (间隔: {interval}s, 超时: {timeout}ms)...\n")
        self.append_result("-" * 60 + "\n")
        
        self.reset_stats()
        self.current_target_label.config(text=target)
        
        # 启动连续ping
        success = self.ping_service.start_continuous_ping(
            target, 
            interval, 
            timeout, 
            self.on_ping_result
        )
        
        if not success:
            mbox.showerror("启动失败", "无法启动连续ping测试")
    
    def stop_ping(self):
        """停止ping测试"""
        if self.ping_service.is_running:
            self.ping_service.stop_ping()
            self.append_result("\n测试已停止\n")
        else:
            self.append_result("当前没有正在运行的测试\n")
    
    def on_range_ping_result(self, data):
        """范围ping结果回调"""
        # 在主线程中更新UI
        self.after(0, lambda: self.update_range_ping_ui(data))
    
    def update_range_ping_ui(self, data):
        """更新范围ping的UI"""
        if data['type'] == 'info':
            self.append_result(f"{data['message']}\n")
        elif data['type'] == 'error':
            self.append_result(f"❌ {data['message']}\n")
        elif data['type'] == 'results':
            self.show_range_results(data['results'], data['total_count'])
    
    def on_ping_result(self, ping_stats, total_stats):
        """连续ping结果回调"""
        # 在主线程中更新UI
        self.after(0, lambda: self.update_continuous_ping_ui(ping_stats, total_stats))
    
    def update_continuous_ping_ui(self, ping_stats, total_stats):
        """更新连续ping的UI"""
        # 更新统计信息
        self.sent_label.config(text=str(total_stats['total_sent']))
        self.received_label.config(text=str(total_stats['total_received']))
        self.loss_label.config(text=f"{total_stats['packet_loss']:.1f}%")
        
        if total_stats['times']:
            self.avg_label.config(text=f"{total_stats['avg_time']}ms")
        
        # 运行时间
        runtime = datetime.now().timestamp() - total_stats['start_time']
        self.runtime_label.config(text=f"{runtime:.0f}s")
        
        # 显示单次结果
        timestamp = datetime.fromtimestamp(ping_stats['timestamp']).strftime("%H:%M:%S")
        seq = ping_stats['sequence']
        
        if ping_stats['success'] and ping_stats['times']:
            time_ms = ping_stats['times'][0]
            self.append_result(f"[{timestamp}] #{seq}: 时间={time_ms}\n")
        else:
            self.append_result(f"[{timestamp}] #{seq}: 请求超时\n")
    
    def show_ping_result(self, result):
        """显示单次ping测试结果"""
        if result['success']:
            stats = result['stats']
            self.append_result(f"目标: {stats['host']}\n")
            self.append_result(f"数据包: 已发送 {stats['packets_sent']}, 已接收 {stats['packets_received']}, 丢失 {stats['packets_sent'] - stats['packets_received']}\n")
            self.append_result(f"丢包率: {stats['packet_loss']:.1f}%\n")
            
            if stats['times']:
                self.append_result(f"往返时间: 最小 {stats['min_time']}ms, 最大 {stats['max_time']}ms, 平均 {stats['avg_time']}ms\n")
            
            if stats['success']:
                self.append_result("✓ 测试成功\n")
            else:
                self.append_result("✗ 测试失败\n")
        else:
            self.append_result(f"✗ 测试失败: {result['error']}\n")
        
        self.append_result("\n")
    
    def show_range_results(self, results, total_count):
        """显示范围测试结果"""
        self.append_result(f"批量测试完成，共测试 {total_count} 个目标\n\n")
        
        success_count = 0
        total_avg_time = 0
        valid_times = 0
        
        for host, data in results.items():
            stats = data['stats']
            if stats['success']:
                success_count += 1
                self.append_result(f"✓ {host}: 平均 {stats['avg_time']}ms, 丢包率 {stats['packet_loss']:.1f}%\n")
                if stats['avg_time'] and stats['avg_time'] != '*':
                    total_avg_time += stats['avg_time']
                    valid_times += 1
            else:
                self.append_result(f"✗ {host}: 无法访问\n")
        
        # 更新统计信息
        self.total_ips_label.config(text=str(total_count))
        self.success_rate_label.config(text=f"{(success_count/total_count)*100:.1f}%")
        
        if valid_times > 0:
            overall_avg = total_avg_time / valid_times
            self.avg_label.config(text=f"{overall_avg:.0f}ms")
        
        self.append_result(f"\n总结: {success_count}/{total_count} 个目标可达 ({(success_count/total_count)*100:.1f}%)\n\n")
    
    def reset_stats(self):
        """重置统计信息显示"""
        self.current_target_label.config(text="--")
        self.total_ips_label.config(text="--")
        self.sent_label.config(text="0")
        self.received_label.config(text="0")
        self.loss_label.config(text="0%")
        self.success_rate_label.config(text="--")
        self.avg_label.config(text="--")
        self.runtime_label.config(text="0s")
    
    def clear_result(self):
        """清空结果框"""
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.configure(state=DISABLED)
        self.append_result("=== 结果已清空 ===\n\n")
    
    def append_result(self, text):
        """向结果框追加文本"""
        self.result_text.configure(state=NORMAL)
        self.result_text.insert(END, text)
        self.result_text.configure(state=DISABLED)
        self.result_text.see(END) 