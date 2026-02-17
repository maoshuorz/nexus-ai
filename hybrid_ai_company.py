#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid AI Company System - 混合AI公司系统
支持真实AI (Kimi API) 和 模拟AI 两种模式
可无缝切换
"""

import os
import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

# 尝试导入Kimi模块，如果失败则使用模拟模式
try:
    from kimi_agent_runner import KimiAgentRunner, KimiAgentFactory
    KIMI_AVAILABLE = True
except ImportError:
    KIMI_AVAILABLE = False

from advanced_company_v3 import AdvancedCompanySystem, Project, ProjectPhase


@dataclass
class AIMode:
    """AI模式配置"""
    use_real_ai: bool = False
    api_key: Optional[str] = None
    simulate_thinking_time: float = 1.0  # 模拟思考时间(秒)


class HybridAgent:
    """
    混合Agent - 支持真实AI和模拟AI
    """
    
    def __init__(self, agent_id: str, name: str, role: str, mode: AIMode):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.mode = mode
        self.avatar = self._get_avatar()
        
        # 真实AI配置
        self.kimi_runner: Optional[KimiAgentRunner] = None
        self._init_real_ai()
        
        # 决策历史
        self.decisions: List[Dict] = []
    
    def _get_avatar(self) -> str:
        """获取角色头像"""
        avatars = {
            "ceo": "👨‍💼",
            "cmo": "👩‍💼",
            "cto": "👨‍💻",
            "coo": "👩‍💻",
            "cpo": "👨‍🎨",
            "cfo": "👩‍💼",
            "chro": "👨‍💼",
            "observer": "🤖"
        }
        return avatars.get(self.agent_id, "🤖")
    
    def _init_real_ai(self):
        """初始化真实AI"""
        if not self.mode.use_real_ai or not KIMI_AVAILABLE:
            return
        
        try:
            config = KimiAgentFactory.create_ceo_agent(self.mode.api_key)
            # 根据角色选择正确的factory方法
            factory_methods = {
                "ceo": KimiAgentFactory.create_ceo_agent,
                "cmo": KimiAgentFactory.create_cmo_agent,
                "cto": KimiAgentFactory.create_cto_agent,
                "cfo": KimiAgentFactory.create_cfo_agent,
                "cpo": KimiAgentFactory.create_cpo_agent,
                "coo": KimiAgentFactory.create_coo_agent,
                "chro": KimiAgentFactory.create_chro_agent
            }
            
            factory_method = factory_methods.get(self.agent_id, KimiAgentFactory.create_ceo_agent)
            config = factory_method(self.mode.api_key)
            
            # 创建runner但不启动session（在think方法中启动）
            self.kimi_runner = KimiAgentRunner(config)
            
        except Exception as e:
            print(f"⚠️ {self.name} AI初始化失败: {e}")
            self.kimi_runner = None
    
    async def think(self, task: str, context: Dict = None) -> Dict:
        """
        Agent思考并做出决策
        
        根据模式选择真实AI或模拟AI
        """
        if self.mode.use_real_ai and self.kimi_runner:
            return await self._real_ai_think(task, context)
        else:
            return await self._simulated_think(task, context)
    
    async def _real_ai_think(self, task: str, context: Dict) -> Dict:
        """使用真实AI思考"""
        try:
            async with self.kimi_runner:
                result = await self.kimi_runner.think(task, context)
                
                # 记录决策
                self.decisions.append({
                    "timestamp": datetime.now().isoformat(),
                    "task": task,
                    "result": result,
                    "mode": "real_ai"
                })
                
                return result
                
        except Exception as e:
            print(f"⚠️ {self.name} 真实AI调用失败: {e}")
            print(f"   切换到模拟模式...")
            return await self._simulated_think(task, context)
    
    async def _simulated_think(self, task: str, context: Dict) -> Dict:
        """使用模拟AI思考"""
        # 模拟思考时间
        await asyncio.sleep(self.mode.simulate_thinking_time)
        
        # 根据角色生成不同的决策风格
        decision = self._generate_role_specific_decision(task, context)
        
        # 记录决策
        self.decisions.append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "result": decision,
            "mode": "simulated"
        })
        
        return decision
    
    def _generate_role_specific_decision(self, task: str, context: Dict) -> Dict:
        """根据角色生成特定风格的决策"""
        
        # 基础决策模板
        base_decision = {
            "decision": "需要更多信息",
            "confidence": random.uniform(0.6, 0.9),
            "reasoning": f"基于{self.role}的专业分析...",
            "action_items": [],
            "risks": [],
            "recommendations": [],
            "budget_request": 0,
            "timeline_days": 30,
            "team_requirements": []
        }
        
        # 根据角色定制
        if self.agent_id == "ceo":
            base_decision.update({
                "decision": random.choice(["批准", "需要讨论", "拒绝"]),
                "confidence": random.uniform(0.7, 0.95),
                "reasoning": "从战略角度考虑，这个项目符合公司长期发展方向。需要评估风险与回报的平衡。",
                "budget_request": random.randint(300000, 1000000)
            })
            
        elif self.agent_id == "cmo":
            opportunities = context.get("opportunity", {})
            market_size = opportunities.get("market_size", "Unknown")
            
            base_decision.update({
                "decision": "建议进入" if random.random() > 0.3 else "需要更多调研",
                "confidence": random.uniform(0.65, 0.9),
                "reasoning": f"市场规模{market_size}，增长潜力良好。建议快速验证MVP。",
                "recommendations": [
                    "进行用户调研验证需求",
                    "分析竞品差异化策略",
                    "制定GTM策略"
                ]
            })
            
        elif self.agent_id == "cto":
            base_decision.update({
                "decision": "技术上可行" if random.random() > 0.2 else "存在技术挑战",
                "confidence": random.uniform(0.7, 0.95),
                "reasoning": "技术栈选择合理，团队具备相关技能。建议采用微服务架构。",
                "risks": [
                    "AI模型训练需要大量数据",
                    "系统扩展性需要验证"
                ],
                "team_requirements": ["AI工程师", "后端工程师", "DevOps"]
            })
            
        elif self.agent_id == "cfo":
            roi = random.uniform(1.5, 4.0)
            base_decision.update({
                "decision": "财务上可行" if roi > 2.0 else "需要优化成本",
                "confidence": random.uniform(0.7, 0.9),
                "reasoning": f"预计ROI为{roi:.1f}x，投资回报期约18个月。现金流需要关注。",
                "budget_request": random.randint(200000, 800000),
                "risks": [
                    "市场变化可能影响收入预期",
                    "开发成本可能超支"
                ]
            })
            
        elif self.agent_id == "cpo":
            base_decision.update({
                "decision": "产品有市场" if random.random() > 0.3 else "需要产品调整",
                "confidence": random.uniform(0.65, 0.9),
                "reasoning": "用户需求明确，产品差异化有机会。建议聚焦核心功能。",
                "recommendations": [
                    "进行用户访谈",
                    "设计MVP功能集",
                    "制定产品路线图"
                ]
            })
            
        elif self.agent_id == "coo":
            base_decision.update({
                "decision": "运营上可行",
                "confidence": random.uniform(0.7, 0.9),
                "reasoning": "运营流程可设计，团队可以支撑。建议分阶段推进。",
                "action_items": [
                    "设计运营SOP",
                    "招聘运营人员",
                    "建立监控体系"
                ]
            })
            
        elif self.agent_id == "chro":
            base_decision.update({
                "decision": "团队可以支撑",
                "confidence": random.uniform(0.7, 0.9),
                "reasoning": "现有团队技能匹配度70%，需要补充AI和运营人才。",
                "team_requirements": ["AI工程师x2", "产品经理x1", "运营专员x2"]
            })
        
        return base_decision


class HybridAICompanySystem(AdvancedCompanySystem):
    """
    混合AI公司系统
    支持真实AI和模拟AI无缝切换
    """
    
    def __init__(self, company_name: str = "Nexus AI", mode: AIMode = None):
        super().__init__(company_name)
        
        # AI模式
        self.mode = mode or AIMode(use_real_ai=False)
        
        # 创建混合Agent团队
        self.hybrid_agents: Dict[str, HybridAgent] = {}
        self._init_hybrid_agents()
        
        # 系统状态
        self.ai_stats = {
            "real_ai_calls": 0,
            "simulated_calls": 0,
            "total_decisions": 0
        }
        
        print(f"🚀 混合AI公司系统已启动: {company_name}")
        print(f"   模式: {'真实AI' if self.mode.use_real_ai else '模拟AI'}")
    
    def _init_hybrid_agents(self):
        """初始化混合Agent团队"""
        agent_configs = [
            ("ceo", "Alex Chen", "CEO"),
            ("cmo", "Sarah Miller", "CMO"),
            ("cto", "David Kim", "CTO"),
            ("coo", "Emma Wilson", "COO"),
            ("cpo", "Michael Zhang", "CPO"),
            ("cfo", "Lisa Wang", "CFO"),
            ("chro", "James Brown", "CHRO"),
        ]
        
        for agent_id, name, role in agent_configs:
            self.hybrid_agents[agent_id] = HybridAgent(agent_id, name, role, self.mode)
        
        print(f"   已初始化 {len(self.hybrid_agents)} 个混合Agent")
    
    async def run_hybrid_simulation(self, days: int = 3):
        """运行混合AI模拟"""
        print(f"\n{'='*70}")
        print(f"🚀 启动混合AI模拟 - {days} 天")
        print(f"{'='*70}")
        
        for day in range(1, days + 1):
            self.metrics["day"] = day
            
            print(f"\n📅 Day {day}")
            print("-" * 50)
            
            # 1. 混合AI CMO扫描市场
            opportunities = await self._hybrid_cmo_scan()
            
            # 2. 评估机会
            for opp in opportunities[:2]:
                await self._hybrid_evaluate_opportunity(opp)
            
            # 3. 管理项目
            await self._hybrid_manage_projects()
            
            # 4. 生成报告
            await self._hybrid_daily_report()
            
            print(f"\n✅ Day {day} 完成")
            await asyncio.sleep(0.5)
        
        self._print_hybrid_summary()
    
    async def _hybrid_cmo_scan(self) -> List[Dict]:
        """混合AI CMO市场扫描"""
        print("\n📊 CMO分析市场...")
        
        cmo = self.hybrid_agents["cmo"]
        
        result = await cmo.think(
            task="分析AI市场趋势，识别3个最有潜力的创业机会",
            context={
                "current_projects": list(self.projects.keys()),
                "cash_position": self.financials["cash_flow"]
            }
        )
        
        # 更新统计
        self.ai_stats["total_decisions"] += 1
        if result.get("mode") == "real_ai":
            self.ai_stats["real_ai_calls"] += 1
        else:
            self.ai_stats["simulated_calls"] += 1
        
        print(f"   🤖 CMO ({result.get('mode')}): {result.get('decision')}")
        
        # 生成机会
        opportunities = []
        for i in range(3):
            opp = {
                "id": f"opp_{self.metrics['day']}_{i}",
                "name": f"AI机会{i+1}: {random.choice(['内容创作', '客服自动化', '数据分析', '代码生成'])}",
                "description": result.get('reasoning', '')[:100],
                "market_size": random.randint(50, 500) * 1000000,
                "confidence": result.get('confidence', 0.7)
            }
            opportunities.append(opp)
        
        return opportunities
    
    async def _hybrid_evaluate_opportunity(self, opportunity: Dict):
        """混合AI评估机会"""
        print(f"\n🔍 评估: {opportunity['name']}")
        
        project = Project(
            id=f"proj_{opportunity['id']}",
            name=opportunity['name'],
            description=opportunity['description'],
            phase=ProjectPhase.DISCOVERY
        )
        
        # 并行收集评估
        async def evaluate(agent_id: str, aspect: str) -> Dict:
            agent = self.hybrid_agents[agent_id]
            result = await agent.think(
                task=f"从{aspect}角度评估项目",
                context={"opportunity": opportunity}
            )
            self.ai_stats["total_decisions"] += 1
            return result
        
        print("   ⏳ 并行评估...")
        results = await asyncio.gather(
            evaluate("cto", "技术"),
            evaluate("cfo", "财务"),
            evaluate("cpo", "产品")
        )
        
        cto_result, cfo_result, cpo_result = results
        
        # CEO决策
        print("\n👔 CEO决策...")
        ceo = self.hybrid_agents["ceo"]
        
        final_result = await ceo.think(
            task="基于各部门评估，做出投资决策",
            context={
                "opportunity": opportunity,
                "evaluations": {"cto": cto_result, "cfo": cfo_result, "cpo": cpo_result}
            }
        )
        
        self.ai_stats["total_decisions"] += 1
        
        # 解析决策
        decision_text = final_result.get('decision', '').lower()
        approved = any(word in decision_text for word in ['批准', '通过', 'approved', '同意'])
        
        budget = final_result.get('budget_request', random.randint(300000, 800000))
        
        print(f"   ✅ 决策: {'批准' if approved else '拒绝'}")
        print(f"   💵 预算: ¥{budget:,}")
        
        if approved:
            project.budget = budget
            project.phase = ProjectPhase.PLANNING
            self.projects[project.id] = project
            print(f"   🚀 项目启动: {project.name}")
    
    async def _hybrid_manage_projects(self):
        """混合AI管理项目"""
        if not self.projects:
            return
        
        print("\n🚀 管理项目...")
        
        for project in self.projects.values():
            if project.status != "active":
                continue
            
            # COO评估
            coo = self.hybrid_agents["coo"]
            result = await coo.think(
                task=f"评估项目'{project.name}'进度",
                context={"project": {"name": project.name, "progress": project.progress}}
            )
            
            # 更新进度
            if "推进" in result.get('decision', ''):
                project.progress = min(100, project.progress + random.randint(15, 30))
            
            # 消耗预算
            daily_cost = project.budget * 0.005
            project.spent += daily_cost
            self.financials["cash_flow"] -= daily_cost
            
            print(f"   📊 {project.name}: {project.progress:.0f}%")
    
    async def _hybrid_daily_report(self):
        """混合AI日报"""
        print("\n📋 生成日报...")
        
        observer = self.hybrid_agents.get("observer")
        if not observer:
            print(f"   Day {self.metrics['day']} 完成 | 项目: {len(self.projects)} | 现金: ¥{self.financials['cash_flow']:,.0f}")
            return
        
        result = await observer.think(
            task="总结今日运营",
            context={"metrics": self.metrics, "projects": len(self.projects)}
        )
        
        print(f"   📝 {result.get('reasoning', '运营正常')[:80]}...")
    
    def _print_hybrid_summary(self):
        """打印混合AI总结"""
        print(f"\n{'='*70}")
        print("📊 混合AI模拟总结")
        print(f"{'='*70}")
        
        print(f"\n🤖 AI统计:")
        print(f"   总决策数: {self.ai_stats['total_decisions']}")
        print(f"   真实AI调用: {self.ai_stats['real_ai_calls']}")
        print(f"   模拟AI调用: {self.ai_stats['simulated_calls']}")
        
        print(f"\n💰 财务:")
        print(f"   现金流: ¥{self.financials['cash_flow']:,.0f}")
        print(f"   总支出: ¥{self.financials['total_expenses']:,.0f}")
        
        print(f"\n📁 项目:")
        print(f"   项目数: {len(self.projects)}")
        for p in self.projects.values():
            print(f"   - {p.name}: {p.progress:.0f}%")
        
        print(f"\n👥 团队:")
        print(f"   满意度: {self.metrics.get('employee_satisfaction', 100):.1f}%")


# ============== 运行示例 ==============

async def main():
    """主函数"""
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         混合AI公司系统                                       ║")
    print("║         支持真实Kimi AI + 模拟AI                             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # 检查API Key
    api_key = os.getenv("KIMI_API_KEY")
    
    if api_key:
        print("\n✅ 检测到KIMI_API_KEY")
        print(f"   Key: {api_key[:20]}...")
        
        # 尝试使用真实AI
        mode = AIMode(use_real_ai=True, api_key=api_key, simulate_thinking_time=1.0)
        
        print("\n🔄 尝试启动真实AI模式...")
        print("   如果API调用失败，将自动切换到模拟模式\n")
        
    else:
        print("\n⚠️ 未检测到KIMI_API_KEY")
        print("   使用模拟AI模式运行\n")
        
        mode = AIMode(use_real_ai=False, simulate_thinking_time=0.5)
    
    # 创建系统
    company = HybridAICompanySystem("Nexus AI Hybrid", mode)
    
    # 运行模拟
    await company.run_hybrid_simulation(days=3)
    
    print("\n" + "="*70)
    print("✅ 模拟完成!")
    print("="*70)
    
    print("\n💡 提示:")
    print("   如需使用真实AI，请设置环境变量:")
    print("   export KIMI_API_KEY='your-api-key'")
    print("\n   然后重新运行:")
    print("   python3 hybrid_ai_company.py")


if __name__ == "__main__":
    asyncio.run(main())
