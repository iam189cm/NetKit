using System.Diagnostics;
using NETKit.Common;
using NETKit.Core.Models;

namespace NETKit.Core.Services
{
    /// <summary>
    /// 命令执行服务 - 负责执行系统命令
    /// </summary>
    public class CommandExecutionService
    {
        public event Action<string, bool>? StatusUpdated;

        /// <summary>
        /// 执行netsh命令
        /// </summary>
        /// <param name="command">要执行的命令</param>
        /// <returns>执行是否成功</returns>
        public async Task<bool> ExecuteNetshCommandAsync(string command)
        {
            try
            {
                // 输出正在执行的命令用于调试
                OnStatusUpdated($"正在执行命令: {command}", false);
                
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "cmd.exe",
                    Arguments = $"/c chcp 65001 >nul && {command}",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = System.Text.Encoding.UTF8,
                    StandardErrorEncoding = System.Text.Encoding.UTF8
                    // 移除Verb = "runas"，因为程序应该已经以管理员权限运行
                };

                using (Process process = Process.Start(startInfo)!)
                {
                    await process.WaitForExitAsync();
                    
                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();

                    if (process.ExitCode == 0)
                    {
                        if (!string.IsNullOrWhiteSpace(output))
                        {
                            OnStatusUpdated($"命令执行成功: {output.Trim()}", false);
                        }
                        else
                        {
                            OnStatusUpdated("命令执行成功", false);
                        }
                        return true;
                    }
                    else
                    {
                        string errorMessage = !string.IsNullOrWhiteSpace(error) ? error.Trim() : "未知错误";
                        if (!string.IsNullOrWhiteSpace(output))
                        {
                            errorMessage += $" 输出: {output.Trim()}";
                        }
                        OnStatusUpdated($"命令执行失败 (退出代码: {process.ExitCode}): {errorMessage}", true);
                        return false;
                    }
                }
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"执行命令时发生错误: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 构建设置静态IP的netsh命令
        /// </summary>
        /// <param name="config">网络配置</param>
        /// <returns>netsh命令字符串</returns>
        public string BuildSetStaticIPCommand(NetworkConfiguration config)
        {
            string escapedName = EscapeAdapterName(config.AdapterName);
            if (string.IsNullOrWhiteSpace(config.Gateway))
            {
                return string.Format(Constants.Commands.NetshSetStatic,
                    escapedName, config.IPAddress, config.SubnetMask);
            }
            else
            {
                return string.Format(Constants.Commands.NetshSetStaticWithGateway,
                    escapedName, config.IPAddress, config.SubnetMask, config.Gateway);
            }
        }

        /// <summary>
        /// 构建设置DNS的netsh命令
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <param name="dnsServer">DNS服务器地址</param>
        /// <returns>netsh命令字符串</returns>
        public string BuildSetDNSCommand(string adapterName, string dnsServer)
        {
            string escapedName = EscapeAdapterName(adapterName);
            return string.Format(Constants.Commands.NetshSetDNS, escapedName, dnsServer);
        }

        /// <summary>
        /// 构建添加备DNS的netsh命令
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <param name="dnsServer">备DNS服务器地址</param>
        /// <returns>netsh命令字符串</returns>
        public string BuildAddDNSCommand(string adapterName, string dnsServer)
        {
            string escapedName = EscapeAdapterName(adapterName);
            return $"netsh interface ip add dns {escapedName} {dnsServer} index=2";
        }

        /// <summary>
        /// 构建设置DHCP的netsh命令
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>netsh命令字符串</returns>
        public string BuildSetDHCPCommand(string adapterName)
        {
            // 确保适配器名称被正确转义
            string escapedName = EscapeAdapterName(adapterName);
            return string.Format(Constants.Commands.NetshSetDHCP, escapedName);
        }

        /// <summary>
        /// 构建设置DHCP DNS的netsh命令
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>netsh命令字符串</returns>
        public string BuildSetDHCPDNSCommand(string adapterName)
        {
            // 确保适配器名称被正确转义
            string escapedName = EscapeAdapterName(adapterName);
            return string.Format(Constants.Commands.NetshSetDHCPDNS, escapedName);
        }

        /// <summary>
        /// 转义适配器名称，处理特殊字符
        /// </summary>
        /// <param name="adapterName">原始适配器名称</param>
        /// <returns>转义后的适配器名称</returns>
        private string EscapeAdapterName(string adapterName)
        {
            // 对于包含空格或特殊字符的适配器名称，确保被正确引用
            // netsh命令中适配器名称应该用双引号包围
            if (string.IsNullOrWhiteSpace(adapterName))
                return "\"\"";
                
            // 移除可能的前后双引号，然后重新添加
            string trimmedName = adapterName.Trim('"');
            return $"\"{trimmedName}\"";
        }

        /// <summary>
        /// 执行ping命令
        /// </summary>
        /// <param name="target">目标地址</param>
        /// <param name="count">ping次数</param>
        /// <returns>ping结果</returns>
        public async Task<PingResult> ExecutePingAsync(string target, int count = 4)
        {
            try
            {
                string command = $"ping -n {count} {target}";
                
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "cmd.exe",
                    Arguments = $"/c {command}",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (Process process = Process.Start(startInfo)!)
                {
                    await process.WaitForExitAsync();
                    
                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();

                    return new PingResult
                    {
                        Success = process.ExitCode == 0,
                        Output = output,
                        Error = error,
                        Target = target,
                        Count = count
                    };
                }
            }
            catch (Exception ex)
            {
                return new PingResult
                {
                    Success = false,
                    Error = ex.Message,
                    Target = target,
                    Count = count
                };
            }
        }

        /// <summary>
        /// 执行ipconfig命令
        /// </summary>
        /// <param name="parameters">ipconfig参数</param>
        /// <returns>命令输出</returns>
        public async Task<string> ExecuteIPConfigAsync(string parameters = "/all")
        {
            try
            {
                string command = $"ipconfig {parameters}";
                
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "cmd.exe",
                    Arguments = $"/c {command}",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true
                };

                using (Process process = Process.Start(startInfo)!)
                {
                    await process.WaitForExitAsync();
                    
                    string output = await process.StandardOutput.ReadToEndAsync();
                    return output;
                }
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"执行ipconfig失败: {ex.Message}", true);
                return string.Empty;
            }
        }

