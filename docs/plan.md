# NetworkEngineerToolkit 程序更新方案

## 🎯 更新策略概述

本项目采用**渐进式更新策略**，分为当前阶段和未来阶段：
- **当前阶段**: 手动更新 + 版本检查提醒
- **未来阶段**: 结合web系统的简单自动更新

## 🔧 当前阶段实现（简单版）

### 1. 版本检查功能
- 程序内置简单的版本检查机制
- 检查GitHub Releases或JSON文件获取最新版本信息
- 发现新版本时显示友好的提示界面
- 用户可选择访问下载页面或稍后提醒

### 2. 版本管理
```
版本信息显示：
├── 当前版本号
├── 检查更新功能
├── 版本更新日志
└── 官网访问链接
```

### 3. 更新提醒界面
```
┌─────────────────────────────────────┐
│ 🔄 发现新版本                        │
├─────────────────────────────────────┤
│ 当前版本: v1.0.0                    │
│ 最新版本: v1.1.0                    │
│                                     │
│ 更新内容:                           │
│ • 修复网卡检测问题                   │
│ • 新增批量配置功能                   │
│ • 优化用户界面                       │
│                                     │
│ [访问下载页面] [稍后提醒] [忽略]      │
└─────────────────────────────────────┘
```

## 🌐 未来web系统集成

### 1. 项目官网规划
```
官网功能模块：
├── 📖 产品介绍页面 - 功能特性展示
├── 📥 下载页面 - 各版本下载链接
├── 📋 版本更新日志 - 详细更新记录
├── 📚 使用教程 - 操作指南和FAQ
├── 💬 用户反馈 - 问题报告和建议
└── 🔄 在线更新 - 自动更新检查
```

### 2. 更新API设计
```json
// 版本检查接口: GET /api/version/latest
{
  "version": "1.1.0",
  "releaseDate": "2025-06-25",
  "downloadUrl": "https://yoursite.com/download/v1.1.0",
  "description": "修复网卡检测问题，新增批量配置功能",
  "mandatory": false,
  "changelog": [
    "修复Windows 11网卡检测兼容性问题",
    "新增批量网卡配置功能",
    "优化用户界面响应速度",
    "增强错误处理和日志记录"
  ]
}
```

## 📦 发布和部署流程

### 当前阶段发布流程
1. **版本准备**
   ```bash
   # 更新版本号
   # 编译测试
   dotnet build -c Release
   
   # 生成发布包
   dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
   ```

2. **版本发布**
   - 上传到GitHub Releases
   - 更新版本检查的JSON文件
   - 发布版本更新公告

3. **用户通知**
   - 程序启动时自动检查更新
   - 显示更新提醒和下载链接
   - 用户手动下载安装新版本

### 未来阶段发布流程
1. **自动化构建** - CI/CD自动编译和打包
2. **web系统集成** - 在线版本管理和分发
3. **智能更新** - 程序内一键更新功能

## 🛠️ 技术实现要点

### 版本比较算法
```csharp
// 语义化版本号比较 (Major.Minor.Patch)
// 示例: 1.0.0 < 1.0.1 < 1.1.0 < 2.0.0
public static bool IsNewerVersion(string current, string latest)
{
    var currentParts = current.Split('.').Select(int.Parse).ToArray();
    var latestParts = latest.Split('.').Select(int.Parse).ToArray();
    
    for (int i = 0; i < Math.Max(currentParts.Length, latestParts.Length); i++)
    {
        int currentPart = i < currentParts.Length ? currentParts[i] : 0;
        int latestPart = i < latestParts.Length ? latestParts[i] : 0;
        
        if (latestPart > currentPart) return true;
        if (latestPart < currentPart) return false;
    }
    return false;
}
```

### 更新检查服务
```csharp
// 异步检查更新，避免阻塞UI
public async Task<UpdateInfo> CheckForUpdatesAsync()
{
    try
    {
        using var client = new HttpClient();
        var response = await client.GetStringAsync(UPDATE_CHECK_URL);
        var updateInfo = JsonSerializer.Deserialize<UpdateInfo>(response);
        
        if (IsNewerVersion(CurrentVersion, updateInfo.Version))
        {
            return updateInfo;
        }
    }
    catch (Exception ex)
    {
        // 记录错误日志，但不影响程序正常运行
        Logger.LogError($"检查更新失败: {ex.Message}");
    }
    
    return null;
}
```

## 📋 实施计划

### 第一阶段 (立即实施)
- [x] 规范版本号管理
- [ ] 添加版本检查功能
- [ ] 创建更新提醒界面
- [ ] 实现"关于"对话框

### 第二阶段 (短期计划)
- [ ] 设置GitHub Releases发布流程
- [ ] 创建版本检查JSON接口
- [ ] 优化用户更新体验
- [ ] 添加更新历史记录

### 第三阶段 (长期规划)
- [ ] 开发项目官网
- [ ] 实现在线更新系统
- [ ] 添加用户反馈机制
- [ ] 建立自动化发布流程

## 🔍 用户使用指南

### 检查更新
1. 启动程序时自动检查（可在设置中关闭）
2. 手动检查：菜单栏 → 帮助 → 检查更新
3. 关于窗口：菜单栏 → 帮助 → 关于

### 更新程序
1. 收到更新提醒后，点击"访问下载页面"
2. 从官方渠道下载最新版本
3. 关闭当前程序，运行新版本安装包
4. 安装完成后启动新版本

### 版本回退
如果新版本出现问题，可以：
1. 卸载新版本
2. 重新安装之前的稳定版本
3. 或联系技术支持获取帮助

## 📝 更新日志模板

### v1.1.0 (计划中)
**发布日期**: 2025-07-01

**新增功能**:
- ✨ 批量网卡配置功能
- ✨ 配置模板保存和加载
- ✨ 网络连通性测试 (Ping)

**改进优化**:
- 🚀 优化网卡检测性能
- 🚀 改进用户界面响应速度
- 🚀 增强错误处理机制

**问题修复**:
- 🐛 修复Windows 11兼容性问题
- 🐛 修复特殊字符网卡名称显示问题
- 🐛 修复内存泄漏问题

**技术改进**:
- 🔧 升级到.NET 9.0最新版本
- 🔧 重构核心服务架构
- 🔧 添加单元测试覆盖

### v1.0.0 (当前版本)
**发布日期**: 2025-06-22

**核心功能**:
- ✅ 网络适配器选择和管理
- ✅ 静态IP地址配置
- ✅ DHCP自动配置切换
- ✅ 管理员权限检测和提升
- ✅ 实时状态反馈和日志

## 🔗 相关链接

- **项目主页**: [待建设]
- **下载页面**: [待建设]
- **问题反馈**: [GitHub Issues]
- **使用教程**: [待建设]
- **开发文档**: [README.md](./README.md)
