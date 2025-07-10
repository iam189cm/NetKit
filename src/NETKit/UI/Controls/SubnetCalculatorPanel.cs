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

        // 移除对外的状态事件，改为内部状态处理
        // public event Action<string, bool> StatusUpdated;  // 已删除，让状态独立

        public SubnetCalculatorPanel()
        {
            _calculationService = new SubnetCalculationService();
            InitializeComponent();
            SetupEventHandlers();
            LoadCIDROptions();
        }

        private void InitializeComponent()
        {
            this.SuspendLayout();

            // 输入区域
            var grpInput = new GroupBox
            {
                Text = "输入参数",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextPrimary,
                Location = new Point(10, 10),
                Size = new Size(560, 80),
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right
            };

            var lblIP = new Label
            {
                Text = "IP地址/网络:",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextPrimary,
                Location = new Point(15, 25),
                Size = new Size(85, 17),
                TextAlign = ContentAlignment.MiddleLeft
            };

            txtIPAddress = new TextBox
            {
                Font = new Font("Microsoft YaHei UI", 9F),
                Location = new Point(105, 22),
                Size = new Size(150, 23),
                PlaceholderText = "192.168.1.0"
            };

            var lblCIDR = new Label
            {
                Text = "CIDR:",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextPrimary,
                Location = new Point(270, 25),
                Size = new Size(40, 17),
                TextAlign = ContentAlignment.MiddleLeft
            };

            cmbCIDR = new ComboBox
            {
                Font = new Font("Microsoft YaHei UI", 9F),
                Location = new Point(315, 22),
                Size = new Size(60, 25),
                DropDownStyle = ComboBoxStyle.DropDown
            };

            var lblMask = new Label
            {
                Text = "子网掩码:",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextPrimary,
                Location = new Point(15, 50),
                Size = new Size(85, 17),
                TextAlign = ContentAlignment.MiddleLeft
            };

            txtSubnetMask = new TextBox
            {
                Font = new Font("Microsoft YaHei UI", 9F),
                Location = new Point(105, 47),
                Size = new Size(150, 23),
                PlaceholderText = "255.255.255.0"
            };

            btnCalculate = new Button
            {
                Text = "计算",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Color.White,
                BackColor = Constants.Colors.PrimaryBlue,
                FlatStyle = FlatStyle.Flat,
                Location = new Point(390, 22),
                Size = new Size(70, 28)
            };
            btnCalculate.FlatAppearance.BorderSize = 0;

            btnClear = new Button
            {
                Text = "清空",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Color.White,
                BackColor = Constants.Colors.SecondaryGray,
                FlatStyle = FlatStyle.Flat,
                Location = new Point(470, 22),
                Size = new Size(70, 28)
            };
            btnClear.FlatAppearance.BorderSize = 0;

            grpInput.Controls.AddRange(new Control[] { lblIP, txtIPAddress, lblCIDR, cmbCIDR, lblMask, txtSubnetMask, btnCalculate, btnClear });

            // 基础结果显示区域
            var grpResult = new GroupBox
            {
                Text = "计算结果",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextPrimary,
                Location = new Point(10, 100),
                Size = new Size(560, 160),
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right
            };

            txtResult = new TextBox
            {
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextSecondary,
                BackColor = Constants.Colors.PanelBackground,
                Location = new Point(15, 25),
                Size = new Size(530, 120),
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical,
                Text = "请输入IP地址和子网掩码进行计算",
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom
            };

            grpResult.Controls.Add(txtResult);

            // 高级功能Tab控件
            tabAdvanced = new TabControl
            {
                Font = new Font("Microsoft YaHei UI", 9F),
                Location = new Point(10, 270),
                Size = new Size(560, 280),
                Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right | AnchorStyles.Bottom
            };

            // Tab 1: 子网划分
            var tabSubdivision = new TabPage("子网划分");
            CreateSubdivisionTab(tabSubdivision);

            tabAdvanced.TabPages.Add(tabSubdivision);

            // 添加所有控件到主面板
            this.Controls.AddRange(new Control[] { grpInput, grpResult, tabAdvanced });

            this.Size = new Size(580, 560);
            this.ResumeLayout(false);
        }

        private void CreateSubdivisionTab(TabPage tab)
        {
            var grpSubdivision = new GroupBox
            {
                Text = "子网划分参数",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextPrimary,
                Location = new Point(10, 10),
                Size = new Size(530, 80)
            };

            var lblSubnetCount = new Label
            {
                Text = "子网数量:",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextPrimary,
                Location = new Point(15, 25),
                Size = new Size(70, 17)
            };

            txtSubnetCount = new TextBox
            {
                Font = new Font("Microsoft YaHei UI", 9F),
                Location = new Point(90, 22),
                Size = new Size(80, 23),
                PlaceholderText = "4"
            };

            var lblHostsPerSubnet = new Label
            {
                Text = "每子网主机数:",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextPrimary,
                Location = new Point(200, 25),
                Size = new Size(90, 17)
            };

            txtHostsPerSubnet = new TextBox
            {
                Font = new Font("Microsoft YaHei UI", 9F),
                Location = new Point(295, 22),
                Size = new Size(80, 23),
                PlaceholderText = "60"
            };

            btnSubdivide = new Button
            {
                Text = "计算划分",
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Color.White,
                BackColor = Constants.Colors.PrimaryBlue,
                FlatStyle = FlatStyle.Flat,
                Location = new Point(400, 20),
                Size = new Size(80, 28)
            };
            btnSubdivide.FlatAppearance.BorderSize = 0;

            grpSubdivision.Controls.AddRange(new Control[] { lblSubnetCount, txtSubnetCount, lblHostsPerSubnet, txtHostsPerSubnet, btnSubdivide });

            txtSubdivisionResult = new TextBox
            {
                Font = new Font("Microsoft YaHei UI", 9F),
                ForeColor = Constants.Colors.TextSecondary,
                BackColor = Constants.Colors.PanelBackground,
                Location = new Point(10, 100),
                Size = new Size(530, 140),
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical,
                Text = "请先进行基础子网计算，然后设置划分参数"
            };

            tab.Controls.AddRange(new Control[] { grpSubdivision, txtSubdivisionResult });
        }


        private void SetupEventHandlers()
        {
            btnCalculate.Click += BtnCalculate_Click;
            btnClear.Click += BtnClear_Click;
            btnSubdivide.Click += BtnSubdivide_Click;
            
            cmbCIDR.SelectedIndexChanged += CmbCIDR_SelectedIndexChanged;
            txtSubnetMask.TextChanged += TxtSubnetMask_TextChanged;
            
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
                    
                    // 移除对外的状态事件，改为内部状态处理
                    // if (result.IsValid)
                    // {
                    //     OnStatusUpdated("计算完成", false);
                    // }
                    // else
                    // {
                    //     OnStatusUpdated($"计算失败: {result.ErrorMessage}", true);
                    // }
                }
            }
            catch (Exception ex)
            {
                // 移除对外的状态事件，改为内部状态处理
                // OnStatusUpdated($"计算时发生错误: {ex.Message}", true);
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

        // 移除对外的状态事件，改为内部状态处理
        // protected virtual void OnStatusUpdated(string message, bool isError)
        // {
        //     StatusUpdated?.Invoke(message, isError);
        // }

        // 控件声明
        private TextBox txtIPAddress;
        private ComboBox cmbCIDR;
        private TextBox txtSubnetMask;
        private Button btnCalculate;
        private Button btnClear;
        private TextBox txtResult;
        private TabControl tabAdvanced;
        private TextBox txtSubnetCount;
        private TextBox txtHostsPerSubnet;
        private Button btnSubdivide;
        private TextBox txtSubdivisionResult;
    }
}
