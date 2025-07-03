using System.Net.NetworkInformation;
using NETKit.Common;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 网络适配器详细信息类 - 存储网卡的完整配置信息
    /// </summary>
    public class NetworkAdapterInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public OperationalStatus Status { get; set; }
        public NetworkInterfaceType InterfaceType { get; set; }
        public string CurrentIP { get; set; } = "未配置";
        public string CurrentSubnetMask { get; set; } = "未配置";
        public string CurrentGateway { get; set; } = "未配置";
        public List<string> CurrentDNS { get; set; } = new List<string>();
        public bool IsDHCPEnabled { get; set; }
        public string PhysicalAddress { get; set; } = string.Empty;
        public long Speed { get; set; }

        /// <summary>
        /// 获取状态的中文描述
        /// </summary>
        public string StatusText => Status switch
        {
            OperationalStatus.Up => "已连接",
            OperationalStatus.Down => "已断开",
            OperationalStatus.Testing => "测试中",
            OperationalStatus.Unknown => "未知",
            OperationalStatus.Dormant => "休眠",
            OperationalStatus.NotPresent => "不存在",
            OperationalStatus.LowerLayerDown => "底层断开",
            _ => "未知状态"
        };

        /// <summary>
        /// 获取接口类型的中文描述
        /// </summary>
        public string InterfaceTypeText => InterfaceType switch
        {
            NetworkInterfaceType.Ethernet => "以太网",
            NetworkInterfaceType.Wireless80211 => "无线网络",
            NetworkInterfaceType.Loopback => "回环",
            NetworkInterfaceType.Ppp => "PPP",
            NetworkInterfaceType.TokenRing => "令牌环",
            _ => InterfaceType.ToString()
        };

        /// <summary>
        /// 获取速度的友好显示文本
        /// </summary>
        public string SpeedText
        {
            get
            {
                if (Speed <= 0) return "未知";
                if (Speed >= 1_000_000_000) return $"{Speed / 1_000_000_000:F1} Gbps";
                if (Speed >= 1_000_000) return $"{Speed / 1_000_000:F0} Mbps";
                if (Speed >= 1_000) return $"{Speed / 1_000:F0} Kbps";
                return $"{Speed} bps";
            }
        }

        /// <summary>
        /// 获取DNS服务器的显示文本
        /// </summary>
        public string DNSText => CurrentDNS.Count > 0 ? string.Join(", ", CurrentDNS) : "未配置";

        /// <summary>
        /// 检查是否为自动配置的IP地址
        /// </summary>
        public bool IsAutoConfigIP => CurrentIP.StartsWith(Constants.Network.AutoConfigAddress);

        /// <summary>
        /// 检查是否为回环地址
        /// </summary>
        public bool IsLoopbackIP => CurrentIP == Constants.Network.LoopbackAddress;

        /// <summary>
        /// 获取完整的网卡信息显示文本
        /// </summary>
        public string GetFullInfoText()
        {
            return $"网卡名称: {Name}\r\n" +
                   $"描述: {Description}\r\n" +
                   $"状态: {StatusText}\r\n" +
                   $"物理地址: {FormatMacAddress(PhysicalAddress)}\r\n" +
                   $"速度: {SpeedText}\r\n" +
                   $"IP地址: {CurrentIP}\r\n" +
                   $"子网掩码: {CurrentSubnetMask}\r\n" +
                   $"默认网关: {CurrentGateway}\r\n" +
                   $"DNS服务器: {DNSText}\r\n" +
                   $"DHCP: {(IsDHCPEnabled ? "已启用" : "已禁用")}";
        }

        /// <summary>
        /// 格式化MAC地址显示
        /// </summary>
        private string FormatMacAddress(string macAddress)
        {
            if (string.IsNullOrEmpty(macAddress) || macAddress.Length != 12)
                return "未知";

            return string.Join("-", 
                Enumerable.Range(0, 6)
                .Select(i => macAddress.Substring(i * 2, 2))
                .ToArray());
        }

        /// <summary>
        /// 检查网卡是否适合显示（排除虚拟网卡等）
        /// </summary>
        public bool IsSuitableForDisplay()
        {
            string name = Name.ToLower();
            string description = Description.ToLower();
            
            // 排除虚拟适配器
            if (name.Contains("virtual") || description.Contains("virtual") ||
                name.Contains("vpn") || description.Contains("vpn") ||
                name.Contains("miniport") || description.Contains("miniport") ||
                name.Contains("loopback") || description.Contains("loopback") ||
                name.Contains("wfp") || description.Contains("wfp") ||
                name.Contains("qos") || description.Contains("qos") ||
                name.Contains("filter") || description.Contains("filter"))
            {
                return false;
            }
            
            // 检查是否包含物理网卡的关键词
            bool isLikelyPhysical = 
                description.Contains("intel") || 
                description.Contains("realtek") || 
                description.Contains("broadcom") ||
                description.Contains("ethernet") ||
                description.Contains("wi-fi") ||
                description.Contains("wireless");
                
            return isLikelyPhysical;
        }
    }
}
