#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Kimi Coding API (Anthropic兼容模式)
"""

import os
import asyncio
import aiohttp

async def test_kimi_coding_api():
    """测试Kimi Coding API"""
    
    # 获取配置
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding")
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     Kimi Coding API 连接测试                                 ║")
    print("║     Anthropic 兼容模式                                       ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    print(f"\n📝 配置:")
    print(f"   Base URL: {base_url}")
    print(f"   API Key: {api_key[:20]}..." if api_key else "   API Key: 未设置")
    
    if not api_key:
        print("\n❌ 未设置 ANTHROPIC_API_KEY 环境变量")
        print("\n请运行:")
        print("   export ANTHROPIC_API_KEY='sk-kimi-xxxxxx'")
        print("   export ANTHROPIC_BASE_URL='https://api.kimi.com/coding'")
        return False
    
    # 测试API连接
    url = f"{base_url}/v1/messages"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "kimi-coding/k2p5",
        "max_tokens": 100,
        "temperature": 0.7,
        "system": "你是Nexus AI的CEO，简短回答。",
        "messages": [
            {"role": "user", "content": "用一句话介绍你作为CEO的职责。"}
        ]
    }
    
    print(f"\n🔍 测试连接...")
    print(f"   URL: {url}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"   状态码: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    content = data["content"][0]["text"]
                    
                    print("\n✅ 连接成功!")
                    print(f"\n🤖 AI响应:")
                    print(f"   {content}")
                    
                    if "usage" in data:
                        print(f"\n📊 Token用量:")
                        print(f"   输入: {data['usage'].get('input_tokens', 0)}")
                        print(f"   输出: {data['usage'].get('output_tokens', 0)}")
                    
                    return True
                    
                else:
                    error = await response.text()
                    print(f"\n❌ 请求失败:")
                    print(f"   状态码: {response.status}")
                    print(f"   错误: {error[:200]}")
                    return False
                    
    except asyncio.TimeoutError:
        print("\n❌ 连接超时")
        return False
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_setup_guide():
    """打印设置指南"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              配置指南                                         ║
╚══════════════════════════════════════════════════════════════╝

1. 设置环境变量 (当前终端):
   export ANTHROPIC_API_KEY="sk-kimi-xxxxxx"
   export ANTHROPIC_BASE_URL="https://api.kimi.com/coding"
   export KIMI_MODEL="kimi-coding/k2p5"

2. 永久设置 (添加到 ~/.zshrc):
   echo 'export ANTHROPIC_API_KEY="sk-kimi-xxxxxx"' >> ~/.zshrc
   echo 'export ANTHROPIC_BASE_URL="https://api.kimi.com/coding"' >> ~/.zshrc
   source ~/.zshrc

3. 验证设置:
   echo $ANTHROPIC_API_KEY

4. 运行测试:
   python3 test_kimi_coding_api.py

5. 运行多Agent系统:
   python3 company_with_kimi_coding.py

获取API Key:
https://kimi.com (会员页面)
""")


async def main():
    success = await test_kimi_coding_api()
    
    if not success:
        print("\n" + "="*60)
        print("⚠️ 测试失败")
        print("="*60)
        print_setup_guide()
    else:
        print("\n" + "="*60)
        print("✅ 测试通过!")
        print("="*60)
        print("\n🎉 你现在可以运行多Agent系统:")
        print("   python3 company_with_kimi_coding.py")


if __name__ == "__main__":
    asyncio.run(main())
