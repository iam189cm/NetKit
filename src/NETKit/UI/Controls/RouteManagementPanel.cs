using System.ComponentModel;
using NETKit.Core.Models;
using NETKit.Core.Services;
using NETKit.Common;

namespace NETKit.UI.Controls
{
    /// <summary>
    /// 路由管理面板
    /// </summary>
    public partial class RouteManagementPanel : UserControl
    {
        private readonly RouteManagementService _routeService;
        private List<RouteRule> _currentRoutes = new List<RouteRule>();
        private bool _isLoading = false;
        private bool _isDataLoaded = false;

        public event Action<string, bool>? StatusUpdated;

        /// <summary>
        /// 构造函数
        /// </summary>
        public RouteManagementPanel()
        {
            _routeService = new RouteManagementService();
            _routeService.StatusUpdated += OnStatusUpdated;
            
            InitializeComponent();
            InitializeUI();
        }

        /// <summary>
        /// 初始化UI
        /// </summary>
        private void InitializeUI()
        {
            // 设置路由表格
            SetupRouteDataGridView();
            
            // 加载网卡列表
            LoadNetworkAdapters();
            
            // 设置默认值
            numMetric.Value = 1;
            numMetric.Minimum = 1;
            numMetric.Maximum = 9999;
            
            // 绑定事件
            btnRefreshRoutes.Click += BtnRefreshRoutes_Click;
            btnAddRoute.Click += BtnAddRoute_Click;
            btnDeleteRoute.Click += BtnDeleteRoute_Click;
            cmbAdapter.SelectedIndexChanged += CmbAdapter_SelectedIndexChanged;
            
            // 移除自动加载，改为懒加载模式
            ShowInitialLoadingHint();
        }

        /// <summary>
        /// 设置路由表格
        /// </summary>
        private void SetupRouteDataGridView()
        {
            dgvRoutes.AutoGenerateColumns = false;
            dgvRoutes.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            dgvRoutes.MultiSelect = false;
            dgvRoutes.AllowUserToAddRows = false;
            dgvRoutes.AllowUserToDeleteRows = false;
            dgvRoutes.ReadOnly = true;
            dgvRoutes.ScrollBars = ScrollBars.Vertical;
            
            // 添加列
            dgvRoutes.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "DestinationText",
                HeaderText = "网络目标",
                DataPropertyName = "DestinationText",
                Width = 231,
                ReadOnly = true
            });
            
