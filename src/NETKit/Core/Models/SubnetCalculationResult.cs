using System.Net;

namespace NETKit.Core.Models
{
    /// <summary>
    /// 子网计算结果模型
    /// </summary>
    public class SubnetCalculationResult
    {
        /// <summary>
        /// 输入的IP地址
        /// </summary>
        public IPAddress InputIPAddress { get; set; }

        /// <summary>
        /// 子网掩码
        /// </summary>
        public IPAddress SubnetMask { get; set; }

        /// <summary>
        /// CIDR前缀长度
        /// </summary>
        public int PrefixLength { get; set; }

        /// <summary>
        /// 网络地址
        /// </summary>
        public IPAddress NetworkAddress { get; set; }

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
        /// 总主机数量（包括网络地址和广播地址）
        /// </summary>
        public long TotalHostCount { get; set; }

        /// <summary>
        /// 网络类别（A、B、C类）
        /// </summary>
        public string NetworkClass { get; set; }

        /// <summary>
        /// 是否为私有地址
        /// </summary>
        public bool IsPrivateAddress { get; set; }

        /// <summary>
        /// 地址类型描述
        /// </summary>
        public string AddressType { get; set; }

        /// <summary>
        /// IP地址的二进制表示
        /// </summary>
        public string IPAddressBinary { get; set; }

        /// <summary>
        /// 子网掩码的二进制表示
        /// </summary>
        public string SubnetMaskBinary { get; set; }

        /// <summary>
        /// 是否为有效的计算结果
        /// </summary>
        public bool IsValid { get; set; }

        /// <summary>
        /// 错误信息（如果计算失败）
        /// </summary>
        public string ErrorMessage { get; set; }

        public SubnetCalculationResult()
        {
            IsValid = false;
            ErrorMessage = string.Empty;
            NetworkClass = string.Empty;
            AddressType = string.Empty;
            IPAddressBinary = string.Empty;
            SubnetMaskBinary = string.Empty;
        }

        /// <summary>
        /// 获取格式化的结果文本
        /// </summary>
        /// <returns>格式化的计算结果</returns>
        public string GetFormattedResult()
        {
            if (!IsValid)
            {
                return $"计算失败: {ErrorMessage}";
            }

            return $@"网络地址: {NetworkAddress}
广播地址: {BroadcastAddress}
子网掩码: {SubnetMask} (/{PrefixLength})
可用主机: {UsableHostCount:N0} 个
主机范围: {FirstUsableIP} - {LastUsableIP}
网络类别: {NetworkClass}
地址类型: {AddressType}";
        }

        /// <summary>
        /// 获取二进制显示文本
        /// </summary>
        /// <returns>二进制格式的地址信息</returns>
        public string GetBinaryDisplay()
        {
            if (!IsValid)
            {
                return "无效的计算结果";
            }

            return $@"IP地址:   {IPAddressBinary}
子网掩码: {SubnetMaskBinary}";
        }
    }
}
