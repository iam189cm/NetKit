using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Net;
using System.Windows.Forms;
using NETKit.Core.Models;
using NETKit.Common;

namespace NETKit.UI.Controls
{
    /// <summary>
    /// 用于以图形网格形式显示IP扫描结果的专业控件
    /// </summary>
    public class IPGridControl : UserControl
    {
        private List<IPScanItem> _scanItems;
        private Dictionary<ScanStatus, Color> _statusColors;
        private Dictionary<ScanStatus, Brush> _statusBrushes;
        private IPScanItem _selectedItem;
        private IPScanItem _hoveredItem;
        private ToolTip _toolTip;
        private ContextMenuStrip _contextMenu;

        // 网格布局设置
        private const int CellWidth = 60;
        private const int CellHeight = 60;
        private const int CellPadding = 1;
        private const int GridMargin = 10;

        public event Action<IPScanItem> ItemSelected;
        public event Action<IPScanItem> ItemDoubleClicked;

        public IPGridControl()
        {
            InitializeComponent();
            InitializeColors();
            InitializeContextMenu();
            InitializeTooltip();
        }

        private void InitializeComponent()
        {
            this.DoubleBuffered = true;
            this.BackColor = Color.White;
            this.Font = new Font("Consolas", 8F, FontStyle.Regular);
            this.Cursor = Cursors.Hand;
            
            // 启用鼠标事件
            this.MouseMove += OnMouseMove;
            this.MouseClick += OnMouseClick;
            this.MouseDoubleClick += OnMouseDoubleClick;
            this.MouseLeave += OnMouseLeave;
        }

        private void InitializeColors()
        {
            _statusColors = new Dictionary<ScanStatus, Color>
            {
                { ScanStatus.Pending, Color.LightGray },
                { ScanStatus.Success, Color.LimeGreen }, // 在线设备：鲜明绿色
                { ScanStatus.Failed, Color.Crimson },    // 超时设备：鲜明红色
                { ScanStatus.Timeout, Color.Crimson }    // 超时设备：鲜明红色（与Failed相同）
            };

            _statusBrushes = new Dictionary<ScanStatus, Brush>();
            foreach (var kvp in _statusColors)
            {
                _statusBrushes[kvp.Key] = new SolidBrush(kvp.Value);
            }
        }

        private void InitializeContextMenu()
        {
            _contextMenu = new ContextMenuStrip();
            _contextMenu.Items.Add("复制IP地址", null, CopyIPAddress);
            _contextMenu.Items.Add("单独Ping", null, PingSingle);
            _contextMenu.Items.Add("-");
            _contextMenu.Items.Add("查看详情", null, ShowDetails);
        }

        private void InitializeTooltip()
        {
            _toolTip = new ToolTip();
            _toolTip.AutoPopDelay = 5000;
            _toolTip.InitialDelay = 500;
            _toolTip.ReshowDelay = 100;
        }

        /// <summary>
        /// 设置网格的数据源并触发重绘
        /// </summary>
        /// <param name="items">要显示的IP扫描项目列表</param>
        public void SetScanItems(List<IPScanItem> items)
        {
            _scanItems = items ?? new List<IPScanItem>();
            this.Invalidate();
        }

        /// <summary>
        /// 更新网格中的单个项目并触发重绘
        /// </summary>
        /// <param name="item">已更新的项目</param>
        public void UpdateScanItem(IPScanItem item)
        {
            if (_scanItems != null && _scanItems.Contains(item))
            {
                // 找到此项目的矩形并仅使该区域无效
                var rect = GetItemRectangle(item);
                if (rect.HasValue)
                {
                    this.Invalidate(rect.Value);
                }
            }
        }

        /// <summary>
        /// 清除所有扫描项目并重置网格
        /// </summary>
        public void Clear()
        {
            _scanItems?.Clear();
            _selectedItem = null;
            _hoveredItem = null;
            this.Invalidate();
        }

        protected override void OnPaint(PaintEventArgs e)
        {
            base.OnPaint(e);
            var g = e.Graphics;
            g.Clear(this.BackColor);

            if (_scanItems == null || _scanItems.Count == 0)
            {
                DrawEmptyState(g);
                return;
            }

            DrawGrid(g);
        }

