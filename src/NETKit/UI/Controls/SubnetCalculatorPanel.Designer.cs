using NETKit.Common;

namespace NETKit.UI.Controls
{
    partial class SubnetCalculatorPanel
    {
        /// <summary> 
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary> 
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region 组件设计器生成的代码

        /// <summary> 
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.grpInput = new System.Windows.Forms.GroupBox();
            this.btnClear = new System.Windows.Forms.Button();
            this.btnCalculate = new System.Windows.Forms.Button();
            this.txtSubnetMask = new System.Windows.Forms.TextBox();
            this.lblMask = new System.Windows.Forms.Label();
            this.cmbCIDR = new System.Windows.Forms.ComboBox();
            this.lblCIDR = new System.Windows.Forms.Label();
            this.txtIPAddress = new System.Windows.Forms.TextBox();
            this.lblIP = new System.Windows.Forms.Label();
            this.grpResult = new System.Windows.Forms.GroupBox();
            this.txtResult = new System.Windows.Forms.TextBox();
            this.tabAdvanced = new System.Windows.Forms.TabControl();
            this.tabSubdivision = new System.Windows.Forms.TabPage();
            this.txtSubdivisionResult = new System.Windows.Forms.TextBox();
            this.grpSubdivision = new System.Windows.Forms.GroupBox();
            this.btnSubdivide = new System.Windows.Forms.Button();
            this.txtHostsPerSubnet = new System.Windows.Forms.TextBox();
            this.lblHostsPerSubnet = new System.Windows.Forms.Label();
            this.txtSubnetCount = new System.Windows.Forms.TextBox();
            this.lblSubnetCount = new System.Windows.Forms.Label();
            this.grpInput.SuspendLayout();
            this.grpResult.SuspendLayout();
            this.tabAdvanced.SuspendLayout();
            this.tabSubdivision.SuspendLayout();
            this.grpSubdivision.SuspendLayout();
            this.SuspendLayout();
            // 
            // grpInput
            // 
            this.grpInput.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.grpInput.Controls.Add(this.btnClear);
            this.grpInput.Controls.Add(this.btnCalculate);
            this.grpInput.Controls.Add(this.txtSubnetMask);
            this.grpInput.Controls.Add(this.lblMask);
            this.grpInput.Controls.Add(this.cmbCIDR);
            this.grpInput.Controls.Add(this.lblCIDR);
            this.grpInput.Controls.Add(this.txtIPAddress);
            this.grpInput.Controls.Add(this.lblIP);
            this.grpInput.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.grpInput.ForeColor = Constants.Colors.TextPrimary;
            this.grpInput.Location = new System.Drawing.Point(10, 10);
            this.grpInput.Name = "grpInput";
            this.grpInput.Size = new System.Drawing.Size(560, 80);
            this.grpInput.TabIndex = 0;
            this.grpInput.TabStop = false;
            this.grpInput.Text = "输入参数";
            // 
            // btnClear
            // 
            this.btnClear.BackColor = Constants.Colors.SecondaryGray;
            this.btnClear.FlatAppearance.BorderSize = 0;
            this.btnClear.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnClear.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.btnClear.ForeColor = System.Drawing.Color.White;
            this.btnClear.Location = new System.Drawing.Point(470, 22);
            this.btnClear.Name = "btnClear";
            this.btnClear.Size = new System.Drawing.Size(70, 28);
            this.btnClear.TabIndex = 7;
            this.btnClear.Text = "清空";
            this.btnClear.UseVisualStyleBackColor = false;
            this.btnClear.Click += new System.EventHandler(this.BtnClear_Click);
            // 
            // btnCalculate
            // 
            this.btnCalculate.BackColor = Constants.Colors.PrimaryBlue;
            this.btnCalculate.FlatAppearance.BorderSize = 0;
            this.btnCalculate.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnCalculate.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.btnCalculate.ForeColor = System.Drawing.Color.White;
            this.btnCalculate.Location = new System.Drawing.Point(390, 22);
            this.btnCalculate.Name = "btnCalculate";
            this.btnCalculate.Size = new System.Drawing.Size(70, 28);
            this.btnCalculate.TabIndex = 6;
            this.btnCalculate.Text = "计算";
            this.btnCalculate.UseVisualStyleBackColor = false;
            this.btnCalculate.Click += new System.EventHandler(this.BtnCalculate_Click);
            // 
            // txtSubnetMask
            // 
            this.txtSubnetMask.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtSubnetMask.Location = new System.Drawing.Point(105, 47);
            this.txtSubnetMask.Name = "txtSubnetMask";
            this.txtSubnetMask.PlaceholderText = "255.255.255.0";
            this.txtSubnetMask.Size = new System.Drawing.Size(150, 23);
            this.txtSubnetMask.TabIndex = 5;
            this.txtSubnetMask.TextChanged += new System.EventHandler(this.TxtSubnetMask_TextChanged);
            // 
            // lblMask
            // 
            this.lblMask.AutoSize = true;
            this.lblMask.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblMask.ForeColor = Constants.Colors.TextPrimary;
            this.lblMask.Location = new System.Drawing.Point(15, 50);
            this.lblMask.Name = "lblMask";
            this.lblMask.Size = new System.Drawing.Size(68, 17);
            this.lblMask.TabIndex = 4;
            this.lblMask.Text = "子网掩码:";
            // 
            // cmbCIDR
            // 
            this.cmbCIDR.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDown;
            this.cmbCIDR.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.cmbCIDR.FormattingEnabled = true;
            this.cmbCIDR.Location = new System.Drawing.Point(315, 22);
            this.cmbCIDR.Name = "cmbCIDR";
            this.cmbCIDR.Size = new System.Drawing.Size(60, 25);
            this.cmbCIDR.TabIndex = 3;
            this.cmbCIDR.SelectedIndexChanged += new System.EventHandler(this.CmbCIDR_SelectedIndexChanged);
            // 
            // lblCIDR
            // 
            this.lblCIDR.AutoSize = true;
            this.lblCIDR.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblCIDR.ForeColor = Constants.Colors.TextPrimary;
            this.lblCIDR.Location = new System.Drawing.Point(270, 25);
            this.lblCIDR.Name = "lblCIDR";
            this.lblCIDR.Size = new System.Drawing.Size(40, 17);
            this.lblCIDR.TabIndex = 2;
            this.lblCIDR.Text = "CIDR:";
            // 
            // txtIPAddress
            // 
            this.txtIPAddress.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtIPAddress.Location = new System.Drawing.Point(105, 22);
            this.txtIPAddress.Name = "txtIPAddress";
            this.txtIPAddress.PlaceholderText = "192.168.1.0";
            this.txtIPAddress.Size = new System.Drawing.Size(150, 23);
            this.txtIPAddress.TabIndex = 1;
            // 
            // lblIP
            // 
            this.lblIP.AutoSize = true;
            this.lblIP.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblIP.ForeColor = Constants.Colors.TextPrimary;
            this.lblIP.Location = new System.Drawing.Point(15, 25);
            this.lblIP.Name = "lblIP";
            this.lblIP.Size = new System.Drawing.Size(80, 17);
            this.lblIP.TabIndex = 0;
            this.lblIP.Text = "IP地址/网络:";
            // 
            // grpResult
            // 
            this.grpResult.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.grpResult.Controls.Add(this.txtResult);
            this.grpResult.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.grpResult.ForeColor = Constants.Colors.TextPrimary;
            this.grpResult.Location = new System.Drawing.Point(10, 100);
            this.grpResult.Name = "grpResult";
            this.grpResult.Size = new System.Drawing.Size(560, 160);
            this.grpResult.TabIndex = 1;
            this.grpResult.TabStop = false;
            this.grpResult.Text = "计算结果";
            // 
            // txtResult
            // 
            this.txtResult.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.txtResult.BackColor = Constants.Colors.PanelBackground;
            this.txtResult.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtResult.ForeColor = Constants.Colors.TextSecondary;
            this.txtResult.Location = new System.Drawing.Point(15, 25);
            this.txtResult.Multiline = true;
            this.txtResult.Name = "txtResult";
            this.txtResult.ReadOnly = true;
            this.txtResult.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtResult.Size = new System.Drawing.Size(530, 120);
            this.txtResult.TabIndex = 0;
            this.txtResult.Text = "请输入IP地址和子网掩码进行计算";
            // 
            // tabAdvanced
            // 
            this.tabAdvanced.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.tabAdvanced.Controls.Add(this.tabSubdivision);
            this.tabAdvanced.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.tabAdvanced.Location = new System.Drawing.Point(10, 270);
            this.tabAdvanced.Name = "tabAdvanced";
            this.tabAdvanced.SelectedIndex = 0;
            this.tabAdvanced.Size = new System.Drawing.Size(560, 280);
            this.tabAdvanced.TabIndex = 2;
            // 
            // tabSubdivision
            // 
            this.tabSubdivision.Controls.Add(this.txtSubdivisionResult);
            this.tabSubdivision.Controls.Add(this.grpSubdivision);
            this.tabSubdivision.Location = new System.Drawing.Point(4, 26);
            this.tabSubdivision.Name = "tabSubdivision";
            this.tabSubdivision.Padding = new System.Windows.Forms.Padding(3);
            this.tabSubdivision.Size = new System.Drawing.Size(552, 250);
            this.tabSubdivision.TabIndex = 0;
            this.tabSubdivision.Text = "子网划分";
            this.tabSubdivision.UseVisualStyleBackColor = true;
            // 
            // txtSubdivisionResult
            // 
            this.txtSubdivisionResult.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.txtSubdivisionResult.BackColor = Constants.Colors.PanelBackground;
            this.txtSubdivisionResult.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtSubdivisionResult.ForeColor = Constants.Colors.TextSecondary;
            this.txtSubdivisionResult.Location = new System.Drawing.Point(10, 100);
            this.txtSubdivisionResult.Multiline = true;
            this.txtSubdivisionResult.Name = "txtSubdivisionResult";
            this.txtSubdivisionResult.ReadOnly = true;
            this.txtSubdivisionResult.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtSubdivisionResult.Size = new System.Drawing.Size(530, 140);
            this.txtSubdivisionResult.TabIndex = 1;
            this.txtSubdivisionResult.Text = "请先进行基础子网计算，然后设置划分参数";
            // 
            // grpSubdivision
            // 
            this.grpSubdivision.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.grpSubdivision.Controls.Add(this.btnSubdivide);
            this.grpSubdivision.Controls.Add(this.txtHostsPerSubnet);
            this.grpSubdivision.Controls.Add(this.lblHostsPerSubnet);
            this.grpSubdivision.Controls.Add(this.txtSubnetCount);
            this.grpSubdivision.Controls.Add(this.lblSubnetCount);
            this.grpSubdivision.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.grpSubdivision.ForeColor = Constants.Colors.TextPrimary;
            this.grpSubdivision.Location = new System.Drawing.Point(10, 10);
            this.grpSubdivision.Name = "grpSubdivision";
            this.grpSubdivision.Size = new System.Drawing.Size(530, 80);
            this.grpSubdivision.TabIndex = 0;
            this.grpSubdivision.TabStop = false;
            this.grpSubdivision.Text = "子网划分参数";
            // 
            // btnSubdivide
            // 
            this.btnSubdivide.BackColor = Constants.Colors.PrimaryBlue;
            this.btnSubdivide.FlatAppearance.BorderSize = 0;
            this.btnSubdivide.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnSubdivide.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.btnSubdivide.ForeColor = System.Drawing.Color.White;
            this.btnSubdivide.Location = new System.Drawing.Point(400, 20);
            this.btnSubdivide.Name = "btnSubdivide";
            this.btnSubdivide.Size = new System.Drawing.Size(80, 28);
            this.btnSubdivide.TabIndex = 4;
            this.btnSubdivide.Text = "计算划分";
            this.btnSubdivide.UseVisualStyleBackColor = false;
            this.btnSubdivide.Click += new System.EventHandler(this.BtnSubdivide_Click);
            // 
            // txtHostsPerSubnet
            // 
            this.txtHostsPerSubnet.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtHostsPerSubnet.Location = new System.Drawing.Point(295, 22);
            this.txtHostsPerSubnet.Name = "txtHostsPerSubnet";
            this.txtHostsPerSubnet.PlaceholderText = "60";
            this.txtHostsPerSubnet.Size = new System.Drawing.Size(80, 23);
            this.txtHostsPerSubnet.TabIndex = 3;
            // 
            // lblHostsPerSubnet
            // 
            this.lblHostsPerSubnet.AutoSize = true;
            this.lblHostsPerSubnet.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblHostsPerSubnet.ForeColor = Constants.Colors.TextPrimary;
            this.lblHostsPerSubnet.Location = new System.Drawing.Point(200, 25);
            this.lblHostsPerSubnet.Name = "lblHostsPerSubnet";
            this.lblHostsPerSubnet.Size = new System.Drawing.Size(92, 17);
            this.lblHostsPerSubnet.TabIndex = 2;
            this.lblHostsPerSubnet.Text = "每子网主机数:";
            // 
            // txtSubnetCount
            // 
            this.txtSubnetCount.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtSubnetCount.Location = new System.Drawing.Point(90, 22);
            this.txtSubnetCount.Name = "txtSubnetCount";
            this.txtSubnetCount.PlaceholderText = "4";
            this.txtSubnetCount.Size = new System.Drawing.Size(80, 23);
            this.txtSubnetCount.TabIndex = 1;
            // 
            // lblSubnetCount
            // 
            this.lblSubnetCount.AutoSize = true;
            this.lblSubnetCount.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblSubnetCount.ForeColor = Constants.Colors.TextPrimary;
            this.lblSubnetCount.Location = new System.Drawing.Point(15, 25);
            this.lblSubnetCount.Name = "lblSubnetCount";
            this.lblSubnetCount.Size = new System.Drawing.Size(68, 17);
            this.lblSubnetCount.TabIndex = 0;
            this.lblSubnetCount.Text = "子网数量:";
            // 
            // SubnetCalculatorPanel
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.tabAdvanced);
            this.Controls.Add(this.grpResult);
            this.Controls.Add(this.grpInput);
            this.Name = "SubnetCalculatorPanel";
            this.Size = new System.Drawing.Size(580, 560);
            this.grpInput.ResumeLayout(false);
            this.grpInput.PerformLayout();
            this.grpResult.ResumeLayout(false);
            this.grpResult.PerformLayout();
            this.tabAdvanced.ResumeLayout(false);
            this.tabSubdivision.ResumeLayout(false);
            this.tabSubdivision.PerformLayout();
            this.grpSubdivision.ResumeLayout(false);
            this.grpSubdivision.PerformLayout();
            this.ResumeLayout(false);
        }

        #endregion

        private System.Windows.Forms.GroupBox grpInput;
        private System.Windows.Forms.Button btnClear;
        private System.Windows.Forms.Button btnCalculate;
        private System.Windows.Forms.TextBox txtSubnetMask;
        private System.Windows.Forms.Label lblMask;
        private System.Windows.Forms.ComboBox cmbCIDR;
        private System.Windows.Forms.Label lblCIDR;
        private System.Windows.Forms.TextBox txtIPAddress;
        private System.Windows.Forms.Label lblIP;
        private System.Windows.Forms.GroupBox grpResult;
        private System.Windows.Forms.TextBox txtResult;
        private System.Windows.Forms.TabControl tabAdvanced;
        private System.Windows.Forms.TabPage tabSubdivision;
        private System.Windows.Forms.TextBox txtSubdivisionResult;
        private System.Windows.Forms.GroupBox grpSubdivision;
        private System.Windows.Forms.Button btnSubdivide;
        private System.Windows.Forms.TextBox txtHostsPerSubnet;
        private System.Windows.Forms.Label lblHostsPerSubnet;
        private System.Windows.Forms.TextBox txtSubnetCount;
        private System.Windows.Forms.Label lblSubnetCount;
    }
} 