"""
网卡信息显示UI组件
负责显示网卡的详细信息
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from netkit.utils.ui_helper import ui_helper
from netkit.services.netconfig.interface_info import get_network_card_info


class InfoDisplayWidget(tb.LabelFrame):
    """网卡信息显示组件"""
    
    def __init__(self, master, on_status_update=None, **kwargs):
        super().__init__(master, text="当前网卡信息", padding=ui_helper.get_padding(20), **kwargs)
        
        # 回调函数
        self.on_status_update = on_status_update
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 创建主容器
        main_container = tb.Frame(self)
        main_container.pack(fill=BOTH, expand=True)
        
        # 创建可选择的文本显示区域
        self.info_text = tb.Text(
            main_container,
            height=ui_helper.scale_size(12),
            width=ui_helper.scale_size(50),            state=DISABLED,
            wrap=NONE,
            relief=FLAT,
            borderwidth=ui_helper.scale_size(1),
            background='#f8f9fa',
            selectbackground='#0078d4',
            selectforeground='white'
        )
        self.info_text.pack(fill=BOTH, expand=True)
        
        # 添加右键菜单
        self.context_menu = tb.Menu(self, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_selected_text)
        self.context_menu.add_command(label="全选", command=self.select_all_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="复制所有信息", command=self.copy_all_info)
        
        # 绑定右键菜单
        self.info_text.bind("<Button-3>", self.show_context_menu)
        
        # 初始化显示
        self.show_no_selection_info()
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            # 检查是否有选中的文本
            if self.info_text.selection_get():
                self.context_menu.entryconfig("复制", state=NORMAL)
            else:
                self.context_menu.entryconfig("复制", state=DISABLED)
        except:
            self.context_menu.entryconfig("复制", state=DISABLED)
        
        self.context_menu.post(event.x_root, event.y_root)
    
    def copy_selected_text(self):
        """复制选中的文本"""
        try:
            selected_text = self.info_text.selection_get()
            if selected_text:
                self.clipboard_clear()
                self.clipboard_append(selected_text)
                self._append_status("已复制选中内容到剪贴板\n")
        except:
            self._append_status("没有选中的内容\n")
    
    def select_all_text(self):
        """全选文本"""
        self.info_text.tag_add(SEL, "1.0", END)
        self.info_text.mark_set(INSERT, "1.0")
        self.info_text.see(INSERT)
    
    def copy_all_info(self):
        """复制所有网卡信息到剪贴板"""
        try:
            # 获取所有文本内容
            all_text = self.info_text.get("1.0", END).strip()
            if all_text and all_text != "请选择网卡以查看详细信息":
                self.clipboard_clear()
                self.clipboard_append(all_text)
                self._append_status("已复制所有网卡信息到剪贴板\n")
            else:
                self._append_status("没有可复制的网卡信息\n")
        except Exception as e:
            self._append_status(f"复制失败: {str(e)}\n")
    
    def _append_status(self, text):
        """追加状态信息"""
        if self.on_status_update:
            self.on_status_update(text)
    
    def _update_text_display(self, content):
        """更新文本显示内容"""
        self.info_text.config(state=NORMAL)
        self.info_text.delete("1.0", END)
        self.info_text.insert("1.0", content)
        self.info_text.config(state=DISABLED)
    
    def show_no_selection_info(self):
        """显示未选择网卡的状态"""
        content = "请选择网卡以查看详细信息"
        self._update_text_display(content)
    
    def update_interface_info(self, interface_name):
        """更新网卡信息显示"""
        if not interface_name:
            self.show_no_selection_info()
            return
            
        try:
            # 获取网卡详细信息
            info = get_network_card_info(interface_name)
            
            # 格式化信息显示（左对齐，删除硬件信息分组）
            content_lines = [
                f"网卡名称: {info.get('name', '未知')}",
                f"描述: {info.get('description', '未知')}",
                f"状态: {info.get('status', '未知')}",
                f"物理地址: {info.get('mac', '未知')}",
                f"速度: {info.get('speed', '未知')}",
                "",
                "网络配置:",
                f"IP地址: {info.get('ip', '未配置')}",
                f"子网掩码: {info.get('mask', '未配置')}",
                f"默认网关: {info.get('gateway', '未配置')}",
                f"DNS服务器1: {info.get('dns1', '未配置')}",
                f"DNS服务器2: {info.get('dns2', '未配置')}"
            ]
            
            content = '\n'.join(content_lines)
            self._update_text_display(content)
            
            self._append_status(f"已选择网卡: {info.get('name', interface_name)}\n")
            
        except Exception as e:
            error_content = f"获取网卡信息失败: {str(e)}"
            self._update_text_display(error_content)
            self._append_status(f"获取网卡信息失败: {str(e)}\n")
    
    def force_update_interface_info(self, interface_name):
        """强制更新网卡信息显示，绕过缓存"""
        if not interface_name:
            self.show_no_selection_info()
            return
            
        try:
            # 强制刷新：先清除可能的缓存，然后获取最新信息
            from netkit.services.netconfig.interface_info import get_network_info_service
            service = get_network_info_service()
            
            # 清除WMI引擎缓存
            service.wmi_engine.clear_cache()
            
            # 获取最新的网卡详细信息
            info = service.get_network_card_info(interface_name, force_refresh=True)
            
            # 格式化信息显示
            content_lines = [
                f"网卡名称: {info.get('name', '未知')}",
                f"描述: {info.get('description', '未知')}",
                f"状态: {info.get('status', '未知')}",
                f"物理地址: {info.get('mac', '未知')}",
                f"速度: {info.get('speed', '未知')}",
                "",
                "网络配置:",
                f"IP地址: {info.get('ip', '未配置')}",
                f"子网掩码: {info.get('mask', '未配置')}",
                f"默认网关: {info.get('gateway', '未配置')}",
                f"DNS服务器1: {info.get('dns1', '未配置')}",
                f"DNS服务器2: {info.get('dns2', '未配置')}"
            ]
            
            content = '\n'.join(content_lines)
            self._update_text_display(content)
            
            self._append_status(f"已强制刷新网卡信息: {info.get('name', interface_name)}\n")
            
        except Exception as e:
            error_content = f"强制获取网卡信息失败: {str(e)}"
            self._update_text_display(error_content)
            self._append_status(f"强制获取网卡信息失败: {str(e)}\n")
    
    def get_current_info(self):
        """获取当前显示的网卡信息（以字典形式返回）"""
        try:
            content = self.info_text.get("1.0", END).strip()
            if not content or content == "请选择网卡以查看详细信息":
                return {}
            
            # 解析文本内容为字典
            info = {}
            lines = content.split('\n')
            for line in lines:
                if ':' in line and not line.startswith(' '):
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    # 转换为原来的字段名
                    if key == '网卡名称':
                        info['name'] = value
                    elif key == '描述':
                        info['desc'] = value
                    elif key == '状态':
                        info['status'] = value
                    elif key == '物理地址':
                        info['mac'] = value
                    elif key == '速度':
                        info['speed'] = value
                    elif key == 'IP地址':
                        info['ip'] = value
                    elif key == '子网掩码':
                        info['mask'] = value
                    elif key == '默认网关':
                        info['gateway'] = value
                    elif key == 'DNS服务器1':
                        info['dns1'] = value
                    elif key == 'DNS服务器2':
                        info['dns2'] = value
            
            return info
        except Exception as e:
            self._append_status(f"解析网卡信息失败: {str(e)}\n")
            return {} 