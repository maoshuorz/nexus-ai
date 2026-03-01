#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Multi-Agent Company System - 高级多Agent公司系统
拓展版 - 支持更多功能和更复杂的协作
"""

import json
import asyncio
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable
from enum import Enum, auto
from pathlib import Path
import uuid

class TaskPriority(Enum):
    """任务优先级"""
    CRITICAL = auto()  # 紧急
    HIGH = auto()      # 高
    MEDIUM = auto()    # 中
    LOW = auto()       # 低

class AgentState(Enum):
    """Agent状态"""
    IDLE = "idle"           # 空闲
    WORKING = "working"     # 工作中
    THINKING = "thinking"   # 思考中
    WAITING = "waiting"     # 等待中
    OFFLINE = "offline"     # 离线

class ProjectPhase(Enum):
    """项目阶段"""
    DISCOVERY = "发现"
    RESEARCH = "调研"
    PLANNING = "规划"
    DEVELOPMENT = "开发"
    TESTING = "测试"
    LAUNCH = "发布"
    GROWTH = "增长"
    MAINTENANCE = "维护"
    SUNSET = "下线"

@dataclass
class Skill:
    """技能"""
    name: str
    level: int  # 1-10
    experience: int = 0  # 经验值
    
    def improve(self, amount: int = 1):
        """提升技能"""
        self.experience += amount
        if self.experience >= self.level * 100:
            self.level += 1
            self.experience = 0
            return True
        return False

@dataclass
class Task:
    """任务"""
    id: str
    title: str
    description: str
    assigned_to: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    subtasks: List['Task'] = field(default_factory=list)
    progress: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status,
            "priority": self.priority.name,
            "progress": f"{self.progress:.0f}%",
            "assigned_to": self.assigned_to
        }

@dataclass
class Agent:
    """增强版Agent"""
    id: str
    name: str
    role: str
    avatar: str = "🤖"
    state: AgentState = AgentState.IDLE
    current_task: Optional[Task] = None
    skills: Dict[str, Skill] = field(default_factory=dict)
    performance_score: float = 100.0
    energy: float = 100.0  # 精力值
    stress: float = 0.0    # 压力值
    happiness: float = 100.0  # 满意度
    tasks_completed: int = 0
    tasks_failed: int = 0
    messages_sent: int = 0
    collaboration_score: float = 100.0
    specialties: List[str] = field(default_factory=list)
    workload: int = 0  # 当前工作量
    max_workload: int = 5  # 最大工作量
    
    def __post_init__(self):
        """初始化默认技能"""
        if not self.skills:
            self.skills = {
                "communication": Skill("沟通", 7),
                "problem_solving": Skill("问题解决", 7),
                "teamwork": Skill("团队协作", 7)
            }
        # Star Office 桥接（延迟初始化）
        self._bridge = None
    
    def set_state(self, state: str, note: str = ""):
        """发布 Agent 状态到 Star Office 看板（异步，不阻塞主逻辑）

        Args:
            state: 状态字符串，支持 idle/writing/researching/executing/syncing/error
                   以及 Nexus AI 内部状态 working/thinking/waiting/offline
            note:  当前任务描述（可选）

        示例:
            self.set_state("writing", "正在分析市场数据")
            self.set_state("idle")
        """
        if self._bridge is None:
            try:
                from star_office_bridge import StatePublisher
                self._bridge = StatePublisher(self.name)
            except ImportError:
                self._bridge = False  # 标记为已尝试，不再重试
        if self._bridge:
            self._bridge.set_state(state, note)

    def can_take_task(self) -> bool:
        """是否能接受新任务"""
        return (self.state == AgentState.IDLE and 
                self.workload < self.max_workload and
                self.energy > 20 and
                self.stress < 80)
    
    def assign_task(self, task: Task) -> bool:
        """分配任务"""
        if not self.can_take_task():
            return False
        
        self.current_task = task
        task.assigned_to = self.id
        self.state = AgentState.WORKING
        self.workload += 1
        return True
    
    def complete_task(self, success: bool = True):
        """完成任务"""
        if success:
            self.tasks_completed += 1
            self.performance_score = min(100, self.performance_score + 2)
            self.happiness = min(100, self.happiness + 5)
            # 提升相关技能
            for skill in self.skills.values():
                if skill.improve(10):
                    print(f"🎉 {self.name} 的 {skill.name} 技能提升到 Lv.{skill.level}!")
        else:
            self.tasks_failed += 1
            self.performance_score = max(0, self.performance_score - 5)
            self.stress = min(100, self.stress + 10)
        
        self.workload -= 1
        self.current_task = None
        self.state = AgentState.IDLE if self.workload == 0 else AgentState.WORKING
    
    def rest(self, hours: int = 1):
        """休息恢复"""
        self.energy = min(100, self.energy + hours * 10)
        self.stress = max(0, self.stress - hours * 5)
        self.state = AgentState.IDLE
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "avatar": self.avatar,
            "state": self.state.value,
            "current_task": self.current_task.title if self.current_task else None,
            "skills": {k: {"level": v.level, "exp": v.experience} for k, v in self.skills.items()},
            "performance": f"{self.performance_score:.0f}",
            "energy": f"{self.energy:.0f}",
            "stress": f"{self.stress:.0f}",
            "happiness": f"{self.happiness:.0f}",
            "workload": f"{self.workload}/{self.max_workload}"
        }

@dataclass
class Meeting:
    """会议"""
    id: str
    title: str
    participants: List[str]
    agenda: List[str]
    start_time: datetime
    duration: int  # 分钟
    decisions: List[str] = field(default_factory=list)
    action_items: List[Task] = field(default_factory=list)
    status: str = "scheduled"  # scheduled, ongoing, completed

@dataclass
class Project:
    """增强版项目"""
    id: str
    name: str
    description: str
    phase: ProjectPhase
    status: str = "active"
    
    # 财务
    budget: float = 0.0
    spent: float = 0.0
    revenue: float = 0.0
    projected_revenue: float = 0.0
    
    # 团队
    owner: str = ""  # 项目负责人
    team: Dict[str, str] = field(default_factory=dict)  # agent_id -> role
    stakeholders: List[str] = field(default_factory=list)
    
    # 进度
    progress: float = 0.0
    milestones: List[Dict] = field(default_factory=list)
    current_milestone: int = 0
    
    # 任务
    tasks: List[Task] = field(default_factory=list)
    completed_tasks: List[Task] = field(default_factory=list)
    
    # 时间
    start_date: datetime = field(default_factory=datetime.now)
    target_date: Optional[datetime] = None
    actual_end_date: Optional[datetime] = None
    
    # 质量
    quality_score: float = 0.0
    customer_satisfaction: float = 0.0
    
    # 风险
    risks: List[Dict] = field(default_factory=list)
    
    def add_task(self, task: Task):
        """添加任务"""
        self.tasks.append(task)
    
    def update_progress(self):
        """更新进度"""
        if not self.tasks:
            self.progress = 0.0
            return
        
        completed = len([t for t in self.tasks if t.status == "completed"])
        self.progress = (completed / len(self.tasks)) * 100
    
    def get_roi(self) -> float:
        """计算ROI"""
        if self.spent == 0:
            return 0.0
        return (self.revenue - self.spent) / self.spent * 100
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phase": self.phase.value,
            "status": self.status,
            "budget": f"¥{self.budget:,.0f}",
            "spent": f"¥{self.spent:,.0f}",
            "revenue": f"¥{self.revenue:,.0f}",
            "roi": f"{self.get_roi():.1f}%",
            "progress": f"{self.progress:.0f}%",
            "team_size": len(self.team),
            "tasks": f"{len(self.completed_tasks)}/{len(self.tasks)}"
        }

class AdvancedCompanySystem:
    """高级多Agent公司系统"""
    
    def __init__(self, company_name: str = "Nexus AI"):
        self.company_name = company_name
        self.company_id = str(uuid.uuid4())[:8]
        
        # 核心组件
        self.agents: Dict[str, Agent] = {}
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.meetings: List[Meeting] = []
        
        # 通信
        self.messages: List[Dict] = []
        self.notifications: List[Dict] = []
        
        # 财务
        self.financials = {
            "initial_capital": 2000000,  # 200万初始资金
            "cash_flow": 2000000,
            "total_revenue": 0,
            "total_expenses": 0,
            "investment_history": [],
            "monthly_burn_rate": 0
        }
        
        # 市场
        self.market = {
            "trends": [],
            "competitors": [],
            "opportunities": [],
            "threats": []
        }
        
        # 运营
        self.metrics = {
            "round": 0,
            "day": 1,
            "total_meetings": 0,
            "total_decisions": 0,
            "employee_satisfaction": 100.0,
            "customer_satisfaction": 0.0
        }
        
        self._init_agents()
        self._init_market_data()
    
    def _init_agents(self):
        """初始化Agent团队"""
        agent_configs = [
            {
                "id": "ceo",
                "name": "Alex Chen",
                "role": "CEO",
                "avatar": "👨‍💼",
                "specialties": ["战略决策", "领导力", "融资"],
                "skills": {
                    "leadership": Skill("领导力", 9),
                    "strategy": Skill("战略规划", 9),
                    "communication": Skill("沟通", 8)
                }
            },
            {
                "id": "cmo",
                "name": "Sarah Miller",
                "role": "CMO",
                "avatar": "👩‍💼",
                "specialties": ["市场分析", "用户洞察", "品牌建设"],
                "skills": {
                    "marketing": Skill("营销", 9),
                    "analytics": Skill("数据分析", 8),
                    "communication": Skill("沟通", 8)
                }
            },
            {
                "id": "cto",
                "name": "David Kim",
                "role": "CTO",
                "avatar": "👨‍💻",
                "specialties": ["技术架构", "AI/ML", "研发管理"],
                "skills": {
                    "programming": Skill("编程", 10),
                    "architecture": Skill("架构设计", 9),
                    "innovation": Skill("创新", 8)
                }
            },
            {
                "id": "coo",
                "name": "Emma Wilson",
                "role": "COO",
                "avatar": "👩‍💻",
                "specialties": ["运营管理", "流程优化", "团队协作"],
                "skills": {
                    "operations": Skill("运营", 9),
                    "management": Skill("管理", 8),
                    "teamwork": Skill("团队协作", 9)
                }
            },
            {
                "id": "cpo",
                "name": "Michael Zhang",
                "role": "CPO",
                "avatar": "👨‍🎨",
                "specialties": ["产品设计", "用户体验", "产品策略"],
                "skills": {
                    "design": Skill("设计", 9),
                    "ux": Skill("用户体验", 9),
                    "strategy": Skill("产品策略", 8)
                }
            },
            {
                "id": "cfo",
                "name": "Lisa Wang",
                "role": "CFO",
                "avatar": "👩‍💼",
                "specialties": ["财务规划", "投资分析", "风险控制"],
                "skills": {
                    "finance": Skill("财务", 10),
                    "analysis": Skill("分析", 9),
                    "risk_management": Skill("风险管理", 8)
                }
            },
            {
                "id": "chro",
                "name": "James Brown",
                "role": "CHRO",
                "avatar": "👨‍💼",
                "specialties": ["人才招聘", "企业文化", "员工发展"],
                "skills": {
                    "recruiting": Skill("招聘", 9),
                    "culture": Skill("文化建设", 8),
                    "development": Skill("人才发展", 8)
                }
            },
            {
                "id": "observer",
                "name": "System AI",
                "role": "Observer",
                "avatar": "🤖",
                "specialties": ["系统监控", "数据分析", "优化建议"],
                "skills": {
                    "monitoring": Skill("监控", 10),
                    "analytics": Skill("分析", 10),
                    "optimization": Skill("优化", 9)
                }
            }
        ]
        
        for config in agent_configs:
            self.agents[config["id"]] = Agent(
                id=config["id"],
                name=config["name"],
                role=config["role"],
                avatar=config["avatar"],
                specialties=config["specialties"],
                skills=config.get("skills", {})
            )
    
    def _init_market_data(self):
        """初始化市场数据"""
        self.market["trends"] = [
            {"name": "生成式AI", "growth": 65, "maturity": "growth", "opportunity": "high"},
            {"name": "AI Agent平台", "growth": 45, "maturity": "early", "opportunity": "high"},
            {"name": "自动化工作流", "growth": 35, "maturity": "growth", "opportunity": "medium"},
            {"name": "低代码/无代码", "growth": 25, "maturity": "mature", "opportunity": "medium"},
            {"name": "Web3基础设施", "growth": 15, "maturity": "early", "opportunity": "low"}
        ]
    
    async def run_daily_simulation(self) -> Dict:
        """运行每日模拟"""
        self.metrics["day"] += 1
        
        print(f"\n{'='*70}")
        print(f"📅 Day {self.metrics['day']} - {self.company_name}")
        print(f"{'='*70}")
        
        # 1. 晨会
        await self._morning_standup()
        
        # 2. CMO市场扫描
        opportunities = await self._cmo_market_scan()
        
        # 3. 评估机会
        for opp in opportunities[:3]:
            await self._evaluate_opportunity(opp)
        
        # 4. 项目执行
        await self._execute_projects()
        
        # 5. 团队管理
        await self._hr_management()
        
        # 6. 财务结算
        await self._daily_financials()
        
        # 7. Observer日报
        await self._daily_report()
        
        return self.get_full_dashboard()
    
    async def _morning_standup(self):
        """每日晨会"""
        print("\n🌅 Morning Standup")
        
        meeting = Meeting(
            id=f"standup_{self.metrics['day']}",
            title=f"Day {self.metrics['day']} Standup",
            participants=[a.id for a in self.agents.values() if a.role != "Observer"],
            agenda=["昨日进展", "今日计划", "阻塞问题"],
            start_time=datetime.now(),
            duration=15
        )
        
        for agent in self.agents.values():
            if agent.current_task:
                print(f"  {agent.avatar} {agent.name}: {agent.current_task.title} ({agent.current_task.progress:.0f}%)")
        
        self.meetings.append(meeting)
        self.metrics["total_meetings"] += 1
    
    async def _cmo_market_scan(self) -> List[Dict]:
        """CMO扫描市场"""
        cmo = self.agents["cmo"]
        cmo.state = AgentState.WORKING
        
        print(f"\n📊 {cmo.avatar} {cmo.name} scanning market...")
        
        opportunities = []
        for trend in self.market["trends"]:
            if trend["opportunity"] in ["high", "medium"] and random.random() > 0.3:
                opp = {
                    "id": str(uuid.uuid4())[:8],
                    "name": f"{trend['name']} Platform",
                    "market_size": random.randint(100, 1000) * 1000000,
                    "growth_rate": trend["growth"],
                    "difficulty": random.choice(["easy", "medium", "hard"]),
                    "description": f"AI-powered {trend['name']} solution"
                }
                opportunities.append(opp)
                self._log_message("cmo", "all", f"发现机会: {opp['name']}", "opportunity")
        
        cmo.tasks_completed += 1
        cmo.state = AgentState.IDLE
        
        return opportunities
    
    async def _evaluate_opportunity(self, opportunity: Dict):
        """评估机会"""
        print(f"\n🔍 Evaluating: {opportunity['name']}")
        
        # 创建项目
        project = Project(
            id=f"proj_{opportunity['id']}",
            name=opportunity['name'],
            description=opportunity['description'],
            phase=ProjectPhase.DISCOVERY,
            projected_revenue=opportunity['market_size'] * random.uniform(0.001, 0.01)
        )
        
        # 多Agent评估会议
        meeting = Meeting(
            id=f"eval_{opportunity['id']}",
            title=f"Evaluate {opportunity['name']}",
            participants=["cto", "cfo", "cpo", "coo"],
            agenda=["技术评估", "财务评估", "产品评估", "运营评估"],
            start_time=datetime.now(),
            duration=60
        )
        
        # 并行评估
        eval_results = await asyncio.gather(
            self._agent_evaluate("cto", project, "technical"),
            self._agent_evaluate("cfo", project, "financial"),
            self._agent_evaluate("cpo", project, "product"),
            self._agent_evaluate("coo", project, "operational")
        )
        
        # CEO决策
        decision = await self._ceo_decision(project, eval_results)
        
        if decision["approved"]:
            project.budget = decision["budget"]
            project.phase = ProjectPhase.PLANNING
            project.owner = "ceo"
            project.team = {
                "cto": "Tech Lead",
                "cpo": "Product Lead",
                "coo": "Operations Lead",
                "cfo": "Financial Oversight"
            }
            self.projects[project.id] = project
            
            # 创建任务
            self._create_project_tasks(project)
            
            print(f"✅ Project approved: {project.name} (Budget: ¥{project.budget:,.0f})")
        else:
            print(f"❌ Project rejected: {project.name} ({decision['reason']})")
        
        meeting.decisions.append(decision)
        self.meetings.append(meeting)
    
    async def _agent_evaluate(self, agent_id: str, project: Project, aspect: str) -> Dict:
        """Agent评估"""
        agent = self.agents[agent_id]
        agent.state = AgentState.THINKING
        
        await asyncio.sleep(0.5)  # 模拟思考时间
        
        scores = {
            "technical": {"feasible": True, "complexity": random.choice(["low", "medium", "high"]), "score": random.randint(60, 95)},
            "financial": {"roi": random.uniform(1.5, 4.0), "risk": random.choice(["low", "medium", "high"]), "score": random.randint(60, 95)},
            "product": {"market_fit": random.choice(["poor", "fair", "good", "excellent"]), "innovation": random.randint(60, 95), "score": random.randint(60, 95)},
            "operational": {"team_ready": random.choice([True, False]), "resources": random.choice(["sufficient", "limited", "insufficient"]), "score": random.randint(60, 95)}
        }
        
        agent.state = AgentState.IDLE
        agent.tasks_completed += 1
        
        return {"agent": agent_id, "aspect": aspect, **scores[aspect]}
    
    async def _ceo_decision(self, project: Project, eval_results: List[Dict]) -> Dict:
        """CEO决策"""
        ceo = self.agents["ceo"]
        ceo.state = AgentState.THINKING
        
        # 综合评分
        total_score = sum(r.get("score", 0) for r in eval_results)
        avg_score = total_score / len(eval_results)
        
        # 决策逻辑
        approved = avg_score >= 75 and all(r.get("feasible", True) for r in eval_results if "feasible" in r)
        
        budget = random.randint(200000, 800000) if approved else 0
        
        decision = {
            "approved": approved,
            "budget": budget,
            "reason": "综合评分通过" if approved else "评分不足或存在风险",
            "avg_score": avg_score,
            "confidence": random.uniform(0.7, 0.95)
        }
        
        ceo.state = AgentState.IDLE
        ceo.tasks_completed += 1
        self.metrics["total_decisions"] += 1
        
        self._log_message("ceo", "all", f"决策: {project.name} - {'批准' if approved else '拒绝'}", "decision")
        
        return decision
    
    def _create_project_tasks(self, project: Project):
        """创建项目任务"""
        tasks_data = [
            {"title": "需求分析", "assigned_to": "cpo", "duration": 7},
            {"title": "技术架构设计", "assigned_to": "cto", "duration": 10},
            {"title": "UI/UX设计", "assigned_to": "cpo", "duration": 14},
            {"title": "后端开发", "assigned_to": "cto", "duration": 30},
            {"title": "前端开发", "assigned_to": "cto", "duration": 25},
            {"title": "测试与QA", "assigned_to": "coo", "duration": 14},
            {"title": "部署上线", "assigned_to": "cto", "duration": 5},
            {"title": "市场推广", "assigned_to": "cmo", "duration": 21}
        ]
        
        for i, td in enumerate(tasks_data):
            task = Task(
                id=f"task_{project.id}_{i}",
                title=td["title"],
                description=f"{td['title']} for {project.name}",
                assigned_to=td["assigned_to"],
                deadline=datetime.now() + timedelta(days=td["duration"])
            )
            project.add_task(task)
            self.tasks[task.id] = task
    
    async def _execute_projects(self):
        """执行项目"""
        print("\n🚀 Project Execution")
        
        for project in self.projects.values():
            if project.status != "active":
                continue
            
            # 更新进度
            for task in project.tasks:
                if task.status == "pending" and random.random() > 0.5:
                    task.status = "in_progress"
                    agent = self.agents.get(task.assigned_to)
                    if agent:
                        agent.assign_task(task)
                
                elif task.status == "in_progress":
                    task.progress = min(100, task.progress + random.randint(10, 30))
                    
                    if task.progress >= 100:
                        task.status = "completed"
                        project.completed_tasks.append(task)
                        
                        agent = self.agents.get(task.assigned_to)
                        if agent:
                            agent.complete_task(success=True)
            
            project.update_progress()
            
            # 消耗预算
            if project.progress < 100:
                daily_cost = project.budget * 0.005  # 每天消耗0.5%
                project.spent += daily_cost
                self.financials["total_expenses"] += daily_cost
                self.financials["cash_flow"] -= daily_cost
            
            print(f"  📊 {project.name}: {project.progress:.0f}% (¥{project.spent:,.0f} spent)")
    
    async def _hr_management(self):
        """HR管理"""
        chro = self.agents["chro"]
        
        # 检查员工状态
        for agent in self.agents.values():
            if agent.id == "observer":
                continue
            
            # 压力管理
            if agent.stress > 70:
                agent.happiness -= 5
                self._log_message("chro", agent.id, "注意压力管理，建议休息", "warning")
            
            # 休息恢复
            if agent.energy < 30:
                agent.rest(2)
                self._log_message("chro", agent.id, "已安排休息时间", "info")
        
        # 计算员工满意度
        total_happiness = sum(a.happiness for a in self.agents.values() if a.id != "observer")
        self.metrics["employee_satisfaction"] = total_happiness / 7
    
    async def _daily_financials(self):
        """每日财务"""
        print("\n💰 Daily Financials")
        print(f"  Cash Flow: ¥{self.financials['cash_flow']:,.0f}")
        print(f"  Revenue: ¥{self.financials['total_revenue']:,.0f}")
        print(f"  Expenses: ¥{self.financials['total_expenses']:,.0f}")
    
    async def _daily_report(self):
        """每日报告"""
        observer = self.agents["observer"]
        
        print("\n📋 Daily Report")
        
        # 统计
        active_projects = len([p for p in self.projects.values() if p.status == "active"])
        completed_tasks = sum(len(p.completed_tasks) for p in self.projects.values())
        
        print(f"  Active Projects: {active_projects}")
        print(f"  Completed Tasks: {completed_tasks}")
        print(f"  Employee Satisfaction: {self.metrics['employee_satisfaction']:.1f}%")
        
        observer.tasks_completed += 1
    
    def _log_message(self, from_id: str, to_id: str, content: str, msg_type: str):
        """记录消息"""
        self.messages.append({
            "id": str(uuid.uuid4())[:8],
            "from": from_id,
            "to": to_id,
            "content": content,
            "type": msg_type,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_full_dashboard(self) -> Dict:
        """获取完整仪表盘"""
        return {
            "company": {
                "name": self.company_name,
                "id": self.company_id,
                "day": self.metrics["day"],
                "status": "operating"
            },
            "financials": {
                "cash_flow": f"¥{self.financials['cash_flow']:,.0f}",
                "revenue": f"¥{self.financials['total_revenue']:,.0f}",
                "expenses": f"¥{self.financials['total_expenses']:,.0f}",
                "burn_rate": f"¥{self.financials['monthly_burn_rate']:,.0f}/月"
            },
            "agents": [a.to_dict() for a in self.agents.values()],
            "projects": [p.to_dict() for p in self.projects.values()],
            "metrics": {
                "day": self.metrics["day"],
                "meetings": self.metrics["total_meetings"],
                "decisions": self.metrics["total_decisions"],
                "employee_satisfaction": f"{self.metrics['employee_satisfaction']:.1f}%"
            },
            "recent_messages": self.messages[-10:]
        }

async def main():
    """运行高级模拟"""
    print("="*70)
    print("🏢 Advanced Multi-Agent Company System")
    print("="*70)
    print("\nSimulating 8 AI Agents running a tech company\n")
    
    company = AdvancedCompanySystem(company_name="Nexus AI Technologies")
    
    # 运行7天模拟
    for day in range(7):
        dashboard = await company.run_daily_simulation()
        await asyncio.sleep(1)
        print("\n" + "-"*70)
    
    # 最终报告
    print("\n" + "="*70)
    print("📊 Final Dashboard")
    print("="*70)
    print(json.dumps(dashboard, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
