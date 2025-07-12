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
            lblNetworkAdapter = new Label();
            cmbNetworkAdapters = new ComboBox();
            lblIpAddress = new Label();
            txtIpAddress = new TextBox();
            lblIpError = new Label();
            lblSubnetMask = new Label();
            txtSubnetMask = new TextBox();
            lblSubnetError = new Label();
            lblGateway = new Label();
            txtGateway = new TextBox();
            lblGatewayError = new Label();
            lblDnsServer = new Label();
            txtDnsServer = new TextBox();
            lblDnsError = new Label();
            lblSecondaryDnsServer = new Label();
            txtSecondaryDnsServer = new TextBox();
            lblSecondaryDnsError = new Label();
            btnApplyConfig = new Button();
            btnRefreshAdapters = new Button();
            lblStatus = new Label();
            txtStatus = new TextBox();
            chkShowAllAdapters = new CheckBox();
            grpAdapterInfo = new GroupBox();
            txtAdapterInfoContent = new TextBox();
            tabControlMain = new TabControl();
            tabPageIpConfig = new TabPage();
            chkDhcp = new CheckBox();
            tabPagePingTest = new TabPage();
            ipGridControl = new NETKit.UI.Controls.IPGridControl();
            scanStatisticsPanel = new NETKit.UI.Controls.ScanStatisticsPanel();
            scanControlPanel = new NETKit.UI.Controls.ScanControlPanel();
            tabPageSubnetCalc = new TabPage();
            subnetCalculatorPanel = new NETKit.UI.Controls.SubnetCalculatorPanel();
            tabPageTraceRoute = new TabPage();
            traceRoutePanel = new NETKit.UI.Controls.TraceRoutePanel();
            tabPageRouteManagement = new TabPage();
            routeManagementPanel = new NETKit.UI.Controls.RouteManagementPanel();
            grpAdapterInfo.SuspendLayout();
            tabControlMain.SuspendLayout();
            tabPageIpConfig.SuspendLayout();
            tabPagePingTest.SuspendLayout();
            tabPageSubnetCalc.SuspendLayout();
            tabPageTraceRoute.SuspendLayout();
            tabPageRouteManagement.SuspendLayout();
            SuspendLayout();
            // 
            // lblNetworkAdapter
            // 
            lblNetworkAdapter.AutoSize = true;
            lblNetworkAdapter.Font = new Font("Microsoft YaHei UI", 9F);
            lblNetworkAdapter.ForeColor = Color.FromArgb(51, 51, 51);
            lblNetworkAdapter.Location = new Point(65, 65);
            lblNetworkAdapter.Margin = new Padding(6, 0, 6, 0);
            lblNetworkAdapter.Name = "lblNetworkAdapter";
            lblNetworkAdapter.Size = new Size(101, 28);
            lblNetworkAdapter.TabIndex = 0;
            lblNetworkAdapter.Text = "网卡选择:";
            // 
            // cmbNetworkAdapters
            // 
            cmbNetworkAdapters.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbNetworkAdapters.Font = new Font("Microsoft YaHei UI", 9F);
            cmbNetworkAdapters.FormattingEnabled = true;
            cmbNetworkAdapters.Location = new Point(241, 60);
            cmbNetworkAdapters.Margin = new Padding(6);
            cmbNetworkAdapters.Name = "cmbNetworkAdapters";
            cmbNetworkAdapters.Size = new Size(777, 36);
            cmbNetworkAdapters.TabIndex = 1;
            // 
            // lblIpAddress
            // 
            lblIpAddress.AutoSize = true;
            lblIpAddress.Font = new Font("Microsoft YaHei UI", 9F);
            lblIpAddress.ForeColor = Color.FromArgb(51, 51, 51);
            lblIpAddress.Location = new Point(65, 541);
            lblIpAddress.Margin = new Padding(6, 0, 6, 0);
            lblIpAddress.Name = "lblIpAddress";
            lblIpAddress.Size = new Size(78, 28);
            lblIpAddress.TabIndex = 2;
            lblIpAddress.Text = "IP地址:";
            // 
            // txtIpAddress
            // 
            txtIpAddress.BorderStyle = BorderStyle.FixedSingle;
            txtIpAddress.Font = new Font("Microsoft YaHei UI", 9F);
            txtIpAddress.Location = new Point(241, 536);
            txtIpAddress.Margin = new Padding(6);
            txtIpAddress.Name = "txtIpAddress";
            txtIpAddress.PlaceholderText = "例如: 192.168.1.100";
            txtIpAddress.Size = new Size(593, 34);
            txtIpAddress.TabIndex = 3;
            // 
            // lblIpError
            // 
            lblIpError.AutoSize = true;
            lblIpError.Font = new Font("Microsoft YaHei UI", 8F);
            lblIpError.ForeColor = Color.Red;
            lblIpError.Location = new Point(241, 579);
            lblIpError.Margin = new Padding(6, 0, 6, 0);
            lblIpError.Name = "lblIpError";
            lblIpError.Size = new Size(0, 25);
            lblIpError.TabIndex = 18;
            lblIpError.Visible = false;
            // 
            // lblSubnetMask
            // 
            lblSubnetMask.AutoSize = true;
            lblSubnetMask.Font = new Font("Microsoft YaHei UI", 9F);
            lblSubnetMask.ForeColor = Color.FromArgb(51, 51, 51);
            lblSubnetMask.Location = new Point(65, 616);
            lblSubnetMask.Margin = new Padding(6, 0, 6, 0);
            lblSubnetMask.Name = "lblSubnetMask";
            lblSubnetMask.Size = new Size(101, 28);
            lblSubnetMask.TabIndex = 4;
            lblSubnetMask.Text = "子网掩码:";
            // 
            // txtSubnetMask
            // 
            txtSubnetMask.BorderStyle = BorderStyle.FixedSingle;
            txtSubnetMask.Font = new Font("Microsoft YaHei UI", 9F);
            txtSubnetMask.Location = new Point(241, 610);
            txtSubnetMask.Margin = new Padding(6);
            txtSubnetMask.Name = "txtSubnetMask";
            txtSubnetMask.PlaceholderText = "例如: 255.255.255.0";
            txtSubnetMask.Size = new Size(593, 34);
            txtSubnetMask.TabIndex = 5;
            // 
            // lblSubnetError
            // 
            lblSubnetError.AutoSize = true;
            lblSubnetError.Font = new Font("Microsoft YaHei UI", 8F);
            lblSubnetError.ForeColor = Color.Red;
            lblSubnetError.Location = new Point(241, 653);
            lblSubnetError.Margin = new Padding(6, 0, 6, 0);
            lblSubnetError.Name = "lblSubnetError";
            lblSubnetError.Size = new Size(0, 25);
            lblSubnetError.TabIndex = 19;
            lblSubnetError.Visible = false;
            // 
            // lblGateway
            // 
            lblGateway.AutoSize = true;
            lblGateway.Font = new Font("Microsoft YaHei UI", 9F);
            lblGateway.ForeColor = Color.FromArgb(51, 51, 51);
            lblGateway.Location = new Point(65, 691);
            lblGateway.Margin = new Padding(6, 0, 6, 0);
            lblGateway.Name = "lblGateway";
            lblGateway.Size = new Size(101, 28);
            lblGateway.TabIndex = 6;
            lblGateway.Text = "默认网关:";
            // 
            // txtGateway
            // 
            txtGateway.BorderStyle = BorderStyle.FixedSingle;
            txtGateway.Font = new Font("Microsoft YaHei UI", 9F);
            txtGateway.Location = new Point(241, 685);
            txtGateway.Margin = new Padding(6);
            txtGateway.Name = "txtGateway";
            txtGateway.PlaceholderText = "例如: 192.168.1.1";
            txtGateway.Size = new Size(593, 34);
            txtGateway.TabIndex = 7;
            // 
            // lblGatewayError
            // 
            lblGatewayError.AutoSize = true;
            lblGatewayError.Font = new Font("Microsoft YaHei UI", 8F);
            lblGatewayError.ForeColor = Color.Red;
            lblGatewayError.Location = new Point(241, 728);
            lblGatewayError.Margin = new Padding(6, 0, 6, 0);
            lblGatewayError.Name = "lblGatewayError";
            lblGatewayError.Size = new Size(0, 25);
            lblGatewayError.TabIndex = 20;
            lblGatewayError.Visible = false;
            // 
            // lblDnsServer
            // 
            lblDnsServer.AutoSize = true;
            lblDnsServer.Font = new Font("Microsoft YaHei UI", 9F);
            lblDnsServer.ForeColor = Color.FromArgb(51, 51, 51);
            lblDnsServer.Location = new Point(65, 765);
            lblDnsServer.Margin = new Padding(6, 0, 6, 0);
            lblDnsServer.Name = "lblDnsServer";
            lblDnsServer.Size = new Size(146, 28);
            lblDnsServer.TabIndex = 8;
            lblDnsServer.Text = "主DNS服务器:";
            // 
            // txtDnsServer
            // 
            txtDnsServer.BorderStyle = BorderStyle.FixedSingle;
            txtDnsServer.Font = new Font("Microsoft YaHei UI", 9F);
            txtDnsServer.Location = new Point(241, 760);
            txtDnsServer.Margin = new Padding(6);
            txtDnsServer.Name = "txtDnsServer";
            txtDnsServer.PlaceholderText = "例如: 8.8.8.8";
            txtDnsServer.Size = new Size(593, 34);
            txtDnsServer.TabIndex = 9;
            // 
            // lblDnsError
            // 
            lblDnsError.AutoSize = true;
            lblDnsError.Font = new Font("Microsoft YaHei UI", 8F);
            lblDnsError.ForeColor = Color.Red;
            lblDnsError.Location = new Point(241, 803);
            lblDnsError.Margin = new Padding(6, 0, 6, 0);
            lblDnsError.Name = "lblDnsError";
            lblDnsError.Size = new Size(0, 25);
            lblDnsError.TabIndex = 21;
            lblDnsError.Visible = false;
            // 
            // lblSecondaryDnsServer
            // 
            lblSecondaryDnsServer.AutoSize = true;
            lblSecondaryDnsServer.Font = new Font("Microsoft YaHei UI", 9F);
            lblSecondaryDnsServer.ForeColor = Color.FromArgb(51, 51, 51);
            lblSecondaryDnsServer.Location = new Point(65, 840);
            lblSecondaryDnsServer.Margin = new Padding(6, 0, 6, 0);
            lblSecondaryDnsServer.Name = "lblSecondaryDnsServer";
            lblSecondaryDnsServer.Size = new Size(146, 28);
            lblSecondaryDnsServer.TabIndex = 22;
            lblSecondaryDnsServer.Text = "备DNS服务器:";
            // 
            // txtSecondaryDnsServer
            // 
            txtSecondaryDnsServer.BorderStyle = BorderStyle.FixedSingle;
            txtSecondaryDnsServer.Font = new Font("Microsoft YaHei UI", 9F);
            txtSecondaryDnsServer.Location = new Point(241, 834);
            txtSecondaryDnsServer.Margin = new Padding(6);
            txtSecondaryDnsServer.Name = "txtSecondaryDnsServer";
            txtSecondaryDnsServer.PlaceholderText = "例如: 8.8.4.4 (可选)";
            txtSecondaryDnsServer.Size = new Size(593, 34);
            txtSecondaryDnsServer.TabIndex = 23;
            // 
            // lblSecondaryDnsError
            // 
            lblSecondaryDnsError.AutoSize = true;
            lblSecondaryDnsError.Font = new Font("Microsoft YaHei UI", 8F);
            lblSecondaryDnsError.ForeColor = Color.Red;
            lblSecondaryDnsError.Location = new Point(241, 877);
            lblSecondaryDnsError.Margin = new Padding(6, 0, 6, 0);
            lblSecondaryDnsError.Name = "lblSecondaryDnsError";
            lblSecondaryDnsError.Size = new Size(0, 25);
            lblSecondaryDnsError.TabIndex = 24;
            lblSecondaryDnsError.Visible = false;
            // 
            // btnApplyConfig
            // 
            btnApplyConfig.BackColor = Color.FromArgb(74, 144, 226);
            btnApplyConfig.FlatAppearance.BorderSize = 0;
            btnApplyConfig.FlatStyle = FlatStyle.Flat;
            btnApplyConfig.Font = new Font("Microsoft YaHei UI", 9F);
            btnApplyConfig.ForeColor = Color.White;
            btnApplyConfig.Location = new Point(457, 896);
            btnApplyConfig.Margin = new Padding(6);
            btnApplyConfig.Name = "btnApplyConfig";
            btnApplyConfig.Size = new Size(149, 52);
            btnApplyConfig.TabIndex = 10;
            btnApplyConfig.Text = "应用配置";
            btnApplyConfig.UseVisualStyleBackColor = false;
            btnApplyConfig.Click += btnApplyConfig_Click;
            // 
            // btnRefreshAdapters
            // 
            btnRefreshAdapters.BackColor = Color.FromArgb(74, 144, 226);
            btnRefreshAdapters.FlatAppearance.BorderSize = 0;
            btnRefreshAdapters.FlatStyle = FlatStyle.Flat;
            btnRefreshAdapters.Font = new Font("Microsoft YaHei UI", 9F);
            btnRefreshAdapters.ForeColor = Color.White;
            btnRefreshAdapters.Location = new Point(661, 112);
            btnRefreshAdapters.Margin = new Padding(6);
            btnRefreshAdapters.Name = "btnRefreshAdapters";
            btnRefreshAdapters.Size = new Size(149, 52);
            btnRefreshAdapters.TabIndex = 12;
            btnRefreshAdapters.Text = "刷新网卡";
            btnRefreshAdapters.UseVisualStyleBackColor = false;
            btnRefreshAdapters.Click += btnRefreshAdapters_Click;
            // 
            // lblStatus
            // 
            lblStatus.AutoSize = true;
            lblStatus.Font = new Font("Microsoft YaHei UI", 9F);
            lblStatus.ForeColor = Color.FromArgb(51, 51, 51);
            lblStatus.Location = new Point(65, 971);
            lblStatus.Margin = new Padding(6, 0, 6, 0);
            lblStatus.Name = "lblStatus";
            lblStatus.Size = new Size(59, 28);
            lblStatus.TabIndex = 13;
            lblStatus.Text = "状态:";
            // 
            // txtStatus
            // 
            txtStatus.BackColor = Color.White;
            txtStatus.BorderStyle = BorderStyle.FixedSingle;
            txtStatus.Font = new Font("Microsoft YaHei UI", 9.75F);
            txtStatus.ForeColor = Color.FromArgb(102, 102, 102);
            txtStatus.Location = new Point(65, 1008);
            txtStatus.Margin = new Padding(6);
            txtStatus.Multiline = true;
            txtStatus.Name = "txtStatus";
            txtStatus.ReadOnly = true;
            txtStatus.ScrollBars = ScrollBars.Vertical;
            txtStatus.Size = new Size(955, 157);
            txtStatus.TabIndex = 14;
            txtStatus.Text = "等待操作...";
            // 
            // chkShowAllAdapters
            // 
            chkShowAllAdapters.AutoSize = true;
            chkShowAllAdapters.Font = new Font("Microsoft YaHei UI", 8.25F);
            chkShowAllAdapters.ForeColor = Color.FromArgb(102, 102, 102);
            chkShowAllAdapters.Location = new Point(241, 118);
            chkShowAllAdapters.Margin = new Padding(6);
            chkShowAllAdapters.Name = "chkShowAllAdapters";
            chkShowAllAdapters.Size = new Size(158, 31);
            chkShowAllAdapters.TabIndex = 15;
            chkShowAllAdapters.Text = "显示所有网卡";
            chkShowAllAdapters.UseVisualStyleBackColor = true;
            chkShowAllAdapters.CheckedChanged += chkShowAllAdapters_CheckedChanged;
            // 
            // grpAdapterInfo
            // 
            grpAdapterInfo.Controls.Add(txtAdapterInfoContent);
            grpAdapterInfo.Font = new Font("Microsoft YaHei UI", 9F);
            grpAdapterInfo.ForeColor = Color.FromArgb(51, 51, 51);
            grpAdapterInfo.Location = new Point(65, 168);
            grpAdapterInfo.Margin = new Padding(6);
            grpAdapterInfo.Name = "grpAdapterInfo";
            grpAdapterInfo.Padding = new Padding(6);
            grpAdapterInfo.Size = new Size(956, 336);
            grpAdapterInfo.TabIndex = 17;
            grpAdapterInfo.TabStop = false;
            grpAdapterInfo.Text = "当前网卡信息";
            // 
            // txtAdapterInfoContent
            // 
            txtAdapterInfoContent.BackColor = Color.FromArgb(250, 250, 250);
            txtAdapterInfoContent.BorderStyle = BorderStyle.None;
            txtAdapterInfoContent.Font = new Font("Microsoft YaHei UI", 9F);
            txtAdapterInfoContent.ForeColor = Color.FromArgb(102, 102, 102);
            txtAdapterInfoContent.Location = new Point(28, 47);
            txtAdapterInfoContent.Margin = new Padding(6);
            txtAdapterInfoContent.Multiline = true;
            txtAdapterInfoContent.Name = "txtAdapterInfoContent";
            txtAdapterInfoContent.ReadOnly = true;
            txtAdapterInfoContent.Size = new Size(901, 271);
            txtAdapterInfoContent.TabIndex = 0;
            txtAdapterInfoContent.Text = "请选择网络适配器";
            // 
            // tabControlMain
            // 
            tabControlMain.Controls.Add(tabPageIpConfig);
            tabControlMain.Controls.Add(tabPagePingTest);
            tabControlMain.Controls.Add(tabPageSubnetCalc);
            tabControlMain.Controls.Add(tabPageTraceRoute);
            tabControlMain.Controls.Add(tabPageRouteManagement);
            tabControlMain.Dock = DockStyle.Fill;
            tabControlMain.Location = new Point(0, 0);
            tabControlMain.Margin = new Padding(6);
            tabControlMain.Name = "tabControlMain";
            tabControlMain.SelectedIndex = 0;
            tabControlMain.Size = new Size(1114, 1269);
            tabControlMain.TabIndex = 0;
            // 
            // tabPageIpConfig
            // 
            tabPageIpConfig.Controls.Add(chkShowAllAdapters);
            tabPageIpConfig.Controls.Add(txtStatus);
            tabPageIpConfig.Controls.Add(lblStatus);
            tabPageIpConfig.Controls.Add(btnRefreshAdapters);
            tabPageIpConfig.Controls.Add(btnApplyConfig);
            tabPageIpConfig.Controls.Add(lblSecondaryDnsError);
            tabPageIpConfig.Controls.Add(txtSecondaryDnsServer);
            tabPageIpConfig.Controls.Add(lblSecondaryDnsServer);
            tabPageIpConfig.Controls.Add(lblDnsError);
            tabPageIpConfig.Controls.Add(txtDnsServer);
            tabPageIpConfig.Controls.Add(lblDnsServer);
            tabPageIpConfig.Controls.Add(lblGatewayError);
            tabPageIpConfig.Controls.Add(txtGateway);
            tabPageIpConfig.Controls.Add(lblGateway);
            tabPageIpConfig.Controls.Add(lblSubnetError);
            tabPageIpConfig.Controls.Add(txtSubnetMask);
            tabPageIpConfig.Controls.Add(lblSubnetMask);
            tabPageIpConfig.Controls.Add(chkDhcp);
            tabPageIpConfig.Controls.Add(lblIpError);
            tabPageIpConfig.Controls.Add(txtIpAddress);
            tabPageIpConfig.Controls.Add(lblIpAddress);
            tabPageIpConfig.Controls.Add(grpAdapterInfo);
            tabPageIpConfig.Controls.Add(cmbNetworkAdapters);
            tabPageIpConfig.Controls.Add(lblNetworkAdapter);
            tabPageIpConfig.Location = new Point(4, 37);
            tabPageIpConfig.Margin = new Padding(6);
            tabPageIpConfig.Name = "tabPageIpConfig";
            tabPageIpConfig.Padding = new Padding(6);
            tabPageIpConfig.Size = new Size(1106, 1228);
            tabPageIpConfig.TabIndex = 0;
            tabPageIpConfig.Text = "IP 配置";
            tabPageIpConfig.UseVisualStyleBackColor = true;
            // 
            // chkDhcp
            // 
            chkDhcp.AutoSize = true;
            chkDhcp.Font = new Font("Microsoft YaHei UI", 9F);
            chkDhcp.ForeColor = Color.FromArgb(51, 51, 51);
            chkDhcp.Location = new Point(854, 539);
            chkDhcp.Margin = new Padding(6);
            chkDhcp.Name = "chkDhcp";
            chkDhcp.Size = new Size(97, 32);
            chkDhcp.TabIndex = 4;
            chkDhcp.Text = "DHCP";
            chkDhcp.UseVisualStyleBackColor = true;
            chkDhcp.CheckedChanged += chkDhcp_CheckedChanged;
            // 
            // tabPagePingTest
            // 
            tabPagePingTest.Controls.Add(ipGridControl);
            tabPagePingTest.Controls.Add(scanStatisticsPanel);
            tabPagePingTest.Controls.Add(scanControlPanel);
            tabPagePingTest.Location = new Point(4, 37);
            tabPagePingTest.Margin = new Padding(6);
            tabPagePingTest.Name = "tabPagePingTest";
            tabPagePingTest.Padding = new Padding(6);
            tabPagePingTest.Size = new Size(1106, 1228);
            tabPagePingTest.TabIndex = 1;
            tabPagePingTest.Text = "Ping 测试";
            tabPagePingTest.UseVisualStyleBackColor = true;
            // 
            // ipGridControl
            // 
            ipGridControl.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            ipGridControl.BackColor = Color.White;
            ipGridControl.Font = new Font("Consolas", 8F);
            ipGridControl.Location = new Point(6, 123);
            ipGridControl.Margin = new Padding(6);
            ipGridControl.Name = "ipGridControl";
            ipGridControl.Size = new Size(1088, 928);
            ipGridControl.TabIndex = 2;
            // 
            // scanStatisticsPanel
            // 
            scanStatisticsPanel.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            scanStatisticsPanel.Font = new Font("Microsoft YaHei UI", 9F, FontStyle.Regular, GraphicsUnit.Point, 134);
            scanStatisticsPanel.Location = new Point(6, 1057);
            scanStatisticsPanel.Margin = new Padding(11, 9, 11, 9);
            scanStatisticsPanel.Name = "scanStatisticsPanel";
            scanStatisticsPanel.Size = new Size(1088, 149);
            scanStatisticsPanel.TabIndex = 1;
            // 
            // scanControlPanel
            // 
            scanControlPanel.Dock = DockStyle.Top;
            scanControlPanel.Font = new Font("Microsoft YaHei UI", 9F, FontStyle.Regular, GraphicsUnit.Point, 134);
            scanControlPanel.Location = new Point(6, 6);
            scanControlPanel.Margin = new Padding(11, 9, 11, 9);
            scanControlPanel.Name = "scanControlPanel";
            scanControlPanel.Size = new Size(1094, 112);
            scanControlPanel.TabIndex = 0;
            // 
            // tabPageSubnetCalc
            // 
            tabPageSubnetCalc.Controls.Add(subnetCalculatorPanel);
            tabPageSubnetCalc.Location = new Point(4, 37);
            tabPageSubnetCalc.Margin = new Padding(6);
            tabPageSubnetCalc.Name = "tabPageSubnetCalc";
            tabPageSubnetCalc.Padding = new Padding(6);
            tabPageSubnetCalc.Size = new Size(1106, 1228);
            tabPageSubnetCalc.TabIndex = 2;
            tabPageSubnetCalc.Text = "子网计算";
            tabPageSubnetCalc.UseVisualStyleBackColor = true;
            // 
            // subnetCalculatorPanel
            // 
            subnetCalculatorPanel.Dock = DockStyle.Fill;
            subnetCalculatorPanel.Location = new Point(6, 6);
            subnetCalculatorPanel.Margin = new Padding(6);
            subnetCalculatorPanel.Name = "subnetCalculatorPanel";
            subnetCalculatorPanel.Size = new Size(1094, 1216);
            subnetCalculatorPanel.TabIndex = 0;
            // 
            // tabPageTraceRoute
            // 
            tabPageTraceRoute.Controls.Add(traceRoutePanel);
            tabPageTraceRoute.Location = new Point(4, 37);
            tabPageTraceRoute.Margin = new Padding(6);
            tabPageTraceRoute.Name = "tabPageTraceRoute";
            tabPageTraceRoute.Padding = new Padding(6);
            tabPageTraceRoute.Size = new Size(1106, 1228);
            tabPageTraceRoute.TabIndex = 3;
            tabPageTraceRoute.Text = "路由跟踪";
            tabPageTraceRoute.UseVisualStyleBackColor = true;
            // 
            // traceRoutePanel
            // 
            traceRoutePanel.BackColor = Color.FromArgb(245, 245, 245);
            traceRoutePanel.Dock = DockStyle.Fill;
            traceRoutePanel.Location = new Point(6, 6);
            traceRoutePanel.Margin = new Padding(11);
            traceRoutePanel.Name = "traceRoutePanel";
            traceRoutePanel.Size = new Size(1094, 1216);
            traceRoutePanel.TabIndex = 0;
            // 
            // tabPageRouteManagement
            // 
            tabPageRouteManagement.Controls.Add(routeManagementPanel);
            tabPageRouteManagement.Location = new Point(4, 37);
            tabPageRouteManagement.Margin = new Padding(6);
            tabPageRouteManagement.Name = "tabPageRouteManagement";
            tabPageRouteManagement.Padding = new Padding(6);
            tabPageRouteManagement.Size = new Size(1106, 1228);
            tabPageRouteManagement.TabIndex = 4;
            tabPageRouteManagement.Text = "路由管理";
            tabPageRouteManagement.UseVisualStyleBackColor = true;
            // 
            // routeManagementPanel
            // 
            routeManagementPanel.Dock = DockStyle.Fill;
            routeManagementPanel.Location = new Point(6, 6);
            routeManagementPanel.Margin = new Padding(11, 9, 11, 9);
            routeManagementPanel.Name = "routeManagementPanel";
            routeManagementPanel.Size = new Size(1094, 1216);
            routeManagementPanel.TabIndex = 0;
            routeManagementPanel.Load += routeManagementPanel_Load;
            // 
            // MainForm
            // 
            AutoScaleDimensions = new SizeF(13F, 28F);
            AutoScaleMode = AutoScaleMode.Font;
            BackColor = Color.FromArgb(245, 245, 245);
            ClientSize = new Size(1114, 1269);
            Controls.Add(tabControlMain);
            Font = new Font("Microsoft YaHei UI", 9F);
            FormBorderStyle = FormBorderStyle.FixedSingle;
            Margin = new Padding(6);
            MaximizeBox = false;
            Name = "MainForm";
            StartPosition = FormStartPosition.CenterScreen;
            Text = "NETKit v1.5.1";
            Load += MainForm_Load;
            grpAdapterInfo.ResumeLayout(false);
            grpAdapterInfo.PerformLayout();
            tabControlMain.ResumeLayout(false);
            tabPageIpConfig.ResumeLayout(false);
            tabPageIpConfig.PerformLayout();
            tabPagePingTest.ResumeLayout(false);
            tabPageSubnetCalc.ResumeLayout(false);
            tabPageTraceRoute.ResumeLayout(false);
            tabPageRouteManagement.ResumeLayout(false);
            ResumeLayout(false);
        }

        #endregion

        private System.Windows.Forms.Label lblNetworkAdapter;
        private System.Windows.Forms.ComboBox cmbNetworkAdapters;
        private System.Windows.Forms.Label lblIpAddress;
        private System.Windows.Forms.TextBox txtIpAddress;
        private System.Windows.Forms.Label lblIpError;
        private System.Windows.Forms.Label lblSubnetMask;
        private System.Windows.Forms.TextBox txtSubnetMask;
        private System.Windows.Forms.Label lblSubnetError;
        private System.Windows.Forms.Label lblGateway;
        private System.Windows.Forms.TextBox txtGateway;
        private System.Windows.Forms.Label lblGatewayError;
        private System.Windows.Forms.Label lblDnsServer;
        private System.Windows.Forms.TextBox txtDnsServer;
        private System.Windows.Forms.Label lblDnsError;
        private System.Windows.Forms.Label lblSecondaryDnsServer;
        private System.Windows.Forms.TextBox txtSecondaryDnsServer;
        private System.Windows.Forms.Label lblSecondaryDnsError;
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
        private System.Windows.Forms.TabPage tabPageTraceRoute;
        private System.Windows.Forms.TabPage tabPageRouteManagement;
        private Controls.ScanControlPanel scanControlPanel;
        private Controls.ScanStatisticsPanel scanStatisticsPanel;
        private Controls.IPGridControl ipGridControl;
        private Controls.SubnetCalculatorPanel subnetCalculatorPanel;
        private Controls.TraceRoutePanel traceRoutePanel;
        private Controls.RouteManagementPanel routeManagementPanel;
        private System.Windows.Forms.CheckBox chkDhcp;
    }
}
