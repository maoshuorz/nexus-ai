#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real AI Company System - 真实AI公司系统
集成Kimi K2.5模型的完整示例
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional

# 导入Kimi Agent模块
from kimi_agent_runner import KimiAgentRunner, KimiAgentFactory, KimiAgentConfig

# 导入基础公司系统
from advanced_company_v3 import AdvancedCompanySystem, Project, ProjectPhase, Task, TaskPriority


class RealAICompanySystem(AdvancedCompanySystem):
    """
    使用真实AI Agent的公司系统
    继承自AdvancedCompanySystem，将模拟决策替换为真实AI决策
    """
    
    def __init__(self, company_name: str = "Nexus AI"):
        super().__init__(company_name)
        
        # 获取API Key
        self.api_key = os.getenv("KIMI_API_KEY")
        if not self.api_key:
            raise ValueError("请设置KIMI_API_KEY环境变量")
        
        # 初始化AI Agent配置
        self._init_ai_agents()
        
        # AI决策记录
        self.ai_decisions: List[Dict] = []
        
        print(f"🤖 真实AI公司系统已启动: {company_name}")
        print(f"   API Key: {self.api_key[:20]}...")
    
    def _init_ai_agents(self):
        """初始化所有AI Agent配置"""
        factory = KimiAgentFactory
        
        self.ai_configs = {
            "ceo": factory.create_ceo_agent(self.api_key),
            "cmo": factory.create_cmo_agent(self.api_key),
            "cto": factory.create_cto_agent(self.api_key),
            "cfo": factory.create_cfo_agent(self.api_key),
            "cpo": factory.create_cpo_agent(self.api_key),
            "coo": factory.create_coo_agent(self.api_key),
            "chro": factory.create_chro_agent(self.api_key),
        }
        
        print(f"   已初始化 {len(self.ai_configs)} 个AI Agent")
    
    async def run_ai_simulation(self, days: int = 1):
        """运行AI驱动的模拟"""
        print(f"\n{'='*70}")
        print(f"🚀 启动AI驱动模拟 - {days} 天")
        print(f"{'='*70}")
        
        for day in range(1, days + 1):
            self.metrics["day"] = day
            
            print(f"\n📅 Day {day} - AI Agent工作模式")
            print("-" * 50)
            
            # 1. AI CMO扫描市场
            opportunities = await self._ai_cmo_market_scan()
            
            # 2. 对每个机会进行AI评估
            for opp in opportunities[:2]:  # 限制每天评估2个
                await self._ai_evaluate_opportunity(opp)
            
            # 3. AI管理项目执行
            await self._ai_manage_projects()
            
            # 4. AI HR管理
            await self._ai_hr_management()
            
            # 5. 生成日报
            await self._ai_daily_report()
            
            print(f"\n✅ Day {day} 完成")
            await asyncio.sleep(1)
        
        # 输出总结
        self._print_summary()
    
    async def _ai_cmo_market_scan(self) -> List[Dict]:
        """AI CMO扫描市场"""
        print("\n📊 AI CMO正在分析市场...")
        
        config = self.ai_configs["cmo"]
        
        async with KimiAgentRunner(config) as cmo:
            result = await cmo.think(
                task="分析当前AI市场趋势，识别最有潜力的3个创业机会。考虑：市场规模、增长趋势、竞争格局、进入壁垒",
                context={
                    "company": self.company_name,
                    "current_projects": [
                        {"name": p.name, "phase": p.phase.value, "progress": p.progress}
                        for p in self.projects.values()
                    ],
                    "cash_position": self.financials["cash_flow"],
                    "existing_products": ["AI内容平台", "自动化工具"]
                }
            )
            
            print(f"   🤖 CMO决策: {result.get('decision')}")
            print(f"   📈 信心度: {result.get('confidence', 0)}")
            
            # 从AI响应中提取机会
            opportunities = []
            recommendations = result.get('recommendations', [])
            
            for i, rec in enumerate(recommendations[:3]):
                opp = {
                    "id": f"ai_opp_{self.metrics['day']}_{i}",
                    "name": rec if isinstance(rec, str) else rec.get('name', f'机会{i+1}'),
                    "description": result.get('reasoning', '')[:200],
                    "confidence": result.get('confidence', 0.7),
                    "market_size": random.randint(50, 500) * 1000000
                }
                opportunities.append(opp)
                print(f"   💡 发现机会: {opp['name']}")
            
            # 记录决策
            self.ai_decisions.append({
                "timestamp": datetime.now().isoformat(),
                "agent": "CMO",
                "type": "market_scan",
                "result": result
            })
            
            return opportunities
    
    async def _ai_evaluate_opportunity(self, opportunity: Dict):
        """AI多Agent评估机会"""
        print(f"\n🔍 AI团队评估: {opportunity['name']}")
        
        # 创建项目
        project = Project(
            id=f"ai_proj_{opportunity['id']}",
            name=opportunity['name'],
            description=opportunity['description'],
            phase=ProjectPhase.DISCOVERY,
            projected_revenue=opportunity.get('market_size', 0) * 0.01
        )
        
        # 并行收集各Agent评估
        async def get_agent_evaluation(agent_id: str, aspect: str) -> Dict:
            config = self.ai_configs[agent_id]
            async with KimiAgentRunner(config) as agent:
                return await agent.think(
                    task=f"从{aspect}角度评估项目'{opportunity['name']}'",
                    context={
                        "opportunity": opportunity,
                        "company_resources": {
                            "cash": self.financials["cash_flow"],
                            "team_size": len(self.agents)
                        }
                    }
                )
        
        # 并行执行评估
        print("   ⏳ 并行评估中...")
        eval_results = await asyncio.gather(
            get_agent_evaluation("cto", "技术可行性"),
            get_agent_evaluation("cfo", "财务可行性"),
            get_agent_evaluation("cpo", "产品可行性"),
            get_agent_evaluation("coo", "运营可行性")
        )
        
        cto_eval, cfo_eval, cpo_eval, coo_eval = eval_results
        
        print(f"   💻 CTO: {cto_eval.get('decision')} (置信度: {cto_eval.get('confidence')})")
        print(f"   💰 CFO: {cfo_eval.get('decision')} (置信度: {cfo_eval.get('confidence')})")
        print(f"   🎨 CPO: {cpo_eval.get('decision')} (置信度: {cpo_eval.get('confidence')})")
        print(f"   ⚙️  COO: {coo_eval.get('decision')} (置信度: {coo_eval.get('confidence')})")
        
        # AI CEO综合决策
        print("\n👔 AI CEO正在综合决策...")
        
        ceo_config = self.ai_configs["ceo"]
        async with KimiAgentRunner(ceo_config) as ceo:
            final_decision = await ceo.think(
                task=f"基于各部门评估，决定是否投资'{opportunity['name']}'项目",
                context={
                    "opportunity": opportunity,
                    "evaluations": {
                        "cto": cto_eval,
                        "cfo": cfo_eval,
                        "cpo": cpo_eval,
                        "coo": coo_eval
                    },
                    "company_status": {
                        "cash_flow": self.financials["cash_flow"],
                        "active_projects": len(self.projects)
                    }
                }
            )
        
        # 解析CEO决策
        decision_text = final_decision.get('decision', '').lower()
        approved = any(word in decision_text for word in ['批准', '通过', 'approved', 'yes', '同意'])
        
        budget = final_decision.get('budget_request', 0)
        if budget == 0:
            budget = random.randint(300000, 800000)
        
        print(f"   ✅ CEO决策: {'批准' if approved else '拒绝'}")
        print(f"   💵 预算: ¥{budget:,}")
        print(f"   📝 理由: {final_decision.get('reasoning', '')[:100]}...")
        
        if approved:
            project.budget = budget
            project.phase = ProjectPhase.PLANNING
            project.owner = "ceo"
            project.team = {
                "cto": "Tech Lead",
                "cpo": "Product Lead", 
                "coo": "Operations Lead",
                "cfo": "Financial Oversight"
            }
            self.projects[project.id] = project
            print(f"   🚀 项目已启动: {project.name}")
            
            # 记录成功决策
            self.ai_decisions.append({
                "timestamp": datetime.now().isoformat(),
                "agent": "CEO",
                "type": "project_approval",
                "project": project.name,
                "budget": budget,
                "result": final_decision
            })
        else:
            print(f"   ❌ 项目被拒绝")
    
    async def _ai_manage_projects(self):
        """AI管理项目执行"""
        if not self.projects:
            return
        
        print("\n🚀 AI管理项目执行...")
        
        for project in self.projects.values():
            if project.status != "active":
                continue
            
            # AI COO评估项目进度
            coo_config = self.ai_configs["coo"]
            async with KimiAgentRunner(coo_config) as coo:
                result = await coo.think(
                    task=f"评估项目'{project.name}'的执行情况和下一步行动",
                    context={
                        "project": {
                            "name": project.name,
                            "progress": project.progress,
                            "phase": project.phase.value,
                            "budget": project.budget,
                            "spent": project.spent
                        }
                    }
                )
            
            # 根据AI建议更新项目
            action = result.get('decision', '')
            if '推进' in action or '继续' in action:
                project.progress = min(100, project.progress + random.randint(10, 25))
            elif '加速' in action:
                project.progress = min(100, project.progress + random.randint(20, 35))
            
            # 消耗预算
            daily_cost = project.budget * 0.005
            project.spent += daily_cost
            self.financials["cash_flow"] -= daily_cost
            self.financials["total_expenses"] += daily_cost
            
            print(f"   📊 {project.name}: {project.progress:.0f}% (¥{project.spent:,.0f})")
    
    async def _ai_hr_management(self):
        """AI HR管理"""
        print("\n👥 AI HR团队管理...")
        
        chro_config = self.ai_configs["chro"]
        
        # 检查团队状态
        team_status = {
            agent.id: {
                "energy": agent.energy,
                "stress": agent.stress,
                "happiness": agent.happiness,
                "workload": agent.workload
            }
            for agent in self.agents.values() if agent.id != "observer"
        }
        
        async with KimiAgentRunner(chro_config) as chro:
            result = await chro.think(
                task="评估团队状态，提供管理建议",
                context={"team_status": team_status}
            )
        
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"   💡 HR建议: {recommendations[0] if isinstance(recommendations[0], str) else '关注团队健康'}")
        
        # 更新员工满意度
        total_happiness = sum(a.happiness for a in self.agents.values() if a.id != "observer")
        self.metrics["employee_satisfaction"] = total_happiness / 7
    
    async def _ai_daily_report(self):
        """AI生成日报"""
        print("\n📋 AI生成日报...")
        
        observer_config = self.ai_configs.get("observer") or KimiAgentConfig(
            agent_id="observer",
            name="System AI",
            role="Observer",
            system_prompt="你是公司运营观察员，负责总结每日运营情况。",
            api_key=self.api_key
        )
        
        async with KimiAgentRunner(observer_config) as observer:
            result = await observer.think(
                task="总结今日公司运营情况",
                context={
                    "day": self.metrics["day"],
                    "projects": len(self.projects),
                    "cash_flow": self.financials["cash_flow"],
                    "employee_satisfaction": self.metrics["employee_satisfaction"]
                }
            )
        
        summary = result.get('reasoning', '今日运营正常')[:100]
        print(f"   📝 {summary}...")
    
    def _print_summary(self):
        """打印模拟总结"""
        print(f"\n{'='*70}")
        print("📊 AI模拟总结")
        print(f"{'='*70}")
        
        print(f"\n💰 财务状况:")
        print(f"   现金流: ¥{self.financials['cash_flow']:,.0f}")
        print(f"   总支出: ¥{self.financials['total_expenses']:,.0f}")
        
        print(f"\n📁 项目情况:")
        print(f"   项目数: {len(self.projects)}")
        for p in self.projects.values():
            print(f"   - {p.name}: {p.progress:.0f}% (ROI: {p.get_roi():.1f}%)")
        
        print(f"\n🤖 AI决策记录:")
        print(f"   总决策数: {len(self.ai_decisions)}")
        
        # 按类型统计
        decision_types = {}
        for d in self.ai_decisions:
            t = d.get('type', 'unknown')
            decision_types[t] = decision_types.get(t, 0) + 1
        
        for t, count in decision_types.items():
            print(f"   - {t}: {count}次")
        
        print(f"\n👥 团队状态:")
        print(f"   满意度: {self.metrics['employee_satisfaction']:.1f}%")


# ============== 辅助函数 ==============

import random  # 用于fallback随机数

async def main():
    """主函数 - 运行真实AI公司系统"""
    
    # 检查API Key
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ 错误: 请设置KIMI_API_KEY环境变量")
        print("   export KIMI_API_KEY='your-api-key'")
        return
    
    print("🚀 启动真实AI公司系统")
    print(f"   API Key: {api_key[:20]}...")
    
    try:
        # 创建系统
        company = RealAICompanySystem("Nexus AI with Kimi Agents")
        
        # 运行3天AI模拟
        await company.run_ai_simulation(days=3)
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 设置事件循环策略（macOS兼容）
    import sys
    if sys.platform == 'darwin':
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
    
    # 运行
    asyncio.run(main())
