using System.Text.RegularExpressions;
using NETKit.Core.Models;
using NETKit.Core.Helpers;
using NETKit.Common;

namespace NETKit.Core.Services
{
    /// <summary>
    /// 路由管理服务 - 负责路由表的管理和操作
    /// </summary>
    public class RouteManagementService
    {
        private readonly CommandExecutionService _commandService;
        private readonly NetworkAdapterService _adapterService;

        public event Action<string, bool>? StatusUpdated;

        /// <summary>
        /// 构造函数
        /// </summary>
        public RouteManagementService()
        {
            _commandService = new CommandExecutionService();
            _adapterService = new NetworkAdapterService();

            // 订阅子服务的状态更新事件
            _commandService.StatusUpdated += OnStatusUpdated;
            _adapterService.StatusUpdated += OnStatusUpdated;
        }

        /// <summary>
        /// 获取当前路由表
        /// </summary>
        /// <returns>路由规则列表</returns>
        public async Task<List<RouteRule>> GetRouteTableAsync()
        {
            try
            {
                OnStatusUpdated("正在获取路由表信息...", false);
                
                var result = await _commandService.ExecuteRouteCommandAsync("print");
                if (!result.Success)
                {
                    OnStatusUpdated($"获取路由表失败: {result.Error}", true);
                    return new List<RouteRule>();
                }

                var routes = ParseRouteTable(result.Output);
                OnStatusUpdated($"成功获取 {routes.Count} 条路由规则", false);
                
                return routes;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"获取路由表时发生错误: {ex.Message}", true);
                return new List<RouteRule>();
            }
        }

