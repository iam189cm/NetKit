using NETKit.Core.Helpers;
using NETKit.Common;

namespace NETKit.UI.Forms
{
    /// <summary>
    /// MainForm的输入验证相关功能
    /// </summary>
    public partial class MainForm
    {
        #region 输入验证初始化

        /// <summary>
        /// 初始化输入验证
        /// </summary>
        private void InitializeInputValidation()
        {
            // 初始化验证定时器
            _validationTimer = new System.Windows.Forms.Timer();
            _validationTimer.Interval = 500; // 500ms延迟验证
            _validationTimer.Tick += ValidationTimer_Tick;

            // 为IP地址输入框添加事件
            txtIpAddress.KeyPress += IpTextBox_KeyPress;
            txtIpAddress.TextChanged += IpTextBox_TextChanged;
            txtIpAddress.Leave += IpTextBox_Leave;

            // 为子网掩码输入框添加事件
            txtSubnetMask.KeyPress += IpTextBox_KeyPress;
            txtSubnetMask.TextChanged += SubnetTextBox_TextChanged;
            txtSubnetMask.Leave += SubnetTextBox_Leave;

            // 为网关输入框添加事件
            txtGateway.KeyPress += IpTextBox_KeyPress;
            txtGateway.TextChanged += GatewayTextBox_TextChanged;
            txtGateway.Leave += GatewayTextBox_Leave;

            // 为DNS服务器输入框添加事件
            txtDnsServer.KeyPress += IpTextBox_KeyPress;
            txtDnsServer.TextChanged += DnsTextBox_TextChanged;
            txtDnsServer.Leave += DnsTextBox_Leave;

            // 为备DNS服务器输入框添加事件
            txtSecondaryDnsServer.KeyPress += IpTextBox_KeyPress;
            txtSecondaryDnsServer.TextChanged += SecondaryDnsTextBox_TextChanged;
            txtSecondaryDnsServer.Leave += SecondaryDnsTextBox_Leave;
        }

        #endregion

        #region 输入限制事件

        /// <summary>
        /// IP地址输入框按键事件 - 限制只能输入数字和点
        /// </summary>
        private void IpTextBox_KeyPress(object sender, KeyPressEventArgs e)
        {
            // 允许数字、点、控制字符（退格、删除等）
            if (!char.IsDigit(e.KeyChar) && e.KeyChar != '.' && !char.IsControl(e.KeyChar))
            {
                e.Handled = true;
            }
        }

        #endregion

        #region 文本变化事件

        /// <summary>
        /// IP地址输入框文本变化事件
        /// </summary>
        private void IpTextBox_TextChanged(object sender, EventArgs e)
        {
            _lastChangedTextBox = sender as TextBox;
            _validationTimer.Stop();
            _validationTimer.Start();
        }

        /// <summary>
        /// 子网掩码输入框文本变化事件
        /// </summary>
        private void SubnetTextBox_TextChanged(object sender, EventArgs e)
        {
            _lastChangedTextBox = sender as TextBox;
            _validationTimer.Stop();
            _validationTimer.Start();
        }

        /// <summary>
        /// 网关输入框文本变化事件
        /// </summary>
        private void GatewayTextBox_TextChanged(object sender, EventArgs e)
        {
            _lastChangedTextBox = sender as TextBox;
            _validationTimer.Stop();
            _validationTimer.Start();
        }

        /// <summary>
        /// DNS输入框文本变化事件
        /// </summary>
        private void DnsTextBox_TextChanged(object sender, EventArgs e)
        {
            _lastChangedTextBox = sender as TextBox;
            _validationTimer.Stop();
            _validationTimer.Start();
        }

        /// <summary>
        /// 备DNS输入框文本变化事件
        /// </summary>
        private void SecondaryDnsTextBox_TextChanged(object sender, EventArgs e)
        {
            _lastChangedTextBox = sender as TextBox;
            _validationTimer.Stop();
            _validationTimer.Start();
        }

        #endregion

        #region 失去焦点事件

        /// <summary>
        /// IP地址输入框失去焦点事件
        /// </summary>
        private void IpTextBox_Leave(object sender, EventArgs e)
        {
            ValidateTextBox(sender as TextBox);
        }

