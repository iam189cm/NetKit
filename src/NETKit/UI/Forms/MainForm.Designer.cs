using NETKit.Common;

namespace NETKit.UI.Forms
{
    partial class MainForm
    {
        /// <summary>
        ///  必需的设计器变量
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        ///  清理所有正在使用的资源
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows 窗体设计器生成的代码

        /// <summary>
        ///  设计器支持所需的方法 - 不要修改
        ///  使用代码编辑器修改此方法的内容
        /// </summary>
        private void InitializeComponent()
        {
            this.lblNetworkAdapter = new System.Windows.Forms.Label();
            this.cmbNetworkAdapters = new System.Windows.Forms.ComboBox();
            this.lblIpAddress = new System.Windows.Forms.Label();
            this.txtIpAddress = new System.Windows.Forms.TextBox();
            this.lblSubnetMask = new System.Windows.Forms.Label();
            this.txtSubnetMask = new System.Windows.Forms.TextBox();
            this.lblGateway = new System.Windows.Forms.Label();
            this.txtGateway = new System.Windows.Forms.TextBox();
            this.lblDnsServer = new System.Windows.Forms.Label();
            this.txtDnsServer = new System.Windows.Forms.TextBox();
            this.btnApplyConfig = new System.Windows.Forms.Button();
            this.btnRefreshAdapters = new System.Windows.Forms.Button();
            this.lblStatus = new System.Windows.Forms.Label();
            this.txtStatus = new System.Windows.Forms.TextBox();
            this.chkShowAllAdapters = new System.Windows.Forms.CheckBox();
            this.grpAdapterInfo = new System.Windows.Forms.GroupBox();
            this.txtAdapterInfoContent = new System.Windows.Forms.TextBox();
            this.tabControlMain = new System.Windows.Forms.TabControl();
            this.tabPageIpConfig = new System.Windows.Forms.TabPage();
            this.tabPagePingTest = new System.Windows.Forms.TabPage();
            this.tabPageSubnetCalc = new System.Windows.Forms.TabPage();
            this.scanControlPanel = new NETKit.UI.Controls.ScanControlPanel();
            this.scanStatisticsPanel = new NETKit.UI.Controls.ScanStatisticsPanel();
            this.ipGridControl = new NETKit.UI.Controls.IPGridControl();
            this.subnetCalculatorPanel = new NETKit.UI.Controls.SubnetCalculatorPanel();
            this.grpAdapterInfo.SuspendLayout();
            this.tabControlMain.SuspendLayout();
            this.tabPageIpConfig.SuspendLayout();
            this.tabPagePingTest.SuspendLayout();
            this.tabPageSubnetCalc.SuspendLayout();
            this.SuspendLayout();
            // 
            // lblNetworkAdapter
            // 
            this.lblNetworkAdapter.AutoSize = true;
            this.lblNetworkAdapter.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblNetworkAdapter.ForeColor = Constants.Colors.TextPrimary;
            this.lblNetworkAdapter.Location = new System.Drawing.Point(35, 35);
            this.lblNetworkAdapter.Name = "lblNetworkAdapter";
            this.lblNetworkAdapter.Size = new System.Drawing.Size(68, 17);
            this.lblNetworkAdapter.TabIndex = 0;
            this.lblNetworkAdapter.Text = "网卡选择:";
            // 
            // cmbNetworkAdapters
            // 
            this.cmbNetworkAdapters.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbNetworkAdapters.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.cmbNetworkAdapters.FormattingEnabled = true;
            this.cmbNetworkAdapters.Location = new System.Drawing.Point(130, 32);
            this.cmbNetworkAdapters.Name = "cmbNetworkAdapters";
            this.cmbNetworkAdapters.Size = new System.Drawing.Size(420, 25);
            this.cmbNetworkAdapters.TabIndex = 1;
            // 
            // grpAdapterInfo
            // 
            this.grpAdapterInfo.Controls.Add(this.txtAdapterInfoContent);
            this.grpAdapterInfo.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.grpAdapterInfo.ForeColor = Constants.Colors.TextPrimary;
            this.grpAdapterInfo.Location = new System.Drawing.Point(35, 90);
            this.grpAdapterInfo.Name = "grpAdapterInfo";
            this.grpAdapterInfo.Size = new System.Drawing.Size(515, 160);
            this.grpAdapterInfo.TabIndex = 17;
            this.grpAdapterInfo.TabStop = false;
            this.grpAdapterInfo.Text = "当前网卡信息";
            // 
            // txtAdapterInfoContent
            // 
            this.txtAdapterInfoContent.BackColor = Constants.Colors.PanelBackground;
            this.txtAdapterInfoContent.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.txtAdapterInfoContent.Font = new System.Drawing.Font("Microsoft YaHei UI", 8F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtAdapterInfoContent.ForeColor = Constants.Colors.TextSecondary;
            this.txtAdapterInfoContent.Location = new System.Drawing.Point(15, 25);
            this.txtAdapterInfoContent.Multiline = true;
            this.txtAdapterInfoContent.Name = "txtAdapterInfoContent";
            this.txtAdapterInfoContent.ReadOnly = true;
            this.txtAdapterInfoContent.ShortcutsEnabled = true;
            this.txtAdapterInfoContent.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtAdapterInfoContent.Size = new System.Drawing.Size(485, 125);
            this.txtAdapterInfoContent.TabIndex = 0;
            this.txtAdapterInfoContent.Text = "请选择网络适配器";
            // 
            // lblIpAddress
            // 
            this.lblIpAddress.AutoSize = true;
            this.lblIpAddress.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblIpAddress.ForeColor = Constants.Colors.TextPrimary;
            this.lblIpAddress.Location = new System.Drawing.Point(35, 260);
            this.lblIpAddress.Name = "lblIpAddress";
            this.lblIpAddress.Size = new System.Drawing.Size(56, 17);
            this.lblIpAddress.TabIndex = 2;
            this.lblIpAddress.Text = "IP地址:";
            // 
            // txtIpAddress
            // 
            this.txtIpAddress.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtIpAddress.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtIpAddress.Location = new System.Drawing.Point(130, 257);
            this.txtIpAddress.Name = "txtIpAddress";
            this.txtIpAddress.PlaceholderText = "例如: 192.168.1.100";
            this.txtIpAddress.Size = new System.Drawing.Size(320, 23);
            this.txtIpAddress.TabIndex = 3;
            // 
            // chkDhcp
            // 
            this.chkDhcp = new System.Windows.Forms.CheckBox();
            this.chkDhcp.AutoSize = true;
            this.chkDhcp.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.chkDhcp.ForeColor = Constants.Colors.TextPrimary;
            this.chkDhcp.Location = new System.Drawing.Point(460, 259);
            this.chkDhcp.Name = "chkDhcp";
            this.chkDhcp.Size = new System.Drawing.Size(63, 21);
            this.chkDhcp.TabIndex = 4;
            this.chkDhcp.Text = "DHCP";
            this.chkDhcp.UseVisualStyleBackColor = true;
            this.chkDhcp.CheckedChanged += new System.EventHandler(this.chkDhcp_CheckedChanged);
            // 
            // lblSubnetMask
            // 
            this.lblSubnetMask.AutoSize = true;
            this.lblSubnetMask.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblSubnetMask.ForeColor = Constants.Colors.TextPrimary;
            this.lblSubnetMask.Location = new System.Drawing.Point(35, 300);
            this.lblSubnetMask.Name = "lblSubnetMask";
            this.lblSubnetMask.Size = new System.Drawing.Size(68, 17);
            this.lblSubnetMask.TabIndex = 4;
            this.lblSubnetMask.Text = "子网掩码:";
            // 
            // txtSubnetMask
            // 
            this.txtSubnetMask.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtSubnetMask.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtSubnetMask.Location = new System.Drawing.Point(130, 297);
            this.txtSubnetMask.Name = "txtSubnetMask";
            this.txtSubnetMask.PlaceholderText = "例如: 255.255.255.0";
            this.txtSubnetMask.Size = new System.Drawing.Size(320, 23);
            this.txtSubnetMask.TabIndex = 5;
            // 
            // lblGateway
            // 
            this.lblGateway.AutoSize = true;
            this.lblGateway.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblGateway.ForeColor = Constants.Colors.TextPrimary;
            this.lblGateway.Location = new System.Drawing.Point(35, 340);
            this.lblGateway.Name = "lblGateway";
            this.lblGateway.Size = new System.Drawing.Size(68, 17);
            this.lblGateway.TabIndex = 6;
            this.lblGateway.Text = "默认网关:";
            // 
            // txtGateway
            // 
            this.txtGateway.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtGateway.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtGateway.Location = new System.Drawing.Point(130, 337);
            this.txtGateway.Name = "txtGateway";
            this.txtGateway.PlaceholderText = "例如: 192.168.1.1";
            this.txtGateway.Size = new System.Drawing.Size(320, 23);
            this.txtGateway.TabIndex = 7;
            // 
            // lblDnsServer
            // 
            this.lblDnsServer.AutoSize = true;
            this.lblDnsServer.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblDnsServer.ForeColor = Constants.Colors.TextPrimary;
            this.lblDnsServer.Location = new System.Drawing.Point(35, 380);
            this.lblDnsServer.Name = "lblDnsServer";
            this.lblDnsServer.Size = new System.Drawing.Size(80, 17);
            this.lblDnsServer.TabIndex = 8;
            this.lblDnsServer.Text = "DNS服务器:";
            // 
            // txtDnsServer
            // 
            this.txtDnsServer.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtDnsServer.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtDnsServer.Location = new System.Drawing.Point(130, 377);
            this.txtDnsServer.Name = "txtDnsServer";
            this.txtDnsServer.PlaceholderText = "例如: 8.8.8.8";
            this.txtDnsServer.Size = new System.Drawing.Size(320, 23);
            this.txtDnsServer.TabIndex = 9;
            // 
            // btnApplyConfig
            // 
            this.btnApplyConfig.BackColor = Constants.Colors.PrimaryBlue;
            this.btnApplyConfig.FlatAppearance.BorderSize = 0;
            this.btnApplyConfig.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnApplyConfig.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.btnApplyConfig.ForeColor = System.Drawing.Color.White;
            this.btnApplyConfig.Location = new System.Drawing.Point(190, 420);
            this.btnApplyConfig.Name = "btnApplyConfig";
            this.btnApplyConfig.Size = new System.Drawing.Size(100, 38);
            this.btnApplyConfig.TabIndex = 10;
            this.btnApplyConfig.Text = "应用配置";
            this.btnApplyConfig.UseVisualStyleBackColor = false;
            this.btnApplyConfig.Click += new System.EventHandler(this.btnApplyConfig_Click);
            // 
            // btnRefreshAdapters
            // 
            this.btnRefreshAdapters.BackColor = Constants.Colors.PrimaryBlue;
            this.btnRefreshAdapters.FlatAppearance.BorderSize = 0;
            this.btnRefreshAdapters.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnRefreshAdapters.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.btnRefreshAdapters.ForeColor = System.Drawing.Color.White;
            this.btnRefreshAdapters.Location = new System.Drawing.Point(260, 60);
            this.btnRefreshAdapters.Name = "btnRefreshAdapters";
            this.btnRefreshAdapters.Size = new System.Drawing.Size(90, 28);
            this.btnRefreshAdapters.TabIndex = 12;
            this.btnRefreshAdapters.Text = "刷新网卡";
            this.btnRefreshAdapters.UseVisualStyleBackColor = false;
            this.btnRefreshAdapters.Click += new System.EventHandler(this.btnRefreshAdapters_Click);
            // 
            // lblStatus
            // 
            this.lblStatus.AutoSize = true;
            this.lblStatus.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblStatus.ForeColor = Constants.Colors.TextPrimary;
            this.lblStatus.Location = new System.Drawing.Point(35, 480);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(44, 17);
            this.lblStatus.TabIndex = 13;
            this.lblStatus.Text = "状态:";
            // 
            // txtStatus
            // 
            this.txtStatus.BackColor = Constants.Colors.ControlBackground;
            this.txtStatus.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtStatus.Font = new System.Drawing.Font("Microsoft YaHei UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtStatus.ForeColor = Constants.Colors.TextSecondary;
            this.txtStatus.Location = new System.Drawing.Point(35, 500);
            this.txtStatus.Multiline = true;
            this.txtStatus.Name = "txtStatus";
            this.txtStatus.ReadOnly = true;
            this.txtStatus.ScrollBars = System.Windows.Forms.ScrollBars.Vertical;
            this.txtStatus.Size = new System.Drawing.Size(515, 85);
            this.txtStatus.TabIndex = 14;
            this.txtStatus.Text = Constants.UI.WaitingStatus;
            // 
            // chkShowAllAdapters
            // 
            this.chkShowAllAdapters.AutoSize = true;
            this.chkShowAllAdapters.Font = new System.Drawing.Font("Microsoft YaHei UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.chkShowAllAdapters.ForeColor = Constants.Colors.TextSecondary;
            this.chkShowAllAdapters.Location = new System.Drawing.Point(130, 63);
            this.chkShowAllAdapters.Name = "chkShowAllAdapters";
            this.chkShowAllAdapters.Size = new System.Drawing.Size(111, 20);
            this.chkShowAllAdapters.TabIndex = 15;
            this.chkShowAllAdapters.Text = "显示所有网卡";
            this.chkShowAllAdapters.UseVisualStyleBackColor = true;
            this.chkShowAllAdapters.CheckedChanged += new System.EventHandler(this.chkShowAllAdapters_CheckedChanged);
            // 
            // tabControlMain
            // 
            this.tabControlMain.Controls.Add(this.tabPageIpConfig);
            this.tabControlMain.Controls.Add(this.tabPagePingTest);
            this.tabControlMain.Controls.Add(this.tabPageSubnetCalc);
            this.tabControlMain.Dock = System.Windows.Forms.DockStyle.Fill;
            this.tabControlMain.Location = new System.Drawing.Point(0, 0);
            this.tabControlMain.Name = "tabControlMain";
            this.tabControlMain.SelectedIndex = 0;
            this.tabControlMain.Size = new System.Drawing.Size(600, 680);
            this.tabControlMain.TabIndex = 0;
            // 
            // tabPageIpConfig
            // 
            this.tabPageIpConfig.Controls.Add(this.chkShowAllAdapters);
            this.tabPageIpConfig.Controls.Add(this.txtStatus);
            this.tabPageIpConfig.Controls.Add(this.lblStatus);
            this.tabPageIpConfig.Controls.Add(this.btnRefreshAdapters);
            this.tabPageIpConfig.Controls.Add(this.btnApplyConfig);
            this.tabPageIpConfig.Controls.Add(this.txtDnsServer);
            this.tabPageIpConfig.Controls.Add(this.lblDnsServer);
            this.tabPageIpConfig.Controls.Add(this.txtGateway);
            this.tabPageIpConfig.Controls.Add(this.lblGateway);
            this.tabPageIpConfig.Controls.Add(this.txtSubnetMask);
            this.tabPageIpConfig.Controls.Add(this.lblSubnetMask);
            this.tabPageIpConfig.Controls.Add(this.chkDhcp);
            this.tabPageIpConfig.Controls.Add(this.txtIpAddress);
            this.tabPageIpConfig.Controls.Add(this.lblIpAddress);
            this.tabPageIpConfig.Controls.Add(this.grpAdapterInfo);
            this.tabPageIpConfig.Controls.Add(this.cmbNetworkAdapters);
            this.tabPageIpConfig.Controls.Add(this.lblNetworkAdapter);
            this.tabPageIpConfig.Location = new System.Drawing.Point(4, 24);
            this.tabPageIpConfig.Name = "tabPageIpConfig";
            this.tabPageIpConfig.Padding = new System.Windows.Forms.Padding(3);
            this.tabPageIpConfig.Size = new System.Drawing.Size(592, 652);
            this.tabPageIpConfig.TabIndex = 0;
            this.tabPageIpConfig.Text = "IP 配置";
            this.tabPageIpConfig.UseVisualStyleBackColor = true;
            // 
            // tabPagePingTest
            // 
            this.tabPagePingTest.Controls.Add(this.ipGridControl);
            this.tabPagePingTest.Controls.Add(this.scanStatisticsPanel);
            this.tabPagePingTest.Controls.Add(this.scanControlPanel);
            this.tabPagePingTest.Location = new System.Drawing.Point(4, 24);
            this.tabPagePingTest.Name = "tabPagePingTest";
            this.tabPagePingTest.Padding = new System.Windows.Forms.Padding(3);
            this.tabPagePingTest.Size = new System.Drawing.Size(592, 652);
            this.tabPagePingTest.TabIndex = 1;
            this.tabPagePingTest.Text = "Ping 测试";
            this.tabPagePingTest.UseVisualStyleBackColor = true;
            // 
            // scanControlPanel
            // 
            this.scanControlPanel.Dock = System.Windows.Forms.DockStyle.Top;
            this.scanControlPanel.Location = new System.Drawing.Point(3, 3);
            this.scanControlPanel.Name = "scanControlPanel";
            this.scanControlPanel.Size = new System.Drawing.Size(586, 60);
            this.scanControlPanel.TabIndex = 0;
            // 
            // scanStatisticsPanel
            // 
            this.scanStatisticsPanel.Anchor = ((System.Windows.Forms.AnchorStyles)(((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.scanStatisticsPanel.Location = new System.Drawing.Point(3, 566);
            this.scanStatisticsPanel.Name = "scanStatisticsPanel";
            this.scanStatisticsPanel.Size = new System.Drawing.Size(586, 80);
            this.scanStatisticsPanel.TabIndex = 1;
            // 
            // ipGridControl
            // 
            this.ipGridControl.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.ipGridControl.Location = new System.Drawing.Point(3, 66);
            this.ipGridControl.Name = "ipGridControl";
            this.ipGridControl.Size = new System.Drawing.Size(586, 497);
            this.ipGridControl.TabIndex = 2;
            // 
            // tabPageSubnetCalc
            // 
            this.tabPageSubnetCalc.Controls.Add(this.subnetCalculatorPanel);
            this.tabPageSubnetCalc.Location = new System.Drawing.Point(4, 24);
            this.tabPageSubnetCalc.Name = "tabPageSubnetCalc";
            this.tabPageSubnetCalc.Padding = new System.Windows.Forms.Padding(3);
            this.tabPageSubnetCalc.Size = new System.Drawing.Size(592, 652);
            this.tabPageSubnetCalc.TabIndex = 2;
            this.tabPageSubnetCalc.Text = "子网计算";
            this.tabPageSubnetCalc.UseVisualStyleBackColor = true;
            // 
            // subnetCalculatorPanel
            // 
            this.subnetCalculatorPanel.Dock = System.Windows.Forms.DockStyle.Fill;
            this.subnetCalculatorPanel.Location = new System.Drawing.Point(3, 3);
            this.subnetCalculatorPanel.Name = "subnetCalculatorPanel";
            this.subnetCalculatorPanel.Size = new System.Drawing.Size(586, 646);
            this.subnetCalculatorPanel.TabIndex = 0;
            // 
            // MainForm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = Constants.Colors.FormBackground;
            this.ClientSize = new System.Drawing.Size(600, 680);
            this.Controls.Add(this.tabControlMain);
            this.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.Name = "MainForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = Constants.Application.FullTitle;
            this.Load += new System.EventHandler(this.MainForm_Load);
            this.grpAdapterInfo.ResumeLayout(false);
            this.grpAdapterInfo.PerformLayout();
            this.tabControlMain.ResumeLayout(false);
            this.tabPageIpConfig.ResumeLayout(false);
            this.tabPageIpConfig.PerformLayout();
            this.tabPagePingTest.ResumeLayout(false);
            this.tabPageSubnetCalc.ResumeLayout(false);
            this.ResumeLayout(false);
        }

        #endregion

        private System.Windows.Forms.Label lblNetworkAdapter;
        private System.Windows.Forms.ComboBox cmbNetworkAdapters;
        private System.Windows.Forms.Label lblIpAddress;
        private System.Windows.Forms.TextBox txtIpAddress;
        private System.Windows.Forms.Label lblSubnetMask;
        private System.Windows.Forms.TextBox txtSubnetMask;
        private System.Windows.Forms.Label lblGateway;
        private System.Windows.Forms.TextBox txtGateway;
        private System.Windows.Forms.Label lblDnsServer;
        private System.Windows.Forms.TextBox txtDnsServer;
        private System.Windows.Forms.Button btnApplyConfig;
        private System.Windows.Forms.Button btnRefreshAdapters;
        private System.Windows.Forms.Label lblStatus;
        private System.Windows.Forms.TextBox txtStatus;
        private System.Windows.Forms.CheckBox chkShowAllAdapters;
        private System.Windows.Forms.GroupBox grpAdapterInfo;
        private System.Windows.Forms.TextBox txtAdapterInfoContent;
        private System.Windows.Forms.TabControl tabControlMain;
        private System.Windows.Forms.TabPage tabPageIpConfig;
        private System.Windows.Forms.TabPage tabPagePingTest;
        private System.Windows.Forms.TabPage tabPageSubnetCalc;
        private Controls.ScanControlPanel scanControlPanel;
        private Controls.ScanStatisticsPanel scanStatisticsPanel;
        private Controls.IPGridControl ipGridControl;
        private Controls.SubnetCalculatorPanel subnetCalculatorPanel;
        private System.Windows.Forms.CheckBox chkDhcp;
    }
}
