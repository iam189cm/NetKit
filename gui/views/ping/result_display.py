"""
Ping结果显示模块

负责展示ping测试结果的GUI组件
支持实时结果更新和历史记录显示
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from datetime import datetime
import tkinter.filedialog as fd
import tkinter.messagebox as mbox


class PingResultDisplay(tb.LabelFrame):
    """Ping结果显示面板"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="测试结果", padding=ui_helper.get_padding(10), **kwargs)
        self.result_history = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置结果显示UI"""
        # 结果显示模式选择
        mode_frame = tb.Frame(self)
        mode_frame.pack(fill=X, pady=(0, ui_helper.get_padding(10)))
        
        tb.Label(mode_frame, text="显示模式:").pack(side=LEFT)
        
        self.display_mode = tb.StringVar(value="realtime")
        modes = [
            ("实时模式", "realtime"),
            ("汇总模式", "summary"),
            ("详细模式", "detailed")
        ]
        
        for text, value in modes:
            rb = tb.Radiobutton(
                mode_frame,
                text=text,
                variable=self.display_mode,
                value=value,
                command=self.on_mode_change
            )
            rb.pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # 结果文本框
        text_frame = tb.Frame(self)
        text_frame.pack(fill=BOTH, expand=True)
        
        self.result_text = tb.Text(
            text_frame,
            height=ui_helper.scale_size(20),
            state=DISABLED,
            wrap=WORD,
            font=('Consolas', ui_helper.scale_size(9))
        )
        
        # 滚动条
        scrollbar = tb.Scrollbar(text_frame, orient=VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # 控制按钮
        btn_frame = tb.Frame(self)
        btn_frame.pack(fill=X, pady=(ui_helper.get_padding(10), 0))
        
        # 清空结果按钮
        tb.Button(
            btn_frame,
            text="清空结果",
            bootstyle=LIGHT,
            command=self.clear_results,
            width=ui_helper.scale_size(12)
        ).pack(side=LEFT)
        
        # 保存结果按钮
        tb.Button(
            btn_frame,
            text="保存结果",
            bootstyle=INFO,
            command=self.save_results,
            width=ui_helper.scale_size(12)
        ).pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # 导出CSV按钮
        tb.Button(
            btn_frame,
            text="导出CSV",
            bootstyle=SUCCESS,
            command=self.export_csv,
            width=ui_helper.scale_size(12)
        ).pack(side=LEFT, padx=(ui_helper.get_padding(10), 0))
        
        # 自动滚动选项
        self.auto_scroll_var = tb.BooleanVar(value=True)
        tb.Checkbutton(
            btn_frame,
            text="自动滚动",
            variable=self.auto_scroll_var,
            bootstyle="round-toggle"
        ).pack(side=RIGHT)
        
        # 初始化显示
        self.append_result("=== NetKit Ping网络测试工具 ===\n")
        self.append_result("请输入目标地址/范围并选择测试模式\n")
        self.append_result("支持格式: 单个IP、IP范围(1.1.1.1-1.1.1.100)、CIDR(192.168.1.0/24)、主机名\n\n")
    
    def on_mode_change(self):
        """显示模式改变时的处理"""
        mode = self.display_mode.get()
        if mode == "summary":
            self.show_summary_view()
        elif mode == "detailed":
            self.show_detailed_view()
        else:
            self.show_realtime_view()
    
    def show_realtime_view(self):
        """显示实时模式"""
        # 实时模式显示最新的结果
        pass
    
    def show_summary_view(self):
        """显示汇总模式"""
        if not self.result_history:
            self.set_text("暂无测试结果")
            return
        
        # 生成汇总信息
        summary_text = self.generate_summary()
        self.set_text(summary_text)
    
    def show_detailed_view(self):
        """显示详细模式"""
        if not self.result_history:
            self.set_text("暂无测试结果")
            return
        
        # 显示详细的历史记录
        detailed_text = self.generate_detailed_report()
        self.set_text(detailed_text)
    
    def append_result(self, text, result_type="info"):
        """
        追加结果文本
        
        Args:
            text (str): 要追加的文本
            result_type (str): 结果类型 (info, success, error, warning)
        """
        # 记录到历史
        self.result_history.append({
            'timestamp': datetime.now(),
            'text': text,
            'type': result_type
        })
        
        # 只在实时模式下直接显示
        if self.display_mode.get() == "realtime":
            self.result_text.configure(state=NORMAL)
            
            # 根据类型设置文本颜色
            if result_type == "success":
                self.result_text.insert(END, text, "success")
            elif result_type == "error":
                self.result_text.insert(END, text, "error")
            elif result_type == "warning":
                self.result_text.insert(END, text, "warning")
            else:
                self.result_text.insert(END, text)
            
            self.result_text.configure(state=DISABLED)
            
            # 自动滚动到底部
            if self.auto_scroll_var.get():
                self.result_text.see(END)
        
        # 配置文本颜色标签
        self.result_text.tag_config("success", foreground="green")
        self.result_text.tag_config("error", foreground="red")
        self.result_text.tag_config("warning", foreground="orange")
    
    def set_text(self, text):
        """设置文本内容（替换现有内容）"""
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.insert("1.0", text)
        self.result_text.configure(state=DISABLED)
    
    def clear_results(self):
        """清空结果"""
        self.result_text.configure(state=NORMAL)
        self.result_text.delete("1.0", END)
        self.result_text.configure(state=DISABLED)
        self.result_history.clear()
        self.append_result("=== 结果已清空 ===\n\n")
    
    def save_results(self):
        """保存结果到文件"""
        if not self.result_history:
            mbox.showwarning("警告", "没有结果可保存")
            return
        
        filename = fd.asksaveasfilename(
            title="保存测试结果",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.get_all_text())
                mbox.showinfo("成功", f"结果已保存到: {filename}")
            except Exception as e:
                mbox.showerror("错误", f"保存失败: {str(e)}")
    
    def export_csv(self):
        """导出CSV格式的结果"""
        # 这个方法需要从外部获取CSV数据
        # 通常由父组件提供CSV数据
        mbox.showinfo("提示", "CSV导出功能需要在测试完成后使用")
    
    def get_all_text(self):
        """获取所有文本内容"""
        return self.result_text.get("1.0", END)
    
    def generate_summary(self):
        """生成汇总报告"""
        if not self.result_history:
            return "暂无测试数据"
        
        # 统计不同类型的结果
        total_entries = len(self.result_history)
        success_count = len([r for r in self.result_history if r['type'] == 'success'])
        error_count = len([r for r in self.result_history if r['type'] == 'error'])
        warning_count = len([r for r in self.result_history if r['type'] == 'warning'])
        
        first_time = self.result_history[0]['timestamp']
        last_time = self.result_history[-1]['timestamp']
        duration = last_time - first_time
        
        summary = [
            "=== 测试结果汇总 ===",
            f"测试开始时间: {first_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"测试结束时间: {last_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"测试持续时间: {duration}",
            f"总记录数: {total_entries}",
            f"成功记录: {success_count}",
            f"错误记录: {error_count}",
            f"警告记录: {warning_count}",
            "",
            "=== 最近10条记录 ===",
        ]
        
        # 添加最近的记录
        recent_records = self.result_history[-10:]
        for record in recent_records:
            timestamp = record['timestamp'].strftime('%H:%M:%S')
            summary.append(f"[{timestamp}] {record['text'].strip()}")
        
        return "\n".join(summary)
    
    def generate_detailed_report(self):
        """生成详细报告"""
        if not self.result_history:
            return "暂无测试数据"
        
        detailed = ["=== 详细测试记录 ===\n"]
        
        for record in self.result_history:
            timestamp = record['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
            type_indicator = {
                'success': '✓',
                'error': '✗',
                'warning': '⚠',
                'info': 'ℹ'
            }.get(record['type'], '')
            
            detailed.append(f"[{timestamp}] {type_indicator} {record['text'].strip()}")
        
        return "\n".join(detailed)
    
    def show_ping_result(self, stats, result_type="info"):
        """
        显示单次ping测试结果
        
        Args:
            stats (dict): ping统计信息
            result_type (str): 结果类型
        """
        if stats['success']:
            result_lines = [
                f"目标: {stats['host']}",
                f"数据包: 已发送 {stats['packets_sent']}, 已接收 {stats['packets_received']}, 丢失 {stats['packets_sent'] - stats['packets_received']}",
                f"丢包率: {stats['packet_loss']:.1f}%"
            ]
            
            if stats['times']:
                result_lines.append(
                    f"往返时间: 最小 {stats['min_time']}ms, 最大 {stats['max_time']}ms, 平均 {stats['avg_time']}ms"
                )
            
            result_lines.append("✓ 测试成功")
            result_type = "success"
        else:
            result_lines = [f"✗ 测试失败: 无法访问 {stats['host']}"]
            result_type = "error"
        
        result_text = "\n".join(result_lines) + "\n\n"
        self.append_result(result_text, result_type)
    
    def show_continuous_result(self, sequence, timestamp_str, success, response_time=None):
        """
        显示连续ping的单次结果
        
        Args:
            sequence (int): 序列号
            timestamp_str (str): 时间戳字符串
            success (bool): 是否成功
            response_time (int, optional): 响应时间
        """
        if success and response_time is not None:
            result_text = f"[{timestamp_str}] #{sequence}: 时间={response_time}ms\n"
            result_type = "success"
        else:
            result_text = f"[{timestamp_str}] #{sequence}: 请求超时\n"
            result_type = "error"
        
        self.append_result(result_text, result_type) 