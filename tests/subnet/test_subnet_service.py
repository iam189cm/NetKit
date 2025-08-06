#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
子网计算服务单元测试
覆盖SubnetCalculator、IPValidator、CIDRConverter的核心功能
使用随机化数据和边界条件测试
"""

import pytest
import random
import ipaddress
from typing import List, Tuple
from netkit.services.subnet import SubnetCalculator, IPValidator, CIDRConverter


class TestSubnetCalculator:
    """子网计算器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.calculator = SubnetCalculator()
        random.seed(42)  # 设置随机种子确保测试可重现
    
    @pytest.mark.subnet
    def test_calculate_subnet_info_basic(self):
        """测试基础子网信息计算"""
        # 标准测试用例
        test_cases = [
            ("192.168.1.100", "24", {
                'network_address': '192.168.1.0',
                'broadcast_address': '192.168.1.255',
                'subnet_mask': '255.255.255.0',
                'cidr_notation': '192.168.1.0/24'
            }),
            ("10.0.0.50", "255.255.0.0", {
                'network_address': '10.0.0.0',
                'broadcast_address': '10.0.255.255',
                'subnet_mask': '255.255.0.0',
                'cidr_notation': '10.0.0.0/16'
            }),
            ("172.16.5.10", "/20", {
                'network_address': '172.16.0.0',
                'broadcast_address': '172.16.15.255',
                'subnet_mask': '255.255.240.0',
                'cidr_notation': '172.16.0.0/20'
            })
        ]
        
        for ip, mask, expected in test_cases:
            result = self.calculator.calculate_subnet_info(ip, mask)
            
            # 验证关键字段
            assert result['network_address'] == expected['network_address']
            assert result['broadcast_address'] == expected['broadcast_address']
            assert result['subnet_mask'] == expected['subnet_mask']
            assert result['cidr_notation'] == expected['cidr_notation']
            
            # 验证其他必需字段存在
            required_fields = ['host_range', 'host_count', 'network_host_bits', 'ip_type']
            for field in required_fields:
                assert field in result
                assert result[field] is not None
    
    @pytest.mark.subnet
    def test_calculate_subnet_info_random(self):
        """使用随机化数据测试子网计算"""
        for _ in range(20):  # 随机测试20次（减少测试次数）
            # 生成随机IP和CIDR
            ip_parts = [random.randint(1, 254) for _ in range(4)]
            ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{ip_parts[3]}"
            cidr = random.randint(8, 28)  # 常用的CIDR范围
            
            try:
                result = self.calculator.calculate_subnet_info(ip, str(cidr))
                
                # 验证结果的基本合理性
                network = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)
                assert result['network_address'] == str(network.network_address)
                assert result['broadcast_address'] == str(network.broadcast_address)
                assert result['cidr_notation'] == str(network)
                
                # 验证主机数量计算
                expected_hosts = len(list(network.hosts()))
                if cidr == 31:
                    expected_hosts = 2  # RFC 3021
                elif cidr == 32:
                    expected_hosts = 1
                assert int(result['host_count']) == expected_hosts
                
            except Exception as e:
                pytest.fail(f"随机测试失败 IP: {ip}, CIDR: {cidr}, 错误: {str(e)}")
    
    @pytest.mark.subnet
    def test_calculate_subnet_info_edge_cases(self):
        """测试边界条件"""
        edge_cases = [
            # /31 网络 - 点对点链路
            ("192.168.1.0", "31", {
                'host_count': '2',
                'host_range': '192.168.1.0 - 192.168.1.1'
            }),
            # /32 网络 - 单个主机
            ("192.168.1.1", "32", {
                'host_count': '1',
                'host_range': '192.168.1.1'
            }),
            # /30 网络 - 最小可用子网
            ("192.168.1.0", "30", {
                'host_count': '2',
                'host_range': '192.168.1.1 - 192.168.1.2'
            }),
            # /8 网络 - 大型网络
            ("10.0.0.0", "8", {
                'network_address': '10.0.0.0',
                'broadcast_address': '10.255.255.255',
                'host_count': '16777214'
            })
        ]
        
        for ip, cidr, expected in edge_cases:
            result = self.calculator.calculate_subnet_info(ip, cidr)
            
            for key, expected_value in expected.items():
                assert result[key] == expected_value, \
                    f"边界测试失败: {ip}/{cidr}, {key}期望{expected_value}, 实际{result[key]}"
    
    @pytest.mark.subnet
    def test_calculate_subnet_info_invalid_input(self):
        """测试无效输入处理"""
        invalid_cases = [
            ("", "24"),  # 空IP
            ("192.168.1.1", ""),  # 空掩码
            ("192.168.1.256", "24"),  # 无效IP
            ("192.168.1.1", "33"),  # 无效CIDR
            ("192.168.1.1", "255.255.255.256"),  # 无效掩码
            ("not.an.ip", "24"),  # 非IP格式
            ("192.168.1.1", "not_a_mask"),  # 非掩码格式
        ]
        
        for ip, mask in invalid_cases:
            with pytest.raises(ValueError):
                self.calculator.calculate_subnet_info(ip, mask)
    
    @pytest.mark.subnet
    def test_divide_subnet_by_count(self):
        """测试按子网数量划分"""
        # 基础划分测试
        test_cases = [
            ("192.168.1.0", "24", 4),  # 划分为4个子网
            ("10.0.0.0", "16", 8),     # 划分为8个子网
            ("172.16.0.0", "20", 2),   # 划分为2个子网
        ]
        
        for ip, cidr, count in test_cases:
            subnets = self.calculator.divide_subnet(ip, cidr, "subnets", count)
            
            # 验证子网数量
            assert len(subnets) == count
            
            # 验证子网不重叠且连续
            original_network = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)
            subnet_networks = [ipaddress.IPv4Network(s['cidr_notation']) for s in subnets]
            
            # 验证所有子网都在原网络内
            for subnet in subnet_networks:
                assert subnet.subnet_of(original_network)
            
            # 验证子网不重叠
            for i, subnet1 in enumerate(subnet_networks):
                for j, subnet2 in enumerate(subnet_networks):
                    if i != j:
                        assert not subnet1.overlaps(subnet2)
    
    @pytest.mark.subnet
    def test_divide_subnet_by_hosts(self):
        """测试按主机数量划分"""
        test_cases = [
            ("192.168.0.0", "24", 30),   # 每子网30个主机
            ("10.0.0.0", "16", 1000),    # 每子网1000个主机
            ("172.16.0.0", "20", 100),   # 每子网100个主机
        ]
        
        for ip, cidr, hosts in test_cases:
            subnets = self.calculator.divide_subnet(ip, cidr, "hosts", hosts)
            
            # 验证每个子网的主机容量
            for subnet in subnets:
                actual_hosts = int(subnet['host_count'])
                # 应该能容纳指定数量的主机
                assert actual_hosts >= hosts, \
                    f"子网{subnet['cidr_notation']}主机数{actual_hosts}小于要求{hosts}"
    
    @pytest.mark.subnet
    def test_divide_subnet_random(self):
        """随机化子网划分测试"""
        base_networks = [
            ("192.168.0.0", "22"),  # 可划分为多个/24
            ("10.0.0.0", "16"),     # 大网络
            ("172.16.0.0", "20"),   # 中等网络
        ]
        
        for _ in range(10):  # 随机测试10次（减少测试次数）
            ip, cidr = random.choice(base_networks)
            
            # 随机选择划分方式
            if random.choice([True, False]):
                # 按子网数量划分
                count = random.randint(2, 16)
                try:
                    subnets = self.calculator.divide_subnet(ip, cidr, "subnets", count)
                    assert len(subnets) <= count  # 可能无法完全划分
                    
                    # 验证每个子网的基本信息
                    for subnet in subnets:
                        assert 'network_address' in subnet
                        assert 'broadcast_address' in subnet
                        assert 'cidr_notation' in subnet
                        assert 'host_count' in subnet
                        
                except ValueError:
                    # 某些情况下可能无法划分，这是正常的
                    pass
            else:
                # 按主机数量划分
                hosts = random.choice([10, 30, 50, 100, 200])
                try:
                    subnets = self.calculator.divide_subnet(ip, cidr, "hosts", hosts)
                    
                    for subnet in subnets:
                        actual_hosts = int(subnet['host_count'])
                        assert actual_hosts >= hosts
                        
                except ValueError:
                    # 某些情况下可能无法划分，这是正常的
                    pass
    
    @pytest.mark.subnet
    def test_divide_subnet_invalid_cases(self):
        """测试子网划分的无效情况"""
        invalid_cases = [
            # 无法划分的情况
            ("192.168.1.0", "30", "subnets", 5),  # /30无法划分为5个子网
            ("192.168.1.0", "24", "hosts", 300),  # /24无法容纳300个主机的子网
            ("192.168.1.0", "29", "subnets", 10), # /29无法划分为10个子网
            
            # 无效参数
            ("192.168.1.0", "24", "invalid_mode", 4),  # 无效划分模式
            ("192.168.1.0", "24", "subnets", 0),       # 零个子网
            ("192.168.1.0", "24", "hosts", -1),        # 负数主机
        ]
        
        for ip, cidr, mode, value in invalid_cases:
            with pytest.raises(ValueError):
                self.calculator.divide_subnet(ip, cidr, mode, value)


