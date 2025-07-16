
import ipaddress
from typing import List, Dict, Tuple
import math


class SubnetCalculator:
    """子网计算器类"""
    
    def __init__(self):
        pass
    
    def calculate_subnet_info(self, network_str: str) -> Dict:
        """计算单个子网的详细信息"""
        try:
            network = ipaddress.IPv4Network(network_str, strict=False)
            
            # 基本信息
            network_address = str(network.network_address)
            broadcast_address = str(network.broadcast_address)
            netmask = str(network.netmask)
            wildcard = str(network.hostmask)
            prefix_length = network.prefixlen
            
            # 主机信息
            total_addresses = network.num_addresses
            usable_hosts = max(0, total_addresses - 2)  # 减去网络地址和广播地址
            
            # IP地址范围
            hosts = list(network.hosts())
            first_usable = str(hosts[0]) if hosts else "无"
            last_usable = str(hosts[-1]) if hosts else "无"
            
            # 子网类别判断
            if prefix_length <= 8:
                subnet_class = "A类"
            elif prefix_length <= 16:
                subnet_class = "B类"
            elif prefix_length <= 24:
                subnet_class = "C类"
            else:
                subnet_class = "自定义"
            
            return {
                'success': True,
                'network_address': network_address,
                'broadcast_address': broadcast_address,
                'netmask': netmask,
                'wildcard': wildcard,
                'prefix_length': prefix_length,
                'total_addresses': total_addresses,
                'usable_hosts': usable_hosts,
                'first_usable': first_usable,
                'last_usable': last_usable,
                'subnet_class': subnet_class,
                'network_object': network
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def vlsm_calculation(self, base_network_str: str, host_requirements: List[int]) -> Dict:
        """VLSM子网划分计算"""
        try:
            base_network = ipaddress.IPv4Network(base_network_str, strict=False)
            
            # 按主机数需求从大到小排序
            sorted_requirements = sorted(enumerate(host_requirements), key=lambda x: x[1], reverse=True)
            
            results = []
            current_network = base_network
            remaining_networks = [current_network]
            
            for original_index, hosts_needed in sorted_requirements:
                if not remaining_networks:
                    return {
                        'success': False,
                        'error': f"可用地址空间不足，无法分配 {hosts_needed} 个主机"
                    }
                
                # 计算所需的子网前缀长度
                # 需要考虑网络地址和广播地址，所以实际需要 hosts_needed + 2
                required_addresses = hosts_needed + 2
                prefix_bits = 32 - math.ceil(math.log2(required_addresses))
                
                # 确保不超过基础网络的前缀长度
                if prefix_bits < base_network.prefixlen:
                    return {
                        'success': False,
                        'error': f"需求 {hosts_needed} 个主机超出了基础网络容量"
                    }
                
                # 寻找合适的网络段
                allocated = False
                for i, available_net in enumerate(remaining_networks):
                    try:
                        # 尝试在当前可用网络中划分子网
                        subnets = list(available_net.subnets(new_prefix=prefix_bits))
                        if subnets:
                            # 分配第一个子网
                            allocated_subnet = subnets[0]
                            
                            subnet_info = self.calculate_subnet_info(str(allocated_subnet))
                            subnet_info['original_index'] = original_index
                            subnet_info['hosts_required'] = hosts_needed
                            subnet_info['subnet_name'] = f"子网 {original_index + 1}"
                            
                            results.append(subnet_info)
                            
                            # 更新剩余网络列表
                            remaining_networks.pop(i)
                            
                            # 如果有剩余的子网，加入到可用列表中
                            if len(subnets) > 1:
                                remaining_networks.extend(subnets[1:])
                            
                            allocated = True
                            break
                            
                    except ValueError:
                        # 当前网络无法进一步划分
                        continue
                
                if not allocated:
                    return {
                        'success': False,
                        'error': f"无法为需求 {hosts_needed} 个主机分配合适的子网"
                    }
            
            # 按原始顺序排序结果
            results.sort(key=lambda x: x['original_index'])
            
            # 计算利用率
            total_allocated = sum(r['total_addresses'] for r in results)
            total_available = base_network.num_addresses
            utilization = (total_allocated / total_available) * 100
            
            return {
                'success': True,
                'base_network': str(base_network),
                'subnets': results,
                'remaining_networks': [str(net) for net in remaining_networks],
                'utilization': utilization,
                'total_allocated': total_allocated,
                'total_available': total_available
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def subnet_summary(self, networks: List[str]) -> Dict:
        """子网汇总计算"""
        try:
            if not networks:
                return {'success': False, 'error': '请提供至少一个网络地址'}
            
            # 转换为网络对象
            network_objects = []
            for net_str in networks:
                try:
                    net = ipaddress.IPv4Network(net_str, strict=False)
                    network_objects.append(net)
                except:
                    return {'success': False, 'error': f'无效的网络地址: {net_str}'}
            
            # 找到能够包含所有网络的最小汇总网络
            # 先找到所有网络的地址范围
            all_addresses = []
            for net in network_objects:
                all_addresses.extend([net.network_address, net.broadcast_address])
            
            min_addr = min(all_addresses)
            max_addr = max(all_addresses)
            
            # 计算包含范围的最小网络
            for prefix_len in range(0, 33):
                try:
                    candidate = ipaddress.IPv4Network(f"{min_addr}/{prefix_len}", strict=False)
                    if candidate.network_address <= min_addr and candidate.broadcast_address >= max_addr:
                        summary_network = candidate
                        break
                except:
                    continue
            else:
                return {'success': False, 'error': '无法找到合适的汇总网络'}
            
            # 计算统计信息
            total_hosts = sum(net.num_addresses for net in network_objects)
            summary_total = summary_network.num_addresses
            efficiency = (total_hosts / summary_total) * 100
            
            return {
                'success': True,
                'summary_network': str(summary_network),
                'original_networks': networks,
                'total_original_hosts': total_hosts,
                'summary_total_hosts': summary_total,
                'efficiency': efficiency,
                'wasted_addresses': summary_total - total_hosts
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cidr_to_dotted(self, cidr: str) -> Dict:
        """CIDR转点分十进制子网掩码"""
        try:
            if '/' not in cidr:
                return {'success': False, 'error': 'CIDR格式错误，应包含 /'}
            
            network = ipaddress.IPv4Network(cidr, strict=False)
            
            return {
                'success': True,
                'cidr': cidr,
                'dotted_mask': str(network.netmask),
                'wildcard': str(network.hostmask),
                'prefix_length': network.prefixlen
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def dotted_to_cidr(self, ip: str, mask: str) -> Dict:
        """点分十进制转CIDR"""
        try:
            # 验证IP地址
            ipaddress.IPv4Address(ip)
            
            # 验证子网掩码并转换为前缀长度
            mask_obj = ipaddress.IPv4Address(mask)
            mask_int = int(mask_obj)
            
            # 计算前缀长度
            prefix_length = bin(mask_int).count('1')
            
            # 验证子网掩码是否有效（必须是连续的1）
            expected_mask = (0xFFFFFFFF << (32 - prefix_length)) & 0xFFFFFFFF
            if mask_int != expected_mask:
                return {'success': False, 'error': '无效的子网掩码'}
            
            # 创建网络
            network = ipaddress.IPv4Network(f"{ip}/{prefix_length}", strict=False)
            
            return {
                'success': True,
                'ip': ip,
                'mask': mask,
                'cidr': str(network),
                'network_address': str(network.network_address),
                'prefix_length': prefix_length
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# 向后兼容的简单函数
def vlsm(network, hosts_required):
    """VLSM计算（向后兼容）"""
    calculator = SubnetCalculator()
    if isinstance(hosts_required, int):
        hosts_required = [hosts_required]
    
    result = calculator.vlsm_calculation(network, hosts_required)
    if result['success'] and result['subnets']:
        return ipaddress.IPv4Network(result['subnets'][0]['network_address'] + '/' + str(result['subnets'][0]['prefix_length']))
    else:
        raise ValueError(result.get('error', 'VLSM calculation failed'))


def calculate_subnet_details(network_str: str) -> Dict:
    """计算子网详细信息"""
    calculator = SubnetCalculator()
    return calculator.calculate_subnet_info(network_str)


def vlsm_subnetting(base_network: str, host_requirements: List[int]) -> Dict:
    """VLSM子网划分"""
    calculator = SubnetCalculator()
    return calculator.vlsm_calculation(base_network, host_requirements)
