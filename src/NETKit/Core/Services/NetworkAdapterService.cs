using System.Net.NetworkInformation;
using System.Net;
using NETKit.Core.Models;
using NETKit.Common;

namespace NETKit.Core.Services
{
    /// <summary>
    /// 网络适配器服务 - 负责网络适配器的发现和信息获取
    /// </summary>
    public class NetworkAdapterService
    {
        public event Action<string, bool>? StatusUpdated;

        /// <summary>
        /// 获取所有可用的网络适配器
        /// </summary>
        /// <param name="filterType">过滤类型</param>
        /// <returns>网络适配器列表</returns>
        public List<NetworkAdapterItem> GetNetworkAdapters(AdapterFilterType filterType = AdapterFilterType.PhysicalOnly)
        {
            var adapters = new List<NetworkAdapterItem>();

            try
            {
                NetworkInterface[] networkInterfaces = NetworkInterface.GetAllNetworkInterfaces();

                foreach (NetworkInterface adapter in networkInterfaces)
                {
                    // 基本过滤：只显示以太网和无线网络适配器
                    if (adapter.NetworkInterfaceType == NetworkInterfaceType.Ethernet ||
                        adapter.NetworkInterfaceType == NetworkInterfaceType.Wireless80211)
                    {
                        if (ShouldIncludeAdapter(adapter, filterType))
                        {
                            var adapterItem = CreateAdapterItem(adapter);
                            adapters.Add(adapterItem);
                        }
                    }
                }

                OnStatusUpdated($"已加载 {adapters.Count} 个网络适配器", false);
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"加载网络适配器失败: {ex.Message}", true);
            }

            return adapters;
        }

