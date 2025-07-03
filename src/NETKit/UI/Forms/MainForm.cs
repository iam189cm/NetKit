using System.Diagnostics;
using System.Threading;
using System.Collections.Generic;
using System.Linq;
using NETKit.Core.Services;
using NETKit.Core.Models;
using NETKit.Core.Helpers;
using NETKit.Common;

namespace NETKit.UI.Forms
{
    /// <summary>
    /// 主窗体 - 负责UI交互逻辑
    /// </summary>
    public partial class MainForm : Form
    {
        private readonly NetworkConfigService _networkService;
        private readonly NetworkScanService _scanService;
        private CancellationTokenSource _cancellationTokenSource;

        public MainForm()
        {
            InitializeComponent();

            // IP配置服务
            _networkService = new NetworkConfigService();
            _networkService.StatusUpdated += OnStatusUpdated;
            cmbNetworkAdapters.SelectedIndexChanged += CmbNetworkAdapters_SelectedIndexChanged;

            // Ping测试服务
            _scanService = new NetworkScanService(new PingExecutionService());
            _scanService.ProgressUpdated += ScanService_ProgressUpdated;
            _scanService.ScanCompleted += ScanService_ScanCompleted;
            scanControlPanel.OnStartScan += ScanControlPanel_OnStartScan;
            scanControlPanel.OnStopScan += ScanControlPanel_OnStopScan;
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            InitializeForm();
        }

        private void InitializeForm()
        {
            bool isAdmin = SecurityHelper.IsRunAsAdministrator();
            
            // 检查管理员权限
            if (!isAdmin)
            {
                // 如果程序配置了自动管理员权限但仍然没有权限，说明用户拒绝了UAC
                UpdateStatus("程序需要管理员权限才能正常工作。请重新启动程序并允许UAC权限提升。", true);
                
                // 禁用修改按钮
                btnApplyConfig.Enabled = false;
                btnSetDhcp.Enabled = false;
            }
            else
            {
                UpdateStatus("程序已以管理员权限启动，所有功能可正常使用。", false);
                
                // 启用所有功能按钮
                btnApplyConfig.Enabled = true;
                btnSetDhcp.Enabled = true;
            }

            // 加载网络适配器
            LoadNetworkAdapters();
            // 设置默认值
            SetDefaultValues();
            
            // 添加按钮悬停效果
            SetupButtonHoverEffects();
        }

        private void SetDefaultValues()
        {
            // 不设置任何默认值，保持输入框为空
            // 用户可以看到占位符提示文本
        }

        private void LoadNetworkAdapters()
        {
            try
            {
                cmbNetworkAdapters.Items.Clear();
                var adapters = _networkService.GetNetworkAdapters(chkShowAllAdapters.Checked);

                foreach (var adapter in adapters)
                {
                    cmbNetworkAdapters.Items.Add(adapter);
                }

                if (cmbNetworkAdapters.Items.Count > 0)
                {
                    cmbNetworkAdapters.SelectedIndex = 0;
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"加载网络适配器时发生错误: {ex.Message}", true);
            }
        }

        private async void btnApplyConfig_Click(object sender, EventArgs e)
        {
            var selectedAdapter = cmbNetworkAdapters.SelectedItem as NetworkAdapterItem;
            var validation = ValidationHelper.ValidateNetworkConfig(
                selectedAdapter?.Name,
                txtIpAddress.Text,
                txtSubnetMask.Text,
                txtGateway.Text,
                txtDnsServer.Text
            );

            if (!validation.IsValid)
            {
                UpdateStatus($"错误: {validation.Message}", true);
                return;
            }

            // 禁用按钮防止重复点击
            SetButtonsEnabled(false);

            try
            {
                bool success = await _networkService.ApplyStaticIPConfigurationAsync(
                    selectedAdapter!.Name,
                    txtIpAddress.Text,
                    txtSubnetMask.Text,
                    txtGateway.Text,
                    txtDnsServer.Text
                );
                
                if (success)
                {
                    // 刷新网卡信息显示
                    UpdateAdapterInfo();
                }
            }
            finally
            {
                SetButtonsEnabled(true);
            }
        }

