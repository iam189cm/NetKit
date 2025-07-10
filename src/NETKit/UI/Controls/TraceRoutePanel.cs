using System.ComponentModel;
using System.Threading;
using NETKit.Core.Models;
using NETKit.Core.Services;
using NETKit.Common;

namespace NETKit.UI.Controls
{
    /// <summary>
    /// 路由跟踪面板
    /// </summary>
    public partial class TraceRoutePanel : UserControl
    {
        #region 私有字段

        private readonly TraceRouteService _traceService;
        private CancellationTokenSource? _cancellationTokenSource;
        private TraceRouteResult? _currentResult;
        private BindingList<TraceRouteHopDisplay> _bindingList = new();

        #endregion

        #region 事件

        /// <summary>
        /// 移除对外的状态更新事件，改为内部状态处理
        /// </summary>
        // public event Action<string, bool>? StatusUpdated;  // 已删除，让状态独立

        #endregion

        #region 构造函数

        public TraceRoutePanel()
        {
            InitializeComponent();
            _traceService = new TraceRouteService();
            InitializeServices();
            InitializeUI();
        }

        #endregion

        #region 初始化

        /// <summary>
        /// 初始化服务
        /// </summary>
        private void InitializeServices()
        {
            _traceService.HopCompleted += OnHopCompleted;
            _traceService.TraceCompleted += OnTraceCompleted;
            _traceService.StatusUpdated += OnStatusUpdated;
        }

        /// <summary>
        /// 初始化UI
        /// </summary>
        private void InitializeUI()
        {
            // 设置默认值
            txtTargetAddress.Text = "";
            numMaxHops.Value = 30;
            numTimeout.Value = 5000;
            
            // 设置表格
            SetupDataGridView();
            
            // 设置按钮状态
            btnStart.Enabled = true;
            btnStop.Enabled = false;
            
            // 设置输入验证
            txtTargetAddress.TextChanged += TxtTargetAddress_TextChanged;
        }

        /// <summary>
        /// 设置数据表格
        /// </summary>
        private void SetupDataGridView()
        {
            dgvResults.AllowUserToAddRows = false;
            dgvResults.AllowUserToDeleteRows = false;
            dgvResults.ReadOnly = true;
            dgvResults.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            dgvResults.MultiSelect = false;
            dgvResults.AutoGenerateColumns = false;
            dgvResults.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            dgvResults.RowHeadersVisible = false;
            dgvResults.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.None;
            dgvResults.ScrollBars = ScrollBars.Both;
            dgvResults.ColumnHeadersHeight = 30;
            dgvResults.RowTemplate.Height = 26;
            
            // 添加列
            dgvResults.Columns.Clear();
            
            // 跳数列 - 调整宽度，避免换行
            dgvResults.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "HopNumber",
                HeaderText = "跳数",
                Width = 100,
                DataPropertyName = "HopNumber",
                DefaultCellStyle = new DataGridViewCellStyle
                {
                    Alignment = DataGridViewContentAlignment.MiddleCenter,
                    Font = new Font("Microsoft YaHei UI", 9F, FontStyle.Regular)
                }
            });
            