            dgvRoutes.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "SubnetMask",
                HeaderText = "网络掩码",
                DataPropertyName = "SubnetMask",
                Width = 198,
                ReadOnly = true
            });
            
            dgvRoutes.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "Gateway",
                HeaderText = "网关",
                DataPropertyName = "Gateway",
                Width = 169,
                ReadOnly = true
            });
            
            dgvRoutes.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "InterfaceName",
                HeaderText = "接口",
                DataPropertyName = "InterfaceName",
                Width = 260,
                ReadOnly = true
            });
            
            dgvRoutes.Columns.Add(new DataGridViewTextBoxColumn
            {
                Name = "Metric",
                HeaderText = "跃点数",
                DataPropertyName = "Metric",
                Width = 118,
                ReadOnly = true
            });
        }

        /// <summary>
        /// 加载网络适配器
        /// </summary>
        private void LoadNetworkAdapters()
        {
            try
            {
                cmbAdapter.Items.Clear();
                
                // 使用与IP配置页面相同的逻辑获取网卡
                var networkAdapterService = new NetworkAdapterService();
                var adapters = networkAdapterService.GetNetworkAdapters(AdapterFilterType.PhysicalOnly);
                
                foreach (var adapter in adapters)
                {
                    cmbAdapter.Items.Add(adapter);
                }
                
                if (cmbAdapter.Items.Count > 0)
                {
                    cmbAdapter.SelectedIndex = 0;
                }
                
                OnStatusUpdated($"已加载 {adapters.Count} 个网络适配器", false);
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"加载网络适配器失败: {ex.Message}", true);
            }
        }

        /// <summary>
        /// 加载路由表
        /// </summary>
        private async Task LoadRouteTableAsync()
        {
            if (_isLoading) return;
            
            try
            {
                _isLoading = true;
                SetButtonsEnabled(false);
                
                // 显示加载状态
                lblRouteCount.Text = "正在加载路由表...";
                lblConflictInfo.Visible = false;
                
                _currentRoutes = await _routeService.GetRouteTableAsync();
                
                // 更新UI
                dgvRoutes.DataSource = null;
                dgvRoutes.DataSource = _currentRoutes;
                
                // 更新统计信息
                lblRouteCount.Text = $"共 {_currentRoutes.Count} 条路由规则";
                
                // 检测冲突
                await CheckConflictsAsync();
                
                // 标记数据已加载
                _isDataLoaded = true;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"加载路由表失败: {ex.Message}", true);
                lblRouteCount.Text = "加载失败，请点击刷新重试";
            }
            finally
            {
                _isLoading = false;
                SetButtonsEnabled(true);
            }
        }

        /// <summary>
        /// 检测多网卡冲突
        /// </summary>
        private async Task CheckConflictsAsync()
        {
            try
            {
                var conflictResult = await _routeService.DetectMultiAdapterConflictAsync();
                
                if (conflictResult.HasConflict)
                {
                    lblConflictInfo.Text = $"⚠️ {conflictResult.ConflictDescription}";
                    lblConflictInfo.ForeColor = Color.Red;
                    lblConflictInfo.Visible = true;
                    
                    if (!string.IsNullOrEmpty(conflictResult.SuggestedSolution))
                    {
                        OnStatusUpdated($"检测到路由冲突: {conflictResult.SuggestedSolution}", false);
                    }
                }
                else
                {
                    lblConflictInfo.Visible = false;
                }
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"检测路由冲突失败: {ex.Message}", true);
            }
        }

        /// <summary>
        /// 刷新路由表按钮点击事件
        /// </summary>
        private async void BtnRefreshRoutes_Click(object? sender, EventArgs e)
        {
            // 强制重新加载数据
            _isDataLoaded = false;
            await LoadRouteTableAsync();
        }

        /// <summary>
        /// 添加路由规则按钮点击事件
        /// </summary>
        private async void BtnAddRoute_Click(object? sender, EventArgs e)
        {
            try
            {
                // 验证输入
                if (string.IsNullOrWhiteSpace(txtDestination.Text))
                {
                    OnStatusUpdated("请输入网络目标", true);
                    txtDestination.Focus();
                    return;
                }
                
                if (cmbAdapter.SelectedItem == null)
                {
                    OnStatusUpdated("请选择接口", true);
                    cmbAdapter.Focus();
                    return;
                }
                
                var selectedAdapter = (NetworkAdapterItem)cmbAdapter.SelectedItem;
                
                SetButtonsEnabled(false);
                
                // 创建路由规则
                var routeRule = await _routeService.CreateRouteRuleAsync(
                    txtDestination.Text.Trim(),
                    selectedAdapter.Name,
                    (int)numMetric.Value,
                    chkPersistent.Checked);
                
                if (routeRule == null)
                {
                    return; // 错误信息已经在服务中显示
                }
                
                // 添加路由规则
                bool success = await _routeService.AddRouteAsync(routeRule);
                
                if (success)
                {
                    // 清空输入
                    txtDestination.Clear();
                    numMetric.Value = 1;
                    chkPersistent.Checked = false;
                    txtDestination.Focus();
                    
                    // 刷新路由表
                    await LoadRouteTableAsync();
                }
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"添加路由规则失败: {ex.Message}", true);
            }
            finally
            {
                SetButtonsEnabled(true);
            }
        }

        /// <summary>
        /// 删除路由规则按钮点击事件
        /// </summary>
        private async void BtnDeleteRoute_Click(object? sender, EventArgs e)
        {
            try
            {
                if (dgvRoutes.SelectedRows.Count == 0)
                {
                    OnStatusUpdated("请选择要删除的路由规则", true);
                    return;
                }
                
                var selectedRoute = (RouteRule)dgvRoutes.SelectedRows[0].DataBoundItem;
                
                // 确认删除
                var result = MessageBox.Show(
                    $"确定要删除路由规则吗？\n\n{selectedRoute.DestinationText} -> {selectedRoute.Gateway}",
                    "确认删除",
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Question);
                
                if (result != DialogResult.Yes)
                    return;
                
                SetButtonsEnabled(false);
                
                // 删除路由规则
                bool success = await _routeService.DeleteRouteAsync(selectedRoute);
                
                if (success)
                {
                    // 刷新路由表
                    await LoadRouteTableAsync();
                }
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"删除路由规则失败: {ex.Message}", true);
            }
            finally
            {
                SetButtonsEnabled(true);
            }
        }



        /// <summary>
        /// 网卡选择变化事件
        /// </summary>
        private void CmbAdapter_SelectedIndexChanged(object? sender, EventArgs e)
        {
            if (cmbAdapter.SelectedItem is NetworkAdapterItem adapter)
            {
                // 可以显示网卡的详细信息
                OnStatusUpdated($"已选择接口: {adapter.DisplayName}", false);
            }
        }



        /// <summary>
        /// 设置按钮启用状态
        /// </summary>
        /// <param name="enabled">是否启用</param>
        private void SetButtonsEnabled(bool enabled)
        {
            btnRefreshRoutes.Enabled = enabled;
            btnAddRoute.Enabled = enabled;
            btnDeleteRoute.Enabled = enabled;
        }

        /// <summary>
        /// 显示初始加载提示
        /// </summary>
        private void ShowInitialLoadingHint()
        {
            lblRouteCount.Text = "点击刷新按钮或执行操作时将自动加载路由表";
            lblConflictInfo.Visible = false;
        }

        /// <summary>
        /// 确保数据已加载（懒加载）
        /// </summary>
        /// <returns>是否成功加载</returns>
        public async Task<bool> EnsureDataLoaded()
        {
            if (_isDataLoaded) return true;
            
            try
            {
                await LoadRouteTableAsync();
                return _isDataLoaded;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"加载路由表失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 状态更新事件处理
        /// </summary>
        /// <param name="message">状态消息</param>
        /// <param name="isError">是否为错误</param>
        private void OnStatusUpdated(string message, bool isError)
        {
            StatusUpdated?.Invoke(message, isError);
        }

        /// <summary>
        /// 释放资源
        /// </summary>
        /// <param name="disposing">是否释放托管资源</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                if (_routeService != null)
                {
                    _routeService.StatusUpdated -= OnStatusUpdated;
                }
            }
            base.Dispose(disposing);
        }
    }
} 