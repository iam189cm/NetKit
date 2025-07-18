# NetKit DPI 适配功能说明

## 概述

NetKit 现已完全支持 Windows 高 DPI 感知和分辨率适配，能够在不同 DPI 设置和分辨率下提供一致的用户体验。

## 支持的配置

### 分辨率支持
- **1080P (1920x1080)**
- **2K (2560x1440)**  
- **4K (3840x2160)**
- 其他任意分辨率

### DPI 缩放支持
- **100%** - 标准缩放
- **125%** - 小幅缩放
- **150%** - 中等缩放
- **175%** - 大幅缩放
- **200%** - 超大缩放
- 其他任意缩放比例

## 核心特性

### 1. 自动 DPI 感知
- 程序启动时自动检测并启用 Windows DPI 感知
- 支持多种 DPI 感知 API，确保跨 Windows 版本兼容
- 优先使用最新的 Per-Monitor DPI Aware V2 API

### 2. 动态缩放适配
- 所有字体大小根据 DPI 自动缩放
- 控件尺寸（宽度、高度）智能调整
- 内边距和外边距按比例缩放
- 窗口大小自适应当前 DPI 设置

### 3. 统一字体管理
- 使用 Microsoft YaHei 作为统一字体 [[memory:3499469]]
- 字体大小根据缩放因子自动调整
- 支持不同字体粗细（normal、bold）
- 字体缓存机制提高性能

### 4. 智能窗口管理
- 窗口启动时自动居中显示
- 窗口大小根据 DPI 智能调整
- 支持窗口大小调整（适应不同需求）
- 设置合适的最小窗口尺寸

## 技术实现

### UIHelper 模块

核心的 DPI 适配功能由 `netkit.utils.ui_helper` 模块提供：

```python
from netkit.utils.ui_helper import ui_helper

# 启用 DPI 感知
ui_helper.enable_dpi_awareness()

# 初始化缩放
ui_helper.initialize_scaling(root_window)

# 获取适配后的字体
font = ui_helper.get_font(size=12, weight="bold")

# 获取适配后的尺寸
width = ui_helper.scale_size(200)
padding = ui_helper.get_padding(10)

# 设置窗口居中
ui_helper.center_window(window, 800, 600)
```

### 关键方法

#### DPI 感知设置
```python
def enable_dpi_awareness(self) -> bool:
    """启用 Windows 高 DPI 感知"""
    # 尝试使用 Windows 10+ 的 Per-Monitor DPI Aware V2
    # 回退到 Windows 8.1+ 的 Per-Monitor DPI Aware
    # 最后回退到 Windows Vista+ 的 System DPI Aware
```

#### 缩放计算
```python
def scale_size(self, size: int) -> int:
    """根据缩放因子调整尺寸"""
    return max(1, int(size * self._scaling_factor))

def get_font(self, size: int = None, weight: str = "normal") -> Tuple[str, int, str]:
    """获取适配 DPI 的字体"""
    scaled_size = self.scale_size(size)
    return (self._font_family, scaled_size, weight)
```

#### 窗口管理
```python
def center_window(self, window: tk.Tk, width: int, height: int) -> None:
    """将窗口居中显示"""
    scaled_width, scaled_height = self.get_window_size(width, height)
    # 计算居中位置并设置窗口几何
```

## 使用方法

### 1. 启动时初始化

在程序启动时，会自动进行 DPI 适配初始化：

```python
# start_netkit.py
from netkit.utils.ui_helper import ui_helper
ui_helper.enable_dpi_awareness()

# gui/main.py
ui_helper.initialize_scaling(self.app)
ui_helper.center_window(self.app, 1000, 900)
```

### 2. 界面元素适配

所有界面元素都使用适配后的尺寸和字体：

```python
# 字体适配
title = tb.Label(text="标题", font=ui_helper.get_font(18, "bold"))

# 尺寸适配
frame = tb.Frame(width=ui_helper.scale_size(200))
frame.pack(pady=ui_helper.get_padding(10))

# 控件配置
entry = tb.Entry(width=ui_helper.scale_size(30), font=ui_helper.get_font(9))
```

### 3. 布局规范

- **使用 pack() 和 grid() 布局**：避免使用 place() 绝对定位
- **相对尺寸**：所有尺寸都通过 `ui_helper` 计算
- **一致性**：统一使用相同的字体和缩放规则

## 测试验证

### DPI 测试工具

提供了专门的测试工具来验证 DPI 适配效果：

```bash
python scripts/test_dpi_scaling.py
```

测试工具会显示：
- 当前 DPI 设置信息
- 不同大小的字体效果
- 各种控件的显示效果
- 文本框和输入框的适配情况

### 主程序测试

启动主程序验证实际使用效果：

```bash
python start_netkit.py
```

程序启动时会显示 DPI 适配信息：
```
DPI 适配信息:
  缩放因子: 2.00
  DPI: 191
  基础字体大小: 9
```

## 兼容性

### Windows 版本
- **Windows 10/11**: 完全支持，使用最新 DPI API
- **Windows 8.1**: 支持 Per-Monitor DPI Aware
- **Windows 7/Vista**: 支持 System DPI Aware

### 分辨率和 DPI
- **1080P @ 100%**: 缩放因子 1.0
- **1080P @ 125%**: 缩放因子 1.25
- **2K @ 150%**: 缩放因子 1.5
- **4K @ 200%**: 缩放因子 2.0

## 注意事项

### 1. 按钮字体
ttkbootstrap 的 Button 控件不支持 font 参数，字体大小由主题控制。

### 2. 窗口大小策略
窗口大小使用保守的缩放策略（最大 1.5 倍），避免在高 DPI 下窗口过大。

### 3. 性能优化
- 字体缓存机制减少重复计算
- 单例模式确保 UIHelper 只初始化一次
- 缩放计算结果缓存

## 开发指南

### 添加新界面元素

1. **导入 UIHelper**：
```python
from netkit.utils.ui_helper import ui_helper
```

2. **使用适配方法**：
```python
# 字体
font=ui_helper.get_font(size, weight)

# 尺寸
width=ui_helper.scale_size(width)
height=ui_helper.scale_size(height)

# 内边距
padding=ui_helper.get_padding(padding)
pady=ui_helper.get_padding(pady)
padx=ui_helper.get_padding(padx)
```

3. **遵循布局规范**：
- 使用 pack() 或 grid() 布局
- 避免硬编码像素值
- 使用相对尺寸和自适应布局

### 批量更新工具

提供了批量更新脚本来自动适配现有代码：

```bash
python scripts/update_dpi_views.py
```

脚本会自动：
- 添加 ui_helper 导入
- 替换字体设置
- 更新尺寸参数
- 处理内边距和外边距

## 总结

NetKit 的 DPI 适配功能提供了完整的高 DPI 支持，确保在不同分辨率和 DPI 设置下都能提供一致的用户体验。通过统一的 UIHelper 模块，开发者可以轻松创建适配各种显示环境的界面，无需担心字体模糊、控件过小或布局错乱等问题。 