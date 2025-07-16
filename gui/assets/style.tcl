# Netkit 自定义样式配置
# 基于 ttkbootstrap darkly 主题的扩展

# 自定义颜色变量
set colors {
    primary "#007acc"
    secondary "#6c757d"
    success "#28a745"
    info "#17a2b8"
    warning "#ffc107"
    danger "#dc3545"
    light "#f8f9fa"
    dark "#343a40"
}

# 自定义字体
set fonts {
    default_font {"Microsoft YaHei UI" 9}
    heading_font {"Microsoft YaHei UI" 12 bold}
    code_font {"Consolas" 9}
}

# 自定义样式
ttk::style configure "Custom.TButton" \
    -font [dict get $fonts default_font] \
    -padding {10 5}

ttk::style configure "Heading.TLabel" \
    -font [dict get $fonts heading_font] \
    -foreground [dict get $colors primary]

ttk::style configure "Code.TLabel" \
    -font [dict get $fonts code_font] \
    -background [dict get $colors dark] \
    -foreground [dict get $colors light]

# 网络状态指示器样式
ttk::style configure "Success.TLabel" \
    -foreground [dict get $colors success] \
    -font [dict get $fonts default_font]

ttk::style configure "Warning.TLabel" \
    -foreground [dict get $colors warning] \
    -font [dict get $fonts default_font]

ttk::style configure "Danger.TLabel" \
    -foreground [dict get $colors danger] \
    -font [dict get $fonts default_font] 