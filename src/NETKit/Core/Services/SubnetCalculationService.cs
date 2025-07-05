using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using NETKit.Core.Models;

namespace NETKit.Core.Services
{
    /// <summary>
    /// 子网计算服务
    /// </summary>
    public class SubnetCalculationService
    {
        /// <summary>
        /// 计算子网信息
        /// </summary>
        /// <param name="ipAddress">IP地址</param>
        /// <param name="subnetMask">子网掩码</param>
        /// <returns>子网计算结果</returns>
        public SubnetCalculationResult CalculateSubnet(string ipAddress, string subnetMask)
        {
            var result = new SubnetCalculationResult();

            try
            {
                // 验证并解析IP地址
                if (!IPAddress.TryParse(ipAddress, out IPAddress ip))
                {
                    result.ErrorMessage = "无效的IP地址格式";
                    return result;
                }

                // 验证并解析子网掩码
                if (!IPAddress.TryParse(subnetMask, out IPAddress mask))
                {
                    result.ErrorMessage = "无效的子网掩码格式";
                    return result;
                }

                // 验证子网掩码的有效性
                if (!IsValidSubnetMask(mask))
                {
                    result.ErrorMessage = "无效的子网掩码";
                    return result;
                }

                return CalculateSubnetInternal(ip, mask);
            }
            catch (Exception ex)
            {
                result.ErrorMessage = $"计算过程中发生错误: {ex.Message}";
                return result;
            }
        }

        /// <summary>
        /// 使用CIDR表示法计算子网信息
        /// </summary>
        /// <param name="cidrNotation">CIDR表示法 (如: 192.168.1.0/24)</param>
        /// <returns>子网计算结果</returns>
        public SubnetCalculationResult CalculateSubnetFromCIDR(string cidrNotation)
        {
            var result = new SubnetCalculationResult();

            try
            {
                var parts = cidrNotation.Split('/');
                if (parts.Length != 2)
                {
                    result.ErrorMessage = "无效的CIDR格式，应为 IP地址/前缀长度";
                    return result;
                }

                if (!IPAddress.TryParse(parts[0], out IPAddress ip))
                {
                    result.ErrorMessage = "无效的IP地址格式";
                    return result;
                }

                if (!int.TryParse(parts[1], out int prefixLength) || prefixLength < 0 || prefixLength > 32)
                {
                    result.ErrorMessage = "无效的前缀长度，应为0-32之间的整数";
                    return result;
                }

                var mask = PrefixLengthToSubnetMask(prefixLength);
                return CalculateSubnetInternal(ip, mask);
            }
            catch (Exception ex)
            {
                result.ErrorMessage = $"计算过程中发生错误: {ex.Message}";
                return result;
            }
        }

        /// <summary>
        /// 子网划分
        /// </summary>
        /// <param name="networkAddress">网络地址</param>
        /// <param name="currentPrefixLength">当前前缀长度</param>
        /// <param name="subnetCount">需要的子网数量</param>
        /// <returns>划分后的子网列表</returns>
        public List<SubnetInfo> SubdivideNetwork(string networkAddress, int currentPrefixLength, int subnetCount)
        {
            var subnets = new List<SubnetInfo>();

            try
            {
                if (!IPAddress.TryParse(networkAddress, out IPAddress network))
                {
                    return subnets;
                }

                // 计算需要的位数
                int bitsNeeded = (int)Math.Ceiling(Math.Log2(subnetCount));
                int newPrefixLength = currentPrefixLength + bitsNeeded;

                if (newPrefixLength > 30) // 最多到/30，保证每个子网至少有2个可用主机
                {
                    return subnets;
                }

                // 计算子网大小
                long subnetSize = 1L << (32 - newPrefixLength);
                uint networkInt = IPAddressToUInt(network);

                for (int i = 0; i < subnetCount; i++)
                {
                    uint subnetNetworkInt = networkInt + (uint)(i * subnetSize);
                    var subnetNetwork = UIntToIPAddress(subnetNetworkInt);
                    var subnetMask = PrefixLengthToSubnetMask(newPrefixLength);

                    var subnetResult = CalculateSubnetInternal(subnetNetwork, subnetMask);
                    if (subnetResult.IsValid)
                    {
                        var subnetInfo = new SubnetInfo
                        {
                            Name = $"子网 {i + 1}",
                            NetworkAddress = subnetResult.NetworkAddress,
                            PrefixLength = newPrefixLength,
                            SubnetMask = subnetResult.SubnetMask,
                            BroadcastAddress = subnetResult.BroadcastAddress,
                            FirstUsableIP = subnetResult.FirstUsableIP,
                            LastUsableIP = subnetResult.LastUsableIP,
                            UsableHostCount = subnetResult.UsableHostCount
                        };
                        subnets.Add(subnetInfo);
                    }
                }
            }
            catch (Exception)
            {
                // 返回空列表
            }

            return subnets;
        }

