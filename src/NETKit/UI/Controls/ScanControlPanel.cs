using System;
using System.Net;
using System.Windows.Forms;
using System.Text.RegularExpressions;
using NETKit.Core.Models;

namespace NETKit.UI.Controls
{
    /// <summary>
    /// 用于配置和控制网络扫描的用户控件面板
    /// </summary>
    public partial class ScanControlPanel : UserControl
    {
        public event Action<ScanConfiguration> OnStartScan;
        public event Action OnStopScan;

        public ScanControlPanel()
        {
            InitializeComponent();
            InitializeDefaults();
            InitializeEventHandlers();
        }

        private void InitializeDefaults()
        {
            // 设置默认值
            txtIp1.Text = "192";
            txtIp2.Text = "168";
            txtIp3.Text = "1";
            txtRangeStart.Text = "1";
            txtRangeEnd.Text = "254";
            txtTimeout.Text = "200";
        }

        private void InitializeEventHandlers()
        {
            // 为IP地址输入框添加事件处理
            txtIp1.KeyPress += IpTextBox_KeyPress;
            txtIp1.TextChanged += IpTextBox_TextChanged;
            txtIp1.KeyDown += IpTextBox_KeyDown;
            txtIp1.Leave += IpTextBox_Leave;

            txtIp2.KeyPress += IpTextBox_KeyPress;
            txtIp2.TextChanged += IpTextBox_TextChanged;
            txtIp2.KeyDown += IpTextBox_KeyDown;
            txtIp2.Leave += IpTextBox_Leave;

            txtIp3.KeyPress += IpTextBox_KeyPress;
            txtIp3.TextChanged += IpTextBox_TextChanged;
            txtIp3.KeyDown += IpTextBox_KeyDown;
            txtIp3.Leave += IpTextBox_Leave;

            // 为范围输入框添加事件处理
            txtRangeStart.KeyPress += RangeTextBox_KeyPress;
            txtRangeStart.TextChanged += RangeTextBox_TextChanged;
            txtRangeStart.KeyDown += RangeTextBox_KeyDown;
            txtRangeStart.Leave += RangeTextBox_Leave;

            txtRangeEnd.KeyPress += RangeTextBox_KeyPress;
            txtRangeEnd.TextChanged += RangeTextBox_TextChanged;
            txtRangeEnd.KeyDown += RangeTextBox_KeyDown;
            txtRangeEnd.Leave += RangeTextBox_Leave;

            // 为超时输入框添加事件处理
            txtTimeout.KeyPress += TimeoutTextBox_KeyPress;
            txtTimeout.Leave += TimeoutTextBox_Leave;
        }

        #region IP地址输入验证

        private void IpTextBox_KeyPress(object sender, KeyPressEventArgs e)
        {
            // 只允许数字和控制字符
            if (!char.IsControl(e.KeyChar) && !char.IsDigit(e.KeyChar))
            {
                e.Handled = true;
                return;
            }

            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 检查输入后的值是否会超过255
            if (char.IsDigit(e.KeyChar))
            {
                string newText = textBox.Text.Insert(textBox.SelectionStart, e.KeyChar.ToString());
                if (int.TryParse(newText, out int value) && value > 255)
                {
                    e.Handled = true;
                }
            }
        }

        private void IpTextBox_TextChanged(object sender, EventArgs e)
        {
            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 自动跳转到下一个输入框
            if (textBox.Text.Length == 3 && int.TryParse(textBox.Text, out int value) && value <= 255)
            {
                MoveToNextControl(textBox);
            }
        }

        private void IpTextBox_KeyDown(object sender, KeyEventArgs e)
        {
            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 处理点号键，自动跳转到下一个输入框
            if (e.KeyCode == Keys.OemPeriod || e.KeyCode == Keys.Decimal)
            {
                e.Handled = true;
                MoveToNextControl(textBox);
            }
            // 处理退格键，如果当前输入框为空，跳转到上一个输入框
            else if (e.KeyCode == Keys.Back && textBox.Text.Length == 0 && textBox.SelectionStart == 0)
            {
                MoveToPreviousControl(textBox);
            }
        }

        private void IpTextBox_Leave(object sender, EventArgs e)
        {
            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 验证并格式化输入值
            if (int.TryParse(textBox.Text, out int value))
            {
                if (value < 0) value = 0;
                if (value > 255) value = 255;
                
                // 对于第一段IP，最小值为1
                if (textBox == txtIp1 && value < 1) value = 1;
                
                textBox.Text = value.ToString();
            }
            else if (string.IsNullOrEmpty(textBox.Text))
            {
                // 如果为空，设置默认值
                if (textBox == txtIp1) textBox.Text = "192";
                else if (textBox == txtIp2) textBox.Text = "168";
                else if (textBox == txtIp3) textBox.Text = "1";
            }
        }

