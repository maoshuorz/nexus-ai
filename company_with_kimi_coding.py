#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Company System with Kimi Coding
使用Kimi Coding (Anthropic兼容API) 的真实AI多Agent公司系统
"""

import os
import asyncio
import random
from datetime import datetime
from typing import Dict, List

# 导入Kimi Coding Runner
from kimi_coding_runner import KimiCodingRunner, KimiCodingFactory, KimiCodingConfig

# 导入基础公司系统
from advanced_company_v3 import (
    AdvancedCompanySystem, Project, ProjectPhase, 
    Task, TaskPriority, Agent, AgentState
)


class KimiCodingCompanySystem(AdvancedCompanySystem):
    """
    使用Kimi Coding的真实AI公司系统
    """
    
    def __init__(self, company_name: str = "Nexus AI"):
        super().__init__(company_name)
        
        # 获取API配置
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding")
        self.model = os.getenv("KIMI_MODEL", "kimi-coding/k2p5")
        
        if not self.api_key:
            raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")
        
        # 初始化AI Agent
        self._init_kimi_agents()
        
        # AI决策统计
        self.ai_stats = {
            "total_calls": 0,
            "success_calls": 0,
            "failed_calls": 0,
            "total_tokens": 0
        }
        
        print(f"🚀 Kimi Coding AI公司系统已启动: {company_name}")
        print(f"   Model: {self.model}")
        print(f"   Base URL: {self.base_url}")
        print(f"   API Key: {self.api_key[:15]}...")
    
    def _init_kimi_agents(self):
        """初始化Kimi Coding Agents"""
        self.kimi_configs: Dict[str, KimiCodingConfig] = {}
        
        factory = KimiCodingFactory
        
        self.kimi_configs = {
            "ceo": factory.create_ceo_agent(self.api_key),
            "cmo": factory.create_cmo_agent(self.api_key),
            "cto": factory.create_cto_agent(self.api_key),
        }
        
        # 统一设置base_url
        for config in self.kimi_configs.values():
            config.base_url = self.base_url
            config.model = self.model
        
        print(f"   已初始化 {len(self.kimi_configs)} 个Kimi Coding Agents")
    
    async def run_kimi_simulation(self, days: int = 3):
        """运行Kimi Coding驱动的模拟"""
        print(f"\n{'='*70}")
        print(f"🚀 启动Kimi Coding AI模拟 - {days} 天")
        print(f"{'='*70}")
        
        for day in range(1, days + 1):
            self.metrics["day"] = day
            
            print(f"\n📅 Day {day}")
            print("-" * 50)
            
            # 1. AI CMO市场扫描
            opportunities = await self._kimi_cmo_scan()
            
            # 2. 评估机会
            for opp in opportunities[:2]:
                await self._kimi_evaluate_opportunity(opp)
            
            # 3. 管理项目
            await self._kimi_manage_projects()
            
            # 4. 生成报告
            await self._kimi_daily_report()
            
            print(f"\n✅ Day {day} 完成")
            await asyncio.sleep(0.5)
        
        self._print_kimi_summary()
    
    async def _kimi_cmo_scan(self) -> List[Dict]:
        """Kimi Coding CMO市场扫描"""
        print("\n📊 Kimi CMO分析市场...")
        
        config = self.kimi_configs["cmo"]
        
        async with KimiCodingRunner(config) as cmo:
            result = await cmo.think(
                task="分析当前AI市场趋势，识别3个最有潜力的创业机会",
                context={
                    "current_projects": [p.name for p in self.projects.values()],
                    "cash_position": self.financials["cash_flow"],
                    "market_trends": ["AI Agent", "生成式AI", "自动化工具"]
                }
            )
            
            self.ai_stats["total_calls"] += 1
            if "reasoning" in result:
                self.ai_stats["success_calls"] += 1
            
            print(f"   🤖 Kimi CMO: {result.get('decision', '分析完成')}")
            print(f"   📈 信心度: {result.get('confidence', 0)}")
            
            # 生成机会
            opportunities = []
            recommendations = result.get('recommendations', [])
            
            for i in range(3):
                opp = {
                    "id": f"kimi_opp_{self.metrics['day']}_{i}",
                    "name": f"AI机会{i+1}: {random.choice(['Agent平台', '代码助手', '内容生成'])}",
                    "description": result.get('reasoning', 'AI分析的机会')[:100],
                    "market_size": random.randint(50, 500) * 1000000,
                    "confidence": result.get('confidence', 0.7)
                }
                opportunities.append(opp)
                print(f"   💡 {opp['name']}")
            
            return opportunities
    
    async def _kimi_evaluate_opportunity(self, opportunity: Dict):
        """Kimi多Agent评估机会"""
        print(f"\n🔍 Kimi团队评估: {opportunity['name']}")
        
        project = Project(
            id=f"kimi_proj_{opportunity['id']}",
            name=opportunity['name'],
            description=opportunity['description'],
            phase=ProjectPhase.DISCOVERY
        )
        
        # Kimi CTO评估
        print("   💻 Kimi CTO技术评估...")
        cto_config = self.kimi_configs["cto"]
        
        async with KimiCodingRunner(cto_config) as cto:
            cto_result = await cto.think(
                task=f"评估'{opportunity['name']}'的技术可行性",
                context={
                    "opportunity": opportunity,
                    "tech_stack": ["Python", "AI/ML", "Cloud"]
                }
            )
            self.ai_stats["total_calls"] += 1
            print(f"      {cto_result.get('decision')} (置信度: {cto_result.get('confidence')})")
        
        # Kimi CEO决策
        print("\n👔 Kimi CEO决策...")
        ceo_config = self.kimi_configs["ceo"]
        
        async with KimiCodingRunner(ceo_config) as ceo:
            final_result = await ceo.think(
                task=f"基于CTO评估，决定是否投资'{opportunity['name']}'",
                context={
                    "opportunity": opportunity,
                    "cto_assessment": cto_result,
                    "company_cash": self.financials["cash_flow"]
                }
            )
            self.ai_stats["total_calls"] += 1
        
        # 解析决策
        decision_text = final_result.get('decision', '').lower()
        approved = any(word in decision_text for word in ['批准', '通过', 'approved', '同意', 'invest'])
        
        budget = final_result.get('budget_request', random.randint(300000, 800000))
        
        print(f"   ✅ Kimi CEO决策: {'批准' if approved else '拒绝'}")
        print(f"   💵 预算: ¥{budget:,}")
        print(f"   📝 理由: {final_result.get('reasoning', '')[:80]}...")
        
        if approved:
            project.budget = budget
            project.phase = ProjectPhase.PLANNING
            self.projects[project.id] = project
            print(f"   🚀 项目启动: {project.name}")
    
    async def _kimi_manage_projects(self):
        """Kimi管理项目"""
        if not self.projects:
            return
        
        print("\n🚀 Kimi管理项目...")
        
        for project in self.projects.values():
            if project.status != "active":
                continue
            
            # 模拟进度更新
            project.progress = min(100, project.progress + random.randint(10, 25))
            
            # 消耗预算
            daily_cost = project.budget * 0.005
            project.spent += daily_cost
            self.financials["cash_flow"] -= daily_cost
            
            print(f"   📊 {project.name}: {project.progress:.0f}%")
    
    async def _kimi_daily_report(self):
        """生成日报"""
        print(f"\n📋 Day {self.metrics['day']} 完成")
        print(f"   项目数: {len(self.projects)}")
        print(f"   现金: ¥{self.financials['cash_flow']:,.0f}")
    
    def _print_kimi_summary(self):
        """打印Kimi模拟总结"""
        print(f"\n{'='*70}")
        print("📊 Kimi Coding AI模拟总结")
        print(f"{'='*70}")
        
        print(f"\n🤖 AI调用统计:")
        print(f"   总调用: {self.ai_stats['total_calls']}")
        print(f"   成功: {self.ai_stats['success_calls']}")
        print(f"   失败: {self.ai_stats['failed_calls']}")
        
        print(f"\n💰 财务:")
        print(f"   现金流: ¥{self.financials['cash_flow']:,.0f}")
        
        print(f"\n📁 项目:")
        print(f"   项目数: {len(self.projects)}")
        for p in self.projects.values():
            print(f"   - {p.name}: {p.progress:.0f}%")


# ============== 运行入口 ==============

async def main():
    """主函数"""
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         Kimi Coding 真实AI多Agent公司系统                    ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # 检查配置
    api_key = os.getenv("ANTHROPIC_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding")
    
    if not api_key:
        print("\n❌ 错误: 未设置 ANTHROPIC_API_KEY")
        print("\n请运行:")
        print("   export ANTHROPIC_API_KEY='sk-kimi-xxxxxx'")
        print("   export ANTHROPIC_BASE_URL='https://api.kimi.com/coding'")
        return
    
    print(f"\n✅ 配置检查通过")
    print(f"   API Key: {api_key[:15]}...")
    print(f"   Base URL: {base_url}")
    
    try:
        # 创建系统
        company = KimiCodingCompanySystem("Nexus AI with Kimi Coding")
        
        # 运行模拟
        await company.run_kimi_simulation(days=2)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
