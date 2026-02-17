#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Closed Loop Agent Company System
闭环多Agent公司系统 - 参考VoxYZ架构
"""

import os
import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

from advanced_company_v3 import AdvancedCompanySystem, Project, ProjectPhase, Agent, AgentState
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
    proposed_by: str  # Agent ID
    status: ProposalStatus
    created_at: datetime
    auto_approved: bool = False
    rejected_reason: Optional[str] = None
    mission_id: Optional[str] = None
    cap_gates: Dict = field(default_factory=dict)


@dataclass
class MissionStep:
    """任务步骤"""
    id: str
    mission_id: str
    step_kind: str  # market_analysis, tech_eval, etc.
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
    status: str  # running, succeeded, failed
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


@dataclass
class TriggerRule:
    """触发器规则"""
    id: str
    name: str
    condition: str
    action: str
    cooldown_minutes: int
    last_triggered: Optional[datetime] = None
    probability: float = 1.0


class ClosedLoopCompanySystem(AdvancedCompanySystem):
    """
    闭环多Agent公司系统
    参考VoxYZ架构设计
    """
    
    def __init__(self, company_name: str = "Nexus AI"):
        super().__init__(company_name)
        
        # 核心状态存储（替代Supabase）
        self.proposals: Dict[str, Proposal] = {}
        self.missions: Dict[str, Mission] = {}
        self.steps: Dict[str, MissionStep] = {}
        self.events: List[AgentEvent] = []
        self.policies: Dict[str, Any] = self._init_policies()
        self.triggers: List[TriggerRule] = self._init_triggers()
        
        # Agent API配置
        self.agent_apis: Dict[str, KimiCodingConfig] = {}
        self._init_agent_apis()
        
        # 统计
        self.loop_stats = {
            "proposals_created": 0,
            "proposals_approved": 0,
            "proposals_rejected": 0,
            "missions_completed": 0,
            "events_emitted": 0,
            "triggers_fired": 0
        }
        
        print(f"🚀 闭环Agent公司系统已启动: {company_name}")
        print(f"   Mode: Closed Loop (Propose → Approve → Execute → Event → React)")
    
    def _init_policies(self) -> Dict:
        """初始化策略（替代ops_policy表）"""
        return {
            "auto_approve": {
                "enabled": True,
                "allowed_step_kinds": ["market_scan", "tech_eval", "financial_check", "product_review"],
                "confidence_threshold": 0.7
            },
            "daily_quotas": {
                "market_scan": 10,
                "project_eval": 5,
                "content_create": 3
            },
            "cap_gates": {
                "market_scan": {"limit": 10, "window": "daily"},
                "project_approval": {"limit": 3, "window": "daily"},
                "tweet_post": {"limit": 8, "window": "daily"}
            }
        }
    
    def _init_triggers(self) -> List[TriggerRule]:
        """初始化触发器"""
        return [
            TriggerRule(
                id="trigger_market_opportunity",
                name="市场机会触发",
                condition="market_scan.high_potential",
                action="create_proposal:project_eval",
                cooldown_minutes=60,
                probability=0.8
            ),
            TriggerRule(
                id="trigger_mission_failed",
                name="任务失败诊断",
                condition="mission.failed",
                action="create_proposal:diagnose",
                cooldown_minutes=30,
                probability=1.0
            ),
            TriggerRule(
                id="trigger_project_approved",
                name="项目启动",
                condition="proposal.approved",
                action="create_mission:execute_project",
                cooldown_minutes=0,
                probability=1.0
            )
        ]
    
    def _init_agent_apis(self):
        """初始化Agent API配置"""
        from kimi_coding_runner import KimiCodingFactory
        
        base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding")
        
        # 加载每个Agent的API Key
        agents = [
            ("ceo", "Alex Chen"),
            ("cmo", "Sarah Miller"),
            ("cto", "David Kim"),
            ("cfo", "Lisa Wang"),
            ("cpo", "Michael Zhang"),
            ("coo", "Emma Wilson"),
        ]
        
        for agent_id, name in agents:
            api_key = os.getenv(f"KIMI_API_KEY_{agent_id.upper()}") or os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                # 安全获取工厂方法
                factory_method = getattr(KimiCodingFactory, f"create_{agent_id}_agent", None)
                if factory_method:
                    config = factory_method(api_key)
                    config.base_url = base_url
                    self.agent_apis[agent_id] = config
                else:
                    # 创建通用配置
                    config = KimiCodingConfig(
                        agent_id=agent_id,
                        name=name,
                        role=agent_id.upper(),
                        system_prompt=f"你是{name}，{agent_id.upper()}。做出专业决策。",
                        api_key=api_key,
                        base_url=base_url
                    )
                    self.agent_apis[agent_id] = config
    
    # ============== Proposal Service（单入口） ==============
    
    async def create_proposal(self, title: str, description: str, proposed_by: str,
                             step_kinds: List[str], context: Dict = None) -> Proposal:
        """
        创建提案（统一入口）
        包含: Cap Gates检查 → 创建提案 → 自动审批 → 创建任务
        """
        proposal_id = f"prop_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}"
        
        # 1. Cap Gates检查
        gate_results = {}
        for step_kind in step_kinds:
            gate_result = self._check_cap_gate(step_kind)
            gate_results[step_kind] = gate_result
            
            if not gate_result["ok"]:
                # 拒绝提案
                proposal = Proposal(
                    id=proposal_id,
                    title=title,
                    description=description,
                    proposed_by=proposed_by,
                    status=ProposalStatus.REJECTED,
                    created_at=datetime.now(),
                    rejected_reason=gate_result["reason"],
                    cap_gates=gate_results
                )
                self.proposals[proposal_id] = proposal
                self.loop_stats["proposals_rejected"] += 1
                
                # 发出事件
                self._emit_event(
                    agent_id=proposed_by,
                    event_type="proposal_rejected",
                    tags=["proposal", "rejected", step_kind],
                    payload={"proposal_id": proposal_id, "reason": gate_result["reason"]}
                )
                
                print(f"   ❌ Proposal rejected: {gate_result['reason']}")
                return proposal
        
        # 2. 创建提案
        proposal = Proposal(
            id=proposal_id,
            title=title,
            description=description,
            proposed_by=proposed_by,
            status=ProposalStatus.PENDING,
            created_at=datetime.now(),
            cap_gates=gate_results
        )
        self.proposals[proposal_id] = proposal
        self.loop_stats["proposals_created"] += 1
        
        print(f"   📝 Proposal created: {title}")
        
        # 3. 自动审批检查
        await self._evaluate_auto_approve(proposal, step_kinds, context)
        
        return proposal
    
    def _check_cap_gate(self, step_kind: str) -> Dict:
        """
        Cap Gates检查
        在提案阶段就拒绝，不生成队列任务
        """
        gate_config = self.policies["cap_gates"].get(step_kind)
        if not gate_config:
            return {"ok": True}
        
        limit = gate_config["limit"]
        window = gate_config["window"]
        
        # 计算窗口内的数量
        if window == "daily":
            window_start = datetime.now() - timedelta(days=1)
        else:
            window_start = datetime.now() - timedelta(hours=1)
        
        # 统计该类型步骤的数量
        count = sum(
            1 for step in self.steps.values()
            if step.step_kind == step_kind 
            and step.started_at 
            and step.started_at > window_start
        )
        
        if count >= limit:
            return {
                "ok": False,
                "reason": f"{step_kind} quota reached ({count}/{limit} in {window})"
            }
        
        return {"ok": True, "current": count, "limit": limit}
    
    async def _evaluate_auto_approve(self, proposal: Proposal, step_kinds: List[str], context: Dict):
        """自动审批评估"""
        policy = self.policies["auto_approve"]
        
        if not policy["enabled"]:
            return
        
        # 检查所有步骤类型是否允许自动审批
        if not all(sk in policy["allowed_step_kinds"] for sk in step_kinds):
            return
        
        # 检查Agent信心度（如果有）
        confidence = context.get("confidence", 0.8) if context else 0.8
        if confidence < policy["confidence_threshold"]:
            return
        
        # 自动批准
        proposal.status = ProposalStatus.APPROVED
        proposal.auto_approved = True
        self.loop_stats["proposals_approved"] += 1
        
        print(f"   ✅ Auto-approved")
        
        # 创建任务
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
        
        print(f"   🚀 Mission created: {len(steps)} steps")
        
        # 发出事件
        self._emit_event(
            agent_id="system",
            event_type="mission_created",
            tags=["mission", "created"],
            payload={"mission_id": mission_id, "proposal_id": proposal.id}
        )
        
        # 执行步骤
        await self._execute_mission(mission)
    
    def _get_step_agent(self, step_kind: str) -> str:
        """获取步骤对应的Agent"""
        mapping = {
            "market_scan": "cmo",
            "tech_eval": "cto",
            "financial_check": "cfo",
            "product_review": "cpo",
            "ops_eval": "coo",
            "strategic_decision": "ceo"
        }
        return mapping.get(step_kind, "ceo")
    
    async def _execute_mission(self, mission: Mission):
        """执行任务"""
        for step in mission.steps:
            if step.status != StepStatus.QUEUED:
                continue
            
            # 标记为运行中
            step.status = StepStatus.RUNNING
            step.started_at = datetime.now()
            
            print(f"   ⚙️ Executing: {step.step_kind} → {step.assigned_to}")
            
            # 调用Agent执行
            result = await self._execute_step(step)
            
            if result["success"]:
                step.status = StepStatus.SUCCEEDED
                step.result = result
                print(f"   ✅ Succeeded")
            else:
                step.status = StepStatus.FAILED
                step.error = result.get("error")
                print(f"   ❌ Failed: {result.get('error')}")
                
                # 触发失败诊断
                await self._trigger_mission_failed(mission, step)
            
            step.completed_at = datetime.now()
        
        # 检查任务完成
        await self._finalize_mission(mission)
    
    async def _execute_step(self, step: MissionStep) -> Dict:
        """执行单个步骤"""
        config = self.agent_apis.get(step.assigned_to)
        
        if not config:
            # 模拟执行
            await asyncio.sleep(0.5)
            return {"success": True, "mode": "simulated"}
        
        try:
            async with KimiCodingRunner(config) as runner:
                result = await runner.think(
                    task=f"执行{step.step_kind}任务",
                    context={"step_id": step.id}
                )
                return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _finalize_mission(self, mission: Mission):
        """完成任务"""
        # 检查所有步骤状态
        all_succeeded = all(s.status == StepStatus.SUCCEEDED for s in mission.steps)
        any_failed = any(s.status == StepStatus.FAILED for s in mission.steps)
        
        if any_failed:
            mission.status = "failed"
        elif all_succeeded:
            mission.status = "succeeded"
            self.loop_stats["missions_completed"] += 1
        else:
            return  # 还有步骤未完成
        
        mission.completed_at = datetime.now()
        
        # 更新提案状态
        proposal = self.proposals.get(mission.proposal_id)
        if proposal:
            proposal.status = ProposalStatus.COMPLETED if all_succeeded else ProposalStatus.FAILED
        
        print(f"   📋 Mission {mission.status}")
        
        # 发出事件
        self._emit_event(
            agent_id="system",
            event_type=f"mission_{mission.status}",
            tags=["mission", mission.status],
            payload={"mission_id": mission.id}
        )
    
    # ============== Event System ==============
    
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
    
    # ============== Triggers ==============
    
    async def _trigger_mission_failed(self, mission: Mission, failed_step: MissionStep):
        """触发任务失败处理"""
        trigger = next((t for t in self.triggers if t.id == "trigger_mission_failed"), None)
        if not trigger:
            return
        
        # 检查冷却
        if trigger.last_triggered:
            cooldown_end = trigger.last_triggered + timedelta(minutes=trigger.cooldown_minutes)
            if datetime.now() < cooldown_end:
                return
        
        # 检查概率
        if random.random() > trigger.probability:
            return
        
        trigger.last_triggered = datetime.now()
        self.loop_stats["triggers_fired"] += 1
        
        # 创建诊断提案
        await self.create_proposal(
            title=f"诊断失败任务: {mission.title}",
            description=f"步骤 {failed_step.step_kind} 失败，需要诊断",
            proposed_by="system",
            step_kinds=["diagnose"],
            context={"failed_mission": mission.id, "failed_step": failed_step.id}
        )
    
    # ============== Main Loop ==============
    
    async def run_closed_loop(self, days: int = 3):
        """运行闭环模拟"""
        print(f"\n{'='*70}")
        print(f"🚀 启动闭环模拟 - {days} 天")
        print(f"   Loop: Propose → Approve → Execute → Event → React")
        print(f"{'='*70}")
        
        for day in range(1, days + 1):
            self.metrics["day"] = day
            
            print(f"\n📅 Day {day}")
            print("-" * 50)
            
            # 1. CMO扫描市场（创建提案）
            await self._day_market_scan()
            
            # 2. 评估机会（创建提案）
            await self._day_evaluate_opportunities()
            
            # 3. CEO决策（自动审批/执行）
            await self._day_strategic_decisions()
            
            # 4. 处理事件和触发器
            await self._day_process_events()
            
            # 5. 自愈检查
            await self._day_self_healing()
            
            print(f"\n✅ Day {day} 完成")
            await asyncio.sleep(0.5)
        
        self._print_closed_loop_summary()
    
    async def _day_market_scan(self):
        """市场扫描"""
        print("\n📊 市场扫描...")
        
        await self.create_proposal(
            title="市场趋势分析",
            description="扫描AI市场，识别机会",
            proposed_by="cmo",
            step_kinds=["market_scan"],
            context={"confidence": 0.85}
        )
    
    async def _day_evaluate_opportunities(self):
        """评估机会"""
        print("\n🔍 评估机会...")
        
        # 模拟发现机会
        opportunities = [
            {"name": "AI Agent平台", "potential": "high"},
            {"name": "代码生成工具", "potential": "medium"}
        ]
        
        for opp in opportunities[:2]:
            await self.create_proposal(
                title=f"评估: {opp['name']}",
                description=f"评估{opp['name']}的可行性",
                proposed_by="cmo",
                step_kinds=["tech_eval", "financial_check"],
                context={"opportunity": opp, "confidence": 0.8}
            )
    
    async def _day_strategic_decisions(self):
        """战略决策"""
        print("\n👔 战略决策...")
        
        # 处理待决提案
        pending = [p for p in self.proposals.values() if p.status == ProposalStatus.PENDING]
        for proposal in pending[:2]:
            # CEO审批
            await self.create_proposal(
                title=f"审批: {proposal.title}",
                description="最终决策",
                proposed_by="ceo",
                step_kinds=["strategic_decision"],
                context={"proposal_id": proposal.id}
            )
    
    async def _day_process_events(self):
        """处理事件"""
        print("\n📡 处理事件...")
        
        unprocessed = [e for e in self.events if not e.processed]
        for event in unprocessed[:5]:
            event.processed = True
            print(f"   📨 {event.event_type}")
    
    async def _day_self_healing(self):
        """自愈检查"""
        print("\n🏥 自愈检查...")
        
        # 检查卡住的任务
        stale_threshold = datetime.now() - timedelta(minutes=30)
        stale_steps = [
            s for s in self.steps.values()
            if s.status == StepStatus.RUNNING
            and s.started_at and s.started_at < stale_threshold
        ]
        
        for step in stale_steps:
            step.status = StepStatus.FAILED
            step.error = "Stale: no progress for 30 minutes"
            print(f"   ⚠️ Recovered stale step: {step.id}")
    
    def _print_closed_loop_summary(self):
        """打印闭环总结"""
        print(f"\n{'='*70}")
        print("📊 闭环模拟总结")
        print(f"{'='*70}")
        
        print(f"\n🔄 闭环统计:")
        for key, value in self.loop_stats.items():
            print(f"   {key}: {value}")
        
        print(f"\n📁 状态:")
        print(f"   Proposals: {len(self.proposals)} (Pending: {len([p for p in self.proposals.values() if p.status == ProposalStatus.PENDING])})")
        print(f"   Missions: {len(self.missions)} (Completed: {len([m for m in self.missions.values() if m.status == 'succeeded'])})")
        print(f"   Steps: {len(self.steps)}")
        print(f"   Events: {len(self.events)}")
        
        print(f"\n💰 财务:")
        print(f"   现金流: ¥{self.financials['cash_flow']:,.0f}")


# ============== Entry Point ==============

async def main():
    """主函数"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         闭环Agent公司系统                                    ║")
    print("║         Closed Loop Architecture                             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    company = ClosedLoopCompanySystem("Nexus AI Closed Loop")
    await company.run_closed_loop(days=3)
    
    print("\n" + "="*70)
    print("✅ 闭环模拟完成!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
