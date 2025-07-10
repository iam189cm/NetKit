using System.Net;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 表示路由跟踪中的单个跳点
    /// </summary>
    public class TraceRouteHop
    {
        /// <summary>
        /// 跳数（从1开始）
        /// </summary>
        public int HopNumber { get; set; }

        /// <summary>
        /// 跳点的IP地址，如果无法到达则为null
        /// </summary>
        public IPAddress? IpAddress { get; set; }

        /// <summary>
        /// 主机名（如果能解析到）
        /// </summary>
        public string? HostName { get; set; }

        /// <summary>
        /// 第一次ping的延迟（毫秒），-1表示超时或失败
        /// </summary>
        public long Delay1 { get; set; } = -1;

        /// <summary>
        /// 第二次ping的延迟（毫秒），-1表示超时或失败
        /// </summary>
        public long Delay2 { get; set; } = -1;

        /// <summary>
        /// 第三次ping的延迟（毫秒），-1表示超时或失败
        /// </summary>
        public long Delay3 { get; set; } = -1;

        /// <summary>
        /// 是否为超时跳点（显示为 * * *）
        /// </summary>
        public bool IsTimeout { get; set; }

        /// <summary>
        /// 是否为最终目标
        /// </summary>
        public bool IsDestination { get; set; }

        /// <summary>
        /// 初始化新的路由跳点
        /// </summary>
        /// <param name="hopNumber">跳数</param>
        public TraceRouteHop(int hopNumber)
        {
            HopNumber = hopNumber;
        }

        /// <summary>
        /// 获取平均延迟
        /// </summary>
        /// <returns>平均延迟，如果所有测量都失败则返回-1</returns>
        public double GetAverageDelay()
        {
            var validDelays = new List<long>();
            
            if (Delay1 >= 0) validDelays.Add(Delay1);
            if (Delay2 >= 0) validDelays.Add(Delay2);
            if (Delay3 >= 0) validDelays.Add(Delay3);
            
            return validDelays.Count > 0 ? validDelays.Average() : -1;
        }

        /// <summary>
        /// 获取显示用的IP地址字符串
        /// </summary>
        /// <returns>IP地址字符串或"* * *"</returns>
        public string GetDisplayAddress()
        {
            if (IsTimeout)
                return "* * *";
            
            return IpAddress?.ToString() ?? "未知";
        }

        /// <summary>
        /// 获取显示用的延迟字符串
        /// </summary>
        /// <param name="delayIndex">延迟索引（1-3）</param>
        /// <returns>延迟字符串</returns>
        public string GetDisplayDelay(int delayIndex)
        {
            long delay = delayIndex switch
            {
                1 => Delay1,
                2 => Delay2,
                3 => Delay3,
                _ => -1
            };

            return delay >= 0 ? $"{delay}ms" : "*";
        }
    }
} 