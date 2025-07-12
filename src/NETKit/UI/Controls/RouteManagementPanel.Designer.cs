namespace NETKit.UI.Controls
{
    partial class RouteManagementPanel
    {
        /// <summary> 
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;



        #region 组件设计器生成的代码

        /// <summary> 
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            grpRouteTable = new GroupBox();
            lblConflictInfo = new Label();
            lblRouteCount = new Label();
            dgvRoutes = new DataGridView();
            btnRefreshRoutes = new Button();
            btnDeleteRoute = new Button();
            grpAddRoute = new GroupBox();
            lblMetric = new Label();
            numMetric = new NumericUpDown();
            lblAdapter = new Label();
            cmbAdapter = new ComboBox();
            lblDestination = new Label();
            txtDestination = new TextBox();
            btnAddRoute = new Button();
            lblDestinationHint = new Label();
            chkPersistent = new CheckBox();
            grpRouteTable.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)dgvRoutes).BeginInit();
            grpAddRoute.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)numMetric).BeginInit();
            SuspendLayout();
            // 
            // grpRouteTable
            // 
            grpRouteTable.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            grpRouteTable.Controls.Add(lblConflictInfo);
            grpRouteTable.Controls.Add(lblRouteCount);
            grpRouteTable.Controls.Add(dgvRoutes);
            grpRouteTable.Controls.Add(btnRefreshRoutes);
            grpRouteTable.Controls.Add(btnDeleteRoute);
            grpRouteTable.Location = new Point(6, 6);
            grpRouteTable.Name = "grpRouteTable";
            grpRouteTable.Size = new Size(574, 380);
            grpRouteTable.TabIndex = 0;
            grpRouteTable.TabStop = false;
            grpRouteTable.Text = "当前路由规则";
            // 
            // lblConflictInfo
            // 
            lblConflictInfo.AutoSize = true;
            lblConflictInfo.ForeColor = Color.Red;
            lblConflictInfo.Location = new Point(6, 25);
            lblConflictInfo.Name = "lblConflictInfo";
            lblConflictInfo.Size = new Size(200, 17);
            lblConflictInfo.TabIndex = 4;
            lblConflictInfo.Text = "⚠️ 检测到路由冲突";
            lblConflictInfo.Visible = false;
            // 
            // lblRouteCount
            // 
            lblRouteCount.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            lblRouteCount.AutoSize = true;
            lblRouteCount.Location = new Point(6, 354);
            lblRouteCount.Name = "lblRouteCount";
            lblRouteCount.Size = new Size(100, 17);
            lblRouteCount.TabIndex = 3;
            lblRouteCount.Text = "共 0 条路由规则";
            // 
            // dgvRoutes
            // 
            dgvRoutes.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            dgvRoutes.ColumnHeadersHeightSizeMode = DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            dgvRoutes.Location = new Point(6, 50);
            dgvRoutes.Name = "dgvRoutes";
            dgvRoutes.Size = new Size(562, 295);
            dgvRoutes.TabIndex = 2;
            // 
            // btnRefreshRoutes
            // 
            btnRefreshRoutes.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            btnRefreshRoutes.Location = new Point(412, 351);
            btnRefreshRoutes.Name = "btnRefreshRoutes";
            btnRefreshRoutes.Size = new Size(75, 23);
            btnRefreshRoutes.TabIndex = 1;
            btnRefreshRoutes.Text = "刷新";
            btnRefreshRoutes.UseVisualStyleBackColor = true;
            // 
            // btnDeleteRoute
            // 
            btnDeleteRoute.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            btnDeleteRoute.Location = new Point(493, 351);
            btnDeleteRoute.Name = "btnDeleteRoute";
            btnDeleteRoute.Size = new Size(75, 23);
            btnDeleteRoute.TabIndex = 0;
            btnDeleteRoute.Text = "删除";
            btnDeleteRoute.UseVisualStyleBackColor = true;
            // 
            // grpAddRoute
            // 
            grpAddRoute.Anchor = AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            grpAddRoute.Controls.Add(lblDestinationHint);
            grpAddRoute.Controls.Add(lblMetric);
            grpAddRoute.Controls.Add(numMetric);
            grpAddRoute.Controls.Add(lblAdapter);
            grpAddRoute.Controls.Add(cmbAdapter);
            grpAddRoute.Controls.Add(lblDestination);
            grpAddRoute.Controls.Add(txtDestination);
            grpAddRoute.Controls.Add(btnAddRoute);
            grpAddRoute.Controls.Add(chkPersistent);
            grpAddRoute.Location = new Point(6, 392);
            grpAddRoute.Name = "grpAddRoute";
            grpAddRoute.Size = new Size(574, 120);
            grpAddRoute.TabIndex = 1;
            grpAddRoute.TabStop = false;
            grpAddRoute.Text = "添加新路由规则";
            // 
            // lblMetric
            // 
            lblMetric.AutoSize = true;
            lblMetric.Location = new Point(370, 25);
            lblMetric.Name = "lblMetric";
            lblMetric.Size = new Size(56, 17);
            lblMetric.TabIndex = 7;
            lblMetric.Text = "跃点数:";
            // 
            // numMetric
            // 
            numMetric.Location = new Point(432, 23);
            numMetric.Maximum = new decimal(new int[] { 9999, 0, 0, 0 });
            numMetric.Minimum = new decimal(new int[] { 1, 0, 0, 0 });
            numMetric.Name = "numMetric";
            numMetric.Size = new Size(80, 23);
            numMetric.TabIndex = 6;
            numMetric.Value = new decimal(new int[] { 1, 0, 0, 0 });
            // 
            // lblAdapter
            // 
            lblAdapter.AutoSize = true;
            lblAdapter.Location = new Point(6, 55);
            lblAdapter.Name = "lblAdapter";
            lblAdapter.Size = new Size(68, 17);
            lblAdapter.TabIndex = 5;
            lblAdapter.Text = "选择接口:";
            // 
            // cmbAdapter
            // 
            cmbAdapter.Anchor = AnchorStyles.Top | AnchorStyles.Left | AnchorStyles.Right;
            cmbAdapter.DisplayMember = "DisplayName";
            cmbAdapter.DropDownStyle = ComboBoxStyle.DropDownList;
            cmbAdapter.FormattingEnabled = true;
            cmbAdapter.Location = new Point(80, 52);
            cmbAdapter.Name = "cmbAdapter";
            cmbAdapter.Size = new Size(362, 25);
            cmbAdapter.TabIndex = 4;
            // 
            // lblDestination
            // 
            lblDestination.AutoSize = true;
            lblDestination.Location = new Point(6, 25);
            lblDestination.Name = "lblDestination";
            lblDestination.Size = new Size(68, 17);
            lblDestination.TabIndex = 3;
            lblDestination.Text = "网络目标:";
            // 
            // txtDestination
            // 
            txtDestination.Location = new Point(80, 22);
            txtDestination.Name = "txtDestination";
            txtDestination.PlaceholderText = "例如: 192.168.1.0/24 或 8.8.8.8";
            txtDestination.Size = new Size(280, 23);
            txtDestination.TabIndex = 2;
            // 
            // chkPersistent
            // 
            chkPersistent.AutoSize = true;
            chkPersistent.Location = new Point(450, 55);
            chkPersistent.Name = "chkPersistent";
            chkPersistent.Size = new Size(88, 21);
            chkPersistent.TabIndex = 8;
            chkPersistent.Text = "永久路由";
            chkPersistent.UseVisualStyleBackColor = true;
            // 
            // btnAddRoute
            // 
            btnAddRoute.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            btnAddRoute.Location = new Point(412, 83);
            btnAddRoute.Name = "btnAddRoute";
            btnAddRoute.Size = new Size(75, 23);
            btnAddRoute.TabIndex = 1;
            btnAddRoute.Text = "添加";
            btnAddRoute.UseVisualStyleBackColor = true;

            // 
            // lblDestinationHint
            // 
            lblDestinationHint.AutoSize = true;
            lblDestinationHint.ForeColor = Color.Gray;
            lblDestinationHint.Location = new Point(80, 83);
            lblDestinationHint.Name = "lblDestinationHint";
            lblDestinationHint.Size = new Size(300, 17);
            lblDestinationHint.TabIndex = 8;
            lblDestinationHint.Text = "支持CIDR格式或单个IP，0.0.0.0/0表示默认路由";
            // 
            // RouteManagementPanel
            // 
            AutoScaleDimensions = new SizeF(7F, 17F);
            AutoScaleMode = AutoScaleMode.Font;
            Controls.Add(grpAddRoute);
            Controls.Add(grpRouteTable);
            Name = "RouteManagementPanel";
            Size = new Size(586, 518);
            grpRouteTable.ResumeLayout(false);
            grpRouteTable.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)dgvRoutes).EndInit();
            grpAddRoute.ResumeLayout(false);
            grpAddRoute.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)numMetric).EndInit();
            ResumeLayout(false);
        }

        #endregion

        private GroupBox grpRouteTable;
        private DataGridView dgvRoutes;
        private Button btnRefreshRoutes;
        private Button btnDeleteRoute;
        private GroupBox grpAddRoute;
        private Label lblDestination;
        private TextBox txtDestination;
        private Button btnAddRoute;
        private Label lblAdapter;
        private ComboBox cmbAdapter;
        private Label lblMetric;
        private NumericUpDown numMetric;
        private Label lblRouteCount;
        private Label lblConflictInfo;
        private Label lblDestinationHint;
        private CheckBox chkPersistent;
    }
} 