            // IP地址列 - 增加宽度，确保IP地址显示完整
            dgvResults.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "IpAddress",
                HeaderText = "IP地址",
                Width = 150,
                DataPropertyName = "DisplayAddress",
                DefaultCellStyle = new DataGridViewCellStyle
                {
                    Font = new Font("Consolas", 9F, FontStyle.Regular),
                    Alignment = DataGridViewContentAlignment.MiddleLeft
                }
            });
            
            // 延迟1列 - 调整宽度和标题，避免换行
            dgvResults.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "Delay1",
                HeaderText = "延迟1",
                Width = 120,
                DataPropertyName = "Delay1Display",
                DefaultCellStyle = new DataGridViewCellStyle
                {
                    Alignment = DataGridViewContentAlignment.MiddleCenter,
                    Font = new Font("Microsoft YaHei UI", 9F, FontStyle.Regular)
                }
            });
            
            // 延迟2列 - 调整宽度和标题，避免换行
            dgvResults.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "Delay2",
                HeaderText = "延迟2",
                Width = 120,
                DataPropertyName = "Delay2Display",
                DefaultCellStyle = new DataGridViewCellStyle
                {
                    Alignment = DataGridViewContentAlignment.MiddleCenter,
                    Font = new Font("Microsoft YaHei UI", 9F, FontStyle.Regular)
                }
            });
            
            // 延迟3列 - 调整宽度和标题，避免换行
            dgvResults.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "Delay3",
                HeaderText = "延迟3",
                Width = 120,
                DataPropertyName = "Delay3Display",
                DefaultCellStyle = new DataGridViewCellStyle
                {
                    Alignment = DataGridViewContentAlignment.MiddleCenter,
                    Font = new Font("Microsoft YaHei UI", 9F, FontStyle.Regular)
                }
            });
            
            // 主机名列 - 调整宽度，剩余空间自动填充
            dgvResults.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "HostName",
                HeaderText = "主机名",
                Width = 200,
                DataPropertyName = "HostName",
                AutoSizeMode = DataGridViewAutoSizeColumnMode.Fill,
                DefaultCellStyle = new DataGridViewCellStyle
                {
                    Font = new Font("Microsoft YaHei UI", 9F, FontStyle.Regular),
                    Alignment = DataGridViewContentAlignment.MiddleLeft
                }
            });

            // 设置数据源
            dgvResults.DataSource = _bindingList;
        }

        #endregion

        #region 事件处理

        /// <summary>
        /// 开始跟踪按钮点击
        /// </summary>
        private async void BtnStart_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrWhiteSpace(txtTargetAddress.Text))
            {
                // StatusUpdated?.Invoke("请输入目标地址", true); // 移除对外状态更新
                return;
            }

            try
            {
                // 清空之前的结果
                _bindingList.Clear();
                lblStatus.Text = "准备开始跟踪...";
                
                // 设置按钮状态
                btnStart.Enabled = false;
                btnStop.Enabled = true;
                
                // 创建取消令牌
                _cancellationTokenSource = new CancellationTokenSource();
                
                // 开始跟踪
                _currentResult = await _traceService.StartTraceAsync(
                    txtTargetAddress.Text.Trim(),
                    (int)numMaxHops.Value,
                    (int)numTimeout.Value,
                    _cancellationTokenSource.Token
                );
            }
            catch (Exception ex)
            {
                // StatusUpdated?.Invoke($"跟踪失败: {ex.Message}", true); // 移除对外状态更新
            }
            finally
            {
                // 恢复按钮状态
                btnStart.Enabled = true;
                btnStop.Enabled = false;
                
                _cancellationTokenSource?.Dispose();
                _cancellationTokenSource = null;
            }
        }

        /// <summary>
        /// 停止跟踪按钮点击
        /// </summary>
        private void BtnStop_Click(object sender, EventArgs e)
        {
            _cancellationTokenSource?.Cancel();
            _traceService.StopTrace();
            
            btnStart.Enabled = true;
            btnStop.Enabled = false;
            
            // StatusUpdated?.Invoke("跟踪已停止", false); // 移除对外状态更新
        }

        /// <summary>
        /// 目标地址文本改变
        /// </summary>
        private void TxtTargetAddress_TextChanged(object sender, EventArgs e)
        {
            btnStart.Enabled = !string.IsNullOrWhiteSpace(txtTargetAddress.Text) && !btnStop.Enabled;
        }

        /// <summary>
        /// 跳点完成事件处理
        /// </summary>
        private void OnHopCompleted(TraceRouteHop hop)
        {
            if (InvokeRequired)
            {
                Invoke(new Action<TraceRouteHop>(OnHopCompleted), hop);
                return;
            }

            // 创建显示用的数据对象
            var displayHop = new TraceRouteHopDisplay
            {
                HopNumber = hop.HopNumber,
                DisplayAddress = hop.GetDisplayAddress(),
                Delay1Display = hop.GetDisplayDelay(1),
                Delay2Display = hop.GetDisplayDelay(2),
                Delay3Display = hop.GetDisplayDelay(3),
                HostName = hop.HostName ?? ""
            };

            // 添加到绑定列表
            _bindingList.Add(displayHop);
            
            // 滚动到最新行并选中
            if (dgvResults.Rows.Count > 0)
            {
                dgvResults.FirstDisplayedScrollingRowIndex = dgvResults.Rows.Count - 1;
                dgvResults.ClearSelection();
                dgvResults.Rows[dgvResults.Rows.Count - 1].Selected = true;
            }
            
            // 更新状态
            lblStatus.Text = $"正在跟踪第 {hop.HopNumber} 跳...";
        }

        /// <summary>
        /// 跟踪完成事件处理
        /// </summary>
        private void OnTraceCompleted(TraceRouteResult result)
        {
            if (InvokeRequired)
            {
                Invoke(new Action<TraceRouteResult>(OnTraceCompleted), result);
                return;
            }

            // 更新状态
            lblStatus.Text = result.GetStatusDescription();
            
            // 恢复按钮状态
            btnStart.Enabled = true;
            btnStop.Enabled = false;
        }

        /// <summary>
        /// 状态更新事件处理
        /// </summary>
        private void OnStatusUpdated(string message)
        {
            if (InvokeRequired)
            {
                Invoke(new Action<string>(OnStatusUpdated), message);
                return;
            }

            lblStatus.Text = message;
            // StatusUpdated?.Invoke(message, false); // 移除对外状态更新
        }

        #endregion

        #region 辅助类

        /// <summary>
        /// 用于数据绑定的跳点显示类
        /// </summary>
        public class TraceRouteHopDisplay
        {
            public int HopNumber { get; set; }
            public string DisplayAddress { get; set; } = string.Empty;
            public string Delay1Display { get; set; } = string.Empty;
            public string Delay2Display { get; set; } = string.Empty;
            public string Delay3Display { get; set; } = string.Empty;
            public string HostName { get; set; } = string.Empty;
        }

        #endregion

        #region 资源清理

        /// <summary>
        /// 释放资源
        /// </summary>
        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _cancellationTokenSource?.Cancel();
                _cancellationTokenSource?.Dispose();
                _traceService?.Dispose();
                components?.Dispose();
            }
            base.Dispose(disposing);
        }

        #endregion
    }
} 