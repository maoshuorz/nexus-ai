#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kimi-Coding/K2P5 API 测试脚本
专门测试 kimi-coding/k2p5 模型连接
"""

import os
import asyncio
import aiohttp

# 可能的API端点配置
API_ENDPOINTS = [
    {
        "name": "Moonshot Official",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "kimi-coding/k2p5"
    },
    {
        "name": "Moonshot (alternative)",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "kimi-k2p5"  # 可能的别名
    },
    {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "model": "kimi-coding/k2p5"
    }
]

async def test_endpoint(endpoint: dict, api_key: str) -> dict:
    """测试单个API端点"""
    
    print(f"\n🔍 测试: {endpoint['name']}")
    print(f"   URL: {endpoint['base_url']}")
    print(f"   Model: {endpoint['model']}")
    
    url = f"{endpoint['base_url']}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": endpoint['model'],
        "messages": [
            {"role": "system", "content": "你是一个CEO，简短介绍你的职责。"},
            {"role": "user", "content": "用一句话介绍你作为CEO的职责。"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return {
                        "success": True,
                        "endpoint": endpoint,
                        "content": content,
                        "usage": data.get("usage", {})
                    }
                    
                elif response.status == 401:
                    error = await response.text()
                    return {
                        "success": False,
                        "endpoint": endpoint,
                        "error": "Unauthorized - API Key无效",
                        "details": error
                    }
                    
                elif response.status == 404:
                    error = await response.text()
                    return {
                        "success": False,
                        "endpoint": endpoint,
                        "error": "Model not found - 模型不存在",
                        "details": error
                    }
                    
                else:
                    error = await response.text()
                    return {
                        "success": False,
                        "endpoint": endpoint,
                        "error": f"HTTP {response.status}",
                        "details": error
                    }
                    
    except asyncio.TimeoutError:
        return {
            "success": False,
            "endpoint": endpoint,
            "error": "Timeout - 连接超时"
        }
    except Exception as e:
        return {
            "success": False,
            "endpoint": endpoint,
            "error": str(e)
        }


async def test_k2p5_connection():
    """测试 k2p5 模型连接"""
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     Kimi-Coding/K2P5 API 连接测试                           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # 获取API Key
    api_key = os.getenv("KIMI_API_KEY")
    
    if not api_key:
        print("\n❌ 错误: 未找到 KIMI_API_KEY 环境变量")
        print("\n请设置环境变量:")
        print('  export KIMI_API_KEY="your-api-key"')
        return
    
    print(f"\n📝 API Key: {api_key[:15]}...{api_key[-10:]}")
    
    # 测试所有端点
    results = []
    for endpoint in API_ENDPOINTS:
        result = await test_endpoint(endpoint, api_key)
        results.append(result)
        
        if result["success"]:
            print(f"   ✅ 成功!")
            print(f"   🤖 响应: {result['content'][:80]}...")
            if result.get('usage'):
                print(f"   📊 Tokens: {result['usage']}")
        else:
            print(f"   ❌ 失败: {result['error']}")
            if result.get('details'):
                print(f"   📄 详情: {result['details'][:200]}")
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试结果总结")
    print("="*60)
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    print(f"\n✅ 成功: {len(successful)}/{len(results)}")
    for r in successful:
        print(f"   • {r['endpoint']['name']}: {r['endpoint']['model']}")
    
    if failed:
        print(f"\n❌ 失败: {len(failed)}/{len(results)}")
        for r in failed:
            print(f"   • {r['endpoint']['name']}: {r['error']}")
    
    # 推荐配置
    if successful:
        best = successful[0]
        print("\n" + "="*60)
        print("💡 推荐配置")
        print("="*60)
        print(f"""
API_BASE_URL = "{best['endpoint']['base_url']}"
MODEL = "{best['endpoint']['model']}"
API_KEY = "your-api-key"

添加到 ~/.zshrc:
export KIMI_API_KEY="{api_key}"
export KIMI_BASE_URL="{best['endpoint']['base_url']}"
export KIMI_MODEL="{best['endpoint']['model']}"
""")
    else:
        print("\n" + "="*60)
        print("⚠️ 所有端点测试失败")
        print("="*60)
        print("""
可能的解决方案:
1. 确认API Key是否正确
2. 检查API Key是否过期
3. 确认账户余额充足
4. 联系Kimi/Moonshot技术支持
5. 尝试不同的API端点

获取新API Key:
https://platform.moonshot.cn
""")


def print_api_info():
    """打印API信息"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              Kimi-Coding/K2P5 API 信息                        ║
╚══════════════════════════════════════════════════════════════╝

官方文档: https://platform.moonshot.cn/docs

模型名称: kimi-coding/k2p5
API格式: OpenAI兼容格式
认证方式: Bearer Token

示例请求:
curl https://api.moonshot.cn/v1/chat/completions \\
  -H "Authorization: Bearer $KIMI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "kimi-coding/k2p5",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'

Python示例:
import openai

client = openai.OpenAI(
    api_key="your-api-key",
    base_url="https://api.moonshot.cn/v1"
)

response = client.chat.completions.create(
    model="kimi-coding/k2p5",
    messages=[{"role": "user", "content": "Hello"}]
)
""")


async def main():
    """主函数"""
    await test_k2p5_connection()
    print_api_info()


if __name__ == "__main__":
    asyncio.run(main())
