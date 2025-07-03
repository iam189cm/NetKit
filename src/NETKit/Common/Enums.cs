namespace NETKit.Common
{
    /// <summary>
    /// 网络配置操作类型
    /// </summary>
    public enum NetworkConfigOperation
    {
        /// <summary>
        /// 设置静态IP
        /// </summary>
        SetStaticIP,
        
        /// <summary>
        /// 设置DHCP
        /// </summary>
        SetDHCP,
        
        /// <summary>
        /// 刷新网卡
        /// </summary>
        RefreshAdapters,
        
        /// <summary>
        /// 获取网卡信息
        /// </summary>
        GetAdapterInfo
    }

    /// <summary>
    /// 操作结果类型
    /// </summary>
    public enum OperationResult
    {
        /// <summary>
        /// 成功
        /// </summary>
        Success,
        
        /// <summary>
        /// 失败
        /// </summary>
        Failed,
        
        /// <summary>
        /// 取消
        /// </summary>
        Cancelled,
        
        /// <summary>
        /// 权限不足
        /// </summary>
        InsufficientPermissions
    }

    /// <summary>
    /// 网络适配器过滤类型
    /// </summary>
    public enum AdapterFilterType
    {
        /// <summary>
        /// 仅物理适配器
        /// </summary>
        PhysicalOnly,
        
        /// <summary>
        /// 所有适配器
        /// </summary>
        All,
        
        /// <summary>
        /// 仅已连接的适配器
        /// </summary>
        ConnectedOnly
    }

    /// <summary>
    /// 日志级别
    /// </summary>
    public enum LogLevel
    {
        /// <summary>
        /// 信息
        /// </summary>
        Info,
        
        /// <summary>
        /// 警告
        /// </summary>
        Warning,
        
        /// <summary>
        /// 错误
        /// </summary>
        Error,
        
        /// <summary>
        /// 调试
        /// </summary>
        Debug
    }

    /// <summary>
    /// UI状态类型
    /// </summary>
    public enum UIState
    {
        /// <summary>
        /// 等待操作
        /// </summary>
        Waiting,
        
        /// <summary>
        /// 正在处理
        /// </summary>
        Processing,
        
        /// <summary>
        /// 操作完成
        /// </summary>
        Completed,
        
        /// <summary>
        /// 操作失败
        /// </summary>
        Failed,
        
        /// <summary>
        /// 权限不足
        /// </summary>
        PermissionDenied
    }

    /// <summary>
    /// 定义单个IP扫描操作的状态，对应颜色编码方案
    /// </summary>
    public enum ScanStatus
    {
        /// <summary>
        /// 灰色：此IP的扫描尚未开始
        /// </summary>
        Pending,

        /// <summary>
        /// 绿色：IP响应成功
        /// </summary>
        Success,

        /// <summary>
        /// 红色：IP未响应（例如：主机不可达）
        /// </summary>
        Failed,

        /// <summary>
        /// 橙色：ping请求超时
        /// </summary>
        Timeout
    }
}
