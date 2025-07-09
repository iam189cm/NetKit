namespace NETKit.Common
{
    /// <summary>
    /// 应用程序常量定义
    /// </summary>
    public static class Constants
    {
        /// <summary>
        /// 应用程序信息
        /// </summary>
        public static class Application
        {
            public const string Name = "NETKit v1.4";
            public const string DisplayName = "NETKit v1.4";
            public const string ShortName = "NETKit";
            public const string Version = "1.4";
            public const string FullTitle = "NETKit v1.4";
        }

        /// <summary>
        /// 网络配置相关常量
        /// </summary>
        public static class Network
        {
            public const string DefaultSubnetMask = "255.255.255.0";
            public const string DefaultDNS = "8.8.8.8";
            public const string DefaultSecondaryDNS = "8.8.4.4";
            public const string LoopbackAddress = "127.0.0.1";
            public const string AutoConfigAddress = "169.254.";
        }

        /// <summary>
        /// 用户界面相关常量
        /// </summary>
        public static class UI
        {
            public const string WaitingStatus = "等待操作...";
            public const string AdminRequiredMessage = "提示: 当前以普通用户身份运行，无法修改网络配置。请点击\"管理员重启\"按钮以获取完整功能。";
            public const string AdminModeMessage = "程序已以管理员权限运行，可以修改网络配置";
        }

        /// <summary>
        /// 系统命令相关常量
        /// </summary>
        public static class Commands
        {
            public const string NetshSetStatic = "netsh interface ip set address \"{0}\" static {1} {2}";
            public const string NetshSetStaticWithGateway = "netsh interface ip set address \"{0}\" static {1} {2} {3}";
            public const string NetshSetDHCP = "netsh interface ip set address \"{0}\" dhcp";
            public const string NetshSetDNS = "netsh interface ip set dns \"{0}\" static {1}";
            public const string NetshSetDHCPDNS = "netsh interface ip set dns \"{0}\" dhcp";
        }

        /// <summary>
        /// 颜色常量 - Snipaste风格配色
        /// </summary>
        public static class Colors
        {
            // Snipaste风格主色调
            public static readonly System.Drawing.Color PrimaryBlue = System.Drawing.Color.FromArgb(74, 144, 226);
            public static readonly System.Drawing.Color PrimaryBlueHover = System.Drawing.Color.FromArgb(53, 122, 189);
            
            // 背景色
            public static readonly System.Drawing.Color FormBackground = System.Drawing.Color.FromArgb(245, 245, 245);
            public static readonly System.Drawing.Color ControlBackground = System.Drawing.Color.White;
            public static readonly System.Drawing.Color PanelBackground = System.Drawing.Color.FromArgb(250, 250, 250);
            
            // 文字颜色
            public static readonly System.Drawing.Color TextPrimary = System.Drawing.Color.FromArgb(51, 51, 51);
            public static readonly System.Drawing.Color TextSecondary = System.Drawing.Color.FromArgb(102, 102, 102);
            public static readonly System.Drawing.Color TextMuted = System.Drawing.Color.FromArgb(153, 153, 153);
            
            // 边框颜色
            public static readonly System.Drawing.Color BorderLight = System.Drawing.Color.FromArgb(224, 224, 224);
            public static readonly System.Drawing.Color BorderMedium = System.Drawing.Color.FromArgb(204, 204, 204);
            public static readonly System.Drawing.Color BorderDark = System.Drawing.Color.FromArgb(187, 187, 187);
            
            // 状态颜色
            public static readonly System.Drawing.Color SuccessGreen = System.Drawing.Color.FromArgb(92, 184, 92);
            public static readonly System.Drawing.Color SuccessGreenHover = System.Drawing.Color.FromArgb(76, 174, 76);
            public static readonly System.Drawing.Color WarningOrange = System.Drawing.Color.FromArgb(240, 173, 78);
            public static readonly System.Drawing.Color DangerRed = System.Drawing.Color.FromArgb(217, 83, 79);
            public static readonly System.Drawing.Color DangerRedHover = System.Drawing.Color.FromArgb(201, 48, 44);
            
            // 悬停和焦点效果
            public static readonly System.Drawing.Color HoverLight = System.Drawing.Color.FromArgb(248, 249, 250);
            public static readonly System.Drawing.Color FocusBorder = System.Drawing.Color.FromArgb(74, 144, 226);
            
            // 兼容性保持
            public static readonly System.Drawing.Color SecondaryGray = System.Drawing.Color.FromArgb(108, 117, 125);
            public static readonly System.Drawing.Color SecondaryGrayHover = System.Drawing.Color.FromArgb(90, 98, 104);
        }
    }
}
