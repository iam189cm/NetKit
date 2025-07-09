using System.Net;
using System.Text.RegularExpressions;
using NETKit.Core.Models;
using NETKit.Common;

namespace NETKit.Core.Helpers
{
    /// <summary>
    /// IP验证结果级别
    /// </summary>
    public enum ValidationLevel
    {
        Success,
        Warning,
        Error
    }

    /// <summary>
    /// IP验证详细结果
    /// </summary>
    public class IPValidationResult
    {
        public ValidationLevel Level { get; set; }
        public string Message { get; set; } = string.Empty;
        public bool IsValid => Level != ValidationLevel.Error;
    }

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
        /// 详细验证IP地址格式，返回验证结果和提示信息
        /// </summary>
        /// <param name="ipAddress">IP地址字符串</param>
        /// <returns>详细验证结果</returns>
        public static IPValidationResult ValidateIPAddressWithDetails(string ipAddress)
        {
            if (string.IsNullOrWhiteSpace(ipAddress))
            {
                return new IPValidationResult { Level = ValidationLevel.Error, Message = "" };
            }

            string trimmed = ipAddress.Trim();

            // 检查基本格式
            if (!IPAddressRegex.IsMatch(trimmed))
            {
                // 检查是否包含非法字符
                if (trimmed.Any(c => !char.IsDigit(c) && c != '.'))
                {
                    return new IPValidationResult { Level = ValidationLevel.Error, Message = "只能包含数字和点" };
                }

                // 检查点的数量
                int dotCount = trimmed.Count(c => c == '.');
                if (dotCount != 3)
                {
                    return new IPValidationResult { Level = ValidationLevel.Error, Message = "IP地址格式不完整" };
                }

                // 检查是否有空段
                string[] parts = trimmed.Split('.');
                if (parts.Any(string.IsNullOrEmpty))
                {
                    return new IPValidationResult { Level = ValidationLevel.Error, Message = "IP地址段不能为空" };
                }

                // 检查每段是否为数字
                foreach (string part in parts)
                {
                    if (!int.TryParse(part, out int value))
                    {
                        return new IPValidationResult { Level = ValidationLevel.Error, Message = "IP地址段必须为数字" };
                    }
                    if (value > 255)
                    {
                        return new IPValidationResult { Level = ValidationLevel.Error, Message = "IP段不能超过255" };
                    }
                }

                return new IPValidationResult { Level = ValidationLevel.Error, Message = "IP地址格式不正确" };
            }

            // 基本格式正确，进行详细检查
            if (!IPAddress.TryParse(trimmed, out IPAddress addr))
            {
                return new IPValidationResult { Level = ValidationLevel.Error, Message = "无效的IP地址" };
            }

            byte[] bytes = addr.GetAddressBytes();

            // 检查特殊IP地址
            if (bytes[0] == 0)
            {
                if (trimmed == "0.0.0.0")
                {
                    return new IPValidationResult { Level = ValidationLevel.Warning, Message = "这是默认路由地址" };
                }
                return new IPValidationResult { Level = ValidationLevel.Error, Message = "无效的IP地址" };
            }

            if (bytes[0] == 127)
            {
                return new IPValidationResult { Level = ValidationLevel.Warning, Message = "这是回环地址" };
            }

            if (bytes[0] >= 224 && bytes[0] <= 239)
            {
                return new IPValidationResult { Level = ValidationLevel.Warning, Message = "这是组播地址" };
            }

            if (bytes[0] >= 240)
            {
                return new IPValidationResult { Level = ValidationLevel.Error, Message = "这是保留地址" };
            }

            if (trimmed == "255.255.255.255")
            {
                return new IPValidationResult { Level = ValidationLevel.Warning, Message = "这是广播地址" };
            }

            // 移除私有IP地址检查警告
            return new IPValidationResult { Level = ValidationLevel.Success, Message = "IP地址有效" };
        }

        /// <summary>
        /// 详细验证子网掩码格式
        /// </summary>
        /// <param name="subnetMask">子网掩码字符串</param>
        /// <returns>详细验证结果</returns>
        public static IPValidationResult ValidateSubnetMaskWithDetails(string subnetMask)
        {
            if (string.IsNullOrWhiteSpace(subnetMask))
            {
                return new IPValidationResult { Level = ValidationLevel.Error, Message = "" };
            }

            string trimmed = subnetMask.Trim();

            // 只检查点分十进制格式 - 不支持CIDR格式
            if (!IsValidIPAddress(trimmed))
            {
                return new IPValidationResult { Level = ValidationLevel.Error, Message = "子网掩码格式不正确" };
            }

            // 验证是否为有效的子网掩码
            if (IPAddress.TryParse(trimmed, out IPAddress mask))
            {
                byte[] bytes = mask.GetAddressBytes();
                uint maskValue = (uint)(bytes[0] << 24 | bytes[1] << 16 | bytes[2] << 8 | bytes[3]);
                
                if (!IsValidSubnetMaskValue(maskValue))
                {
                    return new IPValidationResult { Level = ValidationLevel.Error, Message = "不是有效的子网掩码" };
                }
            }

            return new IPValidationResult { Level = ValidationLevel.Success, Message = "子网掩码有效" };
        }

