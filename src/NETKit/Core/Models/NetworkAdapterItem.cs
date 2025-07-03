namespace NETKit.Core.Models
{
    /// <summary>
    /// 网络适配器项目类 - 用于下拉框显示的数据模型
    /// </summary>
    public class NetworkAdapterItem
    {
        /// <summary>
        /// 网卡名称
        /// </summary>
        public string Name { get; set; } = string.Empty;
        
        /// <summary>
        /// 网卡描述
        /// </summary>
        public string Description { get; set; } = string.Empty;
        
        /// <summary>
        /// 显示名称（名称 + 描述）
        /// </summary>
        public string DisplayName { get; set; } = string.Empty;
        
        /// <summary>
        /// 是否为物理网卡
        /// </summary>
        public bool IsPhysical { get; set; } = true;
        
        /// <summary>
        /// 是否已连接
        /// </summary>
        public bool IsConnected { get; set; } = false;
        
        /// <summary>
        /// 网卡类型
        /// </summary>
        public string InterfaceType { get; set; } = string.Empty;

        /// <summary>
        /// 构造函数
        /// </summary>
        public NetworkAdapterItem()
        {
        }

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="name">网卡名称</param>
        /// <param name="description">网卡描述</param>
        public NetworkAdapterItem(string name, string description)
        {
            Name = name;
            Description = description;
            DisplayName = $"{name} ({description})";
        }

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="name">网卡名称</param>
        /// <param name="description">网卡描述</param>
        /// <param name="isPhysical">是否为物理网卡</param>
        /// <param name="isConnected">是否已连接</param>
        public NetworkAdapterItem(string name, string description, bool isPhysical, bool isConnected)
        {
            Name = name;
            Description = description;
            DisplayName = $"{name} ({description})";
            IsPhysical = isPhysical;
            IsConnected = isConnected;
        }

        /// <summary>
        /// 重写ToString方法，用于下拉框显示
        /// </summary>
        /// <returns>显示名称</returns>
        public override string ToString()
        {
            return DisplayName;
        }

        /// <summary>
        /// 重写Equals方法
        /// </summary>
        /// <param name="obj">比较对象</param>
        /// <returns>是否相等</returns>
        public override bool Equals(object? obj)
        {
            if (obj is NetworkAdapterItem other)
            {
                return Name.Equals(other.Name, StringComparison.OrdinalIgnoreCase);
            }
            return false;
        }

        /// <summary>
        /// 重写GetHashCode方法
        /// </summary>
        /// <returns>哈希码</returns>
        public override int GetHashCode()
        {
            return Name.ToLowerInvariant().GetHashCode();
        }

        /// <summary>
        /// 获取简短的显示名称
        /// </summary>
        public string GetShortDisplayName()
        {
            if (Description.Length > 30)
            {
                return $"{Name} ({Description.Substring(0, 27)}...)";
            }
            return DisplayName;
        }

        /// <summary>
        /// 检查是否为以太网适配器
        /// </summary>
        public bool IsEthernet()
        {
            return InterfaceType.Contains("Ethernet", StringComparison.OrdinalIgnoreCase) ||
                   Description.Contains("Ethernet", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// 检查是否为无线网络适配器
        /// </summary>
        public bool IsWireless()
        {
            return InterfaceType.Contains("Wireless", StringComparison.OrdinalIgnoreCase) ||
                   Description.Contains("Wi-Fi", StringComparison.OrdinalIgnoreCase) ||
                   Description.Contains("Wireless", StringComparison.OrdinalIgnoreCase);
        }
    }
}
