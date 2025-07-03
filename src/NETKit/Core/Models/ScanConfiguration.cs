using System.Net;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 表示网络扫描操作的配置
    /// </summary>
    public class ScanConfiguration
    {
        /// <summary>
        /// 获取或设置扫描的起始IP地址
        /// </summary>
        public IPAddress StartAddress { get; set; }

        /// <summary>
        /// 获取或设置扫描的结束IP地址
        /// </summary>
        public IPAddress EndAddress { get; set; }

        /// <summary>
        /// 获取或设置每个ping请求的超时时间（毫秒）
        /// </summary>
        public int Timeout { get; set; } = 200;

        /// <summary>
        /// 获取或设置最大并发ping操作数量
        /// </summary>
        public int MaxConcurrentScans { get; set; } = 20;
    }
}