        /// <summary>
        /// VLSM计算
        /// </summary>
        /// <param name="networkAddress">网络地址</param>
        /// <param name="currentPrefixLength">当前前缀长度</param>
        /// <param name="requirements">VLSM需求列表</param>
        /// <returns>分配结果</returns>
        public List<VLSMRequirement> CalculateVLSM(string networkAddress, int currentPrefixLength, List<VLSMRequirement> requirements)
        {
            var result = new List<VLSMRequirement>();

            try
            {
                if (!IPAddress.TryParse(networkAddress, out IPAddress network))
                {
                    return result;
                }

                // 按需要的主机数量降序排序（大的子网先分配）
                var sortedRequirements = requirements.OrderByDescending(r => r.RequiredHosts).ToList();
                
                uint currentNetworkInt = IPAddressToUInt(network);
                uint networkMaskInt = IPAddressToUInt(PrefixLengthToSubnetMask(currentPrefixLength));
                uint networkBaseInt = currentNetworkInt & networkMaskInt;
                uint availableSpace = ~networkMaskInt + 1;

                foreach (var requirement in sortedRequirements)
                {
                    requirement.CalculatePrefixLength();
                    
                    if (requirement.CalculatedPrefixLength < currentPrefixLength)
                    {
                        // 需要的子网比当前网络还大，无法分配
                        continue;
                    }

                    // 计算子网大小
                    uint subnetSize = (uint)(1L << (32 - requirement.CalculatedPrefixLength));
                    
                    // 检查是否还有足够空间
                    if (currentNetworkInt + subnetSize <= networkBaseInt + availableSpace)
                    {
                        var subnetNetwork = UIntToIPAddress(currentNetworkInt);
                        var subnetMask = PrefixLengthToSubnetMask(requirement.CalculatedPrefixLength);
                        
                        var subnetResult = CalculateSubnetInternal(subnetNetwork, subnetMask);
                        if (subnetResult.IsValid)
                        {
                            requirement.AllocatedSubnet = new SubnetInfo
                            {
                                Name = requirement.Name,
                                NetworkAddress = subnetResult.NetworkAddress,
                                PrefixLength = requirement.CalculatedPrefixLength,
                                SubnetMask = subnetResult.SubnetMask,
                                BroadcastAddress = subnetResult.BroadcastAddress,
                                FirstUsableIP = subnetResult.FirstUsableIP,
                                LastUsableIP = subnetResult.LastUsableIP,
                                UsableHostCount = subnetResult.UsableHostCount,
                                IsAllocated = true
                            };
                            requirement.IsAllocated = true;
                            
                            // 移动到下一个可用地址
                            currentNetworkInt += subnetSize;
                        }
                    }
                    
                    result.Add(requirement);
                }
            }
            catch (Exception)
            {
                // 返回部分结果
            }

            return result;
        }

