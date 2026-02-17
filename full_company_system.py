#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整版闭环Agent公司系统
复杂项目：Agent工作流搭建服务
充分利用所有7个Agent
"""

import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

# 导入基础组件
from advanced_company_v3 import AdvancedCompanySystem, Project, ProjectPhase
from kimi_coding_runner import KimiCodingRunner, KimiCodingConfig


class ProposalStatus(Enum):
    """提案状态"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class StepStatus(Enum):
    """步骤状态"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass
class Proposal:
    """提案"""
    id: str
    title: str
    description: str
    proposed_by: str
    status: ProposalStatus
    created_at: datetime
    auto_approved: bool = False
    rejected_reason: Optional[str] = None
    mission_id: Optional[str] = None


@dataclass
class MissionStep:
    """任务步骤"""
    id: str
    mission_id: str
    step_kind: str
    status: StepStatus
    assigned_to: Optional[str] = None
    result: Optional[Dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class Mission:
    """任务"""
    id: str
    proposal_id: str
    title: str
    status: str
    steps: List[MissionStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class AgentEvent:
    """Agent事件"""
    id: str
    agent_id: str
    event_type: str
    tags: List[str]
    payload: Dict
    created_at: datetime
    processed: bool = False


class FullCompanySystem(AdvancedCompanySystem):
    """
    完整版闭环Agent公司系统
    复杂项目场景，激活所有7个Agent
    """
    
    def __init__(self, company_name: str = "Nexus AI"):
        super().__init__(company_name)
        
        # 核心状态存储
        self.proposals: Dict[str, Proposal] = {}
        self.missions: Dict[str, Mission] = {}
        self.steps: Dict[str, MissionStep] = {}
        self.events: List[AgentEvent] = []
        
        # 策略配置
        self.policies = self._init_policies()
        
        # Agent API配置
        self.agent_apis: Dict[str, KimiCodingConfig] = {}
        self._init_agent_apis()
        
        # 统计
        self.loop_stats = {
            "proposals_created": 0,
            "proposals_approved": 0,
            "proposals_rejected": 0,
            "missions_completed": 0,
            "missions_failed": 0,
            "events_emitted": 0,
            "agent_calls": {agent: 0 for agent in ["ceo", "cmo", "cto", "cfo", "cpo", "coo", "chro"]}
        }
        
        print(f"🚀 完整版闭环Agent公司系统已启动: {company_name}")
        print(f"   项目类型: Agent工作流搭建服务")
        print(f"   激活Agent: CEO, CMO, CTO, CFO, CPO, COO, CHRO (全部7个)")
    
    def _init_policies(self) -> Dict:
        """初始化策略"""
        return {
            "auto_approve": {
                "enabled": True,
                "confidence_threshold": 0.7
            },
            "cap_gates": {
                "market_analysis": {"limit": 5, "window": "daily"},
                "design_review": {"limit": 3, "window": "daily"},
                "pricing_analysis": {"limit": 2, "window": "daily"},
                "backend_setup": {"limit": 2, "window": "daily"},
                "customer_support": {"limit": 10, "window": "daily"},
                "team_recruitment": {"limit": 3, "window": "daily"},
            }
        }
    
    def _init_agent_apis(self):
        """初始化所有Agent的API配置"""
        from kimi_coding_runner import KimiCodingFactory
        
        base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding")
        
        agents = [
            ("ceo", "Alex Chen", "CEO"),
            ("cmo", "Sarah Miller", "CMO"),
            ("cto", "David Kim", "CTO"),
            ("cfo", "Lisa Wang", "CFO"),
            ("cpo", "Michael Zhang", "CPO"),
            ("coo", "Emma Wilson", "COO"),
            ("chro", "James Brown", "CHRO"),
        ]
        
        for agent_id, name, role in agents:
            api_key = os.getenv(f"KIMI_API_KEY_{agent_id.upper()}") or os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                factory_method = getattr(KimiCodingFactory, f"create_{agent_id}_agent", None)
                if factory_method:
                    config = factory_method(api_key)
                else:
                    # 通用配置
                    config = KimiCodingConfig(
                        agent_id=agent_id,
                        name=name,
                        role=role,
                        system_prompt=f"你是{name}，{role}。提供专业建议。",
                        api_key=api_key,
                        base_url=base_url
                    )
                config.base_url = base_url
                self.agent_apis[agent_id] = config
        
        print(f"   已配置 {len(self.agent_apis)} 个Agent API")
    
    # ============== Proposal Service ==============
    
    async def create_proposal(self, title: str, description: str, proposed_by: str,
                             step_kinds: List[str], context: Dict = None) -> Proposal:
        """创建提案（统一入口）"""
        proposal_id = f"prop_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}"
        
        # Cap Gates检查
        for step_kind in step_kinds:
            gate_result = self._check_cap_gate(step_kind)
            if not gate_result["ok"]:
                proposal = Proposal(
                    id=proposal_id,
                    title=title,
                    description=description,
                    proposed_by=proposed_by,
                    status=ProposalStatus.REJECTED,
                    created_at=datetime.now(),
                    rejected_reason=gate_result["reason"]
                )
                self.proposals[proposal_id] = proposal
                self.loop_stats["proposals_rejected"] += 1
                self._emit_event(proposed_by, "proposal_rejected", 
                                ["proposal", "rejected"],
                                {"proposal_id": proposal_id, "reason": gate_result["reason"]})
                print(f"   ❌ Rejected: {gate_result['reason']}")
                return proposal
        
        # 创建提案
        proposal = Proposal(
            id=proposal_id,
            title=title,
            description=description,
            proposed_by=proposed_by,
            status=ProposalStatus.PENDING,
            created_at=datetime.now()
        )
        self.proposals[proposal_id] = proposal
        self.loop_stats["proposals_created"] += 1
        
        print(f"   📝 Proposal: {title}")
        
        # 自动审批
        await self._evaluate_auto_approve(proposal, step_kinds, context)
        
        return proposal
    
    def _check_cap_gate(self, step_kind: str) -> Dict:
        """Cap Gates检查"""
        gate_config = self.policies["cap_gates"].get(step_kind)
        if not gate_config:
            return {"ok": True}
        
        limit = gate_config["limit"]
        window_start = datetime.now() - timedelta(days=1 if gate_config["window"] == "daily" else 1)
        
        count = sum(
            1 for step in self.steps.values()
            if step.step_kind == step_kind 
            and step.started_at and step.started_at > window_start
        )
        
        if count >= limit:
            return {"ok": False, "reason": f"{step_kind} quota full ({count}/{limit})"}
        
        return {"ok": True}
    
    async def _evaluate_auto_approve(self, proposal: Proposal, step_kinds: List[str], context: Dict):
        """自动审批评估"""
        policy = self.policies["auto_approve"]
        
        if not policy["enabled"]:
            return
        
        confidence = context.get("confidence", 0.8) if context else 0.8
        if confidence < policy["confidence_threshold"]:
            return
        
        proposal.status = ProposalStatus.APPROVED
        proposal.auto_approved = True
        self.loop_stats["proposals_approved"] += 1
        
        print(f"   ✅ Auto-approved")
        
        await self._create_mission(proposal, step_kinds, context)
    
    # ============== Mission & Execution ==============
    
    async def _create_mission(self, proposal: Proposal, step_kinds: List[str], context: Dict):
        """创建任务"""
        mission_id = f"mission_{proposal.id}"
        
        steps = []
        for i, step_kind in enumerate(step_kinds):
            step = MissionStep(
                id=f"step_{mission_id}_{i}",
                mission_id=mission_id,
                step_kind=step_kind,
                status=StepStatus.QUEUED,
                assigned_to=self._get_step_agent(step_kind)
            )
            steps.append(step)
            self.steps[step.id] = step
        
        mission = Mission(
            id=mission_id,
            proposal_id=proposal.id,
            title=proposal.title,
            status="running",
            steps=steps
        )
        self.missions[mission_id] = mission
        proposal.mission_id = mission_id
        proposal.status = ProposalStatus.EXECUTING
        
        print(f"   🚀 Mission: {len(steps)} steps")
        
        self._emit_event("system", "mission_created", ["mission", "created"],
                        {"mission_id": mission_id, "proposal_id": proposal.id})
        
        await self._execute_mission(mission)
    
    def _get_step_agent(self, step_kind: str) -> str:
        """获取步骤对应的Agent"""
        mapping = {
            # 营销
            "market_analysis": "cmo",
            "marketing_strategy": "cmo",
            "customer_acquisition": "cmo",
            
            # 客户维护
            "customer_support": "coo",
            "customer_retention": "coo",
            "service_design": "cpo",
            
            # 设计
            "ux_design": "cpo",
            "ui_design": "cpo",
            "brand_design": "cpo",
            
            # 收费
            "pricing_analysis": "cfo",
            "revenue_model": "cfo",
            "cost_estimation": "cfo",
            
            # 后端
            "backend_architecture": "cto",
            "api_design": "cto",
            "infrastructure": "cto",
            "security_review": "cto",
            
            # 团队
            "team_planning": "chro",
            "recruitment": "chro",
            "skill_assessment": "chro",
            
            # 决策
            "strategic_decision": "ceo",
            "final_approval": "ceo",
        }
        return mapping.get(step_kind, "ceo")
    
    async def _execute_mission(self, mission: Mission):
        """执行任务"""
        for step in mission.steps:
            if step.status != StepStatus.QUEUED:
                continue
            
            step.status = StepStatus.RUNNING
            step.started_at = datetime.now()
            
            print(f"   ⚙️  {step.step_kind:20} → {step.assigned_to.upper()}")
            
            result = await self._execute_step(step)
            
            if result["success"]:
                step.status = StepStatus.SUCCEEDED
                step.result = result
                print(f"   ✅ Succeeded")
                self.loop_stats["agent_calls"][step.assigned_to] += 1
            else:
                step.status = StepStatus.FAILED
                step.error = result.get("error")
                print(f"   ❌ Failed: {result.get('error', 'Unknown')}")
                await self._handle_step_failure(mission, step)
            
            step.completed_at = datetime.now()
        
        await self._finalize_mission(mission)
    
    async def _execute_step(self, step: MissionStep) -> Dict:
        """执行单个步骤"""
        config = self.agent_apis.get(step.assigned_to)
        
        if not config:
            await asyncio.sleep(0.3)
            return {"success": True, "mode": "simulated", "agent": step.assigned_to}
        
        try:
            async with KimiCodingRunner(config) as runner:
                result = await runner.think(
                    task=f"执行{step.step_kind}任务",
                    context={"step_id": step.id, "step_kind": step.step_kind}
                )
                return {"success": True, "result": result, "agent": step.assigned_to}
        except Exception as e:
            return {"success": False, "error": str(e), "agent": step.assigned_to}
    
    async def _handle_step_failure(self, mission: Mission, failed_step: MissionStep):
        """处理步骤失败"""
        print(f"   🚨 Trigger: mission_failed diagnosis")
        
        await self.create_proposal(
            title=f"诊断: {failed_step.step_kind} 失败",
            description=f"步骤 {failed_step.step_kind} 执行失败，需要诊断和修复",
            proposed_by="system",
            step_kinds=["diagnosis", "recovery_plan"],
            context={"failed_mission": mission.id, "failed_step": failed_step.id}
        )
    
    async def _finalize_mission(self, mission: Mission):
        """完成任务"""
        all_succeeded = all(s.status == StepStatus.SUCCEEDED for s in mission.steps)
        any_failed = any(s.status == StepStatus.FAILED for s in mission.steps)
        
        if any_failed:
            mission.status = "failed"
            self.loop_stats["missions_failed"] += 1
        elif all_succeeded:
            mission.status = "succeeded"
            self.loop_stats["missions_completed"] += 1
        else:
            return
        
        mission.completed_at = datetime.now()
        
        proposal = self.proposals.get(mission.proposal_id)
        if proposal:
            proposal.status = ProposalStatus.COMPLETED if all_succeeded else ProposalStatus.FAILED
        
        print(f"   📋 Mission {mission.status.upper()}")
        
        self._emit_event("system", f"mission_{mission.status}",
                        ["mission", mission.status],
                        {"mission_id": mission.id})
    
    def _emit_event(self, agent_id: str, event_type: str, tags: List[str], payload: Dict):
        """发出事件"""
        event = AgentEvent(
            id=f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}",
            agent_id=agent_id,
            event_type=event_type,
            tags=tags,
            payload=payload,
            created_at=datetime.now()
        )
        self.events.append(event)
        self.loop_stats["events_emitted"] += 1
    
    # ============== 复杂项目场景 ==============
    
    async def run_full_simulation(self, days: int = 3):
        """运行完整模拟 - Agent工作流搭建服务"""
        print(f"\n{'='*70}")
        print(f"🚀 完整版闭环模拟 - Agent工作流搭建服务")
        print(f"{'='*70}")
        print("\n📋 项目类型: 为客户搭建完整Agent工作流系统")
        print("   包含: 营销 + 客户维护 + 设计 + 收费 + 后端 + 团队")
        print()
        
        for day in range(1, days + 1):
            self.metrics["day"] = day
            
            print(f"\n📅 Day {day}")
            print("-" * 70)
            
            # 1. CMO市场分析
            await self._phase_marketing(day)
            
            # 2. CPO设计阶段
            await self._phase_design(day)
            
            # 3. CTO后端架构
            await self._phase_backend(day)
            
            # 4. CFO收费模型
            await self._phase_pricing(day)
            
            # 5. COO客户维护
            await self._phase_customer_support(day)
            
            # 6. CHRO团队组建
            await self._phase_team_building(day)
            
            # 7. CEO最终决策
            await self._phase_strategic_decision(day)
            
            # 8. 处理事件
            await self._process_events()
            
            # 9. 自愈检查
            await self._self_healing()
            
            print(f"\n✅ Day {day} 完成")
        
        self._print_full_summary()
    
    async def _phase_marketing(self, day: int):
        """营销阶段 - CMO主导"""
        print(f"\n📊 Phase 1: 营销战略 (CMO)")
        
        await self.create_proposal(
            title=f"Day {day}: Agent工作流市场分析",
            description="分析目标市场，定位客户需求，制定获客策略",
            proposed_by="cmo",
            step_kinds=["market_analysis", "marketing_strategy", "customer_acquisition"],
            context={"confidence": 0.85, "market": "Agent Workflow SaaS"}
        )
    
    async def _phase_design(self, day: int):
        """设计阶段 - CPO主导"""
        print(f"\n🎨 Phase 2: 产品设计 (CPO)")
        
        await self.create_proposal(
            title=f"Day {day}: Agent工作流UX/UI设计",
            description="设计用户体验流程，界面交互，品牌形象",
            proposed_by="cpo",
            step_kinds=["ux_design", "ui_design", "brand_design"],
            context={"confidence": 0.8}
        )
    
    async def _phase_backend(self, day: int):
        """后端阶段 - CTO主导"""
        print(f"\n💻 Phase 3: 后端架构 (CTO)")
        
        await self.create_proposal(
            title=f"Day {day}: Agent工作流系统架构",
            description="设计系统架构，API接口，基础设施，安全方案",
            proposed_by="cto",
            step_kinds=["backend_architecture", "api_design", "infrastructure", "security_review"],
            context={"confidence": 0.9}
        )
    
    async def _phase_pricing(self, day: int):
        """收费阶段 - CFO主导"""
        print(f"\n💰 Phase 4: 收费模型 (CFO)")
        
        await self.create_proposal(
            title=f"Day {day}: Agent工作流定价策略",
            description="分析成本结构，设计收费模式，制定价格策略",
            proposed_by="cfo",
            step_kinds=["cost_estimation", "pricing_analysis", "revenue_model"],
            context={"confidence": 0.75}
        )
    
    async def _phase_customer_support(self, day: int):
        """客户维护阶段 - COO主导"""
        print(f"\n🤝 Phase 5: 客户维护 (COO)")
        
        await self.create_proposal(
            title=f"Day {day}: 客户服务体系搭建",
            description="设计客户支持流程，维护策略，服务标准",
            proposed_by="coo",
            step_kinds=["customer_support", "customer_retention", "service_design"],
            context={"confidence": 0.8}
        )
    
    async def _phase_team_building(self, day: int):
        """团队组建阶段 - CHRO主导"""
        print(f"\n👥 Phase 6: 团队组建 (CHRO)")
        
        await self.create_proposal(
            title=f"Day {day}: 实施团队招聘规划",
            description="评估技能需求，制定招聘计划，组建实施团队",
            proposed_by="chro",
            step_kinds=["skill_assessment", "team_planning", "recruitment"],
            context={"confidence": 0.8}
        )
    
    async def _phase_strategic_decision(self, day: int):
        """战略决策阶段 - CEO主导"""
        print(f"\n👔 Phase 7: 战略决策 (CEO)")
        
        # 汇总所有评估结果
        await self.create_proposal(
            title=f"Day {day}: 项目整体战略决策",
            description="综合各部门评估，做出最终投资决策",
            proposed_by="ceo",
            step_kinds=["strategic_decision", "final_approval"],
            context={"confidence": 0.9, "phase": "final"}
        )
    
    async def _process_events(self):
        """处理事件"""
        unprocessed = [e for e in self.events if not e.processed]
        if unprocessed:
            print(f"\n📡 Processing {len(unprocessed)} events...")
            for event in unprocessed[:10]:
                event.processed = True
    
    async def _self_healing(self):
        """自愈检查"""
        stale_threshold = datetime.now() - timedelta(minutes=30)
        stale_steps = [
            s for s in self.steps.values()
            if s.status == StepStatus.RUNNING
            and s.started_at and s.started_at < stale_threshold
        ]
        
        if stale_steps:
            print(f"\n🏥 Recovered {len(stale_steps)} stale steps")
            for step in stale_steps:
                step.status = StepStatus.FAILED
                step.error = "Stale: timeout"
    
    def _print_full_summary(self):
        """打印完整总结"""
        print(f"\n{'='*70}")
        print("📊 完整版闭环模拟总结")
        print(f"{'='*70}")
        
        print(f"\n🔄 闭环统计:")
        for key, value in self.loop_stats.items():
            if key != "agent_calls":
                print(f"   {key}: {value}")
        
        print(f"\n🤖 Agent调用统计:")
        for agent, count in self.loop_stats["agent_calls"].items():
            status = "✅" if count > 0 else "⚠️"
            print(f"   {status} {agent.upper():6} : {count}次")
        
        print(f"\n📁 系统状态:")
        print(f"   Proposals: {len(self.proposals)}")
        print(f"   Missions: {len(self.missions)} (Succeeded: {len([m for m in self.missions.values() if m.status == 'succeeded'])})")
        print(f"   Steps: {len(self.steps)}")
        print(f"   Events: {len(self.events)}")
        
        print(f"\n💰 财务:")
        print(f"   现金流: ¥{self.financials['cash_flow']:,.0f}")
        
        # 激活率
        active_agents = sum(1 for c in self.loop_stats["agent_calls"].values() if c > 0)
        print(f"\n📈 Agent激活率: {active_agents}/7 ({active_agents/7*100:.0f}%)")


# ============== 入口 ==============

async def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         完整版闭环Agent公司系统                              ║")
    print("║         复杂项目：Agent工作流搭建服务                        ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    company = FullCompanySystem("Nexus AI Full Stack")
    await company.run_full_simulation(days=2)
    
    print("\n" + "="*70)
    print("✅ 完整版模拟完成!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