        /// <summary>
        /// 子网掩码输入框失去焦点事件
        /// </summary>
        private void SubnetTextBox_Leave(object sender, EventArgs e)
        {
            ValidateTextBox(sender as TextBox);
        }

        /// <summary>
        /// 网关输入框失去焦点事件
        /// </summary>
        private void GatewayTextBox_Leave(object sender, EventArgs e)
        {
            ValidateTextBox(sender as TextBox);
        }

        /// <summary>
        /// DNS输入框失去焦点事件
        /// </summary>
        private void DnsTextBox_Leave(object sender, EventArgs e)
        {
            ValidateTextBox(sender as TextBox);
        }

        /// <summary>
        /// 备DNS输入框失去焦点事件
        /// </summary>
        private void SecondaryDnsTextBox_Leave(object sender, EventArgs e)
        {
            ValidateTextBox(sender as TextBox);
        }

        #endregion

        #region 验证逻辑

        /// <summary>
        /// 验证定时器事件
        /// </summary>
        private void ValidationTimer_Tick(object sender, EventArgs e)
        {
            _validationTimer.Stop();
            
            if (_lastChangedTextBox != null)
            {
                ValidateTextBox(_lastChangedTextBox);
            }
        }

        /// <summary>
        /// 验证文本框输入
        /// </summary>
        private void ValidateTextBox(TextBox textBox)
        {
            if (textBox == null) return;

            Label errorLabel = GetErrorLabel(textBox);
            if (errorLabel == null) return;

            IPValidationResult result;

            if (textBox == txtSubnetMask)
            {
                result = ValidationHelper.ValidateSubnetMaskWithDetails(textBox.Text);
            }
            else
            {
                // 对于备DNS，允许为空
                if (textBox == txtSecondaryDnsServer && string.IsNullOrWhiteSpace(textBox.Text))
                {
                    result = new IPValidationResult { Level = ValidationLevel.Success, Message = "" };
                }
                else
                {
                    result = ValidationHelper.ValidateIPAddressWithDetails(textBox.Text);
                }
            }

            ShowValidationResult(errorLabel, result);
        }

        /// <summary>
        /// 获取对应的错误提示Label
        /// </summary>
        private Label GetErrorLabel(TextBox textBox)
        {
            if (textBox == txtIpAddress) return lblIpError;
            if (textBox == txtSubnetMask) return lblSubnetError;
            if (textBox == txtGateway) return lblGatewayError;
            if (textBox == txtDnsServer) return lblDnsError;
            if (textBox == txtSecondaryDnsServer) return lblSecondaryDnsError;
            return null;
        }

        #endregion

        #region 验证结果显示

        /// <summary>
        /// 显示验证结果
        /// </summary>
        private void ShowValidationResult(Label errorLabel, IPValidationResult result)
        {
            switch (result.Level)
            {
                case ValidationLevel.Error:
                    ShowError(errorLabel, result.Message);
                    break;
                case ValidationLevel.Warning:
                    ShowWarning(errorLabel, result.Message);
                    break;
                case ValidationLevel.Success:
                    HideError(errorLabel);
                    break;
            }
        }

        /// <summary>
        /// 显示错误信息
        /// </summary>
        private void ShowError(Label errorLabel, string message)
        {
            if (string.IsNullOrEmpty(message))
            {
                errorLabel.Visible = false;
                return;
            }

            errorLabel.Text = message;
            errorLabel.ForeColor = Color.Red;
            errorLabel.Visible = true;
        }

        /// <summary>
        /// 显示警告信息
        /// </summary>
        private void ShowWarning(Label errorLabel, string message)
        {
            if (string.IsNullOrEmpty(message))
            {
                errorLabel.Visible = false;
                return;
            }

            errorLabel.Text = message;
            errorLabel.ForeColor = Color.Orange;
            errorLabel.Visible = true;
        }

        /// <summary>
        /// 隐藏错误信息
        /// </summary>
        private void HideError(Label errorLabel)
        {
            errorLabel.Visible = false;
        }

        #endregion
    }
}
