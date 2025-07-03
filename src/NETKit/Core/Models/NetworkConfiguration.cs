using NETKit.Common;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 网络配置信息类 - 存储网络配置参数
    /// </summary>
    public class NetworkConfiguration
    {
        /// <summary>
        /// 网络适配器名称
        /// </summary>
        public string AdapterName { get; set; } = string.Empty;

        /// <summary>
        /// IP地址
        /// </summary>
        public string IPAddress { get; set; } = string.Empty;

        /// <summary>
        /// 子网掩码
        /// </summary>
        public string SubnetMask { get; set; } = Constants.Network.DefaultSubnetMask;

        /// <summary>
        /// 默认网关
        /// </summary>
        public string Gateway { get; set; } = string.Empty;

        /// <summary>
        /// 主DNS服务器
        /// </summary>
        public string PrimaryDNS { get; set; } = Constants.Network.DefaultDNS;

        /// <summary>
        /// 备用DNS服务器
        /// </summary>
        public string SecondaryDNS { get; set; } = Constants.Network.DefaultSecondaryDNS;

        /// <summary>
        /// 是否使用DHCP
        /// </summary>
        public bool UseDHCP { get; set; } = false;

        /// <summary>
        /// 配置名称（用于保存配置时的标识）
        /// </summary>
        public string ConfigurationName { get; set; } = string.Empty;

        /// <summary>
        /// 配置描述
        /// </summary>
        public string Description { get; set; } = string.Empty;

        /// <summary>
        /// 创建时间
        /// </summary>
        public DateTime CreatedTime { get; set; } = DateTime.Now;

        /// <summary>
        /// 最后修改时间
        /// </summary>
        public DateTime LastModifiedTime { get; set; } = DateTime.Now;

        /// <summary>
        /// 构造函数
        /// </summary>
        public NetworkConfiguration()
        {
        }

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="adapterName">网络适配器名称</param>
        public NetworkConfiguration(string adapterName)
        {
            AdapterName = adapterName;
        }

        /// <summary>
        /// 构造函数 - 静态IP配置
        /// </summary>
        /// <param name="adapterName">网络适配器名称</param>
        /// <param name="ipAddress">IP地址</param>
        /// <param name="subnetMask">子网掩码</param>
        /// <param name="gateway">网关</param>
        /// <param name="dns">DNS服务器</param>
        public NetworkConfiguration(string adapterName, string ipAddress, string subnetMask, string gateway, string dns)
        {
            AdapterName = adapterName;
            IPAddress = ipAddress;
            SubnetMask = subnetMask;
            Gateway = gateway;
            PrimaryDNS = dns;
            UseDHCP = false;
        }

        /// <summary>
        /// 创建DHCP配置
        /// </summary>
        /// <param name="adapterName">网络适配器名称</param>
        /// <returns>DHCP配置实例</returns>
        public static NetworkConfiguration CreateDHCPConfig(string adapterName)
        {
            return new NetworkConfiguration
            {
                AdapterName = adapterName,
                UseDHCP = true,
                ConfigurationName = "DHCP自动配置",
                Description = "使用DHCP自动获取IP地址"
            };
        }

        /// <summary>
        /// 创建静态IP配置
        /// </summary>
        /// <param name="adapterName">网络适配器名称</param>
        /// <param name="ipAddress">IP地址</param>
        /// <param name="subnetMask">子网掩码</param>
        /// <param name="gateway">网关</param>
        /// <param name="dns">DNS服务器</param>
        /// <returns>静态IP配置实例</returns>
        public static NetworkConfiguration CreateStaticConfig(string adapterName, string ipAddress, 
            string subnetMask, string gateway, string dns)
        {
            return new NetworkConfiguration
            {
                AdapterName = adapterName,
                IPAddress = ipAddress,
                SubnetMask = subnetMask,
                Gateway = gateway,
                PrimaryDNS = dns,
                UseDHCP = false,
                ConfigurationName = $"静态IP配置 - {ipAddress}",
                Description = $"静态IP地址配置：{ipAddress}/{subnetMask}"
            };
        }

        /// <summary>
        /// 验证配置是否有效
        /// </summary>
        /// <returns>验证结果</returns>
        public ValidationResult Validate()
        {
            if (string.IsNullOrWhiteSpace(AdapterName))
            {
                return new ValidationResult(false, "网络适配器名称不能为空");
            }

            if (UseDHCP)
            {
                return new ValidationResult(true, "DHCP配置验证通过");
            }

            // 静态IP配置验证
            if (string.IsNullOrWhiteSpace(IPAddress))
            {
                return new ValidationResult(false, "IP地址不能为空");
            }

            if (string.IsNullOrWhiteSpace(SubnetMask))
            {
                return new ValidationResult(false, "子网掩码不能为空");
            }

            if (!System.Net.IPAddress.TryParse(IPAddress, out _))
            {
                return new ValidationResult(false, "IP地址格式不正确");
            }

            if (!System.Net.IPAddress.TryParse(SubnetMask, out _))
            {
                return new ValidationResult(false, "子网掩码格式不正确");
            }

            if (!string.IsNullOrWhiteSpace(Gateway) && !System.Net.IPAddress.TryParse(Gateway, out _))
            {
                return new ValidationResult(false, "网关地址格式不正确");
            }

            if (!string.IsNullOrWhiteSpace(PrimaryDNS) && !System.Net.IPAddress.TryParse(PrimaryDNS, out _))
            {
                return new ValidationResult(false, "主DNS服务器地址格式不正确");
            }

            if (!string.IsNullOrWhiteSpace(SecondaryDNS) && !System.Net.IPAddress.TryParse(SecondaryDNS, out _))
            {
                return new ValidationResult(false, "备用DNS服务器地址格式不正确");
            }

            return new ValidationResult(true, "配置验证通过");
        }

        /// <summary>
        /// 克隆配置
        /// </summary>
        /// <returns>克隆的配置实例</returns>
        public NetworkConfiguration Clone()
        {
            return new NetworkConfiguration
            {
                AdapterName = AdapterName,
                IPAddress = IPAddress,
                SubnetMask = SubnetMask,
                Gateway = Gateway,
                PrimaryDNS = PrimaryDNS,
                SecondaryDNS = SecondaryDNS,
                UseDHCP = UseDHCP,
                ConfigurationName = ConfigurationName,
                Description = Description,
                CreatedTime = CreatedTime,
                LastModifiedTime = DateTime.Now
            };
        }

        /// <summary>
        /// 获取配置摘要
        /// </summary>
        /// <returns>配置摘要文本</returns>
        public string GetSummary()
        {
            if (UseDHCP)
            {
                return $"DHCP自动配置 - {AdapterName}";
            }

            return $"静态IP: {IPAddress}/{SubnetMask} - {AdapterName}";
        }

        /// <summary>
        /// 重写ToString方法
        /// </summary>
        /// <returns>配置的字符串表示</returns>
        public override string ToString()
        {
            return GetSummary();
        }
    }

    /// <summary>
    /// 验证结果类
    /// </summary>
    public class ValidationResult
    {
        /// <summary>
        /// 是否验证通过
        /// </summary>
        public bool IsValid { get; }

        /// <summary>
        /// 验证消息
        /// </summary>
        public string Message { get; }

        /// <summary>
        /// 构造函数
        /// </summary>
        /// <param name="isValid">是否验证通过</param>
        /// <param name="message">验证消息</param>
        public ValidationResult(bool isValid, string message)
        {
            IsValid = isValid;
            Message = message;
        }

        /// <summary>
        /// 创建成功的验证结果
        /// </summary>
        /// <param name="message">消息</param>
        /// <returns>验证结果</returns>
        public static ValidationResult Success(string message = "验证通过")
        {
            return new ValidationResult(true, message);
        }

        /// <summary>
        /// 创建失败的验证结果
        /// </summary>
        /// <param name="message">错误消息</param>
        /// <returns>验证结果</returns>
        public static ValidationResult Failure(string message)
        {
            return new ValidationResult(false, message);
        }
    }
}
