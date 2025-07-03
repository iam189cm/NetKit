using NETKit.Core.Models;
using NETKit.Core.Helpers;
using NETKit.Common;

namespace NETKit.Core.Services
{
    /// <summary>
    /// 网络配置服务 - 负责网络配置的核心业务逻辑
    /// </summary>
    public class NetworkConfigService
    {
        private readonly CommandExecutionService _commandService;
        private readonly NetworkAdapterService _adapterService;

        public event Action<string, bool>? StatusUpdated;

        /// <summary>
        /// 构造函数
        /// </summary>
        public NetworkConfigService()
        {
            _commandService = new CommandExecutionService();
            _adapterService = new NetworkAdapterService();

            // 订阅子服务的状态更新事件
            _commandService.StatusUpdated += OnStatusUpdated;
            _adapterService.StatusUpdated += OnStatusUpdated;
        }

        /// <summary>
        /// 获取所有可用的网络适配器
        /// </summary>
        /// <param name="showAllAdapters">是否显示所有适配器</param>
        /// <returns>网络适配器列表</returns>
        public List<NetworkAdapterItem> GetNetworkAdapters(bool showAllAdapters = false)
        {
            var filterType = showAllAdapters ? AdapterFilterType.All : AdapterFilterType.PhysicalOnly;
            return _adapterService.GetNetworkAdapters(filterType);
        }

        /// <summary>
        /// 获取指定网络适配器的详细信息
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>网络适配器详细信息</returns>
        public NetworkAdapterInfo? GetAdapterDetails(string adapterName)
        {
            return _adapterService.GetAdapterDetails(adapterName);
        }

