using System.Diagnostics;
using System.Net;
using System.Text;
using System.Text.RegularExpressions;
using NETKit.Core.Models;

namespace NETKit.Core.Services
{
    /// <summary>
    /// 路由跟踪服务
    /// </summary>
    public class TraceRouteService
    {
        /// <summary>
        /// 当单个跳点完成时触发
        /// </summary>
        public event Action<TraceRouteHop>? HopCompleted;

        /// <summary>
        /// 当跟踪完成时触发
        /// </summary>
        public event Action<TraceRouteResult>? TraceCompleted;

        /// <summary>
        /// 当状态更新时触发
        /// </summary>
        public event Action<string>? StatusUpdated;

        private Process? _currentProcess;
        private readonly object _lockObject = new();

        /// <summary>
        /// 异步开始路由跟踪
        /// </summary>
        /// <param name="targetAddress">目标地址</param>
        /// <param name="maxHops">最大跳数</param>
        /// <param name="timeoutMs">超时时间（毫秒）</param>
        /// <param name="cancellationToken">取消令牌</param>
        /// <returns>跟踪结果</returns>
        public async Task<TraceRouteResult> StartTraceAsync(
            string targetAddress, 
            int maxHops = 30, 
            int timeoutMs = 5000,
            CancellationToken cancellationToken = default)
        {
            var result = new TraceRouteResult
            {
                TargetAddress = targetAddress,
                MaxHops = maxHops,
                TimeoutMs = timeoutMs,
                StartTime = DateTime.Now
            };

            try
            {
                StatusUpdated?.Invoke($"开始跟踪到 {targetAddress} 的路由...");

                // 构建tracert命令
                var arguments = $"-h {maxHops} -w {timeoutMs} {targetAddress}";
                
                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "tracert",
                    Arguments = arguments,
                    UseShellExecute = false,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    CreateNoWindow = true,
                    StandardOutputEncoding = Encoding.GetEncoding("GBK") // 处理中文输出
                };

                lock (_lockObject)
                {
                    _currentProcess = new Process { StartInfo = processStartInfo };
                }

                var outputBuilder = new StringBuilder();
                var errorBuilder = new StringBuilder();

                _currentProcess.OutputDataReceived += (sender, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        outputBuilder.AppendLine(e.Data);
                        ProcessOutputLine(e.Data, result);
                    }
                };

                _currentProcess.ErrorDataReceived += (sender, e) =>
                {
                    if (!string.IsNullOrEmpty(e.Data))
                    {
                        errorBuilder.AppendLine(e.Data);
                    }
                };

                _currentProcess.Start();
                _currentProcess.BeginOutputReadLine();
                _currentProcess.BeginErrorReadLine();

                // 等待进程完成或取消
                while (!_currentProcess.HasExited)
                {
                    if (cancellationToken.IsCancellationRequested)
                    {
                        StopTrace();
                        result.IsCancelled = true;
                        StatusUpdated?.Invoke("跟踪已取消");
                        break;
                    }
                    await Task.Delay(100, cancellationToken);
                }

                if (!result.IsCancelled)
                {
                    await _currentProcess.WaitForExitAsync();
                    
                    if (_currentProcess.ExitCode != 0 && errorBuilder.Length > 0)
                    {
                        result.ErrorMessage = errorBuilder.ToString().Trim();
                    }
                    else
                    {
                        result.IsCompleted = true;
                    }
                }
            }
            catch (Exception ex)
            {
                result.ErrorMessage = ex.Message;
                StatusUpdated?.Invoke($"跟踪失败: {ex.Message}");
            }
            finally
            {
                result.EndTime = DateTime.Now;
                lock (_lockObject)
                {
                    _currentProcess?.Dispose();
                    _currentProcess = null;
                }
                
                StatusUpdated?.Invoke(result.GetStatusDescription());
                TraceCompleted?.Invoke(result);
            }

