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
        #region 私有字段

        private readonly NetworkConfigService _networkService;
        private readonly NetworkScanService _scanService;
        private CancellationTokenSource? _cancellationTokenSource;

        // 实时验证定时器
        private System.Windows.Forms.Timer? _validationTimer;
        private TextBox? _lastChangedTextBox;

        #endregion

        #region 构造函数和初始化

        public MainForm()
        {
            InitializeComponent();

            // 在构造函数中初始化readonly字段
            _networkService = new NetworkConfigService();
            _scanService = new NetworkScanService(new PingExecutionService());

            InitializeServices();
            InitializeEventHandlers();
            InitializeInputValidation();
        }

        /// <summary>
        /// 初始化服务
        /// </summary>
        private void InitializeServices()
        {
            // IP配置服务事件绑定
            _networkService.StatusUpdated += OnStatusUpdated;

            // Ping测试服务事件绑定
            _scanService.ProgressUpdated += ScanService_ProgressUpdated;
            _scanService.ScanCompleted += ScanService_ScanCompleted;
        }

        /// <summary>
        /// 初始化事件处理器
        /// </summary>
        private void InitializeEventHandlers()
        {
            // 网络适配器相关事件
            cmbNetworkAdapters.SelectedIndexChanged += CmbNetworkAdapters_SelectedIndexChanged;

            // 扫描控制面板事件
            scanControlPanel.OnStartScan += ScanControlPanel_OnStartScan;
            scanControlPanel.OnStopScan += ScanControlPanel_OnStopScan;

            // 标签页切换事件 - 用于路由管理面板懒加载
            tabControlMain.SelectedIndexChanged += TabControlMain_SelectedIndexChanged;

            // 移除子网计算和路由跟踪面板的状态事件绑定，让它们独立处理状态
            // subnetCalculatorPanel.StatusUpdated += OnStatusUpdated;  // 已删除
            // traceRoutePanel.StatusUpdated += OnStatusUpdated;        // 已删除

            // 路由管理面板事件绑定 - 已移除，让其状态独立处理，不显示在IP配置界面
            // routeManagementPanel.StatusUpdated += OnStatusUpdated;   // 已删除
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            InitializeForm();
        }

        /// <summary>
        /// 初始化窗体
        /// </summary>
        private void InitializeForm()
        {
            CheckAdministratorPrivileges();
            LoadNetworkAdapters();
            SetDefaultValues();
            SetupButtonHoverEffects();
        }

        /// <summary>
        /// 检查管理员权限
        /// </summary>
        private void CheckAdministratorPrivileges()
        {
            bool isAdmin = SecurityHelper.IsRunAsAdministrator();

            if (!isAdmin)
            {
                UpdateStatus("程序需要管理员权限才能正常工作。请重新启动程序并允许UAC权限提升。", true);
                btnApplyConfig.Enabled = false;
            }
            else
            {
                UpdateStatus("程序已以管理员权限启动，所有功能可正常使用。", false);
                btnApplyConfig.Enabled = true;
            }
        }

        /// <summary>
        /// 设置默认值
        /// </summary>
        private void SetDefaultValues()
        {
            // 不设置任何默认值，保持输入框为空
            // 用户可以看到占位符提示文本
        }

        #endregion

        #region UI状态管理

        /// <summary>
        /// 更新状态信息
        /// </summary>
        private void OnStatusUpdated(string message, bool isError)
        {
            if (InvokeRequired)
            {
                Invoke(new Action<string, bool>(UpdateStatus), message, isError);
            }
            else
            {
                UpdateStatus(message, isError);
            }
        }

        /// <summary>
        /// 更新状态显示
        /// </summary>
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

        /// <summary>
        /// 设置按钮启用状态
        /// </summary>
        private void SetButtonsEnabled(bool enabled)
        {
            // 只有在管理员模式下才启用修改按钮
            if (SecurityHelper.IsRunAsAdministrator())
            {
                btnApplyConfig.Enabled = enabled;
            }

            btnRefreshAdapters.Enabled = enabled;
        }

        /// <summary>
        /// 设置按钮悬停效果
        /// </summary>
        private void SetupButtonHoverEffects()
        {
            SetupButtonHover(btnApplyConfig, Constants.Colors.PrimaryBlue, Constants.Colors.PrimaryBlueHover);
            SetupButtonHover(btnRefreshAdapters, Constants.Colors.PrimaryBlue, Constants.Colors.PrimaryBlueHover);
        }

        /// <summary>
        /// 为单个按钮设置悬停效果
        /// </summary>
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

        #endregion

        #region 资源清理

        /// <summary>
        /// 窗体关闭时的清理
        /// </summary>
        protected override void OnFormClosed(FormClosedEventArgs e)
        {
            _cancellationTokenSource?.Cancel();
            _networkService?.Dispose();
            _validationTimer?.Dispose();
            base.OnFormClosed(e);
        }

        #endregion

        /// <summary>
        /// 标签页切换事件处理 - 实现路由管理面板懒加载
        /// </summary>
        private async void TabControlMain_SelectedIndexChanged(object? sender, EventArgs e)
        {
            // 检查是否切换到路由管理标签页
            if (tabControlMain.SelectedTab == tabPageRouteManagement)
            {
                try
                {
                    // 触发路由管理面板的懒加载
                    await routeManagementPanel.EnsureDataLoaded();
                }
                catch (Exception ex)
                {
                    // 静默处理异常，避免影响用户体验
                    System.Diagnostics.Debug.WriteLine($"路由管理面板加载失败: {ex.Message}");
                }
            }
        }

        private void routeManagementPanel_Load(object sender, EventArgs e)
        {

        }
    }
}
