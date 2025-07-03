using System.Net;
using System.Text.RegularExpressions;
using NETKit.Core.Models;
using NETKit.Common;

namespace NETKit.Core.Helpers
{
    /// <summary>
    /// 验证辅助类 - 负责输入验证逻辑
    /// </summary>
    public static class ValidationHelper
    {
        /// <summary>
        /// IP地址验证的正则表达式
        /// </summary>
        private static readonly Regex IPAddressRegex = new Regex(
            @"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
            RegexOptions.Compiled);

        /// <summary>
        /// 验证IP地址格式
        /// </summary>
        /// <param name="ipAddress">IP地址字符串</param>
        /// <returns>是否为有效的IP地址</returns>
        public static bool IsValidIPAddress(string ipAddress)
        {
            if (string.IsNullOrWhiteSpace(ipAddress))
                return false;

            return IPAddress.TryParse(ipAddress, out _) && IPAddressRegex.IsMatch(ipAddress);
        }

        /// <summary>
        /// 验证子网掩码格式
        /// </summary>
        /// <param name="subnetMask">子网掩码字符串</param>
        /// <returns>是否为有效的子网掩码</returns>
        public static bool IsValidSubnetMask(string subnetMask)
        {
            if (!IsValidIPAddress(subnetMask))
                return false;

            if (IPAddress.TryParse(subnetMask, out IPAddress mask))
            {
                byte[] bytes = mask.GetAddressBytes();
                uint maskValue = (uint)(bytes[0] << 24 | bytes[1] << 16 | bytes[2] << 8 | bytes[3]);
                
                // 检查是否为有效的子网掩码（连续的1后跟连续的0）
                return IsValidSubnetMaskValue(maskValue);
            }

            return false;
        }

        /// <summary>
        /// 检查子网掩码值是否有效
        /// </summary>
        /// <param name="maskValue">子网掩码数值</param>
        /// <returns>是否有效</returns>
        private static bool IsValidSubnetMaskValue(uint maskValue)
        {
            // 反转位，检查是否为连续的1后跟连续的0
            uint inverted = ~maskValue;
            return (inverted & (inverted + 1)) == 0;
        }

        /// <summary>
        /// 验证网络配置输入
        /// </summary>
        /// <param name="selectedAdapter">选中的网络适配器</param>
        /// <param name="ipAddress">IP地址</param>
        /// <param name="subnetMask">子网掩码</param>
        /// <param name="gateway">网关地址</param>
        /// <param name="dnsServer">DNS服务器地址</param>
        /// <returns>验证结果</returns>
        public static ValidationResult ValidateNetworkConfig(string? selectedAdapter, string ipAddress, 
            string subnetMask, string? gateway = null, string? dnsServer = null)
        {
            if (string.IsNullOrWhiteSpace(selectedAdapter))
            {
                return ValidationResult.Failure("请选择网络适配器");
            }

            if (string.IsNullOrWhiteSpace(ipAddress))
            {
                return ValidationResult.Failure("请输入IP地址");
            }

            if (string.IsNullOrWhiteSpace(subnetMask))
            {
                return ValidationResult.Failure("请输入子网掩码");
            }

            if (!IsValidIPAddress(ipAddress))
            {
                return ValidationResult.Failure("IP地址格式不正确");
            }

            if (!IsValidSubnetMask(subnetMask))
            {
                return ValidationResult.Failure("子网掩码格式不正确");
            }

            if (!string.IsNullOrWhiteSpace(gateway) && !IsValidIPAddress(gateway))
            {
                return ValidationResult.Failure("网关地址格式不正确");
            }

            if (!string.IsNullOrWhiteSpace(dnsServer) && !IsValidIPAddress(dnsServer))
            {
                return ValidationResult.Failure("DNS服务器地址格式不正确");
            }

            // 检查IP地址是否在子网范围内
            if (!string.IsNullOrWhiteSpace(gateway))
            {
                if (!IsIPInSameSubnet(ipAddress, gateway, subnetMask))
                {
                    return ValidationResult.Failure("网关地址与IP地址不在同一子网内");
                }
            }

            // 检查是否为私有IP地址范围 - 改为警告而不是阻止
            // 注释掉强制检查，允许用户使用公网IP地址
            /*
            if (!IsPrivateIPAddress(ipAddress))
            {
                return ValidationResult.Failure("建议使用私有IP地址范围（如192.168.x.x、10.x.x.x、172.16-31.x.x）");
            }
            */

            return ValidationResult.Success("验证通过");
        }

        /// <summary>
        /// 验证网络配置对象
        /// </summary>
        /// <param name="config">网络配置对象</param>
        /// <returns>验证结果</returns>
        public static ValidationResult ValidateNetworkConfiguration(NetworkConfiguration config)
        {
            if (config == null)
            {
                return ValidationResult.Failure("配置对象不能为空");
            }

            if (config.UseDHCP)
            {
                return ValidateDHCPConfiguration(config);
            }
            else
            {
                return ValidateStaticConfiguration(config);
            }
        }

