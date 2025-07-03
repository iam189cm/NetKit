namespace NETKit.UI.Controls
{
    partial class ScanStatisticsPanel
    {
        /// <summary> 
        /// 必需的设计器变量
        /// </summary>
        private System.ComponentModel.IContainer components = null;


        #region Component Designer generated code

        /// <summary> 
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容
        /// </summary>
        private void InitializeComponent()
        {
            this.grpStatistics = new System.Windows.Forms.GroupBox();
            this.lblProgress = new System.Windows.Forms.Label();
            this.progressBar = new System.Windows.Forms.ProgressBar();
            this.lblProgressText = new System.Windows.Forms.Label();
            this.lblOnline = new System.Windows.Forms.Label();
            this.lblTimeout = new System.Windows.Forms.Label();
            this.grpStatistics.SuspendLayout();
            this.SuspendLayout();
            // 
            // grpStatistics
            // 
            this.grpStatistics.Controls.Add(this.lblTimeout);
            this.grpStatistics.Controls.Add(this.lblOnline);
            this.grpStatistics.Controls.Add(this.lblProgressText);
            this.grpStatistics.Controls.Add(this.progressBar);
            this.grpStatistics.Controls.Add(this.lblProgress);
            this.grpStatistics.Dock = System.Windows.Forms.DockStyle.Fill;
            this.grpStatistics.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.grpStatistics.Location = new System.Drawing.Point(0, 0);
            this.grpStatistics.Name = "grpStatistics";
            this.grpStatistics.Size = new System.Drawing.Size(580, 80);
            this.grpStatistics.TabIndex = 0;
            this.grpStatistics.TabStop = false;
            this.grpStatistics.Text = "扫描统计";
            // lblOnline
            // 
            this.lblOnline.AutoSize = true;
            this.lblOnline.ForeColor = System.Drawing.Color.Green;
            this.lblOnline.Location = new System.Drawing.Point(10, 25);
            this.lblOnline.Name = "lblOnline";
            this.lblOnline.Size = new System.Drawing.Size(68, 17);
            this.lblOnline.TabIndex = 6;
            this.lblOnline.Text = "在线设备: 0个";
            // 
            // lblTimeout
            // 
            this.lblTimeout.AutoSize = true;
            this.lblTimeout.ForeColor = System.Drawing.Color.Red;
            this.lblTimeout.Location = new System.Drawing.Point(120, 25);
            this.lblTimeout.Name = "lblTimeout";
            this.lblTimeout.Size = new System.Drawing.Size(68, 17);
            this.lblTimeout.TabIndex = 8;
            this.lblTimeout.Text = "超时设备: 0个";
            // 
            // lblProgress
            // 
            this.lblProgress.AutoSize = true;
            this.lblProgress.Location = new System.Drawing.Point(10, 50);
            this.lblProgress.Name = "lblProgress";
            this.lblProgress.Size = new System.Drawing.Size(44, 17);
            this.lblProgress.TabIndex = 3;
            this.lblProgress.Text = "进度:";
            // 
            // progressBar
            // 
            this.progressBar.Location = new System.Drawing.Point(60, 48);
            this.progressBar.Name = "progressBar";
            this.progressBar.Size = new System.Drawing.Size(200, 20);
            this.progressBar.Style = System.Windows.Forms.ProgressBarStyle.Continuous;
            this.progressBar.TabIndex = 4;
            // 
            // lblProgressText
            // 
            this.lblProgressText.AutoSize = true;
            this.lblProgressText.Location = new System.Drawing.Point(270, 50);
            this.lblProgressText.Name = "lblProgressText";
            this.lblProgressText.Size = new System.Drawing.Size(80, 17);
            this.lblProgressText.TabIndex = 5;
            this.lblProgressText.Text = "0% (0/0)";
            // 
            // ScanStatisticsPanel
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 17F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.grpStatistics);
            this.Font = new System.Drawing.Font("Microsoft YaHei UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.Name = "ScanStatisticsPanel";
            this.Size = new System.Drawing.Size(580, 80);
            this.grpStatistics.ResumeLayout(false);
            this.grpStatistics.PerformLayout();
            this.ResumeLayout(false);
        }

        #endregion

        private System.Windows.Forms.GroupBox grpStatistics;
        private System.Windows.Forms.Label lblProgress;
        private System.Windows.Forms.ProgressBar progressBar;
        private System.Windows.Forms.Label lblProgressText;
        private System.Windows.Forms.Label lblOnline;
        private System.Windows.Forms.Label lblTimeout;
    }
}
