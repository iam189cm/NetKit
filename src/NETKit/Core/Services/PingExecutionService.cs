using System.Net;
using System.Net.NetworkInformation;
using System.Threading.Tasks;
using NETKit.Core.Models;
using NETKit.Common;

namespace NETKit.Core.Services
{
    /// <summary>
    /// 提供执行单个ping请求的服务
    /// </summary>
    public class PingExecutionService
    {
        /// <summary>
        /// 异步向指定IP地址发送ping请求
        /// </summary>
        /// <param name="ipAddress">要ping的IP地址</param>
        /// <param name="timeout">ping请求的超时时间（毫秒）</param>
        /// <returns>包含ping操作结果的 <see cref="IPScanItem"/></returns>
        public async Task<IPScanItem> PingAsync(IPAddress ipAddress, int timeout)
        {
            var scanItem = new IPScanItem(ipAddress);
            using (var ping = new Ping())
            {
                try
                {
                    var reply = await ping.SendPingAsync(ipAddress, timeout);

                    if (reply.Status == IPStatus.Success)
                    {
                        scanItem.Status = ScanStatus.Success;
                        scanItem.RoundtripTime = reply.RoundtripTime;
                    }
                    else if (reply.Status == IPStatus.TimedOut)
                    {
                        scanItem.Status = ScanStatus.Timeout;
                    }
                    else
                    {
                        scanItem.Status = ScanStatus.Failed;
                    }
                }
                catch (PingException)
                {
                    // 捕获异常，如"未知主机"等
                    scanItem.Status = ScanStatus.Failed;
                }
            }
            return scanItem;
        }
    }
}
