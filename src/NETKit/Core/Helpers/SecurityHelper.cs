using System.Security.Principal;
using System.Diagnostics;
using NETKit.Common;

namespace NETKit.Core.Helpers
{
    /// <summary>
    /// 安全辅助类 - 负责权限检查和管理员操作
    /// </summary>
    public static class SecurityHelper
    {
        /// <summary>
        /// 检查是否以管理员权限运行
        /// </summary>
        /// <returns>是否为管理员权限</returns>
        public static bool IsRunAsAdministrator()
        {
            try
            {
                var identity = WindowsIdentity.GetCurrent();
                var principal = new WindowsPrincipal(identity);
                return principal.IsInRole(WindowsBuiltInRole.Administrator);
            }
            catch (Exception)
            {
                return false;
            }
        }

        /// <summary>
        /// 获取当前用户信息
        /// </summary>
        /// <returns>用户信息字符串</returns>
        public static string GetCurrentUserInfo()
        {
            try
            {
                var identity = WindowsIdentity.GetCurrent();
                string userName = identity.Name ?? "未知用户";
                string role = IsRunAsAdministrator() ? "管理员" : "普通用户";
                return $"{userName} ({role})";
            }
            catch (Exception)
            {
                return "未知用户 (权限检查失败)";
            }
        }

        /// <summary>
        /// 获取当前用户名
        /// </summary>
        /// <returns>用户名</returns>
        public static string GetCurrentUserName()
        {
            try
            {
                var identity = WindowsIdentity.GetCurrent();
                return identity.Name ?? "未知用户";
            }
            catch (Exception)
            {
                return "未知用户";
            }
        }

        /// <summary>
        /// 检查是否需要管理员权限
        /// </summary>
        /// <param name="operation">操作类型</param>
        /// <returns>是否需要管理员权限</returns>
        public static bool RequiresAdminPrivileges(NetworkConfigOperation operation)
        {
            return operation switch
            {
                NetworkConfigOperation.SetStaticIP => true,
                NetworkConfigOperation.SetDHCP => true,
                NetworkConfigOperation.RefreshAdapters => false,
                NetworkConfigOperation.GetAdapterInfo => false,
                _ => false
            };
        }

        /// <summary>
        /// 验证操作权限
        /// </summary>
        /// <param name="operation">操作类型</param>
        /// <returns>权限验证结果</returns>
        public static OperationResult ValidateOperationPermission(NetworkConfigOperation operation)
        {
            if (!RequiresAdminPrivileges(operation))
            {
                return OperationResult.Success;
            }

            return IsRunAsAdministrator() ? OperationResult.Success : OperationResult.InsufficientPermissions;
        }

        /// <summary>
        /// 以管理员身份重启应用程序
        /// </summary>
        /// <returns>重启操作结果</returns>
        public static OperationResult RestartAsAdministrator()
        {
            try
            {
                // 获取当前可执行文件路径
                string exePath = Application.ExecutablePath;
                
                // 创建进程启动信息
                ProcessStartInfo startInfo = new ProcessStartInfo
                {
                    FileName = exePath,
                    UseShellExecute = true,
                    Verb = "runas" // 这会触发UAC提示
                };
                
                // 启动新进程
                Process.Start(startInfo);
                
                return OperationResult.Success;
            }
            catch (System.ComponentModel.Win32Exception)
            {
                // 用户取消了UAC提示
                return OperationResult.Cancelled;
            }
            catch (Exception)
            {
                return OperationResult.Failed;
            }
        }

        /// <summary>
        /// 检查UAC是否启用
        /// </summary>
        /// <returns>UAC是否启用</returns>
        public static bool IsUACEnabled()
        {
            try
            {
                using (var key = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(
                    @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"))
                {
                    if (key != null)
                    {
                        var enableLUA = key.GetValue("EnableLUA");
                        return enableLUA != null && (int)enableLUA == 1;
                    }
                }
                return true; // 默认假设UAC已启用
            }
            catch (Exception)
            {
                return true; // 出错时假设UAC已启用
            }
        }

        /// <summary>
        /// 获取权限状态描述
        /// </summary>
        /// <returns>权限状态描述</returns>
        public static string GetPermissionStatusDescription()
        {
            if (IsRunAsAdministrator())
            {
                return Constants.UI.AdminModeMessage;
            }
            else
            {
                return Constants.UI.AdminRequiredMessage;
            }
        }

        /// <summary>
        /// 检查是否可以执行网络配置操作
        /// </summary>
        /// <returns>是否可以执行网络配置操作</returns>
        public static bool CanPerformNetworkOperations()
        {
            return IsRunAsAdministrator();
        }

        /// <summary>
        /// 尝试提升权限并执行操作
        /// </summary>
        /// <param name="operation">要执行的操作</param>
        /// <param name="showRestartPrompt">是否显示重启提示</param>
        /// <returns>操作结果</returns>
        public static OperationResult TryElevateAndExecute(NetworkConfigOperation operation, bool showRestartPrompt = true)
        {
            var permissionResult = ValidateOperationPermission(operation);
            
            if (permissionResult == OperationResult.Success)
            {
                return OperationResult.Success;
            }

            if (permissionResult == OperationResult.InsufficientPermissions && showRestartPrompt)
            {
                var result = MessageBox.Show(
                    "此操作需要管理员权限。是否要以管理员身份重启程序？",
                    Constants.Application.DisplayName,
                    MessageBoxButtons.YesNo,
                    MessageBoxIcon.Question);

                if (result == DialogResult.Yes)
                {
                    var restartResult = RestartAsAdministrator();
                    if (restartResult == OperationResult.Success)
                    {
                        Application.Exit();
                    }
                    return restartResult;
                }
            }

            return permissionResult;
        }

        /// <summary>
        /// 记录安全相关的日志
        /// </summary>
        /// <param name="message">日志消息</param>
        /// <param name="level">日志级别</param>
        public static void LogSecurityEvent(string message, LogLevel level = LogLevel.Info)
        {
            try
            {
                string timestamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
                string userInfo = GetCurrentUserInfo();
                string logEntry = $"[{timestamp}] [{level}] [Security] {message} - User: {userInfo}";
                
                // 这里可以将日志写入文件或事件日志
                // 目前只是简单的调试输出
                System.Diagnostics.Debug.WriteLine(logEntry);
            }
            catch (Exception)
            {
                // 忽略日志记录错误
            }
        }
    }
}
