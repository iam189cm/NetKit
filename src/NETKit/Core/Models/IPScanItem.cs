using System.Net;
using NETKit.Common;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 表示网络扫描中的单个项目，对应一个IP地址
    /// </summary>
    public class IPScanItem
    {
        /// <summary>
        /// 获取此项目的IP地址
        /// </summary>
        public IPAddress Address { get; }

        /// <summary>
        /// 获取或设置此IP地址扫描的当前状态
        /// </summary>
        public ScanStatus Status { get; set; }

        /// <summary>
        /// 获取或设置ping回复的往返时间（毫秒）
        /// 值为-1表示请求失败或超时
        /// </summary>
        public long RoundtripTime { get; set; }

        /// <summary>
        /// 初始化 <see cref="IPScanItem"/> 类的新实例
        /// </summary>
        /// <param name="address">要扫描的IP地址</param>
        public IPScanItem(IPAddress address)
        {
            Address = address;
            Status = ScanStatus.Pending;
            RoundtripTime = -1;
        }
    }
}
