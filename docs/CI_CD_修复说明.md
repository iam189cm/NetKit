# CI/CD 修复说明

## 修复时间
2025-01-15

## 修复的问题

### 1. Windows Server 2019 镜像弃用问题
**问题描述**：
- GitHub Actions 提示 Windows Server 2019 镜像已于 2025-06-30 被移除
- CI/CD 流程使用了已弃用的 `windows-2019` 镜像

**解决方案**：
- 将 `windows-2019` 替换为 `windows-2022`
- 保留 `windows-latest` 作为最新版本测试
- 更新测试矩阵：`os: [windows-2022, windows-latest]`

### 2. 目录创建失败问题
**问题描述**：
- `mkdir -p reports` 命令在 Windows 中执行失败
- 错误信息：`An item with the specified name D:\a\NetKit\NetKit\reports already exists`

**解决方案**：
- 使用 PowerShell 的 `Test-Path` 和 `New-Item` 命令
- 修改为：
  ```powershell
  if (!(Test-Path "reports")) { New-Item -ItemType Directory -Path "reports" -Force }
  if (!(Test-Path "htmlcov")) { New-Item -ItemType Directory -Path "htmlcov" -Force }
  ```

### 3. Shell 命令兼容性问题
**问题描述**：
- 混合使用了 bash 和 PowerShell 命令
- 在 Windows 环境中 bash 命令可能不稳定

**解决方案**：
- 统一使用 PowerShell 作为默认 shell
- 将所有 bash 风格的命令转换为 PowerShell：
  - `echo` → `Write-Host` (带颜色支持)
  - `[ -f "file" ]` → `Test-Path "file"`
  - `rm -rf` → `Remove-Item -Recurse -Force`
  - `stat` → `(Get-Item).Length`

### 4. GitHub Actions 版本更新
**问题描述**：
- 使用了较旧版本的 codecov action

**解决方案**：
- 更新 `codecov/codecov-action` 从 v3 到 v4

## 修复的文件

1. **`.github/workflows/ci.yml`**
   - 移除 `windows-2019` 镜像
   - 修复目录创建命令
   - 统一使用 PowerShell
   - 更新 codecov action 版本

2. **`.github/workflows/pr.yml`**
   - 统一使用 PowerShell 命令
   - 改进错误输出的可读性
   - 修复清理命令

3. **`.github/workflows/release.yml`**
   - 统一使用 PowerShell 进行文件检查
   - 改进构建验证逻辑

## 预期效果

1. **CI/CD 流程稳定性提升**
   - 消除因镜像弃用导致的构建失败
   - 避免目录已存在的错误

2. **跨平台兼容性改善**
   - 统一使用 PowerShell 确保 Windows 环境兼容性
   - 减少因 shell 差异导致的问题

3. **构建反馈改善**
   - 使用带颜色的输出提升可读性
   - 更清晰的错误信息和状态反馈

## 测试建议

1. 触发一次 CI/CD 流程验证修复效果
2. 检查所有测试步骤是否正常执行
3. 确认构建产物正常生成
4. 验证发布流程的正常工作

## 注意事项

- 所有修改都向后兼容
- 保持了原有的功能逻辑不变
- 仅修复了环境兼容性问题
- 建议在后续更新中继续关注 GitHub Actions 的版本更新 