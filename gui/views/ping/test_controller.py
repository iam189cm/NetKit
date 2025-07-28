"""
Ping测试控制器模块

负责协调各种ping测试模式的控制
包括单次测试、批量测试、连续测试等
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
import tkinter.messagebox as mbox
import threading


class PingTestController(tb.LabelFrame):
    """Ping测试控制面板"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, text="测试模式", padding=ui_helper.get_padding(15), **kwargs)
        self.test_callbacks = {}
        self.is_testing = False
        self.setup_ui()
    
    def setup_ui(self):
        """设置测试控制UI"""
        # 测试模式按钮
        buttons_frame = tb.Frame(self)
        buttons_frame.pack(fill=X)
        
        # 单次测试按钮
        self.single_btn = tb.Button(
            buttons_frame,
            text="单次测试",
            bootstyle=INFO,
            width=ui_helper.scale_size(20),
            command=self.start_single_test
        )
        self.single_btn.pack(fill=X, pady=(0, ui_helper.get_padding(5)))
        
        # 批量/范围测试按钮
        self.batch_btn = tb.Button(
            buttons_frame,
            text="批量/范围测试",
            bootstyle=SUCCESS,
            width=ui_helper.scale_size(20),
            command=self.start_batch_test
        )
        self.batch_btn.pack(fill=X, pady=(0, ui_helper.get_padding(5)))
        
        # 连续测试按钮
        self.continuous_btn = tb.Button(
            buttons_frame,
            text="连续测试",
            bootstyle=WARNING,
            width=ui_helper.scale_size(20),
            command=self.start_continuous_test
        )
        self.continuous_btn.pack(fill=X, pady=(0, ui_helper.get_padding(5)))
        
        # 停止测试按钮
        self.stop_btn = tb.Button(
            buttons_frame,
            text="停止测试",
            bootstyle=DANGER,
            width=ui_helper.scale_size(20),
            command=self.stop_test,
            state=DISABLED
        )
        self.stop_btn.pack(fill=X)
        
        # 高级选项
        advanced_frame = tb.LabelFrame(self, text="高级选项", padding=ui_helper.get_padding(10))
        advanced_frame.pack(fill=X, pady=(ui_helper.get_padding(15), 0))
        
        # 自动重试选项
        self.auto_retry_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            advanced_frame,
            text="失败自动重试",
            variable=self.auto_retry_var,
            bootstyle="round-toggle"
        ).pack(anchor=W, pady=ui_helper.get_padding(2))
        
        # 详细日志选项
        self.verbose_log_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            advanced_frame,
            text="详细日志输出",
            variable=self.verbose_log_var,
            bootstyle="round-toggle"
        ).pack(anchor=W, pady=ui_helper.get_padding(2))
        
        # 声音提醒选项
        self.sound_alert_var = tb.BooleanVar(value=False)
        tb.Checkbutton(
            advanced_frame,
            text="声音提醒",
            variable=self.sound_alert_var,
            bootstyle="round-toggle"
        ).pack(anchor=W, pady=ui_helper.get_padding(2))
        
        # 测试进度条
        self.progress_frame = tb.Frame(self)
        self.progress_frame.pack(fill=X, pady=(ui_helper.get_padding(15), 0))
        
        tb.Label(self.progress_frame, text="测试进度:").pack(anchor=W)
        self.progress_var = tb.DoubleVar()
        self.progress_bar = tb.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            mode='determinate'
        )
        self.progress_bar.pack(fill=X, pady=(ui_helper.get_padding(5), 0))
        
        self.progress_label = tb.Label(
            self.progress_frame,
            text="准备就绪",
            bootstyle=SECONDARY
        )
        self.progress_label.pack(anchor=W, pady=(ui_helper.get_padding(2), 0))
    
    def register_callback(self, test_type, callback):
        """
        注册测试回调函数
        
        Args:
            test_type (str): 测试类型 ('single', 'batch', 'continuous', 'stop')
            callback (callable): 回调函数
        """
        self.test_callbacks[test_type] = callback
    
    def start_single_test(self):
        """开始单次测试"""
        if self.is_testing:
            mbox.showwarning("警告", "请先停止当前测试")
            return
        
        if 'single' in self.test_callbacks:
            self.set_testing_state(True)
            self.update_progress(0, "开始单次测试...")
            
            # 在后台线程中执行测试
            def run_test():
                try:
                    self.test_callbacks['single']()
                except Exception as e:
                    self.after(0, lambda: mbox.showerror("错误", f"单次测试失败: {str(e)}"))
                finally:
                    self.after(0, lambda: self.set_testing_state(False))
            
            threading.Thread(target=run_test, daemon=True).start()
        else:
            mbox.showerror("错误", "单次测试回调未注册")
    
    def start_batch_test(self):
        """开始批量测试"""
        if self.is_testing:
            mbox.showwarning("警告", "请先停止当前测试")
            return
        
        if 'batch' in self.test_callbacks:
            self.set_testing_state(True)
            self.update_progress(0, "开始批量测试...")
            
            def run_test():
                try:
                    self.test_callbacks['batch']()
                except Exception as e:
                    self.after(0, lambda: mbox.showerror("错误", f"批量测试失败: {str(e)}"))
                finally:
                    self.after(0, lambda: self.set_testing_state(False))
            
            threading.Thread(target=run_test, daemon=True).start()
        else:
            mbox.showerror("错误", "批量测试回调未注册")
    
    def start_continuous_test(self):
        """开始连续测试"""
        if self.is_testing:
            mbox.showwarning("警告", "请先停止当前测试")
            return
        
        if 'continuous' in self.test_callbacks:
            self.set_testing_state(True)
            self.update_progress(0, "开始连续测试...")
            
            try:
                success = self.test_callbacks['continuous']()
                if not success:
                    self.set_testing_state(False)
                    mbox.showerror("错误", "无法启动连续测试")
            except Exception as e:
                self.set_testing_state(False)
                mbox.showerror("错误", f"连续测试启动失败: {str(e)}")
        else:
            mbox.showerror("错误", "连续测试回调未注册")
    
    def stop_test(self):
        """停止测试"""
        if 'stop' in self.test_callbacks:
            try:
                self.test_callbacks['stop']()
                self.set_testing_state(False)
                self.update_progress(0, "测试已停止")
            except Exception as e:
                mbox.showerror("错误", f"停止测试失败: {str(e)}")
        else:
            self.set_testing_state(False)
    
    def set_testing_state(self, is_testing):
        """
        设置测试状态
        
        Args:
            is_testing (bool): 是否正在测试
        """
        self.is_testing = is_testing
        
        if is_testing:
            # 禁用测试按钮，启用停止按钮
            self.single_btn.config(state=DISABLED)
            self.batch_btn.config(state=DISABLED)
            self.continuous_btn.config(state=DISABLED)
            self.stop_btn.config(state=NORMAL)
        else:
            # 启用测试按钮，禁用停止按钮
            self.single_btn.config(state=NORMAL)
            self.batch_btn.config(state=NORMAL)
            self.continuous_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)
            
            # 重置进度条
            self.progress_var.set(0)
            self.progress_label.config(text="准备就绪")
    
    def update_progress(self, percentage, message=""):
        """
        更新测试进度
        
        Args:
            percentage (float): 进度百分比 (0-100)
            message (str): 进度消息
        """
        self.progress_var.set(percentage)
        if message:
            self.progress_label.config(text=message)
        
        # 根据进度设置进度条颜色
        if percentage >= 100:
            self.progress_bar.config(bootstyle=SUCCESS)
        elif percentage >= 50:
            self.progress_bar.config(bootstyle=INFO)
        else:
            self.progress_bar.config(bootstyle=WARNING)
    
    def get_test_options(self):
        """
        获取测试选项设置
        
        Returns:
            dict: 测试选项
        """
        return {
            'auto_retry': self.auto_retry_var.get(),
            'verbose_log': self.verbose_log_var.get(),
            'sound_alert': self.sound_alert_var.get()
        }
    
    def set_test_options(self, options):
        """
        设置测试选项
        
        Args:
            options (dict): 测试选项
        """
        if 'auto_retry' in options:
            self.auto_retry_var.set(options['auto_retry'])
        if 'verbose_log' in options:
            self.verbose_log_var.set(options['verbose_log'])
        if 'sound_alert' in options:
            self.sound_alert_var.set(options['sound_alert'])
    
    def show_test_result_summary(self, success_count, total_count, duration):
        """
        显示测试结果摘要
        
        Args:
            success_count (int): 成功数量
            total_count (int): 总数量
            duration (float): 测试持续时间
        """
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        summary_msg = (
            f"测试完成!\n\n"
            f"总数: {total_count}\n"
            f"成功: {success_count}\n"
            f"失败: {total_count - success_count}\n"
            f"成功率: {success_rate:.1f}%\n"
            f"用时: {duration:.1f}秒"
        )
        
        # 根据成功率选择消息框类型
        if success_rate >= 95:
            mbox.showinfo("测试完成", summary_msg)
        elif success_rate >= 80:
            mbox.showwarning("测试完成", summary_msg)
        else:
            mbox.showerror("测试完成", summary_msg)
        
        # 声音提醒
        if self.sound_alert_var.get():
            self.bell()  # 系统提示音
    
    def is_test_running(self):
        """检查是否有测试正在运行"""
        return self.is_testing
    
    def enable_all_buttons(self):
        """启用所有按钮（用于错误恢复）"""
        self.single_btn.config(state=NORMAL)
        self.batch_btn.config(state=NORMAL)
        self.continuous_btn.config(state=NORMAL)
        self.stop_btn.config(state=NORMAL)
    
    def disable_all_buttons(self):
        """禁用所有按钮"""
        self.single_btn.config(state=DISABLED)
        self.batch_btn.config(state=DISABLED)
        self.continuous_btn.config(state=DISABLED)
        self.stop_btn.config(state=DISABLED) 