using NETKit.Common;

namespace NETKit.UI.Controls
{
    partial class TraceRoutePanel
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
            this.lblTarget = new System.Windows.Forms.Label();
            this.txtTargetAddress = new System.Windows.Forms.TextBox();
            this.btnStart = new System.Windows.Forms.Button();
            this.btnStop = new System.Windows.Forms.Button();
            this.lblMaxHops = new System.Windows.Forms.Label();
            this.numMaxHops = new System.Windows.Forms.NumericUpDown();
            this.lblTimeout = new System.Windows.Forms.Label();
            this.numTimeout = new System.Windows.Forms.NumericUpDown();
            this.dgvResults = new System.Windows.Forms.DataGridView();
            this.lblStatus = new System.Windows.Forms.Label();
            this.pnlControls = new System.Windows.Forms.Panel();
            this.pnlResults = new System.Windows.Forms.Panel();
            this.pnlStatus = new System.Windows.Forms.Panel();
            ((System.ComponentModel.ISupportInitialize)(this.numMaxHops)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.numTimeout)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.dgvResults)).BeginInit();
            this.pnlControls.SuspendLayout();
            this.pnlResults.SuspendLayout();
            this.pnlStatus.SuspendLayout();
            this.SuspendLayout();
            // 
            // lblTarget
            // 
            this.lblTarget.AutoSize = true;
            this.lblTarget.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblTarget.ForeColor = Constants.Colors.TextPrimary;
            this.lblTarget.Location = new System.Drawing.Point(15, 15);
            this.lblTarget.Name = "lblTarget";
            this.lblTarget.Size = new System.Drawing.Size(68, 17);
            this.lblTarget.TabIndex = 0;
            this.lblTarget.Text = "目标地址:";
            // 
            // txtTargetAddress
            // 
            this.txtTargetAddress.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtTargetAddress.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.txtTargetAddress.Location = new System.Drawing.Point(90, 12);
            this.txtTargetAddress.Name = "txtTargetAddress";
            this.txtTargetAddress.PlaceholderText = "例如: www.baidu.com 或 8.8.8.8";
            this.txtTargetAddress.Size = new System.Drawing.Size(260, 23);
            this.txtTargetAddress.TabIndex = 1;
            // 
            // btnStart
            // 
            this.btnStart.BackColor = Constants.Colors.PrimaryBlue;
            this.btnStart.FlatAppearance.BorderSize = 0;
            this.btnStart.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnStart.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.btnStart.ForeColor = System.Drawing.Color.White;
            this.btnStart.Location = new System.Drawing.Point(360, 10);
            this.btnStart.Name = "btnStart";
            this.btnStart.Size = new System.Drawing.Size(80, 28);
            this.btnStart.TabIndex = 2;
            this.btnStart.Text = "开始跟踪";
            this.btnStart.UseVisualStyleBackColor = false;
            this.btnStart.Click += new System.EventHandler(this.BtnStart_Click);
            // 
            // btnStop
            // 
            this.btnStop.BackColor = Constants.Colors.WarningRed;
            this.btnStop.FlatAppearance.BorderSize = 0;
            this.btnStop.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnStop.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.btnStop.ForeColor = System.Drawing.Color.White;
            this.btnStop.Location = new System.Drawing.Point(450, 10);
            this.btnStop.Name = "btnStop";
            this.btnStop.Size = new System.Drawing.Size(80, 28);
            this.btnStop.TabIndex = 3;
            this.btnStop.Text = "停止跟踪";
            this.btnStop.UseVisualStyleBackColor = false;
            this.btnStop.Click += new System.EventHandler(this.BtnStop_Click);
            // 
            // lblMaxHops
            // 
            this.lblMaxHops.AutoSize = true;
            this.lblMaxHops.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblMaxHops.ForeColor = Constants.Colors.TextPrimary;
            this.lblMaxHops.Location = new System.Drawing.Point(15, 48);
            this.lblMaxHops.Name = "lblMaxHops";
            this.lblMaxHops.Size = new System.Drawing.Size(68, 17);
            this.lblMaxHops.TabIndex = 4;
            this.lblMaxHops.Text = "最大跳数:";
            // 
            // numMaxHops
            // 
            this.numMaxHops.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.numMaxHops.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.numMaxHops.Location = new System.Drawing.Point(90, 45);
            this.numMaxHops.Maximum = new decimal(new int[] {
            255,
            0,
            0,
            0});
            this.numMaxHops.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.numMaxHops.Name = "numMaxHops";
            this.numMaxHops.Size = new System.Drawing.Size(80, 23);
            this.numMaxHops.TabIndex = 5;
            this.numMaxHops.Value = new decimal(new int[] {
            30,
            0,
            0,
            0});
            // 
            // lblTimeout
            // 
            this.lblTimeout.AutoSize = true;
            this.lblTimeout.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblTimeout.ForeColor = Constants.Colors.TextPrimary;
            this.lblTimeout.Location = new System.Drawing.Point(190, 48);
            this.lblTimeout.Name = "lblTimeout";
            this.lblTimeout.Size = new System.Drawing.Size(68, 17);
            this.lblTimeout.TabIndex = 6;
            this.lblTimeout.Text = "超时时间:";
            // 
            // numTimeout
            // 
            this.numTimeout.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.numTimeout.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.numTimeout.Increment = new decimal(new int[] {
            1000,
            0,
            0,
            0});
            this.numTimeout.Location = new System.Drawing.Point(265, 45);
            this.numTimeout.Maximum = new decimal(new int[] {
            60000,
            0,
            0,
            0});
            this.numTimeout.Minimum = new decimal(new int[] {
            1000,
            0,
            0,
            0});
            this.numTimeout.Name = "numTimeout";
            this.numTimeout.Size = new System.Drawing.Size(80, 23);
            this.numTimeout.TabIndex = 7;
            this.numTimeout.Value = new decimal(new int[] {
            5000,
            0,
            0,
            0});
            // 
            // dgvResults
            // 
            this.dgvResults.AllowUserToAddRows = false;
            this.dgvResults.AllowUserToDeleteRows = false;
            this.dgvResults.BackgroundColor = Constants.Colors.ControlBackground;
            this.dgvResults.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.dgvResults.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvResults.ColumnHeadersHeight = 30;
            this.dgvResults.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dgvResults.GridColor = Constants.Colors.BorderLight;
            this.dgvResults.Location = new System.Drawing.Point(0, 0);
            this.dgvResults.MultiSelect = false;
            this.dgvResults.Name = "dgvResults";
            this.dgvResults.ReadOnly = true;
            this.dgvResults.RowHeadersVisible = false;
            this.dgvResults.RowTemplate.Height = 26;
            this.dgvResults.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dgvResults.Size = new System.Drawing.Size(586, 500);
            this.dgvResults.TabIndex = 8;
            this.dgvResults.DefaultCellStyle.SelectionBackColor = Constants.Colors.SelectionBlue;
            this.dgvResults.DefaultCellStyle.SelectionForeColor = System.Drawing.Color.White;
            this.dgvResults.ColumnHeadersDefaultCellStyle.BackColor = Constants.Colors.HeaderBackground;
            this.dgvResults.ColumnHeadersDefaultCellStyle.ForeColor = Constants.Colors.TextPrimary;
            this.dgvResults.ColumnHeadersDefaultCellStyle.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Bold);
            this.dgvResults.EnableHeadersVisualStyles = false;
            this.dgvResults.CellBorderStyle = System.Windows.Forms.DataGridViewCellBorderStyle.SingleHorizontal;
            this.dgvResults.AlternatingRowsDefaultCellStyle.BackColor = System.Drawing.Color.FromArgb(248, 249, 250);
            // 
            // lblStatus
            // 
            this.lblStatus.AutoSize = true;
            this.lblStatus.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point);
            this.lblStatus.ForeColor = Constants.Colors.TextSecondary;
            this.lblStatus.Location = new System.Drawing.Point(15, 6);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(128, 17);
            this.lblStatus.TabIndex = 9;
            this.lblStatus.Text = "请输入目标地址开始跟踪";
            // 
            // pnlControls
            // 
            this.pnlControls.BackColor = Constants.Colors.FormBackground;
            this.pnlControls.Controls.Add(this.lblTarget);
            this.pnlControls.Controls.Add(this.txtTargetAddress);
            this.pnlControls.Controls.Add(this.btnStart);
            this.pnlControls.Controls.Add(this.btnStop);
            this.pnlControls.Controls.Add(this.lblMaxHops);
            this.pnlControls.Controls.Add(this.numMaxHops);
            this.pnlControls.Controls.Add(this.lblTimeout);
            this.pnlControls.Controls.Add(this.numTimeout);
            this.pnlControls.Dock = System.Windows.Forms.DockStyle.Top;
            this.pnlControls.Location = new System.Drawing.Point(0, 0);
            this.pnlControls.Name = "pnlControls";
            this.pnlControls.Size = new System.Drawing.Size(586, 80);
            this.pnlControls.TabIndex = 10;
            // 
            // pnlResults
            // 
            this.pnlResults.Controls.Add(this.dgvResults);
            this.pnlResults.Dock = System.Windows.Forms.DockStyle.Fill;
            this.pnlResults.Location = new System.Drawing.Point(0, 80);
            this.pnlResults.Name = "pnlResults";
            this.pnlResults.Size = new System.Drawing.Size(586, 500);
            this.pnlResults.TabIndex = 11;
            // 
            // pnlStatus
            // 
            this.pnlStatus.BackColor = Constants.Colors.FormBackground;
            this.pnlStatus.Controls.Add(this.lblStatus);
            this.pnlStatus.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.pnlStatus.Location = new System.Drawing.Point(0, 580);
            this.pnlStatus.Name = "pnlStatus";
            this.pnlStatus.Size = new System.Drawing.Size(586, 33);
            this.pnlStatus.TabIndex = 12;
            // 
            // TraceRoutePanel
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = Constants.Colors.FormBackground;
            this.Controls.Add(this.pnlResults);
            this.Controls.Add(this.pnlControls);
            this.Controls.Add(this.pnlStatus);
            this.Name = "TraceRoutePanel";
            this.Size = new System.Drawing.Size(586, 613);
            ((System.ComponentModel.ISupportInitialize)(this.numMaxHops)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.numTimeout)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.dgvResults)).EndInit();
            this.pnlControls.ResumeLayout(false);
            this.pnlControls.PerformLayout();
            this.pnlResults.ResumeLayout(false);
            this.pnlStatus.ResumeLayout(false);
            this.pnlStatus.PerformLayout();
            this.ResumeLayout(false);
        }

        #endregion

        private System.Windows.Forms.Label lblTarget;
        private System.Windows.Forms.TextBox txtTargetAddress;
        private System.Windows.Forms.Button btnStart;
        private System.Windows.Forms.Button btnStop;
        private System.Windows.Forms.Label lblMaxHops;
        private System.Windows.Forms.NumericUpDown numMaxHops;
        private System.Windows.Forms.Label lblTimeout;
        private System.Windows.Forms.NumericUpDown numTimeout;
        private System.Windows.Forms.DataGridView dgvResults;
        private System.Windows.Forms.Label lblStatus;
        private System.Windows.Forms.Panel pnlControls;
        private System.Windows.Forms.Panel pnlResults;
        private System.Windows.Forms.Panel pnlStatus;
    }
} 