        /// <summary>
        /// 添加路由规则
        /// </summary>
        /// <param name="routeRule">路由规则</param>
        /// <returns>是否成功</returns>
        public async Task<bool> AddRouteAsync(RouteRule routeRule)
        {
            try
            {
                // 验证路由规则
                var validation = routeRule.Validate();
                if (!validation.IsValid)
                {
                    OnStatusUpdated($"路由规则验证失败: {validation.Message}", true);
                    return false;
                }

                // 验证权限
                var permissionResult = SecurityHelper.ValidateOperationPermission(NetworkConfigOperation.SetStaticIP);
                if (permissionResult != OperationResult.Success)
                {
                    OnStatusUpdated("权限不足，无法添加路由", true);
                    return false;
                }

                OnStatusUpdated($"正在添加路由规则: {routeRule.DestinationText} -> {routeRule.Gateway}", false);
                
                string command = _commandService.BuildAddRouteCommand(routeRule);
                var result = await _commandService.ExecuteRouteCommandAsync(command);

                if (result.Success)
                {
                    OnStatusUpdated($"路由规则添加成功: {routeRule.DestinationText}", false);
                    SecurityHelper.LogSecurityEvent($"Route added: {routeRule.DestinationText} via {routeRule.Gateway}");
                }

                return result.Success;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"添加路由规则时发生错误: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 删除路由规则
        /// </summary>
        /// <param name="routeRule">要删除的路由规则</param>
        /// <returns>是否成功</returns>
        public async Task<bool> DeleteRouteAsync(RouteRule routeRule)
        {
            try
            {
                // 验证权限
                var permissionResult = SecurityHelper.ValidateOperationPermission(NetworkConfigOperation.SetStaticIP);
                if (permissionResult != OperationResult.Success)
                {
                    OnStatusUpdated("权限不足，无法删除路由", true);
                    return false;
                }

                OnStatusUpdated($"正在删除路由规则: {routeRule.DestinationText}", false);
                
                string command = _commandService.BuildDeleteRouteCommand(
                    routeRule.DestinationNetwork, 
                    routeRule.SubnetMask, 
                    routeRule.Gateway);
                
                var result = await _commandService.ExecuteRouteCommandAsync(command);

                if (result.Success)
                {
                    OnStatusUpdated($"路由规则删除成功: {routeRule.DestinationText}", false);
                    SecurityHelper.LogSecurityEvent($"Route deleted: {routeRule.DestinationText} via {routeRule.Gateway}");
                }

                return result.Success;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"删除路由规则时发生错误: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 创建路由规则（从用户输入）
        /// </summary>
        /// <param name="destinationInput">网络目标输入</param>
        /// <param name="adapterName">选择的网络接口名称</param>
        /// <param name="metric">跃点数</param>
        /// <param name="isPersistent">是否为永久路由</param>
        /// <returns>路由规则</returns>
        public async Task<RouteRule?> CreateRouteRuleAsync(string destinationInput, string adapterName, int metric = 1, bool isPersistent = false)
        {
            try
            {
                // 获取网卡信息
                var adapterInfo = _adapterService.GetAdapterDetails(adapterName);
                if (adapterInfo == null)
                {
                    OnStatusUpdated($"未找到网络接口: {adapterName}", true);
                    return null;
                }

                // 获取网关
                string gateway = adapterInfo.CurrentGateway;
                if (string.IsNullOrEmpty(gateway) || gateway == "未配置")
                {
                    OnStatusUpdated($"网络接口 {adapterName} 未配置网关", true);
                    return null;
                }

                // 解析网络目标
                string destination, mask;
                if (destinationInput.Contains('/'))
                {
                    // CIDR格式
                    var parts = destinationInput.Split('/');
                    if (parts.Length != 2 || !int.TryParse(parts[1], out int cidr))
                    {
                        OnStatusUpdated("无效的CIDR格式", true);
                        return null;
                    }
                    destination = parts[0];
                    mask = GetMaskFromCidr(cidr);
                }
                else
                {
                    // 单个IP地址，使用/32
                    destination = destinationInput;
                    mask = "255.255.255.255";
                }

                // 验证IP地址格式
                if (!ValidationHelper.IsValidIPAddress(destination))
                {
                    OnStatusUpdated("目标地址格式不正确", true);
                    return null;
                }

                var routeRule = new RouteRule(destination, mask, gateway, adapterName, metric, isPersistent);
                string routeType = isPersistent ? "永久路由" : "临时路由";
                OnStatusUpdated($"创建{routeType}规则: {routeRule.DestinationText} -> {gateway} (通过 {adapterName})", false);
                
                return routeRule;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"创建路由规则时发生错误: {ex.Message}", true);
                return null;
            }
        }

        /// <summary>
        /// 获取可用的网络适配器
        /// </summary>
        /// <returns>网络适配器列表</returns>
        public List<NetworkAdapterItem> GetAvailableAdapters()
        {
            return _adapterService.GetActiveAdapters();
        }

        /// <summary>
        /// 检测多网络接口冲突情况
        /// </summary>
        /// <returns>冲突检测结果</returns>
        public async Task<MultiAdapterConflictResult> DetectMultiAdapterConflictAsync()
        {
            try
            {
                var routes = await GetRouteTableAsync();
                var adapters = GetAvailableAdapters();

                var result = new MultiAdapterConflictResult();
                
                // 查找默认路由
                var defaultRoutes = routes.Where(r => r.IsDefaultRoute).ToList();
                result.DefaultRoutes = defaultRoutes;

                // 检查是否有多个默认路由
                if (defaultRoutes.Count > 1)
                {
                    result.HasConflict = true;
                    result.ConflictDescription = $"发现 {defaultRoutes.Count} 个默认路由，可能导致网络访问问题";
                    
                    // 分析网络接口类型
                    var wiredRoutes = defaultRoutes.Where(r => IsWiredAdapter(r.InterfaceName, adapters)).ToList();
                    var wirelessRoutes = defaultRoutes.Where(r => IsWirelessAdapter(r.InterfaceName, adapters)).ToList();
                    
                    if (wiredRoutes.Any() && wirelessRoutes.Any())
                    {
                        result.ConflictType = "有线+无线冲突";
                        result.SuggestedSolution = "建议将公网流量路由到无线接口，内网流量路由到有线接口";
                    }
                }

                return result;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"检测多网络接口冲突时发生错误: {ex.Message}", true);
                return new MultiAdapterConflictResult { HasConflict = false };
            }
        }

        /// <summary>
        /// 解析路由表输出
        /// </summary>
        /// <param name="routeOutput">route print命令输出</param>
        /// <returns>路由规则列表</returns>
        private List<RouteRule> ParseRouteTable(string routeOutput)
        {
            var routes = new List<RouteRule>();
            
            try
            {
                OnStatusUpdated($"开始解析路由表，输出长度: {routeOutput.Length}", false);
                
                // 查找IPv4路由表部分
                var lines = routeOutput.Split('\n', StringSplitOptions.RemoveEmptyEntries);
                bool inIPv4Section = false;
                bool inRouteSection = false;

                foreach (var line in lines)
                {
                    string trimmedLine = line.Trim();
                    
                    // 寻找IPv4路由表标题（支持中英文）
                    if (trimmedLine.Contains("IPv4 Route Table") || 
                        trimmedLine.Contains("IPv4 路由表") ||
                        trimmedLine.Contains("Active Routes") ||
                        trimmedLine.Contains("活动路由"))
                    {
                        inIPv4Section = true;
                        OnStatusUpdated("找到IPv4路由表部分", false);
                        continue;
                    }
                    
                    // 寻找路由表头（支持中英文）
                    if (inIPv4Section && (trimmedLine.Contains("Network Destination") || 
                                         trimmedLine.Contains("网络目标") ||
                                         trimmedLine.Contains("Destination") ||
                                         trimmedLine.Contains("目标")))
                    {
                        inRouteSection = true;
                        OnStatusUpdated("找到路由表头", false);
                        continue;
                    }
                    
                    // 如果遇到其他section，停止解析
                    if (inRouteSection && (trimmedLine.Contains("=") || trimmedLine.Contains("Persistent Routes")))
                    {
                        break;
                    }
                    
                    // 解析路由条目
                    if (inRouteSection && !string.IsNullOrEmpty(trimmedLine) && 
                        !trimmedLine.Contains("Network Destination") && 
                        !trimmedLine.Contains("网络目标"))
                    {
                        var route = ParseRouteLine(trimmedLine);
                        if (route != null)
                        {
                            routes.Add(route);
                        }
                    }
                }
                
                OnStatusUpdated($"路由表解析完成，找到 {routes.Count} 条路由", false);
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"解析路由表时发生错误: {ex.Message}", true);
            }

            return routes;
        }

        /// <summary>
        /// 解析单行路由信息
        /// </summary>
        /// <param name="line">路由行</param>
        /// <returns>路由规则</returns>
        private RouteRule? ParseRouteLine(string line)
        {
            try
            {
                // 路由表格式: Network Destination  Netmask  Gateway  Interface  Metric
                var parts = line.Split(new char[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                
                OnStatusUpdated($"解析路由行: {line} (分割成 {parts.Length} 部分)", false);
                
                if (parts.Length >= 5)
                {
                    string destination = parts[0];
                    string netmask = parts[1];
                    string gateway = parts[2];
                    string interfaceIP = parts[3];
                    
                    if (int.TryParse(parts[4], out int metric))
                    {
                        // 通过接口IP查找网络接口名称
                        string interfaceName = GetInterfaceNameByIP(interfaceIP);
                        
                        var route = new RouteRule(destination, netmask, gateway, interfaceName, metric);
                        OnStatusUpdated($"成功解析路由: {route.DestinationText} -> {gateway}", false);
                        return route;
                    }
                    else
                    {
                        OnStatusUpdated($"无法解析metric值: {parts[4]}", false);
                    }
                }
                else
                {
                    OnStatusUpdated($"路由行格式不正确，部分数少于5: {parts.Length}", false);
                }
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"解析路由行时出错: {ex.Message}", true);
            }
            
            return null;
        }

        /// <summary>
        /// 通过IP地址查找网络接口名称
        /// </summary>
        /// <param name="interfaceIP">接口IP地址</param>
        /// <returns>网络接口名称</returns>
        private string GetInterfaceNameByIP(string interfaceIP)
        {
            try
            {
                var adapters = _adapterService.GetAllAdapterDetails();
                var matchedAdapter = adapters.FirstOrDefault(a => a.CurrentIP == interfaceIP);
                return matchedAdapter?.Name ?? $"Interface({interfaceIP})";
            }
            catch
            {
                return $"Interface({interfaceIP})";
            }
        }

        /// <summary>
        /// 判断是否为有线网络接口
        /// </summary>
        /// <param name="interfaceName">网络接口名称</param>
        /// <param name="adapters">网络接口列表</param>
        /// <returns>是否为有线网络接口</returns>
        private bool IsWiredAdapter(string interfaceName, List<NetworkAdapterItem> adapters)
        {
            var adapter = adapters.FirstOrDefault(a => a.Name == interfaceName);
            return adapter?.InterfaceType?.Contains("Ethernet") == true;
        }

        /// <summary>
        /// 判断是否为无线网络接口
        /// </summary>
        /// <param name="interfaceName">网络接口名称</param>
        /// <param name="adapters">网络接口列表</param>
        /// <returns>是否为无线网络接口</returns>
        private bool IsWirelessAdapter(string interfaceName, List<NetworkAdapterItem> adapters)
        {
            var adapter = adapters.FirstOrDefault(a => a.Name == interfaceName);
            return adapter?.InterfaceType?.Contains("Wireless") == true;
        }

        /// <summary>
        /// 从CIDR值获取子网掩码
        /// </summary>
        /// <param name="cidr">CIDR值</param>
        /// <returns>子网掩码字符串</returns>
        private string GetMaskFromCidr(int cidr)
        {
            if (cidr < 0 || cidr > 32)
                throw new ArgumentException("CIDR值必须在0-32之间", nameof(cidr));

            uint mask = 0xFFFFFFFF << (32 - cidr);
            return $"{(mask >> 24) & 0xFF}.{(mask >> 16) & 0xFF}.{(mask >> 8) & 0xFF}.{mask & 0xFF}";
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

    /// <summary>
    /// 多网络接口冲突检测结果
    /// </summary>
    public class MultiAdapterConflictResult
    {
        /// <summary>
        /// 是否存在冲突
        /// </summary>
        public bool HasConflict { get; set; }

        /// <summary>
        /// 冲突类型
        /// </summary>
        public string ConflictType { get; set; } = string.Empty;

        /// <summary>
        /// 冲突描述
        /// </summary>
        public string ConflictDescription { get; set; } = string.Empty;

        /// <summary>
        /// 建议的解决方案
        /// </summary>
        public string SuggestedSolution { get; set; } = string.Empty;

        /// <summary>
        /// 默认路由列表
        /// </summary>
        public List<RouteRule> DefaultRoutes { get; set; } = new List<RouteRule>();
    }
} 