        /// <summary>
        /// 刷新DNS缓存
        /// </summary>
        /// <returns>是否成功</returns>
        public async Task<bool> FlushDNSAsync()
        {
            try
            {
                OnStatusUpdated("正在刷新DNS缓存...", false);
                bool success = await ExecuteNetshCommandAsync("ipconfig /flushdns");
                
                if (success)
                {
                    OnStatusUpdated("DNS缓存刷新成功", false);
                }
                
                return success;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"刷新DNS缓存失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 释放IP地址
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>是否成功</returns>
        public async Task<bool> ReleaseIPAsync(string adapterName)
        {
            try
            {
                OnStatusUpdated($"正在释放 {adapterName} 的IP地址...", false);
                bool success = await ExecuteNetshCommandAsync($"ipconfig /release \"{adapterName}\"");
                
                if (success)
                {
                    OnStatusUpdated($"{adapterName} IP地址释放成功", false);
                }
                
                return success;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"释放IP地址失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 更新IP地址
        /// </summary>
        /// <param name="adapterName">适配器名称</param>
        /// <returns>是否成功</returns>
        public async Task<bool> RenewIPAsync(string adapterName)
        {
            try
            {
                OnStatusUpdated($"正在更新 {adapterName} 的IP地址...", false);
                bool success = await ExecuteNetshCommandAsync($"ipconfig /renew \"{adapterName}\"");
                
                if (success)
                {
                    OnStatusUpdated($"{adapterName} IP地址更新成功", false);
                }
                
                return success;
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"更新IP地址失败: {ex.Message}", true);
                return false;
            }
        }

        /// <summary>
        /// 执行route命令
        /// </summary>
        /// <param name="command">route命令参数</param>
        /// <returns>执行结果</returns>
        public async Task<RouteCommandResult> ExecuteRouteCommandAsync(string command)
        {
            try
            {
                string fullCommand = $"route {command}";
                OnStatusUpdated($"正在执行路由命令: {fullCommand}", false);
                
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = "cmd.exe",
                    Arguments = $"/c chcp 65001 >nul && {fullCommand}",
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = System.Text.Encoding.UTF8,
                    StandardErrorEncoding = System.Text.Encoding.UTF8
                };

                using (Process process = Process.Start(startInfo)!)
                {
                    await process.WaitForExitAsync();
                    
                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();

                    var result = new RouteCommandResult
                    {
                        Success = process.ExitCode == 0,
                        Output = output,
                        Error = error,
                        Command = fullCommand,
                        ExitCode = process.ExitCode
                    };

                    if (result.Success)
                    {
                        OnStatusUpdated($"路由命令执行成功", false);
                    }
                    else
                    {
                        string errorMessage = !string.IsNullOrWhiteSpace(error) ? error.Trim() : "未知错误";
                        OnStatusUpdated($"路由命令执行失败: {errorMessage}", true);
                    }

                    return result;
                }
            }
            catch (Exception ex)
            {
                OnStatusUpdated($"执行路由命令时发生错误: {ex.Message}", true);
                return new RouteCommandResult
                {
                    Success = false,
                    Error = ex.Message,
                    Command = command
                };
            }
        }

        /// <summary>
        /// 构建添加路由的命令
        /// </summary>
        /// <param name="routeRule">路由规则</param>
        /// <returns>route命令字符串</returns>
        public string BuildAddRouteCommand(RouteRule routeRule)
        {
            return routeRule.ToRouteCommand();
        }

        /// <summary>
        /// 构建删除路由的命令
        /// </summary>
        /// <param name="destination">目标网络</param>
        /// <param name="mask">子网掩码</param>
        /// <param name="gateway">网关（可选）</param>
        /// <returns>route命令字符串</returns>
        public string BuildDeleteRouteCommand(string destination, string mask, string? gateway = null)
        {
            if (string.IsNullOrEmpty(gateway))
            {
                return $"delete {destination} mask {mask}";
            }
            else
            {
                return $"delete {destination} mask {mask} {gateway}";
            }
        }

        /// <summary>
        /// 构建查看路由表的命令
        /// </summary>
        /// <returns>route命令字符串</returns>
        public string BuildPrintRouteCommand()
        {
            return "print";
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
    /// Ping结果类
    /// </summary>
    public class PingResult
    {
        public bool Success { get; set; }
        public string Output { get; set; } = string.Empty;
        public string Error { get; set; } = string.Empty;
        public string Target { get; set; } = string.Empty;
        public int Count { get; set; }
        public TimeSpan Duration { get; set; }

        public override string ToString()
        {
            return Success ? $"Ping {Target} 成功" : $"Ping {Target} 失败: {Error}";
        }
    }

    /// <summary>
    /// Route命令结果类
    /// </summary>
    public class RouteCommandResult
    {
        public bool Success { get; set; }
        public string Output { get; set; } = string.Empty;
        public string Error { get; set; } = string.Empty;
        public string Command { get; set; } = string.Empty;
        public int ExitCode { get; set; }

        public override string ToString()
        {
            return Success ? $"路由命令执行成功: {Command}" : $"路由命令执行失败: {Error}";
        }
    }
}