            return result;
        }

        /// <summary>
        /// 停止当前的跟踪
        /// </summary>
        public void StopTrace()
        {
            lock (_lockObject)
            {
                try
                {
                    if (_currentProcess != null && !_currentProcess.HasExited)
                    {
                        _currentProcess.Kill();
                    }
                }
                catch (Exception ex)
                {
                    StatusUpdated?.Invoke($"停止跟踪时出错: {ex.Message}");
                }
            }
        }

        /// <summary>
        /// 处理tracert输出的单行数据
        /// </summary>
        /// <param name="line">输出行</param>
        /// <param name="result">结果对象</param>
        private void ProcessOutputLine(string line, TraceRouteResult result)
        {
            try
            {
                // 跳过标题行和空行
                if (string.IsNullOrWhiteSpace(line) || 
                    line.Contains("正在跟踪") || 
                    line.Contains("通过最多") ||
                    line.Contains("跟踪完成"))
                {
                    return;
                }

                // 解析目标IP地址
                if (line.Contains("正在跟踪") && result.TargetIpAddress == null)
                {
                    var ipMatch = Regex.Match(line, @"\[(\d+\.\d+\.\d+\.\d+)\]");
                    if (ipMatch.Success && IPAddress.TryParse(ipMatch.Groups[1].Value, out var targetIp))
                    {
                        result.TargetIpAddress = targetIp;
                    }
                }

                // 解析跳点信息
                // 格式: "  1     1 ms     2 ms     1 ms  192.168.1.1"
                // 或者: "  2     *        *        *     请求超时。"
                var hopMatch = Regex.Match(line, @"^\s*(\d+)\s+(.+)$");
                if (hopMatch.Success)
                {
                    var hopNumber = int.Parse(hopMatch.Groups[1].Value);
                    var hopData = hopMatch.Groups[2].Value.Trim();
                    
                    var hop = ParseHopData(hopNumber, hopData);
                    if (hop != null)
                    {
                        result.AddHop(hop);
                        HopCompleted?.Invoke(hop);
                    }
                }
            }
            catch (Exception ex)
            {
                StatusUpdated?.Invoke($"解析输出时出错: {ex.Message}");
            }
        }

        /// <summary>
        /// 解析单个跳点的数据
        /// </summary>
        /// <param name="hopNumber">跳数</param>
        /// <param name="hopData">跳点数据</param>
        /// <returns>跳点对象</returns>
        private TraceRouteHop? ParseHopData(int hopNumber, string hopData)
        {
            var hop = new TraceRouteHop(hopNumber);

            // 检查是否为超时
            if (hopData.Contains("*") && (hopData.Contains("请求超时") || hopData.Contains("Request timed out")))
            {
                hop.IsTimeout = true;
                return hop;
            }

            // 处理完全超时的情况 (三个星号)
            var starCount = hopData.Count(c => c == '*');
            if (starCount >= 3)
            {
                hop.IsTimeout = true;
                return hop;
            }

            // 解析延迟值 - 更精确的延迟解析模式
            var delayPattern = @"(?:(\d+)\s*ms|(\*))";
            var delayMatches = Regex.Matches(hopData, delayPattern, RegexOptions.IgnoreCase);
            
            // 解析延迟值
            for (int i = 0; i < Math.Min(3, delayMatches.Count); i++)
            {
                var match = delayMatches[i];
                if (match.Groups[1].Success) // 数字
                {
                    if (long.TryParse(match.Groups[1].Value, out var delay))
                    {
                        switch (i)
                        {
                            case 0: hop.Delay1 = delay; break;
                            case 1: hop.Delay2 = delay; break;
                            case 2: hop.Delay3 = delay; break;
                        }
                    }
                }
                // 如果是*，延迟保持默认值-1
            }

            // 解析IP地址 - 更精确的模式
            var ipPattern = @"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b";
            var ipMatch = Regex.Match(hopData, ipPattern);
            if (ipMatch.Success)
            {
                if (IPAddress.TryParse(ipMatch.Groups[1].Value, out var ipAddress))
                {
                    hop.IpAddress = ipAddress;
                }
            }

            // 解析主机名（如果有）
            // 先尝试匹配方括号内的主机名，如：[hostname.com]
            var hostPatternBrackets = @"\[([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,})\]";
            var hostMatchBrackets = Regex.Match(hopData, hostPatternBrackets);
            if (hostMatchBrackets.Success)
            {
                hop.HostName = hostMatchBrackets.Groups[1].Value;
            }
            else
            {
                // 如果没有方括号，尝试匹配普通主机名
                // 但要排除IP地址
                var hostPattern = @"\b([a-zA-Z][a-zA-Z0-9\-\.]*\.[a-zA-Z]{2,})\b";
                var hostMatch = Regex.Match(hopData, hostPattern);
                if (hostMatch.Success)
                {
                    var hostName = hostMatch.Groups[1].Value;
                    // 确保不是IP地址
                    if (!IPAddress.TryParse(hostName, out _))
                    {
                        hop.HostName = hostName;
                    }
                }
            }

            return hop;
        }

        /// <summary>
        /// 释放资源
        /// </summary>
        public void Dispose()
        {
            StopTrace();
        }
    }
} 