        private async void btnSetDhcp_Click(object sender, EventArgs e)
        {
            var selectedAdapter = cmbNetworkAdapters.SelectedItem as NetworkAdapterItem;
            if (selectedAdapter == null)
            {
                UpdateStatus("错误: 请选择网络适配器", true);
                return;
            }

            // 禁用按钮防止重复点击
            SetButtonsEnabled(false);

            try
            {
                bool success = await _networkService.SetDHCPConfigurationAsync(selectedAdapter.Name);
                if (success)
                {
                    // 清空输入框
                    ClearInputFields();
                    
                    // 刷新网卡信息显示
                    UpdateAdapterInfo();
                }
            }
            finally
            {
                SetButtonsEnabled(true);
            }
        }

        private void btnRefreshAdapters_Click(object sender, EventArgs e)
        {
            LoadNetworkAdapters();
        }

        private void chkShowAllAdapters_CheckedChanged(object sender, EventArgs e)
        {
            LoadNetworkAdapters();
            if (chkShowAllAdapters.Checked)
            {
                UpdateStatus("已显示所有网络适配器，包括虚拟适配器", false);
            }
            else
            {
                UpdateStatus("已过滤显示，仅显示物理网络适配器", false);
            }
        }


        private void SetButtonsEnabled(bool enabled)
        {
            // 只有在管理员模式下才启用修改按钮
            if (SecurityHelper.IsRunAsAdministrator())
            {
                btnApplyConfig.Enabled = enabled;
                btnSetDhcp.Enabled = enabled;
            }
            
            btnRefreshAdapters.Enabled = enabled;
        }

        private void ClearInputFields()
        {
            txtIpAddress.Clear();
            txtSubnetMask.Clear();
            txtGateway.Clear();
            txtDnsServer.Clear();
        }

        private void OnStatusUpdated(string message, bool isError)
        {
            // 确保在UI线程中更新
            if (InvokeRequired)
            {
                Invoke(new Action<string, bool>(UpdateStatus), message, isError);
            }
            else
            {
                UpdateStatus(message, isError);
            }
        }

        private void UpdateStatus(string message, bool isError)
        {
            string timestamp = DateTime.Now.ToString("HH:mm:ss");
            string statusMessage = $"[{timestamp}] {message}";

            if (txtStatus.Text == Constants.UI.WaitingStatus)
            {
                txtStatus.Text = statusMessage;
            }
            else
            {
                txtStatus.Text += Environment.NewLine + statusMessage;
            }

            // 滚动到底部
            txtStatus.SelectionStart = txtStatus.Text.Length;
            txtStatus.ScrollToCaret();

            // 错误提示音
            if (isError)
            {
                System.Media.SystemSounds.Hand.Play();
            }
        }

        private void SetupButtonHoverEffects()
        {
            // 为每个按钮添加悬停效果
            SetupButtonHover(btnApplyConfig, Constants.Colors.PrimaryBlue, Constants.Colors.PrimaryBlueHover);
            SetupButtonHover(btnSetDhcp, Constants.Colors.PrimaryBlue, Constants.Colors.PrimaryBlueHover);
            SetupButtonHover(btnRefreshAdapters, Constants.Colors.PrimaryBlue, Constants.Colors.PrimaryBlueHover);
        }

        private void SetupButtonHover(Button button, Color normalColor, Color hoverColor)
        {
            button.MouseEnter += (s, e) =>
            {
                if (button.Enabled)
                {
                    button.BackColor = hoverColor;
                    button.Cursor = Cursors.Hand;
                }
            };

            button.MouseLeave += (s, e) =>
            {
                if (button.Enabled)
                {
                    button.BackColor = normalColor;
                    button.Cursor = Cursors.Default;
                }
            };
        }