        #endregion

        #region 范围输入验证

        private void RangeTextBox_KeyPress(object sender, KeyPressEventArgs e)
        {
            // 只允许数字和控制字符
            if (!char.IsControl(e.KeyChar) && !char.IsDigit(e.KeyChar))
            {
                e.Handled = true;
                return;
            }

            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 检查输入后的值是否会超过254
            if (char.IsDigit(e.KeyChar))
            {
                string newText = textBox.Text.Insert(textBox.SelectionStart, e.KeyChar.ToString());
                if (int.TryParse(newText, out int value) && value > 254)
                {
                    e.Handled = true;
                }
            }
        }

        private void RangeTextBox_TextChanged(object sender, EventArgs e)
        {
            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 自动跳转到下一个输入框
            if (textBox.Text.Length == 3 && int.TryParse(textBox.Text, out int value) && value <= 254)
            {
                MoveToNextControl(textBox);
            }
        }

        private void RangeTextBox_KeyDown(object sender, KeyEventArgs e)
        {
            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 处理退格键
            if (e.KeyCode == Keys.Back && textBox.Text.Length == 0 && textBox.SelectionStart == 0)
            {
                MoveToPreviousControl(textBox);
            }
        }

        private void RangeTextBox_Leave(object sender, EventArgs e)
        {
            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 验证并格式化输入值
            if (int.TryParse(textBox.Text, out int value))
            {
                if (value < 1) value = 1;
                if (value > 254) value = 254;
                textBox.Text = value.ToString();
            }
            else if (string.IsNullOrEmpty(textBox.Text))
            {
                // 如果为空，设置默认值
                if (textBox == txtRangeStart) textBox.Text = "1";
                else if (textBox == txtRangeEnd) textBox.Text = "254";
            }
        }

        #endregion

        #region 超时输入验证

        private void TimeoutTextBox_KeyPress(object sender, KeyPressEventArgs e)
        {
            // 只允许数字和控制字符
            if (!char.IsControl(e.KeyChar) && !char.IsDigit(e.KeyChar))
            {
                e.Handled = true;
                return;
            }

            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 检查输入后的值是否会超过5000
            if (char.IsDigit(e.KeyChar))
            {
                string newText = textBox.Text.Insert(textBox.SelectionStart, e.KeyChar.ToString());
                if (int.TryParse(newText, out int value) && value > 5000)
                {
                    e.Handled = true;
                }
            }
        }

        private void TimeoutTextBox_Leave(object sender, EventArgs e)
        {
            var textBox = sender as TextBox;
            if (textBox == null) return;

            // 验证并格式化输入值
            if (int.TryParse(textBox.Text, out int value))
            {
                if (value < 100) value = 100;
                if (value > 5000) value = 5000;
                textBox.Text = value.ToString();
            }
            else if (string.IsNullOrEmpty(textBox.Text))
            {
                textBox.Text = "200";
            }
        }

        #endregion

        #region 控件导航

        private void MoveToNextControl(TextBox currentTextBox)
        {
            if (currentTextBox == txtIp1)
                txtIp2.Focus();
            else if (currentTextBox == txtIp2)
                txtIp3.Focus();
            else if (currentTextBox == txtIp3)
                txtRangeStart.Focus();
            else if (currentTextBox == txtRangeStart)
                txtRangeEnd.Focus();
            else if (currentTextBox == txtRangeEnd)
                txtTimeout.Focus();
        }

        private void MoveToPreviousControl(TextBox currentTextBox)
        {
            if (currentTextBox == txtIp2)
            {
                txtIp1.Focus();
                txtIp1.SelectionStart = txtIp1.Text.Length;
            }
            else if (currentTextBox == txtIp3)
            {
                txtIp2.Focus();
                txtIp2.SelectionStart = txtIp2.Text.Length;
            }
            else if (currentTextBox == txtRangeStart)
            {
                txtIp3.Focus();
                txtIp3.SelectionStart = txtIp3.Text.Length;
            }
            else if (currentTextBox == txtRangeEnd)
            {
                txtRangeStart.Focus();
                txtRangeStart.SelectionStart = txtRangeStart.Text.Length;
            }
            else if (currentTextBox == txtTimeout)
            {
                txtRangeEnd.Focus();
                txtRangeEnd.SelectionStart = txtRangeEnd.Text.Length;
            }
        }

