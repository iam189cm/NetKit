using System.Net;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 路由规则类 - 存储路由配置信息
    /// </summary>
    public class RouteRule
    {
        /// <summary>
        /// 目标网络地址
        /// </summary>
        public string DestinationNetwork { get; set; } = string.Empty;

        /// <summary>
        /// 子网掩码
        /// </summary>
        public string SubnetMask { get; set; } = string.Empty;

        /// <summary>
        /// 网关地址
        /// </summary>
        public string Gateway { get; set; } = string.Empty;

        /// <summary>
        /// 网卡接口名称
        /// </summary>
        public string InterfaceName { get; set; } = string.Empty;

        /// <summary>
        /// 路由优先级(Metric值，数值越小优先级越高)
        /// </summary>
        public int Metric { get; set; } = 1;

        /// <summary>
        /// 是否为默认路由
        /// </summary>
        public bool IsDefaultRoute => DestinationNetwork == "0.0.0.0" && SubnetMask == "0.0.0.0";

        /// <summary>
        /// 显示用的目标网段文本
        /// </summary>
        public string DestinationText
        {
            get
            {
                if (IsDefaultRoute)
                    return "0.0.0.0/0 (默认路由)";
                
                // 尝试转换为CIDR格式
                try
                {
                    if (IPAddress.TryParse(SubnetMask, out IPAddress mask))
                    {
                        int cidr = GetCidrFromMask(mask);
                        if (cidr > 0)
                            return $"{DestinationNetwork}/{cidr}";
                    }
                }
                catch
                {
                    // 转换失败，使用原始格式
                }
                
                return $"{DestinationNetwork} mask {SubnetMask}";
            }
        }

        /// <summary>
        /// 构造函数
        /// </summary>
        public RouteRule()
        {
        }

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="destination">目标网络</param>
        /// <param name="mask">子网掩码</param>
        /// <param name="gateway">网关</param>
        /// <param name="interfaceName">网卡名称</param>
        /// <param name="metric">优先级</param>
        public RouteRule(string destination, string mask, string gateway, string interfaceName, int metric = 1)
        {
            DestinationNetwork = destination;
            SubnetMask = mask;
            Gateway = gateway;
            InterfaceName = interfaceName;
            Metric = metric;
        }

        /// <summary>
        /// 创建默认路由
        /// </summary>
        /// <param name="gateway">网关</param>
        /// <param name="interfaceName">网卡名称</param>
        /// <param name="metric">优先级</param>
        /// <returns>默认路由规则</returns>
        public static RouteRule CreateDefaultRoute(string gateway, string interfaceName, int metric = 1)
        {
            return new RouteRule("0.0.0.0", "0.0.0.0", gateway, interfaceName, metric);
        }

        /// <summary>
        /// 从CIDR格式创建路由规则
        /// </summary>
        /// <param name="cidrNetwork">CIDR格式网络(如192.168.1.0/24)</param>
        /// <param name="gateway">网关</param>
        /// <param name="interfaceName">网卡名称</param>
        /// <param name="metric">优先级</param>
        /// <returns>路由规则</returns>
        public static RouteRule CreateFromCidr(string cidrNetwork, string gateway, string interfaceName, int metric = 1)
        {
            var parts = cidrNetwork.Split('/');
            if (parts.Length != 2 || !int.TryParse(parts[1], out int cidr))
            {
                throw new ArgumentException("无效的CIDR格式", nameof(cidrNetwork));
            }

            string network = parts[0];
            string mask = GetMaskFromCidr(cidr);
            
            return new RouteRule(network, mask, gateway, interfaceName, metric);
        }

        /// <summary>
        /// 验证路由规则是否有效
        /// </summary>
        /// <returns>验证结果</returns>
        public ValidationResult Validate()
        {
            if (string.IsNullOrWhiteSpace(DestinationNetwork))
                return new ValidationResult(false, "目标网络不能为空");

            if (string.IsNullOrWhiteSpace(SubnetMask))
                return new ValidationResult(false, "子网掩码不能为空");

            if (string.IsNullOrWhiteSpace(Gateway))
                return new ValidationResult(false, "网关不能为空");

            if (string.IsNullOrWhiteSpace(InterfaceName))
                return new ValidationResult(false, "网卡接口不能为空");

            if (!IPAddress.TryParse(DestinationNetwork, out _))
                return new ValidationResult(false, "目标网络地址格式不正确");

            if (!IPAddress.TryParse(SubnetMask, out _))
                return new ValidationResult(false, "子网掩码格式不正确");

            if (!IPAddress.TryParse(Gateway, out _))
                return new ValidationResult(false, "网关地址格式不正确");

            if (Metric < 1 || Metric > 9999)
                return new ValidationResult(false, "优先级必须在1-9999之间");

            return new ValidationResult(true, "路由规则验证通过");
        }

        /// <summary>
        /// 获取用于route命令的字符串表示
        /// </summary>
        /// <returns>route命令参数</returns>
        public string ToRouteCommand()
        {
            return $"add {DestinationNetwork} mask {SubnetMask} {Gateway} metric {Metric}";
        }

        /// <summary>
        /// 从子网掩码获取CIDR值
        /// </summary>
        /// <param name="mask">子网掩码</param>
        /// <returns>CIDR值</returns>
        private int GetCidrFromMask(IPAddress mask)
        {
            byte[] maskBytes = mask.GetAddressBytes();
            int cidr = 0;
            
            foreach (byte b in maskBytes)
            {
                cidr += CountBits(b);
            }
            
            return cidr;
        }

        /// <summary>
        /// 计算字节中的位数
        /// </summary>
        /// <param name="value">字节值</param>
        /// <returns>位数</returns>
        private int CountBits(byte value)
        {
            int count = 0;
            while (value != 0)
            {
                count++;
                value &= (byte)(value - 1);
            }
            return count;
        }

        /// <summary>
        /// 从CIDR值获取子网掩码
        /// </summary>
        /// <param name="cidr">CIDR值</param>
        /// <returns>子网掩码字符串</returns>
        private static string GetMaskFromCidr(int cidr)
        {
            if (cidr < 0 || cidr > 32)
                throw new ArgumentException("CIDR值必须在0-32之间", nameof(cidr));

            uint mask = 0xFFFFFFFF << (32 - cidr);
            return new IPAddress(new byte[]
            {
                (byte)((mask >> 24) & 0xFF),
                (byte)((mask >> 16) & 0xFF),
                (byte)((mask >> 8) & 0xFF),
                (byte)(mask & 0xFF)
            }).ToString();
        }

        /// <summary>
        /// 重写ToString方法
        /// </summary>
        /// <returns>字符串表示</returns>
        public override string ToString()
        {
            return $"{DestinationText} via {Gateway} dev {InterfaceName} metric {Metric}";
        }

        /// <summary>
        /// 重写Equals方法
        /// </summary>
        /// <param name="obj">比较对象</param>
        /// <returns>是否相等</returns>
        public override bool Equals(object? obj)
        {
            if (obj is not RouteRule other)
                return false;

            return DestinationNetwork == other.DestinationNetwork &&
                   SubnetMask == other.SubnetMask &&
                   Gateway == other.Gateway &&
                   InterfaceName == other.InterfaceName;
        }

        /// <summary>
        /// 重写GetHashCode方法
        /// </summary>
        /// <returns>哈希码</returns>
        public override int GetHashCode()
        {
            return HashCode.Combine(DestinationNetwork, SubnetMask, Gateway, InterfaceName);
        }
    }
} 