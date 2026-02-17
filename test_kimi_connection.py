#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kimi API 连接测试脚本
验证API Key和连接是否正常
"""

import os
import asyncio
import aiohttp

async def test_kimi_connection():
    """测试Kimi API连接"""
    
    # 获取API Key
    api_key = os.getenv("KIMI_API_KEY")
    
    if not api_key:
        print("❌ 错误: 未找到KIMI_API_KEY环境变量")
        print("\n请设置环境变量:")
        print("  export KIMI_API_KEY='sk-kimi-I6opLore8BAYYOXt7B8zufYTBIG9VCSY7aR4cddqUxszmpVqA4tQEwZpSFlczkYq'")
        return False
    
    print(f"📝 API Key: {api_key[:20]}...{api_key[-10:]}")
    print("\n🔍 测试连接...")
    
    # 测试API调用
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "kimi-coding/k2p5",
        "messages": [
            {"role": "system", "content": "你是Nexus AI Technologies的CEO，请简短自我介绍。"},
            {"role": "user", "content": "请用一句话介绍你的角色和职责。"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    print("✅ API连接成功!")
                    print(f"\n🤖 AI响应:")
                    print(f"   {content}")
                    
                    # 显示用量信息
                    usage = data.get("usage", {})
                    print(f"\n📊 Token用量:")
                    print(f"   输入: {usage.get('prompt_tokens', 0)} tokens")
                    print(f"   输出: {usage.get('completion_tokens', 0)} tokens")
                    print(f"   总计: {usage.get('total_tokens', 0)} tokens")
                    
                    return True
                    
                elif response.status == 401:
                    print("❌ 错误: API Key无效或已过期")
                    print("   请检查KIMI_API_KEY是否正确")
                    return False
                    
                elif response.status == 429:
                    print("❌ 错误: API请求过于频繁")
                    print("   请稍后再试")
                    return False
                    
                else:
                    error_text = await response.text()
                    print(f"❌ 错误: HTTP {response.status}")
                    print(f"   {error_text}")
                    return False
                    
    except aiohttp.ClientError as e:
        print(f"❌ 网络错误: {e}")
        print("   请检查网络连接")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


async def test_multi_agent():
    """测试多Agent协作"""
    
    print("\n" + "="*60)
    print("🚀 测试多Agent协作")
    print("="*60)
    
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ 未设置API Key")
        return
    
    from kimi_agent_runner import KimiAgentRunner, KimiAgentFactory
    
    # 测试CMO和CTO协作
    print("\n📊 测试CMO市场分析...")
    
    cmo_config = KimiAgentFactory.create_cmo_agent(api_key)
    
    async with KimiAgentRunner(cmo_config) as cmo:
        result = await cmo.think(
            task="分析AI客服市场的潜力和机会",
            context={"market": "AI客服", "budget": 1000000}
        )
        
        print(f"✅ CMO分析完成")
        print(f"   决策: {result.get('decision')}")
        print(f"   信心度: {result.get('confidence')}")
        print(f"   建议: {result.get('recommendations', [])[:2]}")


def print_setup_guide():
    """打印设置指南"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Kimi API 设置指南                                ║
╚══════════════════════════════════════════════════════════════╝

1. 设置环境变量 (当前终端):
   export KIMI_API_KEY="sk-kimi-I6opLore8BAYYOXt7B8zufYTBIG9VCSY7aR4cddqUxszmpVqA4tQEwZpSFlczkYq"

2. 永久设置 (添加到 ~/.zshrc 或 ~/.bash_profile):
   echo 'export KIMI_API_KEY="sk-kimi-I6opLore8BAYYOXt7B8zufYTBIG9VCSY7aR4cddqUxszmpVqA4tQEwZpSFlczkYq"' >> ~/.zshrc
   source ~/.zshrc

3. 验证设置:
   echo $KIMI_API_KEY

4. 运行测试:
   python3 test_kimi_connection.py

5. 运行完整演示:
   python3 real_ai_company.py
""")


async def main():
    """主函数"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         Kimi API 连接测试工具                                ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # 测试连接
    success = await test_kimi_connection()
    
    if success:
        # 测试多Agent
        await test_multi_agent()
        
        print("\n" + "="*60)
        print("✅ 所有测试通过!")
        print("="*60)
        print("\n🎉 你现在可以运行真实AI公司系统:")
        print("   python3 real_ai_company.py")
    else:
        print("\n" + "="*60)
        print("❌ 测试失败")
        print("="*60)
        print_setup_guide()


if __name__ == "__main__":
    asyncio.run(main())
