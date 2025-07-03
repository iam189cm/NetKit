using System;
using System.Collections.Generic;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 表示网络扫描操作的聚合结果
    /// </summary>
    public class NetworkScanResult
    {
        /// <summary>
        /// 获取扫描中包含的所有项目列表
        /// </summary>
        public List<IPScanItem> ScannedItems { get; } = new List<IPScanItem>();

        /// <summary>
        /// 获取或设置扫描的开始时间
        /// </summary>
        public DateTime StartTime { get; set; }

        /// <summary>
        /// 获取或设置扫描的结束时间
        /// </summary>
        public DateTime EndTime { get; set; }

        /// <summary>
        /// 获取扫描的总持续时间
        /// </summary>
        public TimeSpan Duration => EndTime - StartTime;

        /// <summary>
        /// 获取成功到达的设备数量
        /// </summary>
        public int OnlineDevices { get; set; }

        /// <summary>
        /// 获取未到达的设备数量（失败或超时）
        /// </summary>
        public int OfflineDevices { get; set; }

        /// <summary>
        /// 获取扫描的设备总数
        /// </summary>
        public int TotalDevices => OnlineDevices + OfflineDevices;
    }
}