        /// <summary>
        /// 检查IP地址是否在指定子网内
        /// </summary>
        /// <param name="ipAddress">要检查的IP地址</param>
        /// <param name="networkAddress">网络地址</param>
        /// <param name="subnetMask">子网掩码</param>
        /// <returns>是否在子网内</returns>
        public bool IsIPInSubnet(string ipAddress, string networkAddress, string subnetMask)
        {
            try
            {
                if (!IPAddress.TryParse(ipAddress, out IPAddress ip) ||
                    !IPAddress.TryParse(networkAddress, out IPAddress network) ||
                    !IPAddress.TryParse(subnetMask, out IPAddress mask))
                {
                    return false;
                }

                var ipBytes = ip.GetAddressBytes();
                var networkBytes = network.GetAddressBytes();
                var maskBytes = mask.GetAddressBytes();

                for (int i = 0; i < 4; i++)
                {
                    if ((ipBytes[i] & maskBytes[i]) != (networkBytes[i] & maskBytes[i]))
                        return false;
                }

                return true;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// 内部子网计算方法
        /// </summary>
        private SubnetCalculationResult CalculateSubnetInternal(IPAddress ipAddress, IPAddress subnetMask)
        {
            var result = new SubnetCalculationResult
            {
                InputIPAddress = ipAddress,
                SubnetMask = subnetMask,
                PrefixLength = SubnetMaskToPrefixLength(subnetMask)
            };

            // 计算网络地址
            result.NetworkAddress = GetNetworkAddress(ipAddress, subnetMask);
            
            // 计算广播地址
            result.BroadcastAddress = GetBroadcastAddress(result.NetworkAddress, subnetMask);
            
            // 计算主机数量
            int hostBits = 32 - result.PrefixLength;
            result.TotalHostCount = 1L << hostBits;
            result.UsableHostCount = Math.Max(0, result.TotalHostCount - 2);
            
            // 计算可用主机范围
            if (result.UsableHostCount > 0)
            {
                result.FirstUsableIP = GetNextIP(result.NetworkAddress);
                result.LastUsableIP = GetPreviousIP(result.BroadcastAddress);
            }
            else
            {
                result.FirstUsableIP = result.NetworkAddress;
                result.LastUsableIP = result.NetworkAddress;
            }

            // 网络类别和地址类型
            result.NetworkClass = GetNetworkClass(ipAddress);
            result.IsPrivateAddress = IsPrivateAddress(ipAddress);
            result.AddressType = GetAddressType(ipAddress);

            // 二进制表示
            result.IPAddressBinary = IPAddressToBinary(ipAddress);
            result.SubnetMaskBinary = IPAddressToBinary(subnetMask);

            result.IsValid = true;
            return result;
        }

        /// <summary>
        /// 验证子网掩码是否有效
        /// </summary>
        private bool IsValidSubnetMask(IPAddress mask)
        {
            uint maskInt = IPAddressToUInt(mask);
            
            // 检查是否为连续的1后跟连续的0
            uint inverted = ~maskInt;
            return (inverted & (inverted + 1)) == 0;
        }

        /// <summary>
        /// 前缀长度转换为子网掩码
        /// </summary>
        private IPAddress PrefixLengthToSubnetMask(int prefixLength)
        {
            if (prefixLength < 0 || prefixLength > 32)
                throw new ArgumentException("前缀长度必须在0-32之间");

            uint mask = prefixLength == 0 ? 0 : (0xFFFFFFFF << (32 - prefixLength));
            return UIntToIPAddress(mask);
        }

        /// <summary>
        /// 子网掩码转换为前缀长度
        /// </summary>
        private int SubnetMaskToPrefixLength(IPAddress mask)
        {
            uint maskInt = IPAddressToUInt(mask);
            int prefixLength = 0;
            
            while ((maskInt & 0x80000000) != 0)
            {
                prefixLength++;
                maskInt <<= 1;
            }
            
            return prefixLength;
        }

        /// <summary>
        /// 获取网络地址
        /// </summary>
        private IPAddress GetNetworkAddress(IPAddress ipAddress, IPAddress subnetMask)
        {
            uint ipInt = IPAddressToUInt(ipAddress);
            uint maskInt = IPAddressToUInt(subnetMask);
            return UIntToIPAddress(ipInt & maskInt);
        }

        /// <summary>
        /// 获取广播地址
        /// </summary>
        private IPAddress GetBroadcastAddress(IPAddress networkAddress, IPAddress subnetMask)
        {
            uint networkInt = IPAddressToUInt(networkAddress);
            uint maskInt = IPAddressToUInt(subnetMask);
            return UIntToIPAddress(networkInt | ~maskInt);
        }

        /// <summary>
        /// 获取下一个IP地址
        /// </summary>
        private IPAddress GetNextIP(IPAddress ipAddress)
        {
            uint ipInt = IPAddressToUInt(ipAddress);
            return UIntToIPAddress(ipInt + 1);
        }

        /// <summary>
        /// 获取上一个IP地址
        /// </summary>
        private IPAddress GetPreviousIP(IPAddress ipAddress)
        {
            uint ipInt = IPAddressToUInt(ipAddress);
            return UIntToIPAddress(ipInt - 1);
        }

        /// <summary>
        /// 获取网络类别
        /// </summary>
        private string GetNetworkClass(IPAddress ipAddress)
        {
            byte firstOctet = ipAddress.GetAddressBytes()[0];
            
            if (firstOctet >= 1 && firstOctet <= 126)
                return "A类网络";
            else if (firstOctet >= 128 && firstOctet <= 191)
                return "B类网络";
            else if (firstOctet >= 192 && firstOctet <= 223)
                return "C类网络";
            else if (firstOctet >= 224 && firstOctet <= 239)
                return "D类网络(组播)";
            else if (firstOctet >= 240 && firstOctet <= 255)
                return "E类网络(保留)";
            else
                return "未知类别";
        }

        /// <summary>
        /// 检查是否为私有地址
        /// </summary>
        private bool IsPrivateAddress(IPAddress ipAddress)
        {
            byte[] bytes = ipAddress.GetAddressBytes();
            
            // 10.0.0.0/8
            if (bytes[0] == 10)
                return true;
            
            // 172.16.0.0/12
            if (bytes[0] == 172 && bytes[1] >= 16 && bytes[1] <= 31)
                return true;
            
            // 192.168.0.0/16
            if (bytes[0] == 192 && bytes[1] == 168)
                return true;
            
            return false;
        }

        /// <summary>
        /// 获取地址类型
        /// </summary>
        private string GetAddressType(IPAddress ipAddress)
        {
            var types = new List<string>();
            
            if (IsPrivateAddress(ipAddress))
                types.Add("私有地址");
            else
                types.Add("公有地址");
            
            byte firstOctet = ipAddress.GetAddressBytes()[0];
            if (firstOctet >= 224 && firstOctet <= 239)
                types.Add("组播地址");
            else
                types.Add("单播地址");
            
            return string.Join(" | ", types);
        }

        /// <summary>
        /// IP地址转换为二进制字符串
        /// </summary>
        private string IPAddressToBinary(IPAddress ipAddress)
        {
            var bytes = ipAddress.GetAddressBytes();
            var binary = new StringBuilder();
            
            for (int i = 0; i < bytes.Length; i++)
            {
                if (i > 0) binary.Append(".");
                binary.Append(Convert.ToString(bytes[i], 2).PadLeft(8, '0'));
            }
            
            return binary.ToString();
        }

        /// <summary>
        /// IP地址转换为无符号整数
        /// </summary>
        private uint IPAddressToUInt(IPAddress ipAddress)
        {
            var bytes = ipAddress.GetAddressBytes();
            if (BitConverter.IsLittleEndian)
                Array.Reverse(bytes);
            return BitConverter.ToUInt32(bytes, 0);
        }

        /// <summary>
        /// 无符号整数转换为IP地址
        /// </summary>
        private IPAddress UIntToIPAddress(uint ipInt)
        {
            var bytes = BitConverter.GetBytes(ipInt);
            if (BitConverter.IsLittleEndian)
                Array.Reverse(bytes);
            return new IPAddress(bytes);
        }
    }
}
