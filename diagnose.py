#!/usr/bin/env python3
"""
诊断连接问题
"""

import socket
import subprocess
import sys
import json
from pathlib import Path


def check_port(host, port):
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_processes():
    """检查相关进程"""
    try:
        # 检查是否有进程占用 8080 端口
        result = subprocess.run(
            ["netstat", "-ano"], 
            capture_output=True, 
            text=True, 
            shell=True
        )
        
        lines = result.stdout.split('\n')
        port_8080_processes = []
        
        for line in lines:
            if ':8080' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    port_8080_processes.append(pid)
        
        return port_8080_processes
    except Exception as e:
        print(f"检查进程时出错: {e}")
        return []


def main():
    """主函数"""
    print("🔍 连接问题诊断")
    print("=" * 50)
    
    # 检查端口
    print("1. 检查端口 8080 状态...")
    if check_port("127.0.0.1", 8080):
        print("✅ 端口 8080 已开放")
    else:
        print("❌ 端口 8080 未开放")
    
    # 检查进程
    print("\n2. 检查占用端口 8080 的进程...")
    processes = check_processes()
    if processes:
        print(f"✅ 发现 {len(processes)} 个进程占用端口 8080:")
        for pid in processes:
            print(f"   PID: {pid}")
    else:
        print("❌ 没有进程占用端口 8080")
    
    # 检查配置文件
    print("\n3. 检查配置文件...")
    config_file = Path("lagrange-config-template.json")
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            implementations = config.get("Implementations", [])
            if implementations:
                impl = implementations[0]
                print("✅ 配置文件存在")
                print(f"   类型: {impl.get('Type')}")
                print(f"   主机: {impl.get('Host')}")
                print(f"   端口: {impl.get('Port')}")
                print(f"   后缀: {impl.get('Suffix')}")
            else:
                print("❌ 配置文件中没有 Implementations")
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
    else:
        print("❌ 配置文件不存在")
    
    # 建议
    print("\n4. 建议解决方案:")
    print("   1. 确保 Lagrange.OneBot 正在运行")
    print("   2. 检查 Lagrange.OneBot 的日志输出")
    print("   3. 尝试重启 Lagrange.OneBot")
    print("   4. 检查 Windows 防火墙设置")
    print("   5. 尝试使用不同的端口（如 8081）")


if __name__ == "__main__":
    main()
