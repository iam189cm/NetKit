using System.Net;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 子网信息模型
    /// </summary>
    public class SubnetInfo
    {
        /// <summary>
        /// 子网名称或描述
        /// </summary>
        public string Name { get; set; }

        /// <summary>
        /// 网络地址
        /// </summary>
        public IPAddress NetworkAddress { get; set; }

        /// <summary>
        /// CIDR前缀长度
        /// </summary>
        public int PrefixLength { get; set; }

        /// <summary>
        /// 子网掩码
        /// </summary>
        public IPAddress SubnetMask { get; set; }

        /// <summary>
        /// 广播地址
        /// </summary>
        public IPAddress BroadcastAddress { get; set; }

        /// <summary>
        /// 第一个可用主机IP
        /// </summary>
        public IPAddress FirstUsableIP { get; set; }

        /// <summary>
        /// 最后一个可用主机IP
        /// </summary>
        public IPAddress LastUsableIP { get; set; }

        /// <summary>
        /// 可用主机数量
        /// </summary>
        public long UsableHostCount { get; set; }

        /// <summary>
        /// 是否已分配
        /// </summary>
        public bool IsAllocated { get; set; }

        public SubnetInfo()
        {
            Name = string.Empty;
            IsAllocated = false;
        }

        /// <summary>
        /// 获取CIDR表示法
        /// </summary>
        /// <returns>CIDR格式的网络地址</returns>
        public string GetCIDRNotation()
        {
            return $"{NetworkAddress}/{PrefixLength}";
        }

        /// <summary>
        /// 获取主机范围字符串
        /// </summary>
        /// <returns>主机范围描述</returns>
        public string GetHostRange()
        {
            return $"{FirstUsableIP} - {LastUsableIP}";
        }

        /// <summary>
        /// 获取格式化的子网信息
        /// </summary>
        /// <returns>格式化的子网描述</returns>
        public string GetFormattedInfo()
        {
            return $"{Name}: {GetCIDRNotation()} ({GetHostRange()}) - {UsableHostCount} 个主机";
        }

        /// <summary>
        /// 检查指定IP是否在此子网内
        /// </summary>
        /// <param name="ipAddress">要检查的IP地址</param>
        /// <returns>是否在子网内</returns>
        public bool ContainsIP(IPAddress ipAddress)
        {
            if (ipAddress == null || NetworkAddress == null || SubnetMask == null)
                return false;

            var ipBytes = ipAddress.GetAddressBytes();
            var networkBytes = NetworkAddress.GetAddressBytes();
            var maskBytes = SubnetMask.GetAddressBytes();

            for (int i = 0; i < 4; i++)
            {
                if ((ipBytes[i] & maskBytes[i]) != (networkBytes[i] & maskBytes[i]))
                    return false;
            }

            return true;
        }
    }
}
