using System;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using NETKit.Common;
using NETKit.Core.Models;
using NETKit.Core.Services;

namespace NETKit.UI.Controls
{
    /// <summary>
    /// 子网计算主面板
    /// </summary>
    public partial class SubnetCalculatorPanel : UserControl
    {
        private readonly SubnetCalculationService _calculationService;
        private SubnetCalculationResult _currentResult;

        public SubnetCalculatorPanel()
        {
            _calculationService = new SubnetCalculationService();
            InitializeComponent();
            SetupEventHandlers();
            LoadCIDROptions();
        }

        private void SetupEventHandlers()
        {
            // 实时计算
            txtIPAddress.TextChanged += (s, e) => PerformCalculation();
            txtSubnetMask.TextChanged += (s, e) => PerformCalculation();
        }

        private void LoadCIDROptions()
        {
            for (int i = 8; i <= 30; i++)
            {
                cmbCIDR.Items.Add($"/{i}");
            }
        }

        private void BtnCalculate_Click(object sender, EventArgs e)
        {
            PerformCalculation();
        }

        private void BtnClear_Click(object sender, EventArgs e)
        {
            txtIPAddress.Clear();
            txtSubnetMask.Clear();
            cmbCIDR.SelectedIndex = -1;
            txtResult.Text = "请输入IP地址和子网掩码进行计算";
            txtSubdivisionResult.Text = "请先进行基础子网计算，然后设置划分参数";
            _currentResult = null;
        }

        private void PerformCalculation()
        {
            if (string.IsNullOrWhiteSpace(txtIPAddress.Text))
                return;

            try
            {
                SubnetCalculationResult result = null;

                // 检查是否使用CIDR格式
                if (txtIPAddress.Text.Contains('/'))
                {
                    result = _calculationService.CalculateSubnetFromCIDR(txtIPAddress.Text);
                }
                else if (!string.IsNullOrWhiteSpace(txtSubnetMask.Text))
                {
                    result = _calculationService.CalculateSubnet(txtIPAddress.Text, txtSubnetMask.Text);
                }
                else
                {
                    return; // 没有足够的信息进行计算
                }

                if (result != null)
                {
                    _currentResult = result;
                    DisplayResult(result);
                }
            }
            catch (Exception ex)
            {
                txtResult.Text = $"计算时发生错误: {ex.Message}";
            }
        }

        private void DisplayResult(SubnetCalculationResult result)
        {
            if (result.IsValid)
            {
                txtResult.Text = result.GetFormattedResult();
                
                // 同步CIDR选择
                if (cmbCIDR.SelectedItem?.ToString() != $"/{result.PrefixLength}")
                {
                    cmbCIDR.SelectedItem = $"/{result.PrefixLength}";
                }
                
                // 同步子网掩码
                if (txtSubnetMask.Text != result.SubnetMask.ToString())
                {
                    txtSubnetMask.Text = result.SubnetMask.ToString();
                }
            }
            else
            {
                txtResult.Text = result.GetFormattedResult();
            }
        }

        private void CmbCIDR_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (cmbCIDR.SelectedItem != null)
            {
                string cidr = cmbCIDR.SelectedItem.ToString();
                int prefixLength = int.Parse(cidr.Substring(1));
                
                // 计算对应的子网掩码
                uint mask = prefixLength == 0 ? 0 : (0xFFFFFFFF << (32 - prefixLength));
                var maskBytes = BitConverter.GetBytes(mask);
                if (BitConverter.IsLittleEndian)
                    Array.Reverse(maskBytes);
                
                txtSubnetMask.Text = $"{maskBytes[0]}.{maskBytes[1]}.{maskBytes[2]}.{maskBytes[3]}";
                
                PerformCalculation();
            }
        }

        private void TxtSubnetMask_TextChanged(object sender, EventArgs e)
        {
            // 根据子网掩码更新CIDR选择
            if (!string.IsNullOrWhiteSpace(txtSubnetMask.Text))
            {
                try
                {
                    if (System.Net.IPAddress.TryParse(txtSubnetMask.Text, out var mask))
                    {
                        int prefixLength = SubnetMaskToPrefixLength(mask);
                        string cidrText = $"/{prefixLength}";
                        
                        if (cmbCIDR.SelectedItem?.ToString() != cidrText)
                        {
                            cmbCIDR.SelectedItem = cidrText;
                        }
                    }
                }
                catch
                {
                    // 忽略转换错误
                }
            }
        }

        private void BtnSubdivide_Click(object sender, EventArgs e)
        {
            if (_currentResult == null || !_currentResult.IsValid)
            {
                txtSubdivisionResult.Text = "请先进行有效的子网计算";
                return;
            }

            try
            {
                int subnetCount = 0;
                if (!string.IsNullOrWhiteSpace(txtSubnetCount.Text))
                {
                    if (!int.TryParse(txtSubnetCount.Text, out subnetCount) || subnetCount <= 0)
                    {
                        txtSubdivisionResult.Text = "请输入有效的子网数量";
                        return;
                    }
                }
                else if (!string.IsNullOrWhiteSpace(txtHostsPerSubnet.Text))
                {
                    if (int.TryParse(txtHostsPerSubnet.Text, out int hostsPerSubnet) && hostsPerSubnet > 0)
                    {
                        // 根据每子网主机数计算需要的子网数量
                        long totalHosts = _currentResult.UsableHostCount;
                        subnetCount = (int)Math.Ceiling((double)totalHosts / hostsPerSubnet);
                    }
                    else
                    {
                        txtSubdivisionResult.Text = "请输入有效的每子网主机数";
                        return;
                    }
                }
                else
                {
                    txtSubdivisionResult.Text = "请输入子网数量或每子网主机数";
                    return;
                }

                var subnets = _calculationService.SubdivideNetwork(
                    _currentResult.NetworkAddress.ToString(),
                    _currentResult.PrefixLength,
                    subnetCount);

                if (subnets.Any())
                {
                    var resultText = $"成功划分为 {subnets.Count} 个子网:\n\n";
                    foreach (var subnet in subnets)
                    {
                        resultText += $"{subnet.GetFormattedInfo()}\n";
                    }
                    txtSubdivisionResult.Text = resultText;
                }
                else
                {
                    txtSubdivisionResult.Text = "无法进行子网划分，可能是参数不合理或子网过小";
                }
            }
            catch (Exception ex)
            {
                txtSubdivisionResult.Text = $"子网划分时发生错误: {ex.Message}";
            }
        }

        private int SubnetMaskToPrefixLength(System.Net.IPAddress mask)
        {
            var bytes = mask.GetAddressBytes();
            if (BitConverter.IsLittleEndian)
                Array.Reverse(bytes);
            
            uint maskInt = BitConverter.ToUInt32(bytes, 0);
            int prefixLength = 0;
            
            while ((maskInt & 0x80000000) != 0)
            {
                prefixLength++;
                maskInt <<= 1;
            }
            
            return prefixLength;
        }
    }
}