        /// <summary>
        /// 验证子网掩码格式（支持点分十进制和CIDR位数）
        /// </summary>
        /// <param name="subnetMask">子网掩码字符串</param>
        /// <returns>是否为有效的子网掩码</returns>
        public static bool IsValidSubnetMask(string subnetMask)
        {
            if (string.IsNullOrWhiteSpace(subnetMask))
                return false;

            // 检查是否为CIDR位数格式（如 /24 或 24）
            if (TryParseCIDR(subnetMask, out int cidrBits))
            {
                return cidrBits >= 0 && cidrBits <= 32;
            }

            // 检查是否为点分十进制格式
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
        /// 尝试解析CIDR位数格式
        /// </summary>
        /// <param name="input">输入字符串</param>
        /// <param name="cidrBits">解析出的CIDR位数</param>
        /// <returns>是否解析成功</returns>
        private static bool TryParseCIDR(string input, out int cidrBits)
        {
            cidrBits = 0;
            
            if (string.IsNullOrWhiteSpace(input))
                return false;

            string trimmed = input.Trim();
            
            // 移除可能的前缀斜杠
            if (trimmed.StartsWith("/"))
                trimmed = trimmed.Substring(1);

            return int.TryParse(trimmed, out cidrBits);
        }

        /// <summary>
        /// 将CIDR位数转换为点分十进制子网掩码
        /// </summary>
        /// <param name="cidrBits">CIDR位数</param>
        /// <returns>点分十进制子网掩码</returns>
        public static string CIDRToSubnetMask(int cidrBits)
        {
            if (cidrBits < 0 || cidrBits > 32)
                throw new ArgumentOutOfRangeException(nameof(cidrBits), "CIDR位数必须在0-32之间");

            uint mask = 0;
            if (cidrBits > 0)
            {
                mask = 0xFFFFFFFF << (32 - cidrBits);
            }

            byte[] bytes = new byte[4];
            bytes[0] = (byte)(mask >> 24);
            bytes[1] = (byte)(mask >> 16);
            bytes[2] = (byte)(mask >> 8);
            bytes[3] = (byte)mask;

            return new IPAddress(bytes).ToString();
        }

        /// <summary>
        /// 将点分十进制子网掩码转换为CIDR位数
        /// </summary>
        /// <param name="subnetMask">点分十进制子网掩码</param>
        /// <returns>CIDR位数，失败返回-1</returns>
        public static int SubnetMaskToCIDR(string subnetMask)
        {
            if (!IPAddress.TryParse(subnetMask, out IPAddress mask))
                return -1;

            byte[] bytes = mask.GetAddressBytes();
            uint maskValue = (uint)(bytes[0] << 24 | bytes[1] << 16 | bytes[2] << 8 | bytes[3]);

            // 检查是否为有效的子网掩码
            if (!IsValidSubnetMaskValue(maskValue))
                return -1;

            // 计算连续的1的个数
            int cidrBits = 0;
            for (int i = 31; i >= 0; i--)
            {
                if ((maskValue & (1u << i)) != 0)
                    cidrBits++;
                else
                    break;
            }

            return cidrBits;
        }

        /// <summary>
        /// 标准化子网掩码输入（将CIDR格式转换为点分十进制）
        /// </summary>
        /// <param name="subnetMask">子网掩码输入</param>
        /// <returns>标准化的点分十进制子网掩码</returns>
        public static string NormalizeSubnetMask(string subnetMask)
        {
            if (string.IsNullOrWhiteSpace(subnetMask))
                return string.Empty;

            // 如果是CIDR格式，转换为点分十进制
            if (TryParseCIDR(subnetMask, out int cidrBits))
            {
                if (cidrBits >= 0 && cidrBits <= 32)
                {
                    return CIDRToSubnetMask(cidrBits);
                }
            }

            // 如果已经是点分十进制格式，直接返回
            if (IsValidIPAddress(subnetMask))
            {
                return subnetMask;
            }

            return string.Empty;
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

            // 标准化子网掩码为点分十进制格式进行后续验证
            string normalizedSubnetMask = NormalizeSubnetMask(subnetMask);
            if (string.IsNullOrEmpty(normalizedSubnetMask))
            {
                return ValidationResult.Failure("子网掩码格式不正确");
            }

            // 检查IP地址是否在子网范围内
            if (!string.IsNullOrWhiteSpace(gateway))
            {
                if (!IsIPInSameSubnet(ipAddress, gateway, normalizedSubnetMask))
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
