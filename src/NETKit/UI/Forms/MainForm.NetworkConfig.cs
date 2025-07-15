using NETKit.Core.Models;
using NETKit.Core.Helpers;

namespace NETKit.UI.Forms
{
    /// <summary>
    /// MainForm的网络配置相关功能
    /// </summary>
    public partial class MainForm
    {
        #region 网络适配器管理

        /// <summary>
        /// 加载网络适配器列表
        /// </summary>
        private void LoadNetworkAdapters()
        {
            try
            {
                // 记住当前选择的网卡名称
                string selectedAdapterName = null;
                var currentSelected = cmbNetworkAdapters.SelectedItem as NetworkAdapterItem;
                if (currentSelected != null)
                {
                    selectedAdapterName = currentSelected.Name;
                }

                cmbNetworkAdapters.Items.Clear();
                var adapters = _networkService.GetNetworkAdapters(chkShowAllAdapters.Checked);

                foreach (var adapter in adapters)
                {
                    cmbNetworkAdapters.Items.Add(adapter);
                }

                if (cmbNetworkAdapters.Items.Count > 0)
                {
                    // 尝试找到之前选择的网卡
                    int indexToSelect = 0;
                    if (!string.IsNullOrEmpty(selectedAdapterName))
                    {
                        for (int i = 0; i < cmbNetworkAdapters.Items.Count; i++)
                        {
                            var adapter = cmbNetworkAdapters.Items[i] as NetworkAdapterItem;
                            if (adapter != null && adapter.Name == selectedAdapterName)
                            {
                                indexToSelect = i;
                                break;
                            }
                        }
                    }
                    
                    cmbNetworkAdapters.SelectedIndex = indexToSelect;
                }
            }
            catch (Exception ex)
            {
                UpdateStatus($"加载网络适配器时发生错误: {ex.Message}", true);
            }
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

                    // 更新DHCP复选框的状态以反映当前网卡配置
                    chkDhcp.Checked = adapterInfo.IsDHCPEnabled;

                    // 根据DHCP状态更新UI
                    chkDhcp_CheckedChanged(this, EventArgs.Empty);

                    // 如果不是DHCP，则显示当前IP配置（但不显示"未配置"文本）
                    if (!adapterInfo.IsDHCPEnabled)
                    {
                        // 只有当值不是"未配置"时才填入输入框
                        txtIpAddress.Text = adapterInfo.CurrentIP != "未配置" ? adapterInfo.CurrentIP : "";
                        txtSubnetMask.Text = adapterInfo.CurrentSubnetMask != "未配置" ? adapterInfo.CurrentSubnetMask : "";
                        txtGateway.Text = adapterInfo.CurrentGateway != "未配置" ? adapterInfo.CurrentGateway : "";
                        
                        // 处理DNS显示 - 分离主DNS和备DNS
                        if (adapterInfo.DNSText != "未配置" && !string.IsNullOrEmpty(adapterInfo.DNSText))
                        {
                            var dnsServers = adapterInfo.DNSText.Split(',', StringSplitOptions.RemoveEmptyEntries);
                            txtDnsServer.Text = dnsServers.Length > 0 ? dnsServers[0].Trim() : "";
                            txtSecondaryDnsServer.Text = dnsServers.Length > 1 ? dnsServers[1].Trim() : "";
                        }
                        else
                        {
                            txtDnsServer.Text = "";
                            txtSecondaryDnsServer.Text = "";
                        }
                    }
                    else
                    {
                        ClearInputFields();
                    }
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

        #endregion

        #region 网络配置操作

        /// <summary>
        /// 应用网络配置按钮点击事件
        /// </summary>
        private async void btnApplyConfig_Click(object sender, EventArgs e)
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
                bool success;
                if (chkDhcp.Checked)
                {
                    // 设置为DHCP
                    success = await _networkService.SetDHCPConfigurationAsync(selectedAdapter.Name);
                }
                else
                {
                    // 设置为静态IP - 现在支持备DNS
                    var validation = ValidationHelper.ValidateNetworkConfig(
                        selectedAdapter.Name,
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

                    // 创建网络配置对象，包含主DNS和备DNS
                    var config = new NetworkConfiguration
                    {
                        AdapterName = selectedAdapter.Name,
                        IPAddress = txtIpAddress.Text,
                        SubnetMask = txtSubnetMask.Text,
                        Gateway = txtGateway.Text,
                        PrimaryDNS = txtDnsServer.Text,
                        SecondaryDNS = txtSecondaryDnsServer.Text,
                        UseDHCP = false
                    };

                    success = await _networkService.ApplyStaticIPConfigurationAsync(config);
                }

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

        /// <summary>
        /// 刷新适配器按钮点击事件
        /// </summary>
        private void btnRefreshAdapters_Click(object sender, EventArgs e)
        {
            LoadNetworkAdapters();
        }

        /// <summary>
        /// 显示所有适配器复选框变化事件
        /// </summary>
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

        /// <summary>
        /// DHCP复选框变化事件
        /// </summary>
        private void chkDhcp_CheckedChanged(object sender, EventArgs e)
        {
            bool isDhcp = chkDhcp.Checked;

            txtIpAddress.Enabled = !isDhcp;
            txtSubnetMask.Enabled = !isDhcp;
            txtGateway.Enabled = !isDhcp;
            // DNS服务器保持启用，允许用户设置自定义DNS

            if (isDhcp)
            {
                // 如果勾选了DHCP，可以清空静态IP的输入框
                txtIpAddress.Clear();
                txtSubnetMask.Clear();
                txtGateway.Clear();
            }
        }

        /// <summary>
        /// 清空输入字段
        /// </summary>
        private void ClearInputFields()
        {
            txtIpAddress.Clear();
            txtSubnetMask.Clear();
            txtGateway.Clear();
            txtDnsServer.Clear();
            txtSecondaryDnsServer.Clear();
        }

        #endregion
    }
}
