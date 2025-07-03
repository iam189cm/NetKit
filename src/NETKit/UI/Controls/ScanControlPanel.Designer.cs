namespace NETKit.UI.Controls
{
    partial class ScanControlPanel
    {
        /// <summary> 
        /// 必需的设计器变量
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary> 
        /// 清理所有正在使用的资源
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

        #region 组件设计器生成的代码

        /// <summary> 
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容
        /// </summary>
        private void InitializeComponent()
        {
            this.grpScanControl = new System.Windows.Forms.GroupBox();
            this.lblIpAddress = new System.Windows.Forms.Label();
            this.txtIp1 = new System.Windows.Forms.TextBox();
            this.lblDot1 = new System.Windows.Forms.Label();
            this.txtIp2 = new System.Windows.Forms.TextBox();
            this.lblDot2 = new System.Windows.Forms.Label();
            this.txtIp3 = new System.Windows.Forms.TextBox();
            this.lblDot3 = new System.Windows.Forms.Label();
            this.txtRangeStart = new System.Windows.Forms.TextBox();
            this.lblRangeTo = new System.Windows.Forms.Label();
            this.txtRangeEnd = new System.Windows.Forms.TextBox();
            this.lblTimeout = new System.Windows.Forms.Label();
            this.txtTimeout = new System.Windows.Forms.TextBox();
            this.lblTimeoutMs = new System.Windows.Forms.Label();
            this.btnStartScan = new System.Windows.Forms.Button();
            this.btnStopScan = new System.Windows.Forms.Button();
            this.grpScanControl.SuspendLayout();
            this.SuspendLayout();
            // 
            // grpScanControl
            // 
            this.grpScanControl.Controls.Add(this.btnStopScan);
            this.grpScanControl.Controls.Add(this.btnStartScan);
            this.grpScanControl.Controls.Add(this.lblTimeoutMs);
            this.grpScanControl.Controls.Add(this.txtTimeout);
            this.grpScanControl.Controls.Add(this.lblTimeout);
            this.grpScanControl.Controls.Add(this.txtRangeEnd);
            this.grpScanControl.Controls.Add(this.lblRangeTo);
            this.grpScanControl.Controls.Add(this.txtRangeStart);
            this.grpScanControl.Controls.Add(this.lblDot3);
            this.grpScanControl.Controls.Add(this.txtIp3);
            this.grpScanControl.Controls.Add(this.lblDot2);
            this.grpScanControl.Controls.Add(this.txtIp2);
            this.grpScanControl.Controls.Add(this.lblDot1);
            this.grpScanControl.Controls.Add(this.txtIp1);
            this.grpScanControl.Controls.Add(this.lblIpAddress);
            this.grpScanControl.Dock = System.Windows.Forms.DockStyle.Fill;
            this.grpScanControl.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.grpScanControl.Location = new System.Drawing.Point(0, 0);
            this.grpScanControl.Name = "grpScanControl";
            this.grpScanControl.Size = new System.Drawing.Size(650, 60);
            this.grpScanControl.TabIndex = 0;
            this.grpScanControl.TabStop = false;
            this.grpScanControl.Text = "Ping测试";
            // 
            // lblIpAddress
            // 
            this.lblIpAddress.AutoSize = true;
            this.lblIpAddress.Location = new System.Drawing.Point(10, 25);
            this.lblIpAddress.Name = "lblIpAddress";
            this.lblIpAddress.Size = new System.Drawing.Size(25, 17);
            this.lblIpAddress.TabIndex = 0;
            this.lblIpAddress.Text = "IP:";
            // 
            // txtIp1
            // 
            this.txtIp1.Location = new System.Drawing.Point(35, 23);
            this.txtIp1.MaxLength = 3;
            this.txtIp1.Name = "txtIp1";
            this.txtIp1.Size = new System.Drawing.Size(35, 23);
            this.txtIp1.TabIndex = 1;
            this.txtIp1.Text = "192";
            this.txtIp1.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // lblDot1
            // 
            this.lblDot1.AutoSize = true;
            this.lblDot1.Location = new System.Drawing.Point(75, 25);
            this.lblDot1.Name = "lblDot1";
            this.lblDot1.Size = new System.Drawing.Size(15, 17);
            this.lblDot1.TabIndex = 2;
            this.lblDot1.Text = ".";
            // 
            // txtIp2
            // 
            this.txtIp2.Location = new System.Drawing.Point(95, 23);
            this.txtIp2.MaxLength = 3;
            this.txtIp2.Name = "txtIp2";
            this.txtIp2.Size = new System.Drawing.Size(35, 23);
            this.txtIp2.TabIndex = 3;
            this.txtIp2.Text = "168";
            this.txtIp2.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // lblDot2
            // 
            this.lblDot2.AutoSize = true;
            this.lblDot2.Location = new System.Drawing.Point(135, 25);
            this.lblDot2.Name = "lblDot2";
            this.lblDot2.Size = new System.Drawing.Size(15, 17);
            this.lblDot2.TabIndex = 4;
            this.lblDot2.Text = ".";
            // 
            // txtIp3
            // 
            this.txtIp3.Location = new System.Drawing.Point(155, 23);
            this.txtIp3.MaxLength = 3;
            this.txtIp3.Name = "txtIp3";
            this.txtIp3.Size = new System.Drawing.Size(35, 23);
            this.txtIp3.TabIndex = 5;
            this.txtIp3.Text = "1";
            this.txtIp3.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // lblDot3
            // 
            this.lblDot3.AutoSize = true;
            this.lblDot3.Location = new System.Drawing.Point(195, 25);
            this.lblDot3.Name = "lblDot3";
            this.lblDot3.Size = new System.Drawing.Size(15, 17);
            this.lblDot3.TabIndex = 6;
            this.lblDot3.Text = ".";
            // 
            // txtRangeStart
            // 
            this.txtRangeStart.Location = new System.Drawing.Point(215, 23);
            this.txtRangeStart.MaxLength = 3;
            this.txtRangeStart.Name = "txtRangeStart";
            this.txtRangeStart.Size = new System.Drawing.Size(35, 23);
            this.txtRangeStart.TabIndex = 7;
            this.txtRangeStart.Text = "1";
            this.txtRangeStart.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // lblRangeTo
            // 
            this.lblRangeTo.AutoSize = true;
            this.lblRangeTo.Location = new System.Drawing.Point(255, 25);
            this.lblRangeTo.Name = "lblRangeTo";
            this.lblRangeTo.Size = new System.Drawing.Size(15, 17);
            this.lblRangeTo.TabIndex = 8;
            this.lblRangeTo.Text = "-";
            // 
            // txtRangeEnd
            // 
            this.txtRangeEnd.Location = new System.Drawing.Point(275, 23);
            this.txtRangeEnd.MaxLength = 3;
            this.txtRangeEnd.Name = "txtRangeEnd";
            this.txtRangeEnd.Size = new System.Drawing.Size(35, 23);
            this.txtRangeEnd.TabIndex = 9;
            this.txtRangeEnd.Text = "254";
            this.txtRangeEnd.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // lblTimeout
            // 
            this.lblTimeout.AutoSize = true;
            this.lblTimeout.Location = new System.Drawing.Point(325, 25);
            this.lblTimeout.Name = "lblTimeout";
            this.lblTimeout.Size = new System.Drawing.Size(44, 17);
            this.lblTimeout.TabIndex = 10;
            this.lblTimeout.Text = "超时:";
            // 
            // txtTimeout
            // 
            this.txtTimeout.Location = new System.Drawing.Point(375, 23);
            this.txtTimeout.MaxLength = 4;
            this.txtTimeout.Name = "txtTimeout";
            this.txtTimeout.Size = new System.Drawing.Size(40, 23);
            this.txtTimeout.TabIndex = 11;
            this.txtTimeout.Text = "200";
            this.txtTimeout.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            // 
            // lblTimeoutMs
            // 
            this.lblTimeoutMs.AutoSize = true;
            this.lblTimeoutMs.Location = new System.Drawing.Point(420, 25);
            this.lblTimeoutMs.Name = "lblTimeoutMs";
            this.lblTimeoutMs.Size = new System.Drawing.Size(26, 17);
            this.lblTimeoutMs.TabIndex = 12;
            this.lblTimeoutMs.Text = "ms";
            // 
            // btnStartScan
            // 
            this.btnStartScan.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(122)))), ((int)(((byte)(204)))));
            this.btnStartScan.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnStartScan.ForeColor = System.Drawing.Color.White;
            this.btnStartScan.Location = new System.Drawing.Point(465, 20);
            this.btnStartScan.Name = "btnStartScan";
            this.btnStartScan.Size = new System.Drawing.Size(60, 28);
            this.btnStartScan.TabIndex = 13;
            this.btnStartScan.Text = "开始";
            this.btnStartScan.UseVisualStyleBackColor = false;
            this.btnStartScan.Click += new System.EventHandler(this.btnStartScan_Click);
            // 
            // btnStopScan
            // 
            this.btnStopScan.BackColor = System.Drawing.Color.FromArgb(((int)(((byte)(220)))), ((int)(((byte)(53)))), ((int)(((byte)(69)))));
            this.btnStopScan.Enabled = false;
            this.btnStopScan.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnStopScan.ForeColor = System.Drawing.Color.White;
            this.btnStopScan.Location = new System.Drawing.Point(530, 20);
            this.btnStopScan.Name = "btnStopScan";
            this.btnStopScan.Size = new System.Drawing.Size(60, 28);
            this.btnStopScan.TabIndex = 14;
            this.btnStopScan.Text = "停止";
            this.btnStopScan.UseVisualStyleBackColor = false;
            this.btnStopScan.Click += new System.EventHandler(this.btnStopScan_Click);
            // 
            // ScanControlPanel
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 17F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.grpScanControl);
            this.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.Name = "ScanControlPanel";
            this.Size = new System.Drawing.Size(650, 60);
            this.grpScanControl.ResumeLayout(false);
            this.grpScanControl.PerformLayout();
            this.ResumeLayout(false);
        }

        #endregion

        private System.Windows.Forms.GroupBox grpScanControl;
        private System.Windows.Forms.Label lblIpAddress;
        private System.Windows.Forms.TextBox txtIp1;
        private System.Windows.Forms.Label lblDot1;
        private System.Windows.Forms.TextBox txtIp2;
        private System.Windows.Forms.Label lblDot2;
        private System.Windows.Forms.TextBox txtIp3;
        private System.Windows.Forms.Label lblDot3;
        private System.Windows.Forms.TextBox txtRangeStart;
        private System.Windows.Forms.Label lblRangeTo;
        private System.Windows.Forms.TextBox txtRangeEnd;
        private System.Windows.Forms.Label lblTimeout;
        private System.Windows.Forms.TextBox txtTimeout;
        private System.Windows.Forms.Label lblTimeoutMs;
        private System.Windows.Forms.Button btnStartScan;
        private System.Windows.Forms.Button btnStopScan;
    }
}
