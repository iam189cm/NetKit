# NetKit DPI 适配改动说明

## 概述

本次更新为 NetKit 项目添加了完整的 DPI 和分辨率适配功能，确保在不同 Windows 系统和显示设置下都能提供一致的用户体验。

## 新增文件

### 1. 核心模块
- **`netkit/utils/ui_helper.py`** - DPI 适配核心模块
  - UIHelper 类：提供 DPI 感知、字体管理、尺寸计算等功能
  - 单例模式设计，确保全局一致性
  - 支持多种 Windows DPI API，向下兼容

### 2. 工具脚本
- **`scripts/update_dpi_views.py`** - 批量更新视图文件的 DPI 适配脚本
  - 自动添加 ui_helper 导入
  - 批量替换字体和尺寸设置
  - 处理 ttkbootstrap 按钮字体兼容性问题

- **`scripts/test_dpi_scaling.py`** - DPI 缩放测试工具
  - 可视化测试界面
  - 显示当前 DPI 设置信息
  - 测试各种控件的适配效果

### 3. 文档
- **`docs/DPI_适配说明.md`** - 详细的功能说明文档
- **`docs/DPI_适配改动说明.md`** - 本文档

## 修改的文件

### 1. 启动文件
#### `start_netkit.py`
**主要改动：**
- 重构 DPI 感知设置逻辑
- 使用新的 UIHelper 模块
- 改进错误处理和回退机制

**具体修改：**
```python
# 原来的实现
def set_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            print("警告: 无法设置 DPI 感知")

# 新的实现
try:
    from netkit.utils.ui_helper import ui_helper
    ui_helper.enable_dpi_awareness()
except ImportError:
    # 回退到原始实现
```

### 2. 主界面文件
#### `gui/main.py`
**主要改动：**
- 集成 UIHelper 模块
- 动态窗口大小和居中显示
- 所有字体和尺寸使用适配方法

**具体修改：**
```python
# 导入 UIHelper
from netkit.utils.ui_helper import ui_helper

# 窗口初始化
# 原来：self.app.geometry('1000x900')
# 现在：ui_helper.center_window(self.app, 1000, 900)

# 字体设置
# 原来：font=('Microsoft YaHei', 16, 'bold')
# 现在：font=ui_helper.get_font(16, "bold")

# 尺寸设置
# 原来：width=200, padding=10
# 现在：width=ui_helper.scale_size(200), padding=ui_helper.get_padding(10)
```

### 3. 视图文件
所有视图文件都进行了 DPI 适配更新：

#### `gui/views/netconfig/netconfig_view.py`
- 添加 ui_helper 导入
- 标题字体适配
- 内边距和外边距适配

#### `gui/views/netconfig/interface_selector.py`
- 网卡选择下拉框字体和宽度适配
- 按钮和复选框尺寸适配
- 布局间距适配

#### `gui/views/netconfig/info_display.py`
- 文本框高度和宽度适配
- 字体大小适配
- 内边距适配

#### `gui/views/netconfig/config_form.py`
- 输入框字体和宽度适配
- 标签字体适配
- 按钮尺寸适配

#### `gui/views/netconfig/status_display.py`
- 状态文本框高度适配
- 字体大小适配
- 内边距适配

#### `gui/views/ping_view.py`
- 标题字体适配
- 所有控件尺寸适配
- 布局间距适配

#### `gui/views/subnet_view.py`
- 完整的 DPI 适配
- 字体和尺寸全面更新

#### `gui/views/traceroute_view.py`
- 界面元素 DPI 适配
- 字体和布局优化

#### `gui/views/route_view.py`
- 路由表界面适配
- 控件尺寸和字体更新

## 技术实现细节

### 1. DPI 感知策略
采用多层回退策略，确保在不同 Windows 版本下都能正常工作：

```python
def enable_dpi_awareness(self) -> bool:
    try:
        # Windows 10+ Per-Monitor DPI Aware V2
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return True
    except:
        try:
            # Windows 8.1+ Per-Monitor DPI Aware
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            return True
        except:
            try:
                # Windows Vista+ System DPI Aware
                ctypes.windll.user32.SetProcessDPIAware()
                return True
            except:
                return False
```

