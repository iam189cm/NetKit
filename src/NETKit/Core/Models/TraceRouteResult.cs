using System.Net;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 表示完整的路由跟踪结果
    /// </summary>
    public class TraceRouteResult
    {
        /// <summary>
        /// 目标地址
        /// </summary>
        public string TargetAddress { get; set; } = string.Empty;

        /// <summary>
        /// 解析后的目标IP地址
        /// </summary>
        public IPAddress? TargetIpAddress { get; set; }

        /// <summary>
        /// 所有跳点列表
        /// </summary>
        public List<TraceRouteHop> Hops { get; set; } = new();

        /// <summary>
        /// 跟踪开始时间
        /// </summary>
        public DateTime StartTime { get; set; }

        /// <summary>
        /// 跟踪结束时间
        /// </summary>
        public DateTime EndTime { get; set; }

        /// <summary>
        /// 是否成功到达目标
        /// </summary>
        public bool IsCompleted { get; set; }

        /// <summary>
        /// 是否被用户取消
        /// </summary>
        public bool IsCancelled { get; set; }

        /// <summary>
        /// 错误信息（如果有）
        /// </summary>
        public string? ErrorMessage { get; set; }

        /// <summary>
        /// 最大跳数限制
        /// </summary>
        public int MaxHops { get; set; } = 30;

        /// <summary>
        /// 超时时间（毫秒）
        /// </summary>
        public int TimeoutMs { get; set; } = 5000;

        /// <summary>
        /// 获取总跳数
        /// </summary>
        public int TotalHops => Hops.Count;

        /// <summary>
        /// 获取总耗时
        /// </summary>
        public TimeSpan TotalDuration => EndTime - StartTime;

        /// <summary>
        /// 获取平均延迟
        /// </summary>
        /// <returns>平均延迟（毫秒），如果没有有效数据则返回-1</returns>
        public double GetAverageDelay()
        {
            var validDelays = new List<double>();
            
            foreach (var hop in Hops)
            {
                var avgDelay = hop.GetAverageDelay();
                if (avgDelay >= 0)
                {
                    validDelays.Add(avgDelay);
                }
            }
            
            return validDelays.Count > 0 ? validDelays.Average() : -1;
        }

        /// <summary>
        /// 获取成功响应的跳点数量
        /// </summary>
        /// <returns>成功响应的跳点数量</returns>
        public int GetSuccessfulHops()
        {
            return Hops.Count(hop => !hop.IsTimeout && hop.GetAverageDelay() >= 0);
        }

        /// <summary>
        /// 获取超时的跳点数量
        /// </summary>
        /// <returns>超时的跳点数量</returns>
        public int GetTimeoutHops()
        {
            return Hops.Count(hop => hop.IsTimeout);
        }

        /// <summary>
        /// 获取状态描述
        /// </summary>
        /// <returns>状态描述字符串</returns>
        public string GetStatusDescription()
        {
            if (IsCancelled)
                return "跟踪已取消";
            
            if (!string.IsNullOrEmpty(ErrorMessage))
                return $"跟踪失败: {ErrorMessage}";
            
            if (IsCompleted)
                return $"跟踪完成，共{TotalHops}跳，耗时{TotalDuration.TotalSeconds:F1}秒";
            
            return "跟踪进行中...";
        }

        /// <summary>
        /// 添加新的跳点
        /// </summary>
        /// <param name="hop">跳点信息</param>
        public void AddHop(TraceRouteHop hop)
        {
            Hops.Add(hop);
        }

        /// <summary>
        /// 清空所有跳点
        /// </summary>
        public void ClearHops()
        {
            Hops.Clear();
        }
    }
} 