        private void DrawEmptyState(Graphics g)
        {
            var text = "等待扫描...";
            var font = new Font("Microsoft YaHei UI", 12F, FontStyle.Regular);
            var brush = new SolidBrush(Color.Gray);
            var size = g.MeasureString(text, font);
            var x = (this.Width - size.Width) / 2;
            var y = (this.Height - size.Height) / 2;
            
            g.DrawString(text, font, brush, x, y);
            
            font.Dispose();
            brush.Dispose();
        }

        private void DrawGrid(Graphics g)
        {
            // 使用固定大小的单元格 (60x60)
            int itemsPerRow = Math.Max(1, (this.Width - 2 * GridMargin) / (CellWidth + CellPadding));
            
            for (int i = 0; i < _scanItems.Count; i++)
            {
                var item = _scanItems[i];
                int row = i / itemsPerRow;
                int col = i % itemsPerRow;

                var rect = new Rectangle(
                    GridMargin + col * (CellWidth + CellPadding),
                    GridMargin + row * (CellHeight + CellPadding),
                    CellWidth,
                    CellHeight);

                DrawCell(g, item, rect);
            }
        }

        private void DrawCell(Graphics g, IPScanItem item, Rectangle rect)
        {
            // 根据状态填充背景
            var brush = _statusBrushes[item.Status];
            g.FillRectangle(brush, rect);

            // 绘制状态相关的边框
            var borderColor = GetBorderColor(item.Status);
            var borderWidth = GetBorderWidth(item);
            
            // 如果是选中或悬停状态，使用特殊边框
            if (item == _selectedItem)
            {
                borderColor = Color.Blue;
                borderWidth = 3;
            }
            else if (item == _hoveredItem)
            {
                borderColor = Color.DarkBlue;
                borderWidth = 2;
            }

            using (var pen = new Pen(borderColor, borderWidth))
            {
                g.DrawRectangle(pen, rect);
            }

            // 绘制IP地址文本
            var ipText = GetLastOctet(item.Address);
            var textColor = GetTextColor(item.Status);
            
            using (var textBrush = new SolidBrush(textColor))
            {
                var stringFormat = new StringFormat
                {
                    Alignment = StringAlignment.Center,
                    LineAlignment = StringAlignment.Center
                };

                g.DrawString(ipText, this.Font, textBrush, rect, stringFormat);
            }

            // 为成功的ping绘制响应时间
            if (item.Status == ScanStatus.Success && item.RoundtripTime >= 0)
            {
                var timeText = $"{item.RoundtripTime}ms";
                var timeFont = new Font(this.Font.FontFamily, 6.5F);
                // 将响应时间文字向上移动，从底部留出更多空间
                var timeRect = new Rectangle(rect.X + 2, rect.Y + rect.Height - 16, rect.Width - 4, 12);
                
                using (var timeBrush = new SolidBrush(Color.White))
                using (var timeFormat = new StringFormat { 
                    Alignment = StringAlignment.Center,
                    LineAlignment = StringAlignment.Center 
                })
                {
                    g.DrawString(timeText, timeFont, timeBrush, timeRect, timeFormat);
                }
                
                timeFont.Dispose();
            }
        }

        private string GetLastOctet(IPAddress address)
        {
            var bytes = address.GetAddressBytes();
            return bytes[3].ToString();
        }

        private Color GetTextColor(ScanStatus status)
        {
            return status switch
            {
                ScanStatus.Success => Color.White,        // 在绿色背景上使用白色文字
                ScanStatus.Failed => Color.White,         // 在红色背景上使用白色文字
                ScanStatus.Timeout => Color.White,        // 在红色背景上使用白色文字
                _ => Color.Black                           // 在灰色背景上使用黑色文字
            };
        }

        private Color GetBorderColor(ScanStatus status)
        {
            return status switch
            {
                ScanStatus.Success => Color.DarkGreen,    // 在线设备：深绿色边框
                ScanStatus.Failed => Color.DarkRed,       // 超时设备：深红色边框
                ScanStatus.Timeout => Color.DarkRed,      // 超时设备：深红色边框
                _ => Color.DarkGray                        // 等待扫描：深灰色边框
            };
        }

        private int GetBorderWidth(IPScanItem item)
        {
            return item.Status switch
            {
                ScanStatus.Success => 2,                  // 在线设备：粗边框
                ScanStatus.Failed => 2,                   // 超时设备：粗边框
                ScanStatus.Timeout => 2,                  // 超时设备：粗边框
                _ => 1                                     // 等待扫描：细边框
            };
        }