### 2. 缩放计算
使用 Tkinter 的 `tk.call('tk', 'scaling')` 获取系统缩放因子：

```python
def initialize_scaling(self, root: tk.Tk) -> None:
    self._scaling_factor = root.tk.call('tk', 'scaling')
    self._dpi = int(96 * self._scaling_factor)
```

### 3. 字体管理
实现字体缓存机制，提高性能：

```python
def get_font(self, size: int = None, weight: str = "normal", family: str = None):
    cache_key = (family, size, weight)
    if cache_key not in self._font_cache:
        scaled_size = self.scale_size(size)
        self._font_cache[cache_key] = (family, scaled_size, weight)
    return self._font_cache[cache_key]
```

### 4. 窗口大小策略
对窗口大小使用保守的缩放策略，避免在高 DPI 下窗口过大：

```python
def get_window_size(self, base_width: int, base_height: int):
    conservative_factor = min(self._scaling_factor, 1.5)
    width = int(base_width * conservative_factor)
    height = int(base_height * conservative_factor)
    return width, height
```

## 兼容性处理

### 1. ttkbootstrap 按钮字体问题
发现 ttkbootstrap 的 Button 控件不支持 font 参数，在批量更新脚本中添加了特殊处理：

```python
# 移除 Button 控件的 font 参数
content = re.sub(r'(\s+font=ui_helper\.get_font\([^)]+\),?\n)', '', content)
```

### 2. 布局规范
确保所有界面元素都使用相对布局：
- 使用 pack() 和 grid() 布局
- 避免 place() 绝对定位
- 所有尺寸都通过 ui_helper 计算

## 测试验证

### 1. 自动化测试
创建了专门的测试脚本验证 DPI 适配效果：
- 显示当前 DPI 设置
- 测试各种字体大小
- 验证控件适配效果

### 2. 实际测试结果
在测试环境中验证了以下配置：
- **缩放因子**: 2.00
- **DPI**: 191
- **基础字体大小**: 9

程序成功启动并正确显示 DPI 适配信息。

## 性能优化

### 1. 单例模式
UIHelper 使用单例模式，确保全局只有一个实例：

```python
class UIHelper:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UIHelper, cls).__new__(cls)
        return cls._instance
```

### 2. 缓存机制
- 字体缓存：避免重复计算字体参数
- 配置缓存：缓存常用控件配置
- 尺寸缓存：缓存计算结果

### 3. 延迟计算
只在需要时进行缩放计算，避免不必要的性能开销。

## 向后兼容性

### 1. 渐进式升级
- 新的 DPI 功能不影响现有功能
- 保持原有 API 兼容性
- 错误处理确保在不支持 DPI 的环境下也能正常运行

### 2. 回退机制
- 如果 UIHelper 模块导入失败，回退到原始 DPI 设置
- 如果 DPI API 不可用，程序仍能正常启动
- 字体和尺寸设置有默认值兜底

## 开发体验改进

### 1. 统一的 API
提供一致的接口用于字体、尺寸和布局设置：

```python
# 统一的使用方式
font = ui_helper.get_font(size, weight)
width = ui_helper.scale_size(width)
padding = ui_helper.get_padding(padding)
```

### 2. 自动化工具
- 批量更新脚本：自动适配现有代码
- 测试工具：可视化验证适配效果
- 详细文档：完整的使用说明

### 3. 错误处理
- 详细的错误信息和警告
- 优雅的降级处理
- 调试信息输出

## 总结

本次 DPI 适配更新是一个全面的改进，涉及：

1. **新增核心模块** - UIHelper 提供完整的 DPI 适配功能
2. **全面界面更新** - 所有视图文件都进行了适配
3. **工具和文档** - 提供了完整的开发和测试工具
4. **性能优化** - 缓存机制和单例模式提高性能
5. **兼容性保证** - 多层回退策略确保跨版本兼容

这些改动确保了 NetKit 在不同 Windows 系统和显示设置下都能提供一致、清晰的用户体验，满足了现代高分辨率显示器的需求。 