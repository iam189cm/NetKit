using System;
using System.Linq;
using System.Windows.Forms;
using NETKit.Core.Models;

namespace NETKit.UI.Controls
{
    /// <summary>
    /// 用于显示全面网络扫描统计信息的专业用户控件
    /// </summary>
    public partial class ScanStatisticsPanel : UserControl
    {
        private DateTime _scanStartTime;
        private DateTime _scanEndTime;
        private int _totalToScan;
        private int _scannedCount;
        private System.Windows.Forms.Timer _updateTimer;

        public ScanStatisticsPanel()
        {
            InitializeComponent();
            InitializeTimer();
            Reset();
        }

        private void InitializeTimer()
        {
            _updateTimer = new System.Windows.Forms.Timer();
            _updateTimer.Interval = 1000; // 每秒更新一次
            _updateTimer.Tick += UpdateTimer_Tick;
        }

        private void UpdateTimer_Tick(object sender, EventArgs e)
        {
            // 不再更新用时显示
        }

        /// <summary>
        /// 开始扫描统计跟踪
        /// </summary>
        /// <param name="totalToScan">要扫描的IP总数</param>
        public void StartScan(int totalToScan)
        {
            _totalToScan = totalToScan;
            _scannedCount = 0;
            _scanStartTime = DateTime.Now;
            _scanEndTime = DateTime.MinValue;

            if (this.InvokeRequired)
            {
                this.Invoke(new Action(() => UpdateStartScan()));
            }
            else
            {
                UpdateStartScan();
            }

            _updateTimer.Start();
        }

        private void UpdateStartScan()
        {
            progressBar.Maximum = _totalToScan;
            progressBar.Value = 0;
            lblProgressText.Text = $"0% (0/{_totalToScan})";
        }

        /// <summary>
        /// 使用最新的扫描结果统计信息更新面板
        /// </summary>
        /// <param name="result">网络扫描结果</param>
        public void UpdateStatistics(NetworkScanResult result)
        {
            if (this.InvokeRequired)
            {
                this.Invoke(new Action(() => UpdateControls(result)));
            }
            else
            {
                UpdateControls(result);
            }
        }

        /// <summary>
        /// 当单个IP扫描完成时更新进度
        /// </summary>
        /// <param name="item">已完成的扫描项目</param>
        public void UpdateProgress(IPScanItem item)
        {
            _scannedCount++;
            
            if (this.InvokeRequired)
            {
                this.Invoke(new Action(() => UpdateProgressControls()));
            }
            else
            {
                UpdateProgressControls();
            }
        }

        private void UpdateProgressControls()
        {
            if (_totalToScan > 0)
            {
                progressBar.Value = Math.Min(_scannedCount, _totalToScan);
                var percentage = (int)((double)_scannedCount / _totalToScan * 100);
                lblProgressText.Text = $"{percentage}% ({_scannedCount}/{_totalToScan})";
            }
        }

        private void UpdateControls(NetworkScanResult result)
        {
            lblOnline.Text = $"在线设备: {result.OnlineDevices}个";
            
            // 统计超时设备（包括Failed和Timeout状态）
            var timeoutDevices = result.ScannedItems.Count(item => 
                item.Status == Common.ScanStatus.Timeout || 
                item.Status == Common.ScanStatus.Failed);
            lblTimeout.Text = $"超时设备: {timeoutDevices}个";

            // 如果扫描完成，更新结束时间
            if (result.EndTime != DateTime.MinValue)
            {
                _scanEndTime = result.EndTime;
                _updateTimer.Stop();
            }
        }

        /// <summary>
        /// 完成扫描并停止计时器
        /// </summary>
        /// <param name="result">最终扫描结果</param>
        public void CompleteScan(NetworkScanResult result)
        {
            _updateTimer.Stop();
            UpdateStatistics(result);
        }

        /// <summary>
        /// 将面板重置为初始状态
        /// </summary>
        public void Reset()
        {
            _updateTimer?.Stop();
            _scanStartTime = DateTime.MinValue;
            _scanEndTime = DateTime.MinValue;
            _totalToScan = 0;
            _scannedCount = 0;

            if (this.InvokeRequired)
            {
                this.Invoke(new Action(ResetControls));
            }
            else
            {
                ResetControls();
            }
        }

        private void ResetControls()
        {
            lblOnline.Text = "在线设备: 0个";
            lblTimeout.Text = "超时设备: 0个";
            progressBar.Value = 0;
            progressBar.Maximum = 100;
            lblProgressText.Text = "0% (0/0)";
        }

        /// <summary>
        /// 获取当前扫描统计信息的格式化字符串
        /// </summary>
        public string GetStatisticsSummary()
        {
            var summary = $"扫描统计报告\n";
            summary += $"开始时间: {(_scanStartTime != DateTime.MinValue ? _scanStartTime.ToString("yyyy-MM-dd HH:mm:ss") : "未开始")}\n";
            summary += $"结束时间: {(_scanEndTime != DateTime.MinValue ? _scanEndTime.ToString("yyyy-MM-dd HH:mm:ss") : "未完成")}\n";
            summary += $"扫描进度: {lblProgressText.Text}\n";
            summary += $"在线设备: {lblOnline.Text.Replace("在线设备: ", "")}\n";
            summary += $"超时设备: {lblTimeout.Text.Replace("超时设备: ", "")}";
            
            return summary;
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _updateTimer?.Stop();
                _updateTimer?.Dispose();
                components?.Dispose();
            }
            base.Dispose(disposing);
        }
    }
}