        private Rectangle? GetItemRectangle(IPScanItem item)
        {
            if (_scanItems == null) return null;
            
            var index = _scanItems.IndexOf(item);
            if (index < 0) return null;

            int itemsPerRow = Math.Max(1, (this.Width - 2 * GridMargin) / (CellWidth + CellPadding));
            int row = index / itemsPerRow;
            int col = index % itemsPerRow;

            return new Rectangle(
                GridMargin + col * (CellWidth + CellPadding),
                GridMargin + row * (CellHeight + CellPadding),
                CellWidth,
                CellHeight);
        }

        private IPScanItem GetItemAtPoint(Point point)
        {
            if (_scanItems == null) return null;
            
            for (int i = 0; i < _scanItems.Count; i++)
            {
                var rect = GetItemRectangle(_scanItems[i]);
                if (rect.HasValue && rect.Value.Contains(point))
                {
                    return _scanItems[i];
                }
            }
            return null;
        }

        private void OnMouseMove(object sender, MouseEventArgs e)
        {
            var item = GetItemAtPoint(e.Location);
            
            if (item != _hoveredItem)
            {
                _hoveredItem = item;
                this.Invalidate();

                if (item != null)
                {
                    var tooltip = $"IP: {item.Address}\n状态: {GetStatusText(item.Status)}";
                    if (item.Status == ScanStatus.Success && item.RoundtripTime >= 0)
                    {
                        tooltip += $"\n响应时间: {item.RoundtripTime}ms";
                    }
                    _toolTip.SetToolTip(this, tooltip);
                }
                else
                {
                    _toolTip.SetToolTip(this, "");
                }
            }
        }

        private void OnMouseClick(object sender, MouseEventArgs e)
        {
            var item = GetItemAtPoint(e.Location);
            
            if (e.Button == MouseButtons.Left)
            {
                _selectedItem = item;
                this.Invalidate();
                ItemSelected?.Invoke(item);
            }
            else if (e.Button == MouseButtons.Right && item != null)
            {
                _selectedItem = item;
                this.Invalidate();
                _contextMenu.Tag = item;
                _contextMenu.Show(this, e.Location);
            }
        }

        private void OnMouseDoubleClick(object sender, MouseEventArgs e)
        {
            var item = GetItemAtPoint(e.Location);
            if (item != null)
            {
                ItemDoubleClicked?.Invoke(item);
            }
        }

        private void OnMouseLeave(object sender, EventArgs e)
        {
            if (_hoveredItem != null)
            {
                _hoveredItem = null;
                this.Invalidate();
                _toolTip.SetToolTip(this, "");
            }
        }

        private string GetStatusText(ScanStatus status)
        {
            return status switch
            {
                ScanStatus.Pending => "等待扫描",
                ScanStatus.Success => "在线",
                ScanStatus.Failed => "超时",      // 统一为"超时"
                ScanStatus.Timeout => "超时",     // 统一为"超时"
                _ => "未知"
            };
        }

        // 上下文菜单事件处理程序
        private void CopyIPAddress(object sender, EventArgs e)
        {
            if (_contextMenu.Tag is IPScanItem item)
            {
                Clipboard.SetText(item.Address.ToString());
                MessageBox.Show($"IP地址 {item.Address} 已复制到剪贴板", "复制成功", 
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void PingSingle(object sender, EventArgs e)
        {
            if (_contextMenu.Tag is IPScanItem item)
            {
                // 这将触发单个ping操作
                MessageBox.Show($"正在Ping {item.Address}...", "单独Ping", 
                    MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void ShowDetails(object sender, EventArgs e)
        {
            if (_contextMenu.Tag is IPScanItem item)
            {
                var details = $"IP地址: {item.Address}\n" +
                             $"状态: {GetStatusText(item.Status)}\n";
                
                if (item.Status == ScanStatus.Success && item.RoundtripTime >= 0)
                {
                    details += $"响应时间: {item.RoundtripTime}ms\n";
                }
                
                MessageBox.Show(details, "IP详情", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                _toolTip?.Dispose();
                _contextMenu?.Dispose();
                
                foreach (var brush in _statusBrushes.Values)
                {
                    brush?.Dispose();
                }
            }
            base.Dispose(disposing);
        }
    }
}
