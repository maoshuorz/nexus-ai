#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voxyz-Style Multi-Agent Company System
多Agent公司模拟系统 - 增强版
参考: Voxyz AI Agent Platform
"""

import json
import asyncio
import random
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path

class AgentRole(Enum):
    """Agent角色枚举"""
    CEO = "首席执行官"
    CMO = "市场总监"
    CTO = "技术总监"
    COO = "运营总监"
    PR = "品牌总监"
    CFO = "财务总监"
    OBSERVER = "运营观察员"

class ProjectStatus(Enum):
    """项目状态"""
    DISCOVERED = "发现"
    EVALUATING = "评估中"
    APPROVED = "已批准"
    EXECUTING = "执行中"
    MONITORING = "监控中"
    COMPLETED = "已完成"
    FAILED = "失败"

@dataclass
class Agent:
    """Agent实体"""
    id: str
    role: AgentRole
    name: str
    status: str = "idle"  # idle, busy, waiting
    current_task: Optional[str] = None
    skills: List[str] = field(default_factory=list)
    performance_score: float = 100.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role.value,
            "name": self.name,
            "status": self.status,
            "current_task": self.current_task,
            "skills": self.skills,
            "performance_score": self.performance_score,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed
        }

@dataclass
class Message:
    """Agent间消息"""
    id: str
    from_agent: str
    to_agent: str
    content: str
    msg_type: str  # task, response, notification, decision
    timestamp: datetime
    priority: str = "normal"  # high, normal, low
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "from": self.from_agent,
            "to": self.to_agent,
            "content": self.content[:100] + "..." if len(self.content) > 100 else self.content,
            "type": self.msg_type,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority
        }

@dataclass
class Project:
    """项目实体"""
    id: str
    name: str
    description: str
    status: ProjectStatus
    proposed_by: str
    budget: float = 0.0
    spent: float = 0.0
    revenue: float = 0.0
    team: Dict[str, str] = field(default_factory=dict)  # agent_id -> role
    progress: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    phases: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "budget": self.budget,
            "spent": self.spent,
            "revenue": self.revenue,
            "roi": f"{((self.revenue - self.spent) / self.budget * 100):.1f}%" if self.budget > 0 else "N/A",
            "team": self.team,
            "progress": f"{self.progress:.0f}%",
            "created_at": self.created_at.isoformat()
        }

class VoxyzCompanySystem:
    """
    Voxyz风格多Agent公司系统
    核心特性:
    - Agent自主决策
    - 实时协作通信
    - 项目全生命周期管理
    - 智能监控与优化
    """
    
    def __init__(self, company_name: str = "Nexus Innovations"):
        self.company_name = company_name
        self.agents: Dict[str, Agent] = {}
        self.projects: Dict[str, Project] = {}
        self.messages: List[Message] = []
        self.financials = {
            "initial_capital": 1000000,
            "current_balance": 1000000,
            "total_revenue": 0,
            "total_expenses": 0,
            "investment_rounds": []
        }
        self.market_data = {
            "trends": [],
            "competitors": [],
            "opportunities": []
        }
        self.round = 0
        
        self._init_agents()
        self._init_market()
    
    def _init_agents(self):
        """初始化7个核心Agent"""
        agents_config = [
            ("ceo", AgentRole.CEO, "Alex Chen", ["战略决策", "领导力", "资源分配"]),
            ("cmo", AgentRole.CMO, "Sarah Miller", ["市场分析", "用户洞察", "竞品研究"]),
            ("cto", AgentRole.CTO, "David Kim", ["技术架构", "研发管理", "创新"]),
            ("coo", AgentRole.COO, "Emma Wilson", ["运营管理", "流程优化", "执行"]),
            ("pr", AgentRole.PR, "James Brown", ["品牌建设", "公关", "内容营销"]),
            ("cfo", AgentRole.CFO, "Lisa Wang", ["财务规划", "投资分析", "风险控制"]),
            ("observer", AgentRole.OBSERVER, "System", ["监控", "分析", "优化建议"])
        ]
        
        for agent_id, role, name, skills in agents_config:
            self.agents[agent_id] = Agent(
                id=agent_id,
                role=role,
                name=name,
                skills=skills
            )
    
    def _init_market(self):
        """初始化市场环境"""
        self.market_data["trends"] = [
            {"name": "AI应用爆发", "growth": 45, "opportunity": "high"},
            {"name": "远程办公常态化", "growth": 30, "opportunity": "medium"},
            {"name": "绿色科技", "growth": 25, "opportunity": "medium"},
            {"name": "Web3复苏", "growth": 15, "opportunity": "low"}
        ]
        
        self.market_data["competitors"] = [
            {"name": "TechGiant", "strength": "资金雄厚", "threat": "high"},
            {"name": "StartupX", "strength": "创新快速", "threat": "medium"},
            {"name": "LegacyCorp", "strength": "客户基础", "threat": "low"}
        ]
    
    async def run_simulation_round(self):
        """运行一轮公司模拟"""
        self.round += 1
        print(f"\n{'='*60}")
        print(f"🔄 第 {self.round} 轮公司运营模拟")
        print(f"{'='*60}")
        
        # 阶段1: 市场扫描 (CMO)
        opportunities = await self._cmo_scan_market()
        
        # 阶段2: 项目评估 (并行)
        for opp in opportunities[:2]:  # 评估前2个机会
            await self._evaluate_opportunity(opp)
        
        # 阶段3: 决策与执行
        await self._execute_projects()
        
        # 阶段4: 监控与反馈
        await self._observer_monitor()
        
        # 阶段5: 财务结算
        await self._cfo_financial_report()
        
        return self.get_dashboard_data()
    
    async def _cmo_scan_market(self) -> List[Dict]:
        """CMO扫描市场发现机会"""
        print(f"\n📊 CMO {self.agents['cmo'].name} 正在扫描市场...")
        
        opportunities = []
        for trend in self.market_data["trends"]:
            if trend["opportunity"] in ["high", "medium"]:
                opp = {
                    "id": f"opp_{random.randint(1000, 9999)}",
                    "name": f"{trend['name']}解决方案",
                    "market_size": random.randint(50, 500) * 1000000,
                    "growth_rate": trend["growth"],
                    "description": f"基于{trend['name']}的创新产品"
                }
                opportunities.append(opp)
                
                self._add_message(
                    "cmo", "all",
                    f"发现市场机会: {opp['name']}",
                    "opportunity"
                )
        
        self.agents['cmo'].tasks_completed += 1
        return opportunities
    
    async def _evaluate_opportunity(self, opportunity: Dict):
        """多Agent并行评估机会"""
        print(f"\n🔍 评估机会: {opportunity['name']}")
        
        # 创建项目
        project_id = f"proj_{random.randint(1000, 9999)}"
        project = Project(
            id=project_id,
            name=opportunity['name'],
            description=opportunity['description'],
            status=ProjectStatus.EVALUATING,
            proposed_by="cmo"
        )
        
        # 并行评估
        eval_results = await asyncio.gather(
            self._cto_tech_eval(project),
            self._cfo_financial_eval(project, opportunity),
            self._coo_operation_eval(project)
        )
        
        # CEO决策
        decision = await self._ceo_make_decision(project, eval_results)
        
        if decision["approved"]:
            project.status = ProjectStatus.APPROVED
            project.budget = decision["budget"]
            self.projects[project_id] = project
            self._allocate_team(project)
            print(f"✅ 项目 {project.name} 已批准，预算: ¥{project.budget:,.0f}")
        else:
            print(f"❌ 项目 {project.name} 被拒绝: {decision['reason']}")
    
    async def _cto_tech_eval(self, project: Project) -> Dict:
        """CTO技术评估"""
        self.agents['cto'].status = "busy"
        self.agents['cto'].current_task = f"评估 {project.name}"
        
        # 模拟评估
        await asyncio.sleep(0.5)
        
        feasibility = random.choice(["high", "medium", "low"])
        tech_stack = random.choice([
            ["Python", "React", "PostgreSQL"],
            ["Node.js", "Vue", "MongoDB"],
            ["Go", "Flutter", "Redis"]
        ])
        
        result = {
            "feasible": feasibility == "high",
            "tech_stack": tech_stack,
            "timeline": f"{random.randint(2, 6)}个月",
            "risks": random.sample(["技术债务", "人才短缺", "架构风险"], k=random.randint(0, 2))
        }
        
        self._add_message("cto", "ceo", f"技术评估完成: {project.name}", "evaluation")
        self.agents['cto'].status = "idle"
        self.agents['cto'].current_task = None
        self.agents['cto'].tasks_completed += 1
        
        return result
    
    async def _cfo_financial_eval(self, project: Project, opportunity: Dict) -> Dict:
        """CFO财务评估"""
        self.agents['cfo'].status = "busy"
        
        budget = random.randint(100000, 500000)
        roi = random.uniform(1.5, 4.0)
        
        result = {
            "budget_required": budget,
            "expected_roi": f"{roi:.1f}x",
            "break_even": f"{random.randint(6, 18)}个月",
            "risk_level": random.choice(["low", "medium", "high"])
        }
        
        self._add_message("cfo", "ceo", f"财务评估完成: {project.name}", "evaluation")
        self.agents['cfo'].status = "idle"
        self.agents['cfo'].tasks_completed += 1
        
        return result
    
    async def _coo_operation_eval(self, project: Project) -> Dict:
        """COO运营评估"""
        self.agents['coo'].status = "busy"
        
        result = {
            "team_ready": random.choice([True, False]),
            "process_fit": random.choice(["perfect", "good", "needs_adaptation"]),
            "market_timing": random.choice(["optimal", "good", "fair"])
        }
        
        self._add_message("coo", "ceo", f"运营评估完成: {project.name}", "evaluation")
        self.agents['coo'].status = "idle"
        self.agents['coo'].tasks_completed += 1
        
        return result
    
    async def _ceo_make_decision(self, project: Project, eval_results: List[Dict]) -> Dict:
        """CEO做最终决策"""
        self.agents['ceo'].status = "busy"
        
        cto_result, cfo_result, coo_result = eval_results
        
        # 决策逻辑
        score = 0
        if cto_result["feasible"]:
            score += 3
        if float(cfo_result["expected_roi"].replace("x", "")) > 2.0:
            score += 2
        if coo_result["team_ready"]:
            score += 2
        
        approved = score >= 5
        
        decision = {
            "approved": approved,
            "budget": cfo_result["budget_required"] if approved else 0,
            "reason": "综合评估通过" if approved else "风险过高或ROI不足",
            "priority": "high" if score >= 6 else "medium"
        }
        
        self._add_message(
            "ceo", "all",
            f"决策: {project.name} - {'批准' if approved else '拒绝'}",
            "decision"
        )
        
        self.agents['ceo'].status = "idle"
        self.agents['ceo'].tasks_completed += 1
        
        return decision
    
    def _allocate_team(self, project: Project):
        """为项目分配团队"""
        project.team = {
            "cto": "技术负责人",
            "coo": "运营负责人",
            "pr": "市场负责人",
            "cfo": "财务监控"
        }
    
    async def _execute_projects(self):
        """执行进行中的项目"""
        for project in self.projects.values():
            if project.status == ProjectStatus.APPROVED:
                project.status = ProjectStatus.EXECUTING
                print(f"\n🚀 项目 {project.name} 开始执行")
                
                # 模拟进度
                project.progress = min(100, project.progress + random.randint(10, 30))
                project.spent += random.randint(10000, 50000)
                
                if project.progress >= 100:
                    project.status = ProjectStatus.COMPLETED
                    project.revenue = project.budget * random.uniform(1.2, 3.0)
                    self.financials["total_revenue"] += project.revenue
                    print(f"✅ 项目 {project.name} 完成! 收入: ¥{project.revenue:,.0f}")
    
    async def _observer_monitor(self):
        """Observer监控和反馈"""
        print(f"\n👁️ Observer 正在监控系统...")
        
        # 检测协作问题
        issues = []
        for agent in self.agents.values():
            if agent.role != AgentRole.OBSERVER and agent.tasks_failed > 0:
                issues.append(f"{agent.name} 有失败任务")
        
        # 检测资源问题
        if self.financials["current_balance"] < 200000:
            issues.append("资金紧张，需要融资")
        
        if issues:
            self._add_message("observer", "ceo", f"发现问题: {'; '.join(issues)}", "alert")
            print(f"⚠️ 发现问题: {issues}")
        else:
            print("✅ 系统运行正常")
        
        self.agents['observer'].tasks_completed += 1
    
    async def _cfo_financial_report(self):
        """CFO财务报告"""
        self.financials["current_balance"] = (
            self.financials["initial_capital"] +
            self.financials["total_revenue"] -
            self.financials["total_expenses"]
        )
        
        print(f"\n💰 财务报告:")
        print(f"   初始资金: ¥{self.financials['initial_capital']:,.0f}")
        print(f"   总收入: ¥{self.financials['total_revenue']:,.0f}")
        print(f"   总支出: ¥{self.financials['total_expenses']:,.0f}")
        print(f"   当前余额: ¥{self.financials['current_balance']:,.0f}")
    
    def _add_message(self, from_agent: str, to_agent: str, content: str, msg_type: str):
        """添加通信记录"""
        msg = Message(
            id=f"msg_{random.randint(10000, 99999)}",
            from_agent=from_agent,
            to_agent=to_agent,
            content=content,
            msg_type=msg_type,
            timestamp=datetime.now()
        )
        self.messages.append(msg)
    
    def get_dashboard_data(self) -> Dict:
        """获取仪表盘数据"""
        return {
            "company": {
                "name": self.company_name,
                "round": self.round,
                "status": "运营中"
            },
            "financials": self.financials,
            "agents": {k: v.to_dict() for k, v in self.agents.items()},
            "projects": [p.to_dict() for p in self.projects.values()],
            "recent_messages": [m.to_dict() for m in self.messages[-10:]],
            "market": self.market_data
        }

async def main():
    """运行演示"""
    print("="*60)
    print("🏢 Voxyz-Style Multi-Agent Company System")
    print("="*60)
    print("\n模拟7个AI Agent协作运营一家公司")
    print("Agent团队: CEO, CMO, CTO, COO, PR, CFO, Observer\n")
    
    company = VoxyzCompanySystem()
    
    # 运行3轮模拟
    for i in range(3):
        dashboard = await company.run_simulation_round()
        await asyncio.sleep(1)
    
    # 最终报告
    print("\n" + "="*60)
    print("📊 最终仪表盘")
    print("="*60)
    print(json.dumps(dashboard, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
