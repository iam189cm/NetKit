import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.traceroute import TracerouteService
import tkinter.messagebox as mbox
from datetime import datetime


class TracerouteFrame(tb.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.traceroute_service = TracerouteService()
        self.setup_ui()
        
    def setup_ui(self):
        """设置路由追踪界面"""
        # 标题
        title = tb.Label(
            self, 
            text="路由追踪 (Traceroute)",            bootstyle=WARNING
        )
        title.pack(pady=(ui_helper.get_padding(0), ui_helper.get_padding(20)))
        
        # 主要内容区域
        main_frame = tb.Frame(self)
        main_frame.pack(fill=BOTH, expand=True)
        
        # 左侧控制区域
        left_frame = tb.Frame(main_frame)
        left_frame.pack(side=LEFT, fill=Y, padx=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        # 输入参数区域
        input_frame = tb.LabelFrame(left_frame, text="追踪参数", padding=ui_helper.get_padding(15))
        input_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        # 目标地址
        target_frame = tb.Frame(input_frame)
        target_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(target_frame, text="目标地址:").pack(side=LEFT)
        self.target_entry = tb.Entry(target_frame, width=ui_helper.scale_size(25))
        self.target_entry.pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        self.target_entry.insert(0, "www.baidu.com")
        
        # 最大跳数（固定30跳）
        hops_frame = tb.Frame(input_frame)
        hops_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(hops_frame, text="最大跳数:").pack(side=LEFT)
        self.max_hops_label = tb.Label(hops_frame, text="30", bootstyle=INFO)
        self.max_hops_label.pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        # 超时时间（固定5秒）
        timeout_frame = tb.Frame(input_frame)
        timeout_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        tb.Label(timeout_frame, text="超时时间:").pack(side=LEFT)
        self.timeout_label = tb.Label(timeout_frame, text="5秒", bootstyle=INFO)
        self.timeout_label.pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        # 控制按钮
        btn_frame = tb.Frame(input_frame)
        btn_frame.pack(fill=X, pady=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        self.start_btn = tb.Button(
            btn_frame,
            text="开始追踪",
            bootstyle=WARNING,
            command=self.start_traceroute,
            width=ui_helper.scale_size(12)
        )
        self.start_btn.pack(side=LEFT, padx=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        self.stop_btn = tb.Button(
            btn_frame,
            text="停止追踪",
            bootstyle=DANGER,
            command=self.stop_traceroute,
            width=ui_helper.scale_size(12),
            state=DISABLED
        )
        self.stop_btn.pack(side=LEFT, padx=ui_helper.get_padding(5))
        
        # 状态信息区域
        status_frame = tb.LabelFrame(left_frame, text="追踪状态", padding=ui_helper.get_padding(15))
        status_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(10)))
        
        # 当前状态
        self.status_label = tb.Label(
            status_frame, 
            text="就绪", 
            bootstyle=INFO,        )
        self.status_label.pack(pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        # 进度信息
        progress_info_frame = tb.Frame(status_frame)
        progress_info_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        tb.Label(progress_info_frame, text="当前跳数:").pack(side=LEFT)
        self.current_hop_label = tb.Label(progress_info_frame, text="0", bootstyle=PRIMARY)
        self.current_hop_label.pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        # 开始时间
        start_time_frame = tb.Frame(status_frame)
        start_time_frame.pack(fill=X)
        
        tb.Label(start_time_frame, text="开始时间:").pack(side=LEFT)
        self.start_time_label = tb.Label(start_time_frame, text="--", bootstyle=SECONDARY)
        self.start_time_label.pack(side=LEFT, padx=(ui_helper.get_padding(10), ui_helper.get_padding(0)))
        
        # 常用目标快速选择
        quick_frame = tb.LabelFrame(left_frame, text="常用目标", padding=ui_helper.get_padding(10))
        quick_frame.pack(fill=X)
        
        common_targets = [
            "www.baidu.com", "www.google.com", "8.8.8.8", 
            "114.114.114.114", "www.qq.com", "www.163.com"
        ]
        
        for i, target in enumerate(common_targets):
            row = i // 2
            col = i % 2
            
            tb.Button(
                quick_frame,
                text=target,
                bootstyle=OUTLINE,
                command=lambda t=target: self.set_target(t),
                width=ui_helper.scale_size(15)
            ).grid(row=row, column=col, padx=ui_helper.get_padding(3), pady=ui_helper.get_padding(2), sticky=W)
        
        # 右侧结果显示区域
        right_frame = tb.Frame(main_frame)
        right_frame.pack(side=RIGHT, fill=BOTH, expand=True)
        
        result_frame = tb.LabelFrame(right_frame, text="追踪结果", padding=ui_helper.get_padding(10))
        result_frame.pack(fill=BOTH, expand=True)
        
        # 结果表头
        header_frame = tb.Frame(result_frame)
        header_frame.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        header_text = "跳数    响应时间1    响应时间2    响应时间3    IP地址           主机名"
        tb.Label(
            header_frame, 
            text=header_text,
            font=('Consolas', ui_helper.scale_size(10), 'bold'),
            bootstyle=INFO
        ).pack(anchor=W)
        
        # 分隔线
        separator = tb.Separator(result_frame, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(ui_helper.get_padding(0), ui_helper.get_padding(5)))
        
        # 结果文本框
        self.result_text = tb.Text(
            result_frame,
            height=ui_helper.scale_size(20),
            state=DISABLED,
            wrap=NONE,
            font=('Consolas', ui_helper.scale_size(10))
        )
        
        # 滚动条
        v_scrollbar = tb.Scrollbar(result_frame, orient=VERTICAL, command=self.result_text.yview)
        h_scrollbar = tb.Scrollbar(result_frame, orient=HORIZONTAL, command=self.result_text.xview)
        self.result_text.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.result_text.pack(side=LEFT, fill=BOTH, expand=True)
        v_scrollbar.pack(side=RIGHT, fill=Y)
        h_scrollbar.pack(side=BOTTOM, fill=X)
        
        # 清空结果按钮
        clear_btn_frame = tb.Frame(result_frame)
        clear_btn_frame.pack(fill=X, pady=(ui_helper.get_padding(5), ui_helper.get_padding(0)))
        
        tb.Button(
            clear_btn_frame,
            text="清空结果",
            bootstyle=LIGHT,
            command=self.clear_result,
            width=ui_helper.scale_size(12)
        ).pack(side=RIGHT)
        
        # 初始化
        self.append_result("=== Netkit 路由追踪工具 ===\n")
        self.append_result("请输入目标地址并点击'开始追踪'按钮\n\n")
        
    def set_target(self, target):
        """设置目标地址"""
        self.target_entry.delete(0, END)
        self.target_entry.insert(0, target)
        
    def start_traceroute(self):
        """开始路由追踪"""
        target = self.target_entry.get().strip()
        if not target:
            mbox.showwarning("输入错误", "请输入目标地址")
            return
            
        if self.traceroute_service.is_running:
            mbox.showwarning("追踪进行中", "请先停止当前追踪")
            return
            
        # 清空结果
        self.clear_result()
        
        # 更新界面状态
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.status_label.config(text="追踪中...", bootstyle=WARNING)
        self.current_hop_label.config(text="0")
        self.start_time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        
        # 显示追踪开始信息
        self.append_result(f"追踪到 {target} 的路由，最多经过 30 个跃点:\n\n")
        
        # 启动追踪
        success = self.traceroute_service.start_traceroute(
            target, 
            max_hops=30, 
            timeout=5000, 
            callback=self.on_traceroute_result
        )
        
        if not success:
            mbox.showerror("启动失败", "无法启动路由追踪")
            self.reset_ui_state()
            
    def stop_traceroute(self):
        """停止路由追踪"""
        if self.traceroute_service.is_running:
            self.traceroute_service.stop_traceroute()
            self.append_result("\n追踪已被用户停止\n")
            self.status_label.config(text="已停止", bootstyle=DANGER)
        
        self.reset_ui_state()
        
    def on_traceroute_result(self, hop_data):
        """处理追踪结果回调"""
        # 在主线程中更新UI
        self.after(0, lambda: self.update_traceroute_ui(hop_data))
        
    def update_traceroute_ui(self, hop_data):
        """更新追踪结果界面"""
        if hop_data.get('error'):
            self.append_result(f"错误: {hop_data['message']}\n")
            self.status_label.config(text="出错", bootstyle=DANGER)
            self.reset_ui_state()
            return
            
        # 更新当前跳数
        self.current_hop_label.config(text=str(hop_data['hop']))
        
        # 格式化显示结果
        hop_num = hop_data['hop']
        times = hop_data['times']
        ip = hop_data['ip']
        hostname = hop_data['hostname']
        
        # 构建输出行，类似Windows tracert格式
        if hop_data['timeout']:
            # 超时情况
            line = f"{hop_num:>3}     *        *        *     请求超时。\n"
        else:
            # 正常情况
            time1 = times[0] if len(times) > 0 else "*"
            time2 = times[1] if len(times) > 1 else "*"
            time3 = times[2] if len(times) > 2 else "*"
            
            # 格式化时间显示（右对齐）
            time1_str = f"{time1:>10}"
            time2_str = f"{time2:>10}"
            time3_str = f"{time3:>10}"
            
            # 显示IP和主机名
            if hostname and hostname != ip and hostname != '*':
                host_info = f"{ip} [{hostname}]"
            else:
                host_info = ip
                
            line = f"{hop_num:>3}  {time1_str}  {time2_str}  {time3_str}  {host_info}\n"
        
        self.append_result(line)
        
        # 检查是否完成
        if not self.traceroute_service.is_running:
            self.append_result("\n追踪完成。\n")
            self.status_label.config(text="完成", bootstyle=SUCCESS)
            self.reset_ui_state()
            
    def reset_ui_state(self):
        """重置界面状态"""
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        if self.status_label.cget('text') not in ['完成', '出错', '已停止']:
            self.status_label.config(text="就绪", bootstyle=INFO)
        
    def clear_result(self):
        """清空结果框"""
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.configure(state=DISABLED)
        
    def append_result(self, text):
        """向结果框追加文本"""
        self.result_text.configure(state=NORMAL)
        self.result_text.insert(END, text)
        self.result_text.configure(state=DISABLED)
        self.result_text.see(END) 