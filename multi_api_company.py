#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-API Key Company System
每个Agent使用独立API Key的公司系统
"""

import os
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from advanced_company_v3 import AdvancedCompanySystem, Project, ProjectPhase
from kimi_coding_runner import KimiCodingRunner, KimiCodingConfig


@dataclass
class AgentAPIConfig:
    """Agent API配置"""
    agent_id: str
    name: str
    api_key: str
    base_url: str = "https://api.kimi.com/coding"
    model: str = "kimi-coding/k2p5"
    enabled: bool = True


class MultiAPICompanySystem(AdvancedCompanySystem):
    """
    每个Agent独立API的公司系统
    """
    
    def __init__(self, company_name: str = "Nexus AI"):
        # 先初始化api_stats
        self.agent_apis: Dict[str, AgentAPIConfig] = {}
        self.api_stats = {
            "calls_by_agent": {},
            "tokens_by_agent": {},
            "errors_by_agent": {}
        }
        
        # 调用父类初始化
        super().__init__(company_name)
        
        # 初始化Agent API
        self._init_agent_apis()
        
        print(f"🚀 多API Key公司系统已启动: {company_name}")
        self._print_api_status()
    
    def _init_agent_apis(self):
        """初始化每个Agent的API配置"""
        
        # 从环境变量读取每个Agent的API Key
        # 格式: KIMI_API_KEY_<AGENT_ID>
        
        agent_configs = [
            ("ceo", "Alex Chen", "CEO"),
            ("cmo", "Sarah Miller", "CMO"),
            ("cto", "David Kim", "CTO"),
            ("cfo", "Lisa Wang", "CFO"),
            ("cpo", "Michael Zhang", "CPO"),
            ("coo", "Emma Wilson", "COO"),
            ("chro", "James Brown", "CHRO"),
        ]
        
        for agent_id, name, role in agent_configs:
            # 尝试读取专用API Key
            api_key = os.getenv(f"KIMI_API_KEY_{agent_id.upper()}")
            
            # 如果没有专用Key，使用通用Key
            if not api_key:
                api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("KIMI_API_KEY")
            
            base_url = os.getenv(f"KIMI_BASE_URL_{agent_id.upper()}", 
                               os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding"))
            
            model = os.getenv(f"KIMI_MODEL_{agent_id.upper()}",
                            os.getenv("KIMI_MODEL", "kimi-coding/k2p5"))
            
            self.agent_apis[agent_id] = AgentAPIConfig(
                agent_id=agent_id,
                name=name,
                api_key=api_key or "",
                base_url=base_url,
                model=model,
                enabled=bool(api_key)
            )
            
            # 初始化统计
            self.api_stats["calls_by_agent"][agent_id] = 0
            self.api_stats["tokens_by_agent"][agent_id] = 0
            self.api_stats["errors_by_agent"][agent_id] = 0
    
    def _print_api_status(self):
        """打印API状态"""
        print("\n📊 Agent API配置状态:")
        for agent_id, config in self.agent_apis.items():
            status = "✅" if config.enabled else "❌"
            key_preview = config.api_key[:10] + "..." if config.api_key else "未设置"
            print(f"   {status} {config.name} ({agent_id}): {key_preview}")
    
    async def call_agent(self, agent_id: str, task: str, context: dict = None) -> dict:
        """
        调用指定Agent的API
        
        Args:
            agent_id: Agent ID (ceo/cmo/cto等)
            task: 任务描述
            context: 上下文
            
        Returns:
            Agent决策结果
        """
        api_config = self.agent_apis.get(agent_id)
        
        if not api_config or not api_config.enabled:
            print(f"⚠️ {agent_id} API未配置，使用模拟模式")
            return self._simulated_decision(agent_id, task)
        
        # 创建Kimi配置
        kim_config = self._create_kimi_config(api_config)
        
        try:
            async with KimiCodingRunner(kim_config) as runner:
                result = await runner.think(task, context)
                
                # 更新统计
                self.api_stats["calls_by_agent"][agent_id] += 1
                
                return result
                
        except Exception as e:
            print(f"❌ {agent_id} API调用失败: {e}")
            self.api_stats["errors_by_agent"][agent_id] += 1
            return self._simulated_decision(agent_id, task)
    
    def _create_kimi_config(self, api_config: AgentAPIConfig) -> KimiCodingConfig:
        """创建Kimi配置"""
        
        # 根据角色选择系统提示词
        system_prompts = {
            "ceo": """你是CEO。做出战略决策，平衡风险与回报。输出JSON格式决策。""",
            "cmo": """你是CMO。分析市场机会，提供营销建议。输出JSON格式分析。""",
            "cto": """你是CTO。评估技术可行性，提供架构建议。输出JSON格式评估。""",
            "cfo": """你是CFO。进行财务分析，评估投资回报。输出JSON格式分析。""",
            "cpo": """你是CPO。评估产品可行性，提供UX建议。输出JSON格式评估。""",
            "coo": """你是COO。评估运营可行性，提供执行建议。输出JSON格式评估。""",
            "chro": """你是CHRO。管理团队，提供HR建议。输出JSON格式建议。""",
        }
        
        return KimiCodingConfig(
            agent_id=api_config.agent_id,
            name=api_config.name,
            role=api_config.agent_id.upper(),
            system_prompt=system_prompts.get(api_config.agent_id, "你是AI Agent。"),
            api_key=api_config.api_key,
            base_url=api_config.base_url,
            model=api_config.model
        )
    
    def _simulated_decision(self, agent_id: str, task: str) -> dict:
        """模拟决策（当API不可用时）"""
        import random
        
        decisions = {
            "ceo": {"decision": "批准", "confidence": 0.85, "budget_request": random.randint(300000, 800000)},
            "cmo": {"decision": "建议进入", "confidence": 0.8, "recommendations": ["快速验证", "用户调研"]},
            "cto": {"decision": "技术上可行", "confidence": 0.9, "risks": ["技术复杂度"]},
            "cfo": {"decision": "财务可行", "confidence": 0.75, "roi": 2.5},
            "cpo": {"decision": "产品有市场", "confidence": 0.8},
            "coo": {"decision": "运营可行", "confidence": 0.85},
            "chro": {"decision": "团队可支撑", "confidence": 0.8},
        }
        
        base = decisions.get(agent_id, {"decision": "需要讨论", "confidence": 0.6})
        base["reasoning"] = f"{agent_id.upper()}基于分析做出决策"
        base["action_items"] = []
        base["team_requirements"] = []
        base["mode"] = "simulated"
        
        return base
    
    async def run_multi_api_simulation(self, days: int = 3):
        """运行多API模拟"""
        print(f"\n{'='*70}")
        print(f"🚀 启动多API Agent模拟 - {days} 天")
        print(f"{'='*70}")
        
        for day in range(1, days + 1):
            self.metrics["day"] = day
            
            print(f"\n📅 Day {day}")
            print("-" * 50)
            
            # 1. CMO市场分析
            print("\n📊 CMO分析市场...")
            cmo_result = await self.call_agent(
                "cmo",
                "分析AI市场趋势，识别3个创业机会",
                {"budget": self.financials["cash_flow"]}
            )
            print(f"   ✅ CMO: {cmo_result.get('decision')}")
            
            # 2. 创建机会
            opportunities = []
            for i in range(3):
                opp = {
                    "id": f"day{day}_opp{i}",
                    "name": f"AI机会{i+1}",
                    "market_size": random.randint(50, 500) * 1000000
                }
                opportunities.append(opp)
            
            # 3. 评估第一个机会
            if opportunities:
                opp = opportunities[0]
                print(f"\n🔍 评估: {opp['name']}")
                
                # CTO评估
                print("   💻 CTO评估...")
                cto_result = await self.call_agent(
                    "cto",
                    f"评估'{opp['name']}'技术可行性",
                    {"opportunity": opp}
                )
                print(f"      {cto_result.get('decision')}")
                
                # CFO评估
                print("   💰 CFO评估...")
                cfo_result = await self.call_agent(
                    "cfo",
                    f"评估'{opp['name']}'财务可行性",
                    {"opportunity": opp, "budget": 500000}
                )
                print(f"      {cfo_result.get('decision')}")
                
                # CEO决策
                print("\n👔 CEO决策...")
                ceo_result = await self.call_agent(
                    "ceo",
                    f"基于CTO和CFO评估，决定是否投资'{opp['name']}'",
                    {
                        "opportunity": opp,
                        "cto": cto_result,
                        "cfo": cfo_result
                    }
                )
                print(f"   ✅ CEO: {ceo_result.get('decision')}")
                print(f"   💵 预算: ¥{ceo_result.get('budget_request', 0):,}")
                
                # 创建项目
                if "批准" in ceo_result.get('decision', '') or "approved" in ceo_result.get('decision', '').lower():
                    project = Project(
                        id=f"proj_{opp['id']}",
                        name=opp['name'],
                        description="AI项目",
                        phase=ProjectPhase.PLANNING,
                        budget=ceo_result.get('budget_request', 500000)
                    )
                    self.projects[project.id] = project
                    print(f"   🚀 项目启动!")
            
            print(f"\n✅ Day {day} 完成")
        
        self._print_summary()
    
    def _print_summary(self):
        """打印总结"""
        print(f"\n{'='*70}")
        print("📊 多API模拟总结")
        print(f"{'='*70}")
        
        print("\n🤖 API调用统计:")
        for agent_id, count in self.api_stats["calls_by_agent"].items():
            errors = self.api_stats["errors_by_agent"][agent_id]
            config = self.agent_apis[agent_id]
            mode = "🤖 AI" if config.enabled else "📟 模拟"
            print(f"   {mode} {config.name}: {count}次调用" + (f" ({errors}错误)" if errors else ""))
        
        print(f"\n💰 财务:")
        print(f"   项目数: {len(self.projects)}")
        print(f"   现金流: ¥{self.financials['cash_flow']:,.0f}")


# ============== 配置向导 ==============

def print_setup_guide():
    """打印配置指南"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         多API Key配置指南                                     ║
