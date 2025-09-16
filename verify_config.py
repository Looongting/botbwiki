#!/usr/bin/env python3
"""
验证 Lagrange.OneBot 配置
"""

import json
from pathlib import Path


def verify_config():
    """验证配置文件"""
    print("🔍 验证 Lagrange.OneBot 配置")
    print("=" * 50)
    
    # 检查模板文件
    template_file = Path("lagrange-config-template.json")
    if template_file.exists():
        print("✅ 找到配置模板文件")
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 检查关键配置
            uin = config.get("Account", {}).get("Uin", 0)
            if uin == 0:
                print("❌ 请设置您的 QQ 号 (Uin)")
                return False
            else:
                print(f"✅ QQ 号已设置: {uin}")
            
            implementations = config.get("Implementations", [])
            if not implementations:
                print("❌ 没有配置 Implementations")
                return False
            
            impl = implementations[0]
            if impl.get("Type") != "ReverseWebSocket":
                print("❌ 配置类型不是 ReverseWebSocket")
                return False
            
            if impl.get("Port") != 8080:
                print("❌ 端口不是 8080")
                return False
            
            print("✅ 配置验证通过")
            print("\n📋 配置摘要:")
            print(f"   QQ 号: {uin}")
            print(f"   类型: {impl.get('Type')}")
            print(f"   主机: {impl.get('Host')}")
            print(f"   端口: {impl.get('Port')}")
            print(f"   后缀: {impl.get('Suffix')}")
            
            return True
            
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
            return False
    else:
        print("❌ 没有找到配置模板文件")
        return False


def main():
    """主函数"""
    if verify_config():
        print("\n🎯 下一步操作:")
        print("1. 将配置内容复制到 Lagrange.OneBot 目录下的 appsettings.json")
        print("2. 重启 Lagrange.OneBot")
        print("3. 检查 Lagrange.OneBot 日志中是否有 'WebSocket server started' 信息")
        print("4. 重新运行连接检查")
    else:
        print("\n❌ 配置验证失败，请检查配置文件")


if __name__ == "__main__":
    main()
