#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 Kimi Coding 多Agent协作
"""

import os
import asyncio
import sys

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kimi_coding_runner import KimiCodingRunner, KimiCodingFactory

async def quick_test():
    """快速测试"""
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     Kimi Coding 多Agent快速测试                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # 检查配置
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding")
    
    if not api_key:
        print("\n❌ 未设置 ANTHROPIC_API_KEY")
        return
    
    print(f"\n✅ 配置:")
    print(f"   Base URL: {base_url}")
    print(f"   API Key: {api_key[:15]}...")
    
    # 测试1: CMO市场分析
    print("\n" + "="*60)
    print("📊 测试1: CMO市场分析")
    print("="*60)
    
    cmo_config = KimiCodingFactory.create_cmo_agent()
    cmo_config.base_url = base_url
    
    try:
        async with KimiCodingRunner(cmo_config) as cmo:
            print("   🧠 CMO思考中...")
            result = await cmo.think(
                task="分析AI Agent市场，识别最有潜力的创业机会",
                context={
                    "market_trends": ["AI Agent", "AutoGPT", "多Agent系统"],
                    "budget": 1000000
                }
            )
            
            print(f"   ✅ CMO分析完成")
            print(f"   📈 决策: {result.get('decision')}")
            print(f"   💡 建议: {result.get('recommendations', [])[:2]}")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试2: CEO决策
    print("\n" + "="*60)
    print("👔 测试2: CEO投资决策")
    print("="*60)
    
    ceo_config = KimiCodingFactory.create_ceo_agent()
    ceo_config.base_url = base_url
    
    try:
        async with KimiCodingRunner(ceo_config) as ceo:
            print("   🧠 CEO思考中...")
            result = await ceo.think(
                task="基于CMO分析，决定是否投资AI Agent平台项目，预算50万元",
                context={
                    "opportunity": "AI Agent协作平台",
                    "market_size": "100亿美元",
                    "competitors": ["AutoGPT", "MetaGPT"],
                    "company_cash": 2000000
                }
            )
            
            print(f"   ✅ CEO决策完成")
            print(f"   🎯 决策: {result.get('decision')}")
            print(f"   💵 预算: ¥{result.get('budget_request', 0):,}")
            print(f"   📝 理由: {result.get('reasoning', '')[:100]}...")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 测试3: CTO技术评估
    print("\n" + "="*60)
    print("💻 测试3: CTO技术评估")
    print("="*60)
    
    cto_config = KimiCodingFactory.create_cto_agent()
    cto_config.base_url = base_url
    
    try:
        async with KimiCodingRunner(cto_config) as cto:
            print("   🧠 CTO思考中...")
            result = await cto.think(
                task="评估构建AI Agent平台的技术可行性",
                context={
                    "tech_requirements": ["LLM集成", "多Agent协调", "API设计"],
                    "team_skills": ["Python", "AI/ML", "Backend"]
                }
            )
            
            print(f"   ✅ CTO评估完成")
            print(f"   🔧 评估: {result.get('decision')}")
            print(f"   ⚠️ 风险: {result.get('risks', [])[:2]}")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print("\n" + "="*60)
    print("✅ 所有测试完成!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(quick_test())