        /// <summary>
        /// 网卡选择变化事件处理
        /// </summary>
        private void CmbNetworkAdapters_SelectedIndexChanged(object? sender, EventArgs e)
        {
            UpdateAdapterInfo();
        }

        /// <summary>
        /// 更新网卡信息显示
        /// </summary>
        private void UpdateAdapterInfo()
        {
            var selectedAdapter = cmbNetworkAdapters.SelectedItem as NetworkAdapterItem;
            if (selectedAdapter == null)
            {
                txtAdapterInfoContent.Text = "请选择网络适配器";
                return;
            }

            try
            {
                var adapterInfo = _networkService.GetAdapterDetails(selectedAdapter.Name);
                if (adapterInfo != null)
                {
                    // 设置网卡信息文本（现在可以复制）
                    txtAdapterInfoContent.Text = adapterInfo.GetFullInfoText();

                    // 不再自动填充当前网卡配置到输入框
                    // 保持输入框为空，让用户手动输入配置
                }
                else
                {
                    txtAdapterInfoContent.Text = "无法获取网卡详细信息";
                }
            }
            catch (Exception ex)
            {
                txtAdapterInfoContent.Text = $"获取网卡信息时发生错误: {ex.Message}";
                UpdateStatus($"获取网卡信息失败: {ex.Message}", true);
            }
        }

        /// <summary>
        /// 窗体关闭时的清理
        /// </summary>
        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            _cancellationTokenSource?.Cancel();
            _networkService?.Dispose();
            base.OnFormClosed(e);
        }

        #region Ping Test Logic

        private async void ScanControlPanel_OnStartScan(ScanConfiguration config)
        {
            _cancellationTokenSource = new CancellationTokenSource();
            scanControlPanel.SetScanInProgress(true);
            scanStatisticsPanel.Reset();

            var ipList = GetIpRange(config.StartAddress, config.EndAddress)
                .Select(ip => new IPScanItem(ip))
                .ToList();
            
            ipGridControl.SetScanItems(ipList);
            scanStatisticsPanel.StartScan(ipList.Count);

            try
            {
                await _scanService.StartScanAsync(config, _cancellationTokenSource.Token, ipList);
            }
            catch (TaskCanceledException)
            {
                UpdateStatus("扫描已由用户取消。", false);
            }
            catch (Exception ex)
            {
                UpdateStatus($"扫描时发生未知错误: {ex.Message}", true);
            }
            finally
            {
                scanControlPanel.SetScanInProgress(false);
            }
        }

        private void ScanControlPanel_OnStopScan()
        {
            _cancellationTokenSource?.Cancel();
        }

        private void ScanService_ProgressUpdated(IPScanItem item)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => {
                    ipGridControl.UpdateScanItem(item);
                    scanStatisticsPanel.UpdateProgress(item);
                }));
            }
            else
            {
                ipGridControl.UpdateScanItem(item);
                scanStatisticsPanel.UpdateProgress(item);
            }
        }

        private void ScanService_ScanCompleted(NetworkScanResult result)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => scanStatisticsPanel.CompleteScan(result)));
            }
            else
            {
                scanStatisticsPanel.CompleteScan(result);
            }
            UpdateStatus("扫描完成。", false);
        }

        private IEnumerable<System.Net.IPAddress> GetIpRange(System.Net.IPAddress start, System.Net.IPAddress end)
        {
            var startBytes = start.GetAddressBytes();
            var endBytes = end.GetAddressBytes();
            Array.Reverse(startBytes);
            Array.Reverse(endBytes);
            var startNum = BitConverter.ToUInt32(startBytes, 0);
            var endNum = BitConverter.ToUInt32(endBytes, 0);

            for (var i = startNum; i <= endNum; i++)
            {
                var bytes = BitConverter.GetBytes(i);
                Array.Reverse(bytes);
                yield return new System.Net.IPAddress(bytes);
            }
        }

        #endregion
    }
}