        /// <summary>
        /// 验证DHCP配置
        /// </summary>
        /// <param name="config">网络配置</param>
        /// <returns>验证结果</returns>
        private static ValidationResult ValidateDHCPConfiguration(NetworkConfiguration config)
        {
            if (string.IsNullOrWhiteSpace(config.AdapterName))
            {
                return ValidationResult.Failure("网络适配器名称不能为空");
            }

            return ValidationResult.Success("DHCP配置验证通过");
        }

        /// <summary>
        /// 验证静态IP配置
        /// </summary>
        /// <param name="config">网络配置</param>
        /// <returns>验证结果</returns>
        private static ValidationResult ValidateStaticConfiguration(NetworkConfiguration config)
        {
            return ValidateNetworkConfig(
                config.AdapterName,
                config.IPAddress,
                config.SubnetMask,
                config.Gateway,
                config.PrimaryDNS
            );
        }

        /// <summary>
        /// 检查两个IP地址是否在同一子网内
        /// </summary>
        /// <param name="ip1">IP地址1</param>
        /// <param name="ip2">IP地址2</param>
        /// <param name="subnetMask">子网掩码</param>
        /// <returns>是否在同一子网</returns>
        public static bool IsIPInSameSubnet(string ip1, string ip2, string subnetMask)
        {
            try
            {
                if (!IPAddress.TryParse(ip1, out IPAddress addr1) ||
                    !IPAddress.TryParse(ip2, out IPAddress addr2) ||
                    !IPAddress.TryParse(subnetMask, out IPAddress mask))
                {
                    return false;
                }

                byte[] ip1Bytes = addr1.GetAddressBytes();
                byte[] ip2Bytes = addr2.GetAddressBytes();
                byte[] maskBytes = mask.GetAddressBytes();

                for (int i = 0; i < 4; i++)
                {
                    if ((ip1Bytes[i] & maskBytes[i]) != (ip2Bytes[i] & maskBytes[i]))
                    {
                        return false;
                    }
                }

                return true;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// 检查是否为私有IP地址
        /// </summary>
        /// <param name="ipAddress">IP地址</param>
        /// <returns>是否为私有IP地址</returns>
        public static bool IsPrivateIPAddress(string ipAddress)
        {
            if (!IPAddress.TryParse(ipAddress, out IPAddress addr))
                return false;

            byte[] bytes = addr.GetAddressBytes();
            
            // 10.0.0.0 - 10.255.255.255
            if (bytes[0] == 10)
                return true;
            
            // 172.16.0.0 - 172.31.255.255
            if (bytes[0] == 172 && bytes[1] >= 16 && bytes[1] <= 31)
                return true;
            
            // 192.168.0.0 - 192.168.255.255
            if (bytes[0] == 192 && bytes[1] == 168)
                return true;
            
            return false;
        }

        /// <summary>
        /// 验证网络适配器名称
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>验证结果</returns>
        public static ValidationResult ValidateAdapterName(string adapterName)
        {
            if (string.IsNullOrWhiteSpace(adapterName))
            {
                return ValidationResult.Failure("网络适配器名称不能为空");
            }

            if (adapterName.Length > 255)
            {
                return ValidationResult.Failure("网络适配器名称过长");
            }

            return ValidationResult.Success("适配器名称验证通过");
        }

        /// <summary>
        /// 获取IP地址的网络部分
        /// </summary>
        /// <param name="ipAddress">IP地址</param>
        /// <param name="subnetMask">子网掩码</param>
        /// <returns>网络地址</returns>
        public static string GetNetworkAddress(string ipAddress, string subnetMask)
        {
            try
            {
                if (IPAddress.TryParse(ipAddress, out IPAddress ip) && 
                    IPAddress.TryParse(subnetMask, out IPAddress mask))
                {
                    byte[] ipBytes = ip.GetAddressBytes();
                    byte[] maskBytes = mask.GetAddressBytes();
                    byte[] networkBytes = new byte[4];

                    for (int i = 0; i < 4; i++)
                    {
                        networkBytes[i] = (byte)(ipBytes[i] & maskBytes[i]);
                    }

                    return new IPAddress(networkBytes).ToString();
                }
            }
            catch
            {
                // 忽略错误
            }

            return string.Empty;
        }

        /// <summary>
        /// 检查IP地址范围是否冲突
        /// </summary>
        /// <param name="config1">配置1</param>
        /// <param name="config2">配置2</param>
        /// <returns>是否冲突</returns>
        public static bool HasIPConflict(NetworkConfiguration config1, NetworkConfiguration config2)
        {
            if (config1.UseDHCP || config2.UseDHCP)
                return false;

            return config1.IPAddress.Equals(config2.IPAddress, StringComparison.OrdinalIgnoreCase);
        }
    }
}