╚══════════════════════════════════════════════════════════════╝

方式1: 每个Agent独立API Key
  export KIMI_API_KEY_CEO="sk-kimi-xxx1"
  export KIMI_API_KEY_CMO="sk-kimi-xxx2"
  export KIMI_API_KEY_CTO="sk-kimi-xxx3"
  export KIMI_API_KEY_CFO="sk-kimi-xxx4"
  export KIMI_API_KEY_CPO="sk-kimi-xxx5"
  export KIMI_API_KEY_COO="sk-kimi-xxx6"
  export KIMI_API_KEY_CHRO="sk-kimi-xxx7"

方式2: 统一使用一个API Key
  export ANTHROPIC_API_KEY="sk-kimi-xxx"
  export ANTHROPIC_BASE_URL="https://api.kimi.com/coding"

方式3: 混合配置（部分Agent用独立Key）
  export KIMI_API_KEY_CEO="sk-kimi-ceo-key"
  export KIMI_API_KEY_CTO="sk-kimi-cto-key"
  export ANTHROPIC_API_KEY="sk-kimi-general"  # 其他Agent用通用Key

永久配置（添加到 ~/.zshrc）:
  echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.zshrc
  source ~/.zshrc
""")


async def main():
    """主函数"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         多API Key真实AI公司系统                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    # 检查是否有任何API Key
    has_key = any([
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("KIMI_API_KEY_CEO"),
        os.getenv("KIMI_API_KEY_CMO"),
    ])
    
    if not has_key:
        print("\n⚠️ 未检测到API Key")
        print_setup_guide()
        return
    
    try:
        company = MultiAPICompanySystem("Nexus AI Multi-API")
        await company.run_multi_api_simulation(days=2)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import random
    asyncio.run(main())
