namespace NETKit.Core.Models
{
    /// <summary>
    /// VLSM需求模型
    /// </summary>
    public class VLSMRequirement
    {
        /// <summary>
        /// 部门或子网名称
        /// </summary>
        public string Name { get; set; }

        /// <summary>
        /// 需要的主机数量
        /// </summary>
        public int RequiredHosts { get; set; }

        /// <summary>
        /// 计算出的最小子网掩码长度
        /// </summary>
        public int CalculatedPrefixLength { get; set; }

        /// <summary>
        /// 实际可用主机数量
        /// </summary>
        public long ActualHostCount { get; set; }

        /// <summary>
        /// 分配的子网信息
        /// </summary>
        public SubnetInfo AllocatedSubnet { get; set; }

        /// <summary>
        /// 优先级（数字越小优先级越高）
        /// </summary>
        public int Priority { get; set; }

        /// <summary>
        /// 是否已分配
        /// </summary>
        public bool IsAllocated { get; set; }

        public VLSMRequirement()
        {
            Name = string.Empty;
            RequiredHosts = 0;
            CalculatedPrefixLength = 0;
            ActualHostCount = 0;
            Priority = 0;
            IsAllocated = false;
        }

        public VLSMRequirement(string name, int requiredHosts, int priority = 0)
        {
            Name = name;
            RequiredHosts = requiredHosts;
            Priority = priority;
            IsAllocated = false;
            CalculatePrefixLength();
        }

        /// <summary>
        /// 根据需要的主机数计算最小前缀长度
        /// </summary>
        public void CalculatePrefixLength()
        {
            if (RequiredHosts <= 0)
            {
                CalculatedPrefixLength = 32;
                ActualHostCount = 0;
                return;
            }

            // 需要考虑网络地址和广播地址，所以实际需要的地址数是 RequiredHosts + 2
            int totalAddressesNeeded = RequiredHosts + 2;
            
            // 找到能容纳所需地址数的最小的2的幂
            int powerOf2 = 1;
            int hostBits = 0;
            
            while (powerOf2 < totalAddressesNeeded)
            {
                powerOf2 *= 2;
                hostBits++;
            }

            CalculatedPrefixLength = 32 - hostBits;
            ActualHostCount = powerOf2 - 2; // 减去网络地址和广播地址
        }

        /// <summary>
        /// 获取格式化的需求描述
        /// </summary>
        /// <returns>格式化的需求信息</returns>
        public string GetFormattedRequirement()
        {
            return $"{Name}: 需要 {RequiredHosts} 个主机 (/{CalculatedPrefixLength}, 实际可用 {ActualHostCount} 个)";
        }

        /// <summary>
        /// 获取分配结果描述
        /// </summary>
        /// <returns>分配结果信息</returns>
        public string GetAllocationResult()
        {
            if (!IsAllocated || AllocatedSubnet == null)
            {
                return $"{Name}: 未分配";
            }

            return $"{Name}: {AllocatedSubnet.GetCIDRNotation()} ({AllocatedSubnet.GetHostRange()})";
        }
    }
}