        /// <summary>
        /// 获取指定网络适配器的详细信息
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>网络适配器详细信息</returns>
        public NetworkAdapterInfo? GetAdapterDetails(string adapterName)
        {
            try
            {
                NetworkInterface[] networkInterfaces = NetworkInterface.GetAllNetworkInterfaces();
                NetworkInterface? targetAdapter = networkInterfaces.FirstOrDefault(ni => ni.Name == adapterName);

                if (targetAdapter == null)
                {
                    OnStatusUpdated($"未找到网络适配器: {adapterName}", true);
                    return null;
                }

                return CreateAdapterInfo(targetAdapter);
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"获取网卡详细信息失败: {ex.Message}", true);
                return null;
            }
        }

        /// <summary>
        /// 获取所有网络适配器的详细信息
        /// </summary>
        /// <param name="filterType">过滤类型</param>
        /// <returns>网络适配器详细信息列表</returns>
        public List<NetworkAdapterInfo> GetAllAdapterDetails(AdapterFilterType filterType = AdapterFilterType.PhysicalOnly)
        {
            var adapterInfos = new List<NetworkAdapterInfo>();

            try
            {
                NetworkInterface[] networkInterfaces = NetworkInterface.GetAllNetworkInterfaces();

                foreach (NetworkInterface adapter in networkInterfaces)
                {
                    if (ShouldIncludeAdapter(adapter, filterType))
                    {
                        var adapterInfo = CreateAdapterInfo(adapter);
                        adapterInfos.Add(adapterInfo);
                    }
                }
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"获取网卡详细信息失败: {ex.Message}", true);
            }

            return adapterInfos;
        }

        /// <summary>
        /// 检查网络适配器是否存在
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>是否存在</returns>
        public bool AdapterExists(string adapterName)
        {
            try
            {
                NetworkInterface[] networkInterfaces = NetworkInterface.GetAllNetworkInterfaces();
                return networkInterfaces.Any(ni => ni.Name.Equals(adapterName, StringComparison.OrdinalIgnoreCase));
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// 获取活动的网络适配器
        /// </summary>
        /// <returns>活动的网络适配器列表</returns>
        public List<NetworkAdapterItem> GetActiveAdapters()
        {
            return GetNetworkAdapters(AdapterFilterType.ConnectedOnly);
        }

        /// <summary>
        /// 判断是否应该包含该适配器
        /// </summary>
        /// <param name="adapter">网络适配器</param>
        /// <param name="filterType">过滤类型</param>
        /// <returns>是否包含</returns>
        private bool ShouldIncludeAdapter(NetworkInterface adapter, AdapterFilterType filterType)
        {
            // 检查操作状态 - 只包含Up和Down状态的适配器
            if (adapter.OperationalStatus != OperationalStatus.Up && 
                adapter.OperationalStatus != OperationalStatus.Down)
            {
                return false;
            }

            switch (filterType)
            {
                case AdapterFilterType.All:
                    return true;

                case AdapterFilterType.ConnectedOnly:
                    return adapter.OperationalStatus == OperationalStatus.Up;

                case AdapterFilterType.PhysicalOnly:
                default:
                    return IsPhysicalAdapter(adapter);
            }
        }

        /// <summary>
        /// 检查是否为物理网络适配器
        /// </summary>
        /// <param name="adapter">网络适配器</param>
        /// <returns>是否为物理适配器</returns>
        private bool IsPhysicalAdapter(NetworkInterface adapter)
        {
            string name = adapter.Name.ToLower();
            string description = adapter.Description.ToLower();
            
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

        /// <summary>
        /// 创建网络适配器项目
        /// </summary>
        /// <param name="adapter">网络接口</param>
        /// <returns>网络适配器项目</returns>
        private NetworkAdapterItem CreateAdapterItem(NetworkInterface adapter)
        {
            bool isPhysical = IsPhysicalAdapter(adapter);
            bool isConnected = adapter.OperationalStatus == OperationalStatus.Up;
            
            return new NetworkAdapterItem(adapter.Name, adapter.Description, isPhysical, isConnected)
            {
                InterfaceType = adapter.NetworkInterfaceType.ToString()
            };
        }

        /// <summary>
        /// 创建网络适配器详细信息
        /// </summary>
        /// <param name="adapter">网络接口</param>
        /// <returns>网络适配器详细信息</returns>
        private NetworkAdapterInfo CreateAdapterInfo(NetworkInterface adapter)
        {
            var adapterInfo = new NetworkAdapterInfo
            {
                Name = adapter.Name,
                Description = adapter.Description,
                Status = adapter.OperationalStatus,
                InterfaceType = adapter.NetworkInterfaceType,
                PhysicalAddress = adapter.GetPhysicalAddress().ToString(),
                Speed = adapter.Speed
            };

            try
            {
                // 获取IP配置信息
                IPInterfaceProperties ipProperties = adapter.GetIPProperties();
                
                // 获取IPv4地址信息
                var unicastAddresses = ipProperties.UnicastAddresses
                    .Where(addr => addr.Address.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                    .ToList();

                if (unicastAddresses.Any())
                {
                    var primaryAddress = unicastAddresses.First();
                    adapterInfo.CurrentIP = primaryAddress.Address.ToString();
                    
                    // 计算子网掩码
                    if (primaryAddress.IPv4Mask != null)
                    {
                        adapterInfo.CurrentSubnetMask = primaryAddress.IPv4Mask.ToString();
                    }
                }

                // 获取网关信息
                var gateways = ipProperties.GatewayAddresses
                    .Where(gw => gw.Address.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                    .ToList();

                if (gateways.Any())
                {
                    adapterInfo.CurrentGateway = gateways.First().Address.ToString();
                }

                // 获取DNS服务器信息
                var dnsAddresses = ipProperties.DnsAddresses
                    .Where(dns => dns.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)
                    .Select(dns => dns.ToString())
                    .ToList();

                adapterInfo.CurrentDNS = dnsAddresses;

                // 检查是否启用DHCP
                adapterInfo.IsDHCPEnabled = DetectDHCPStatus(unicastAddresses);
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"获取 {adapter.Name} 的IP配置信息时出错: {ex.Message}", true);
            }

            return adapterInfo;
        }

        /// <summary>
        /// 检测DHCP状态
        /// </summary>
        /// <param name="unicastAddresses">单播地址列表</param>
        /// <returns>是否启用DHCP</returns>
        private bool DetectDHCPStatus(List<UnicastIPAddressInformation> unicastAddresses)
        {
            // 通过检查是否有静态IP配置来判断DHCP状态
            return unicastAddresses.Count == 0 || 
                   unicastAddresses.All(addr => addr.Address.ToString().StartsWith(Constants.Network.AutoConfigAddress)) ||
                   !unicastAddresses.Any(addr => addr.IPv4Mask != null);
        }

        /// <summary>
        /// 刷新网络适配器信息
        /// </summary>
        /// <returns>刷新是否成功</returns>
        public bool RefreshAdapters()
        {
            try
            {
                OnStatusUpdated("正在刷新网络适配器信息...", false);
                
                // 这里可以添加额外的刷新逻辑
                // 例如清除缓存、重新枚举等
                
                OnStatusUpdated("网络适配器信息刷新完成", false);
                return true;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"刷新网络适配器失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 触发状态更新事件
        /// </summary>
        /// <param name="message">状态消息</param>
        /// <param name="isError">是否为错误</param>
        protected virtual void OnStatusUpdated(string message, bool isError)
        {
            StatusUpdated?.Invoke(message, isError);
        }
    }
}