        /// <summary>
        /// 应用静态IP配置
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <param name="ipAddress">IP地址</param>
        /// <param name="subnetMask">子网掩码</param>
        /// <param name="gateway">网关地址</param>
        /// <param name="dnsServer">DNS服务器</param>
        /// <returns>配置是否成功</returns>
        public async Task<bool> ApplyStaticIPConfigurationAsync(string adapterName, string ipAddress, 
            string subnetMask, string? gateway = null, string? dnsServer = null)
        {
            try
            {
                // 验证权限
                var permissionResult = SecurityHelper.ValidateOperationPermission(NetworkConfigOperation.SetStaticIP);
                if (permissionResult != OperationResult.Success)
                {
                    OnStatusUpdated("权限不足，无法配置网络", true);
                    return false;
                }

                // 创建配置对象
                var config = NetworkConfiguration.CreateStaticConfig(adapterName, ipAddress, subnetMask, gateway ?? "", dnsServer ?? "");
                
                // 验证配置
                var validationResult = ValidationHelper.ValidateNetworkConfiguration(config);
                if (!validationResult.IsValid)
                {
                    OnStatusUpdated($"配置验证失败: {validationResult.Message}", true);
                    return false;
                }

                return await ApplyStaticIPConfigurationAsync(config);
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"配置失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 应用静态IP配置
        /// </summary>
        /// <param name="config">网络配置</param>
        /// <returns>配置是否成功</returns>
        public async Task<bool> ApplyStaticIPConfigurationAsync(NetworkConfiguration config)
        {
            try
            {
                OnStatusUpdated("正在配置静态IP地址...", false);

                // 设置IP地址和子网掩码
                string setIPCommand = _commandService.BuildSetStaticIPCommand(config);
                bool success = await _commandService.ExecuteNetshCommandAsync(setIPCommand);

                // 设置DNS服务器
                if (success && !string.IsNullOrWhiteSpace(config.PrimaryDNS))
                {
                    string setDNSCommand = _commandService.BuildSetDNSCommand(config.AdapterName, config.PrimaryDNS);
                    await _commandService.ExecuteNetshCommandAsync(setDNSCommand);
                }

                if (success)
                {
                    OnStatusUpdated($"静态IP配置已成功应用到 {config.AdapterName}", false);
                    SecurityHelper.LogSecurityEvent($"Static IP configured for {config.AdapterName}: {config.IPAddress}");
                }

                return success;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"配置失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 设置DHCP配置
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>配置是否成功</returns>
        public async Task<bool> SetDHCPConfigurationAsync(string adapterName)
        {
            try
            {
                // 验证权限
                var permissionResult = SecurityHelper.ValidateOperationPermission(NetworkConfigOperation.SetDHCP);
                if (permissionResult != OperationResult.Success)
                {
                    OnStatusUpdated("权限不足，无法配置网络", true);
                    return false;
                }

                // 检查适配器是否存在
                if (!IsAdapterExists(adapterName))
                {
                    OnStatusUpdated($"网络适配器 {adapterName} 不存在", true);
                    return false;
                }

                var config = NetworkConfiguration.CreateDHCPConfig(adapterName);
                return await SetDHCPConfigurationAsync(config);
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"DHCP配置失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 设置DHCP配置
        /// </summary>
        /// <param name="config">网络配置</param>
        /// <returns>配置是否成功</returns>
        public async Task<bool> SetDHCPConfigurationAsync(NetworkConfiguration config)
        {
            try
            {
                OnStatusUpdated($"正在为 {config.AdapterName} 设置DHCP自动获取IP...", false);

                // 设置为DHCP获取IP
                string setDHCPCommand = _commandService.BuildSetDHCPCommand(config.AdapterName);
                bool success = await _commandService.ExecuteNetshCommandAsync(setDHCPCommand);

                // 设置为DHCP获取DNS
                if (success)
                {
                    string setDHCPDNSCommand = _commandService.BuildSetDHCPDNSCommand(config.AdapterName);
                    bool dnsSuccess = await _commandService.ExecuteNetshCommandAsync(setDHCPDNSCommand);
                    
                    // 即使DNS设置失败，也认为整体操作成功（因为IP已经设置为DHCP）
                    if (!dnsSuccess)
                    {
                        OnStatusUpdated($"警告: DHCP DNS设置可能未完全应用，但IP设置已成功", false);
                    }
                }

                if (success)
                {
                    OnStatusUpdated($"DHCP配置已成功应用到 {config.AdapterName}", false);
                    SecurityHelper.LogSecurityEvent($"DHCP configured for {config.AdapterName}");
                }

                return success;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"DHCP配置失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 刷新网络适配器
        /// </summary>
        /// <returns>刷新是否成功</returns>
        public bool RefreshNetworkAdapters()
        {
            try
            {
                return _adapterService.RefreshAdapters();
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"刷新网络适配器失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 测试网络连通性
        /// </summary>
        /// <param name="target">目标地址</param>
        /// <param name="count">ping次数</param>
        /// <returns>ping结果</returns>
        public async Task<PingResult> TestConnectivityAsync(string target, int count = 4)
        {
            try
            {
                OnStatusUpdated($"正在测试到 {target} 的连通性...", false);
                var result = await _commandService.ExecutePingAsync(target, count);
                
                if (result.Success)
                {
                    OnStatusUpdated($"到 {target} 的连通性测试成功", false);
                }
                else
                {
                    OnStatusUpdated($"到 {target} 的连通性测试失败", true);
                }

                return result;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"连通性测试失败: {ex.Message}", true);
                return new PingResult { Success = false, Error = ex.Message, Target = target };
            }
        }

        /// <summary>
        /// 释放并更新IP地址
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>操作是否成功</returns>
        public async Task<bool> ReleaseAndRenewIPAsync(string adapterName)
        {
            try
            {
                // 验证权限
                var permissionResult = SecurityHelper.ValidateOperationPermission(NetworkConfigOperation.SetDHCP);
                if (permissionResult != OperationResult.Success)
                {
                    OnStatusUpdated("权限不足，无法执行此操作", true);
                    return false;
                }

                OnStatusUpdated($"正在释放和更新 {adapterName} 的IP地址...", false);

                // 释放IP地址
                bool releaseSuccess = await _commandService.ReleaseIPAsync(adapterName);
                if (!releaseSuccess)
                {
                    return false;
                }

                // 等待一段时间
                await Task.Delay(2000);

                // 更新IP地址
                bool renewSuccess = await _commandService.RenewIPAsync(adapterName);
                
                if (renewSuccess)
                {
                    OnStatusUpdated($"{adapterName} IP地址释放和更新完成", false);
                    SecurityHelper.LogSecurityEvent($"IP release/renew completed for {adapterName}");
                }

                return renewSuccess;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"释放和更新IP地址失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 刷新DNS缓存
        /// </summary>
        /// <returns>操作是否成功</returns>
        public async Task<bool> FlushDNSCacheAsync()
        {
            try
            {
                return await _commandService.FlushDNSAsync();
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"刷新DNS缓存失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 获取系统网络配置信息
        /// </summary>
        /// <returns>网络配置信息</returns>
        public async Task<string> GetSystemNetworkInfoAsync()
        {
            try
            {
                OnStatusUpdated("正在获取系统网络配置信息...", false);
                string info = await _commandService.ExecuteIPConfigAsync("/all");
                
                if (!string.IsNullOrEmpty(info))
                {
                    OnStatusUpdated("系统网络配置信息获取成功", false);
                }

                return info;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"获取系统网络配置信息失败: {ex.Message}", true);
                return string.Empty;
            }
        }

        /// <summary>
        /// 验证网络配置
        /// </summary>
        /// <param name="config">网络配置</param>
        /// <returns>验证结果</returns>
        public ValidationResult ValidateConfiguration(NetworkConfiguration config)
        {
            return ValidationHelper.ValidateNetworkConfiguration(config);
        }

        /// <summary>
        /// 检查适配器是否存在
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>是否存在</returns>
        public bool IsAdapterExists(string adapterName)
        {
            return _adapterService.AdapterExists(adapterName);
        }

        /// <summary>
        /// 获取活动的网络适配器
        /// </summary>
        /// <returns>活动的网络适配器列表</returns>
        public List<NetworkAdapterItem> GetActiveAdapters()
        {
            return _adapterService.GetActiveAdapters();
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

        /// <summary>
        /// 释放资源
        /// </summary>
        public void Dispose()
        {
            _commandService.StatusUpdated -= OnStatusUpdated;
            _adapterService.StatusUpdated -= OnStatusUpdated;
        }
    }
}
