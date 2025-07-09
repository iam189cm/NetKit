using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using NETKit.Core.Models;

namespace NETKit.UI.Forms
{
    /// <summary>
    /// MainForm的Ping测试相关功能
    /// </summary>
    public partial class MainForm
    {
        #region Ping测试逻辑

        /// <summary>
        /// 开始扫描事件处理
        /// </summary>
        private async void ScanControlPanel_OnStartScan(ScanConfiguration config)
        {
            _cancellationTokenSource = new CancellationTokenSource();
            scanControlPanel.SetScanInProgress(true);
            scanStatisticsPanel.Reset();

            var ipList = GetIpRange(config.StartAddress, config.EndAddress)
                .Select(ip => new IPScanItem(ip))
                .ToList();
            
            ipGridControl.SetScanItems(ipList);
            scanStatisticsPanel.StartScan(ipList.Count);

            try
            {
                await _scanService.StartScanAsync(config, _cancellationTokenSource.Token, ipList);
            }
            catch (TaskCanceledException)
            {
                UpdateStatus("扫描已由用户取消。", false);
            }
            catch (Exception ex)
            {
                UpdateStatus($"扫描时发生未知错误: {ex.Message}", true);
            }
            finally
            {
                scanControlPanel.SetScanInProgress(false);
            }
        }

        /// <summary>
        /// 停止扫描事件处理
        /// </summary>
        private void ScanControlPanel_OnStopScan()
        {
            _cancellationTokenSource?.Cancel();
        }

        /// <summary>
        /// 扫描进度更新事件处理
        /// </summary>
        private void ScanService_ProgressUpdated(IPScanItem item)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => {
                    ipGridControl.UpdateScanItem(item);
                    scanStatisticsPanel.UpdateProgress(item);
                }));
            }
            else
            {
                ipGridControl.UpdateScanItem(item);
                scanStatisticsPanel.UpdateProgress(item);
            }
        }

        /// <summary>
        /// 扫描完成事件处理
        /// </summary>
        private void ScanService_ScanCompleted(NetworkScanResult result)
        {
            if (InvokeRequired)
            {
                Invoke(new Action(() => scanStatisticsPanel.CompleteScan(result)));
            }
            else
            {
                scanStatisticsPanel.CompleteScan(result);
            }
            UpdateStatus("扫描完成。", false);
        }

        /// <summary>
        /// 生成IP地址范围
        /// </summary>
        /// <param name="start">起始IP地址</param>
        /// <param name="end">结束IP地址</param>
        /// <returns>IP地址枚举</returns>
        private IEnumerable<System.Net.IPAddress> GetIpRange(System.Net.IPAddress start, System.Net.IPAddress end)
        {
            var startBytes = start.GetAddressBytes();
            var endBytes = end.GetAddressBytes();
            Array.Reverse(startBytes);
            Array.Reverse(endBytes);
            var startNum = BitConverter.ToUInt32(startBytes, 0);
            var endNum = BitConverter.ToUInt32(endBytes, 0);

            for (var i = startNum; i <= endNum; i++)
            {
                var bytes = BitConverter.GetBytes(i);
                Array.Reverse(bytes);
                yield return new System.Net.IPAddress(bytes);
            }
        }

        #endregion
    }
}
