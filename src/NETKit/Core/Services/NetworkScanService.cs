using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using NETKit.Core.Models;

namespace NETKit.Core.Services
{
    /// <summary>
    /// 提供IP地址范围扫描服务
    /// </summary>
    public class NetworkScanService
    {
        private readonly PingExecutionService _pingService;

        /// <summary>
        /// 当单个IP扫描完成时发生
        /// </summary>
        public event Action<IPScanItem> ProgressUpdated;

        /// <summary>
        /// 当整个扫描操作完成时发生
        /// </summary>
        public event Action<NetworkScanResult> ScanCompleted;

        public NetworkScanService(PingExecutionService pingService)
        {
            _pingService = pingService;
        }

        /// <summary>
        /// 异步启动网络扫描
        /// </summary>
        /// <param name="config">扫描配置</param>
        /// <param name="cancellationToken">取消操作的令牌</param>
        /// <param name="scanItems">要扫描的IP项目列表（可选，如果提供则使用这些实例）</param>
        public async Task StartScanAsync(ScanConfiguration config, CancellationToken cancellationToken, List<IPScanItem> scanItems = null)
        {
            var scanResult = new NetworkScanResult { StartTime = DateTime.Now };
            var semaphore = new SemaphoreSlim(config.MaxConcurrentScans);

            // 如果提供了scanItems，使用它们；否则创建新的
            List<IPScanItem> itemsToScan;
            if (scanItems != null)
            {
                itemsToScan = scanItems;
            }
            else
            {
                var ipAddresses = GetIpRange(config.StartAddress, config.EndAddress);
                itemsToScan = ipAddresses.Select(ip => new IPScanItem(ip)).ToList();
            }

            var tasks = itemsToScan.Select(async item =>
            {
                await semaphore.WaitAsync(cancellationToken);
                try
                {
                    if (cancellationToken.IsCancellationRequested)
                    {
                        return;
                    }

                    // 执行ping并更新现有的item实例
                    var pingResult = await _pingService.PingAsync(item.Address, config.Timeout);
                    item.Status = pingResult.Status;
                    item.RoundtripTime = pingResult.RoundtripTime;
                    
                    // 安全地调用进度更新事件
                    ProgressUpdated?.Invoke(item);

                    lock (scanResult)
                    {
                        if (item.Status == Common.ScanStatus.Success)
                        {
                            scanResult.OnlineDevices++;
                        }
                        else if (item.Status == Common.ScanStatus.Failed)
                        {
                            scanResult.OfflineDevices++;
                        }
                        // 超时设备不计入离线设备，会在UI中单独统计
                        scanResult.ScannedItems.Add(item);
                    }
                }
                finally
                {
                    semaphore.Release();
                }
            }).ToList();

            await Task.WhenAll(tasks);

            scanResult.EndTime = DateTime.Now;
            ScanCompleted?.Invoke(scanResult);
        }

        private IEnumerable<IPAddress> GetIpRange(IPAddress start, IPAddress end)
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
                yield return new IPAddress(bytes);
            }
        }
    }
}