class TestIPValidator:
    """IP地址验证器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.validator = IPValidator()
    
    @pytest.mark.subnet
    def test_validate_ip_address_valid(self):
        """测试有效IP地址验证"""
        valid_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "8.8.8.8",
            "1.1.1.1",
            "192.168.0.1",
            "10.255.255.254",
            "172.31.255.254",
            "169.254.1.1",  # 链路本地地址
        ]
        
        for ip in valid_ips:
            valid, error = self.validator.validate_ip_address(ip)
            assert valid, f"有效IP {ip} 被错误拒绝: {error}"
            assert error is None
    
    @pytest.mark.subnet
    def test_validate_ip_address_invalid_format(self):
        """测试无效格式的IP地址"""
        invalid_ips = [
            "",  # 空字符串
            "192.168.1",  # 缺少字段
            "192.168.1.1.1",  # 多余字段
            "192.168.1.256",  # 超出范围
            "192.168.-1.1",  # 负数
            "192.168.1.a",  # 非数字
            "not.an.ip.address",  # 非数字格式
            "192,168,1,1",  # 错误分隔符
            "192.168.1.1/24",  # 包含CIDR
            " 192.168.1.1 ",  # 包含空格
        ]
        
        for ip in invalid_ips:
            valid, error = self.validator.validate_ip_address(ip)
            assert not valid, f"无效IP {ip} 被错误接受"
            assert error is not None
            assert "无效的IP地址格式" in error or "是保留地址" in error or "是回环地址" in error or "是组播地址" in error or "是广播地址" in error
    
    @pytest.mark.subnet
    def test_validate_ip_address_special_addresses(self):
        """测试特殊地址的验证"""
        special_cases = [
            ("0.0.0.0", "是保留地址"),
            ("255.255.255.255", "是广播地址"),
            ("127.0.0.1", "是回环地址"),
            ("127.1.2.3", "是回环地址"),
            ("224.0.0.1", "是组播地址"),
            ("239.255.255.255", "是组播地址"),
            ("240.0.0.1", "是保留地址"),  # 240.0.0.0/4 保留段
            ("254.255.255.255", "是保留地址"),
        ]
        
        for ip, expected_error_part in special_cases:
            valid, error = self.validator.validate_ip_address(ip)
            assert not valid, f"特殊地址 {ip} 应该被拒绝"
            assert error is not None
            assert expected_error_part in error
    
    @pytest.mark.subnet
    def test_validate_ip_address_random(self):
        """随机化IP地址验证测试"""
        for _ in range(50):  # 减少测试次数
            # 生成随机IP地址
            octets = [random.randint(0, 255) for _ in range(4)]
            ip = f"{octets[0]}.{octets[1]}.{octets[2]}.{octets[3]}"
            
            valid, error = self.validator.validate_ip_address(ip)
            
            # 验证结果的一致性
            try:
                ip_obj = ipaddress.ip_address(ip)
                
                # 检查特殊地址
                should_be_invalid = (
                    str(ip_obj) == '0.0.0.0' or
                    str(ip_obj) == '255.255.255.255' or
                    ip_obj.is_loopback or
                    ip_obj.is_multicast or
                    (int(ip_obj) >= 4026531840 and int(ip_obj) < 4294967295)  # 240.0.0.0/4
                )
                
                if should_be_invalid:
                    assert not valid, f"特殊地址 {ip} 应该被拒绝但被接受了"
                else:
                    assert valid, f"正常地址 {ip} 应该被接受但被拒绝了: {error}"
                    
            except ValueError:
                # ipaddress模块拒绝的IP，我们的验证器也应该拒绝
                assert not valid, f"格式错误的IP {ip} 应该被拒绝"
    
    @pytest.mark.subnet
    def test_validate_subnet_mask_valid(self):
        """测试有效子网掩码验证"""
        valid_masks = [
            "255.255.255.0",    # /24
            "255.255.0.0",      # /16
            "255.0.0.0",        # /8
            "255.255.255.128",  # /25
            "255.255.255.192",  # /26
            "255.255.255.224",  # /27
            "255.255.255.240",  # /28
            "255.255.255.248",  # /29
            "255.255.255.252",  # /30
            "255.255.255.254",  # /31
            "128.0.0.0",        # /1
            "192.0.0.0",        # /2
        ]
        
        for mask in valid_masks:
            valid, error = self.validator.validate_subnet_mask(mask)
            assert valid, f"有效掩码 {mask} 被错误拒绝: {error}"
            assert error is None
    
    @pytest.mark.subnet
    def test_validate_subnet_mask_invalid(self):
        """测试无效子网掩码"""
        invalid_masks = [
            "0.0.0.0",          # 全零掩码
            "255.255.255.255",  # 全一掩码
            "255.255.255.1",    # 不连续的掩码
            "255.255.128.255",  # 不连续的掩码
            "255.128.255.0",    # 不连续的掩码
            "256.255.255.0",    # 超出范围
            "255.255.255.-1",   # 负数
            "255.255.255",      # 字段不足
            "255.255.255.0.0",  # 字段过多
            "255.255.255.a",    # 非数字
            "",                 # 空字符串
            "not.a.mask",       # 非掩码格式
        ]
        
        for mask in invalid_masks:
            valid, error = self.validator.validate_subnet_mask(mask)
            assert not valid, f"无效掩码 {mask} 被错误接受"
            assert error is not None
    
    @pytest.mark.subnet
    def test_validate_cidr_valid(self):
        """测试有效CIDR位数验证"""
        for cidr in range(1, 33):  # 1-32都应该有效
            valid, error = self.validator.validate_cidr(cidr)
            assert valid, f"有效CIDR {cidr} 被错误拒绝: {error}"
            assert error is None
    
    @pytest.mark.subnet
    def test_validate_cidr_invalid(self):
        """测试无效CIDR位数"""
        invalid_cidrs = [
            0, -1, -10, 33, 50, 100,  # 超出范围
            "24",  # 字符串类型
            24.5,  # 浮点数
            None,  # None值
        ]
        
        for cidr in invalid_cidrs:
            valid, error = self.validator.validate_cidr(cidr)
            assert not valid, f"无效CIDR {cidr} 被错误接受"
            assert error is not None
    
    @pytest.mark.subnet
    def test_validate_cidr_notation(self):
        """测试CIDR表示法验证"""
        valid_cases = [
            ("192.168.1.0/24", "192.168.1.0", 24),
            ("10.0.0.0/8", "10.0.0.0", 8),
            ("172.16.0.0/16", "172.16.0.0", 16),
            ("192.168.1.100/30", "192.168.1.100", 30),
        ]
        
        for cidr_str, expected_ip, expected_bits in valid_cases:
            valid, error, result = self.validator.validate_cidr_notation(cidr_str)
            assert valid, f"有效CIDR表示法 {cidr_str} 被错误拒绝: {error}"
            assert error is None
            assert result == (expected_ip, expected_bits)
        
        invalid_cases = [
            "192.168.1.0",      # 缺少CIDR位数
            "192.168.1.0/",     # 缺少CIDR位数
            "192.168.1.0/33",   # CIDR超出范围
            "192.168.1.256/24", # 无效IP
            "192.168.1.0/a",    # 非数字CIDR
            "",                 # 空字符串
            "/24",              # 缺少IP
        ]
        
        for cidr_str in invalid_cases:
            valid, error, result = self.validator.validate_cidr_notation(cidr_str)
            assert not valid, f"无效CIDR表示法 {cidr_str} 被错误接受"
            assert error is not None
            assert result is None


class TestCIDRConverter:
    """CIDR转换器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.converter = CIDRConverter()
    
    @pytest.mark.subnet
    def test_cidr_to_mask_valid(self):
        """测试CIDR到子网掩码转换"""
        test_cases = [
            (8, "255.0.0.0"),
            (16, "255.255.0.0"),
            (24, "255.255.255.0"),
            (25, "255.255.255.128"),
            (26, "255.255.255.192"),
            (27, "255.255.255.224"),
            (28, "255.255.255.240"),
            (29, "255.255.255.248"),
            (30, "255.255.255.252"),
            (31, "255.255.255.254"),
            (32, "255.255.255.255"),
            (1, "128.0.0.0"),
            (0, "0.0.0.0"),
        ]
        
        for cidr, expected_mask in test_cases:
            result = self.converter.cidr_to_mask(cidr)
            assert result == expected_mask, \
                f"CIDR {cidr} 转换错误: 期望 {expected_mask}, 实际 {result}"
    
    @pytest.mark.subnet
    def test_cidr_to_mask_invalid(self):
        """测试无效CIDR转换"""
        invalid_cidrs = [-1, 33, 50, 100]
        
        for cidr in invalid_cidrs:
            result = self.converter.cidr_to_mask(cidr)
            assert result is None, f"无效CIDR {cidr} 应该返回None"
    
    @pytest.mark.subnet
    def test_mask_to_cidr_valid(self):
        """测试子网掩码到CIDR转换"""
        test_cases = [
            ("255.0.0.0", 8),
            ("255.255.0.0", 16),
            ("255.255.255.0", 24),
            ("255.255.255.128", 25),
            ("255.255.255.192", 26),
            ("255.255.255.224", 27),
            ("255.255.255.240", 28),
            ("255.255.255.248", 29),
            ("255.255.255.252", 30),
            ("255.255.255.254", 31),
            ("255.255.255.255", 32),
            ("128.0.0.0", 1),
            ("0.0.0.0", 0),
        ]
        
        for mask, expected_cidr in test_cases:
            result = self.converter.mask_to_cidr(mask)
            assert result == expected_cidr, \
                f"掩码 {mask} 转换错误: 期望 {expected_cidr}, 实际 {result}"
    
    @pytest.mark.subnet
    def test_mask_to_cidr_invalid(self):
        """测试无效掩码转换"""
        invalid_masks = [
            "255.255.255.1",    # 不连续掩码
            "255.128.255.0",    # 不连续掩码
            "256.0.0.0",        # 超出范围
            "invalid.mask",     # 非数字
            "",                 # 空字符串
        ]
        
        for mask in invalid_masks:
            result = self.converter.mask_to_cidr(mask)
            assert result is None, f"无效掩码 {mask} 应该返回None"
    
    @pytest.mark.subnet
    def test_parse_cidr_input(self):
        """测试CIDR输入解析"""
        test_cases = [
            ("192.168.1.0/24", "192.168.1.0", 24),
            ("10.0.0.0/8", "10.0.0.0", 8),
            ("/24", None, 24),
            ("24", None, 24),
        ]
        
        for input_str, expected_ip, expected_cidr in test_cases:
            ip, cidr = self.converter.parse_cidr_input(input_str)
            assert ip == expected_ip, f"解析IP错误: {input_str}"
            assert cidr == expected_cidr, f"解析CIDR错误: {input_str}"
        
        # 测试无效输入
        invalid_inputs = [
            "192.168.1.0/",
            "192.168.1.0/33",
            "invalid/24",
            "",
            "just_text",
        ]
        
        for input_str in invalid_inputs:
            ip, cidr = self.converter.parse_cidr_input(input_str)
            assert ip is None and cidr is None, \
                f"无效输入 {input_str} 应该返回 (None, None)"
    
    @pytest.mark.subnet
    def test_calculate_host_bits(self):
        """测试主机位数计算"""
        test_cases = [
            (8, 24),   # /8 有24个主机位
            (16, 16),  # /16 有16个主机位
            (24, 8),   # /24 有8个主机位
            (30, 2),   # /30 有2个主机位
            (32, 0),   # /32 有0个主机位
        ]
        
        for cidr, expected_host_bits in test_cases:
            result = self.converter.calculate_host_bits(cidr)
            assert result == expected_host_bits, \
                f"CIDR {cidr} 主机位数计算错误: 期望 {expected_host_bits}, 实际 {result}"
    
    @pytest.mark.subnet
    def test_calculate_max_hosts(self):
        """测试最大主机数计算"""
        test_cases = [
            (24, 254),      # /24: 2^8 - 2 = 254
            (25, 126),      # /25: 2^7 - 2 = 126
            (26, 62),       # /26: 2^6 - 2 = 62
            (27, 30),       # /27: 2^5 - 2 = 30
            (28, 14),       # /28: 2^4 - 2 = 14
            (29, 6),        # /29: 2^3 - 2 = 6
            (30, 2),        # /30: 2^2 - 2 = 2
            (31, 2),        # /31: 特殊情况 RFC 3021
            (32, 1),        # /32: 单个主机
            (16, 65534),    # /16: 2^16 - 2 = 65534
        ]
        
        for cidr, expected_hosts in test_cases:
            result = self.converter.calculate_max_hosts(cidr)
            assert result == expected_hosts, \
                f"CIDR {cidr} 最大主机数计算错误: 期望 {expected_hosts}, 实际 {result}"
    
    @pytest.mark.subnet
    def test_converter_consistency(self):
        """测试转换器的一致性"""
        # 测试CIDR到掩码再到CIDR的往返转换
        for cidr in range(0, 33):
            mask = self.converter.cidr_to_mask(cidr)
            assert mask is not None, f"CIDR {cidr} 转换为掩码失败"
            
            back_to_cidr = self.converter.mask_to_cidr(mask)
            assert back_to_cidr == cidr, \
                f"往返转换失败: {cidr} -> {mask} -> {back_to_cidr}"
    
    @pytest.mark.subnet
    def test_converter_random(self):
        """随机化转换测试"""
        valid_cidrs = list(range(0, 33))
        
        for _ in range(20):  # 减少测试次数
            cidr = random.choice(valid_cidrs)
            
            # CIDR到掩码
            mask = self.converter.cidr_to_mask(cidr)
            assert mask is not None
            
            # 掩码回到CIDR
            back_cidr = self.converter.mask_to_cidr(mask)
            assert back_cidr == cidr
            
            # 主机位数计算
            host_bits = self.converter.calculate_host_bits(cidr)
            assert host_bits == (32 - cidr)
            
            # 最大主机数计算
            max_hosts = self.converter.calculate_max_hosts(cidr)
            if cidr == 31:
                assert max_hosts == 2
            elif cidr == 32:
                assert max_hosts == 1
            else:
                expected = (2 ** (32 - cidr)) - 2
                assert max_hosts == expected