        #endregion

        private void btnStartScan_Click(object sender, EventArgs e)
        {
            try
            {
                // 验证所有输入值
                if (!ValidateInputs(out string errorMessage))
                {
                    MessageBox.Show(errorMessage, "输入错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                var ip1 = (byte)int.Parse(txtIp1.Text);
                var ip2 = (byte)int.Parse(txtIp2.Text);
                var ip3 = (byte)int.Parse(txtIp3.Text);
                var start = (byte)int.Parse(txtRangeStart.Text);
                var end = (byte)int.Parse(txtRangeEnd.Text);

                if (start > end)
                {
                    MessageBox.Show("起始IP不能大于结束IP。", "输入错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                var config = new ScanConfiguration
                {
                    StartAddress = new IPAddress(new[] { ip1, ip2, ip3, start }),
                    EndAddress = new IPAddress(new[] { ip1, ip2, ip3, end }),
                    Timeout = int.Parse(txtTimeout.Text),
                    MaxConcurrentScans = 20  // 固定值，因为我们移除了线程控制
                };

                OnStartScan?.Invoke(config);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"创建扫描配置时出错: {ex.Message}", "错误", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private bool ValidateInputs(out string errorMessage)
        {
            errorMessage = string.Empty;

            // 验证IP地址段
            if (!ValidateIpSegment(txtIp1.Text, "第一段IP", 1, 255, out errorMessage)) return false;
            if (!ValidateIpSegment(txtIp2.Text, "第二段IP", 0, 255, out errorMessage)) return false;
            if (!ValidateIpSegment(txtIp3.Text, "第三段IP", 0, 255, out errorMessage)) return false;

            // 验证范围
            if (!ValidateIpSegment(txtRangeStart.Text, "起始IP", 1, 254, out errorMessage)) return false;
            if (!ValidateIpSegment(txtRangeEnd.Text, "结束IP", 1, 254, out errorMessage)) return false;

            // 验证超时
            if (!ValidateTimeout(txtTimeout.Text, out errorMessage)) return false;

            return true;
        }

        private bool ValidateIpSegment(string text, string fieldName, int min, int max, out string errorMessage)
        {
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(text))
            {
                errorMessage = $"{fieldName}不能为空。";
                return false;
            }

            if (!int.TryParse(text, out int value))
            {
                errorMessage = $"{fieldName}必须是数字。";
                return false;
            }

            if (value < min || value > max)
            {
                errorMessage = $"{fieldName}必须在{min}-{max}之间。";
                return false;
            }

            return true;
        }

        private bool ValidateTimeout(string text, out string errorMessage)
        {
            errorMessage = string.Empty;

            if (string.IsNullOrWhiteSpace(text))
            {
                errorMessage = "超时时间不能为空。";
                return false;
            }

            if (!int.TryParse(text, out int value))
            {
                errorMessage = "超时时间必须是数字。";
                return false;
            }

            if (value < 100 || value > 5000)
            {
                errorMessage = "超时时间必须在100-5000毫秒之间。";
                return false;
            }

            return true;
        }

        private void btnStopScan_Click(object sender, EventArgs e)
        {
            OnStopScan?.Invoke();
        }

        public void SetScanInProgress(bool inProgress)
        {
            btnStartScan.Enabled = !inProgress;
            btnStopScan.Enabled = inProgress;
            
            // 扫描期间禁用所有输入控件
            txtIp1.Enabled = !inProgress;
            txtIp2.Enabled = !inProgress;
            txtIp3.Enabled = !inProgress;
            txtRangeStart.Enabled = !inProgress;
            txtRangeEnd.Enabled = !inProgress;
            txtTimeout.Enabled = !inProgress;
        }

        /// <summary>
        /// 获取当前IP范围的格式化字符串用于显示
        /// </summary>
        public string GetCurrentRange()
        {
            return $"{txtIp1.Text}.{txtIp2.Text}.{txtIp3.Text}.{txtRangeStart.Text} - {txtIp1.Text}.{txtIp2.Text}.{txtIp3.Text}.{txtRangeEnd.Text}";
        }

        /// <summary>
        /// 获取当前范围内的IP总数
        /// </summary>
        public int GetTotalIpCount()
        {
            if (int.TryParse(txtRangeStart.Text, out int start) && int.TryParse(txtRangeEnd.Text, out int end))
            {
                return end - start + 1;
            }
            return 0;
        }
    }
}