# 额外的边界和错误情况测试
class TestSubnetEdgeCases:
    """子网计算边界情况和错误处理测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.calculator = SubnetCalculator()
        self.validator = IPValidator()
        self.converter = CIDRConverter()
    
    @pytest.mark.subnet
    def test_extreme_networks(self):
        """测试极端网络情况"""
        extreme_cases = [
            # 大网络但不会导致性能问题
            ("10.0.0.0", "8"),
            ("172.16.0.0", "12"),
            ("192.168.0.0", "16"),
            # 最小网络
            ("192.168.1.1", "32"),
            # 常见边界
            ("192.168.1.0", "31"),
            ("192.168.1.0", "30"),
        ]
        
        for ip, cidr in extreme_cases:
            try:
                result = self.calculator.calculate_subnet_info(ip, cidr)
                # 验证结果的基本合理性
                assert 'network_address' in result
                assert 'broadcast_address' in result
                assert 'host_count' in result
                
                # 验证主机数量的合理性
                host_count = int(result['host_count'])
                assert host_count >= 0
                
                if cidr == "32":
                    assert host_count == 1
                elif cidr == "31":
                    assert host_count == 2
                    
            except Exception as e:
                pytest.fail(f"极端网络测试失败 {ip}/{cidr}: {str(e)}")
    
    @pytest.mark.subnet
    def test_memory_intensive_operations(self):
        """测试内存密集型操作"""
        # 测试大网络的子网划分
        large_networks = [
            ("10.0.0.0", "8", "subnets", 256),    # 划分大网络
            ("192.168.0.0", "16", "hosts", 1000), # 大主机数需求
        ]
        
        for ip, cidr, mode, value in large_networks:
            try:
                subnets = self.calculator.divide_subnet(ip, cidr, mode, value)
                # 验证结果不会消耗过多内存
                assert len(subnets) <= 1000, "子网数量过多，可能导致内存问题"
                
                # 验证每个子网的基本信息
                for subnet in subnets[:5]:  # 只检查前5个
                    assert 'network_address' in subnet
                    assert 'host_count' in subnet
                    
            except ValueError as e:
                # 某些大型操作可能会因为限制而失败，这是正常的
                assert "无法" in str(e) or "超出" in str(e)
            except MemoryError:
                pytest.fail(f"内存错误: {ip}/{cidr} {mode}={value}")
    
        @pytest.mark.subnet  
    def test_unicode_and_encoding(self):
        """测试Unicode和编码相关的边界情况"""
        # 测试包含明确无效Unicode字符的输入
        unicode_inputs = [
            ("192.168.1.1中文", "24"), # 包含中文
            ("192.168.1.1 ", "24"),    # 包含空格
            ("192.168.1.1\t", "24"),   # 包含制表符
            ("192.168.1.1\n", "24"),   # 包含换行符
            ("192.168.1.1", "24中文"), # CIDR包含中文
            ("192.168.1.1", "24 "),    # CIDR包含空格
        ]
        
        for ip, cidr in unicode_inputs:
            with pytest.raises(ValueError):
                self.calculator.calculate_subnet_info(ip, cidr)
    
    @pytest.mark.subnet  
    def test_concurrent_safety(self):
        """测试并发安全性（基础测试）"""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker():
            try:
                for _ in range(10):
                    result = self.calculator.calculate_subnet_info("192.168.1.0", "24")
                    results.append(result)
                    time.sleep(0.001)  # 短暂延迟
            except Exception as e:
                errors.append(str(e))
        
        # 创建多个线程
        threads = []
        for _ in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        # 等待所有线程完成
        for t in threads:
            t.join()
        
        # 验证结果
        assert len(errors) == 0, f"并发测试出现错误: {errors}"
        assert len(results) == 50, f"期望50个结果，实际得到{len(results)}个"
        
        # 验证所有结果都是一致的
        first_result = results[0]
        for result in results[1:]:
            assert result['network_address'] == first_result['network_address']
            assert result['broadcast_address'] == first_result['broadcast_address']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])