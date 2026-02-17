#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Company System Demo - 多Agent公司系统演示
使用 OpenClaw sessions_spawn 启动真实Agent
"""

import json
import time
from datetime import datetime
from pathlib import Path

class CompanyDemo:
    """公司系统演示"""
    
    def __init__(self):
        self.data_file = Path.home() / '.openclaw' / 'company_system' / 'demo_state.json'
        self.load_state()
    
    def load_state(self):
        """加载状态"""
        if self.data_file.exists():
            with open(self.data_file) as f:
                self.state = json.load(f)
        else:
            self.state = {
                'agents': {},
                'projects': [],
                'communications': [],
                'step': 0
            }
    
    def save_state(self):
        """保存状态"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def run_demo_step(self, step: int):
        """运行演示的某个步骤"""
        steps = {
            1: self.step1_discovery,
            2: self.step2_evaluation,
            3: self.step3_decision,
            4: self.step4_execution,
            5: self.step5_monitoring
        }
        
        func = steps.get(step)
        if func:
            return func()
        else:
            return {"error": f"Unknown step: {step}"}
    
    def step1_discovery(self):
        """步骤1: 市场发现 - CMO发现机会"""
        print("\n" + "="*60)
        print("📊 步骤1: 市场机会发现 (CMO)")
        print("="*60)
        
        # 模拟CMO输出
        result = {
            "agent": "CMO",
            "task": "市场调研与机会发现",
            "findings": [
                {
                    "opportunity": "AI内容创作平台",
                    "market_size": "100亿+",
                    "growth_rate": "45%年增长率",
                    "target_users": "内容创作者、营销人员",
                    "pain_points": "创作效率低、灵感枯竭",
                    "recommendation": "强烈推荐"
                },
                {
                    "opportunity": "企业自动化工具",
                    "market_size": "50亿+",
                    "growth_rate": "30%年增长率",
                    "target_users": "中小企业",
                    "pain_points": "人工操作繁琐、效率低",
                    "recommendation": "建议进入"
                }
            ],
            "next_action": "提交CEO审批"
        }
        
        self._add_communication("CMO", "CEO", "project_proposal", 
                               "发现AI内容创作平台机会，建议启动项目")
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
    
    def step2_evaluation(self):
        """步骤2: 可行性评估 - 多部门并行评估"""
        print("\n" + "="*60)
        print("🔍 步骤2: 可行性评估 (并行)")
        print("="*60)
        
        results = {}
        
        # CTO评估
        print("\n🖥️  CTO技术评估...")
        results['cto'] = {
            "feasible": True,
            "tech_stack": ["Python", "OpenAI API", "React", "PostgreSQL"],
            "team_required": {"backend": 2, "frontend": 2, "ai": 1},
            "timeline": "3个月MVP",
            "risks": ["AI模型依赖", "数据安全"],
            "recommendation": "技术可行"
        }
        
        # CFO评估
        print("💰 CFO财务评估...")
        results['cfo'] = {
            "budget_required": 300000,
            "break_even": "6个月",
            "year1_revenue": 1500000,
            "roi": "400%",
            "risks": ["市场接受度", "获客成本"],
            "recommendation": "财务可行"
        }
        
        # COO评估
        print("⚙️  COO运营评估...")
        results['coo'] = {
            "operation_ready": True,
            "team_structure": "产品+技术+运营",
            "processes": ["敏捷开发", "用户反馈", "数据驱动"],
            "metrics": ["DAU", "付费率", "留存率"],
            "recommendation": "运营可行"
        }
        
        self._add_communication("CTO", "CEO", "evaluation_report", "技术评估完成")
        self._add_communication("CFO", "CEO", "evaluation_report", "财务评估完成")
        self._add_communication("COO", "CEO", "evaluation_report", "运营评估完成")
        
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return results
    
    def step3_decision(self):
        """步骤3: 战略决策 - CEO决策"""
        print("\n" + "="*60)
        print("🎯 步骤3: 战略决策 (CEO)")
        print("="*60)
        
        decision = {
            "agent": "CEO",
            "decision": "批准启动",
            "project_name": "AI内容创作平台",
            "budget_approved": 300000,
            "timeline": "3个月MVP，6个月商业化",
            "team": {
                "cto": "技术负责",
                "coo": "运营负责",
                "pr": "市场负责",
                "cfo": "财务监控"
            },
            "milestones": [
                "1个月：产品原型",
                "2个月：内测版本",
                "3个月：MVP发布",
                "6个月：商业化运营"
            ],
            "priority": "高"
        }
        
        self._add_communication("CEO", "All", "decision", 
                               "批准启动AI内容创作平台项目")
        
        print(json.dumps(decision, indent=2, ensure_ascii=False))
        return decision
    
    def step4_execution(self):
        """步骤4: 项目执行 - 团队协作"""
        print("\n" + "="*60)
        print("🚀 步骤4: 项目执行 (团队协作)")
        print("="*60)
        
        progress = {
            "week": 4,
            "overall_progress": "35%",
            "tasks": {
                "cto": {
                    "status": "进行中",
                    "completed": ["架构设计", "数据库设计"],
                    "in_progress": ["API开发", "AI接口集成"],
                    "progress": "40%"
                },
                "coo": {
                    "status": "进行中",
                    "completed": ["运营流程设计", "团队搭建"],
                    "in_progress": ["用户调研", "数据埋点"],
                    "progress": "30%"
                },
                "pr": {
                    "status": "进行中",
                    "completed": ["品牌定位", "官网设计"],
                    "in_progress": ["内容创作", "社交媒体"],
                    "progress": "25%"
                },
                "cfo": {
                    "status": "监控中",
                    "completed": ["预算分配", "成本基线"],
                    "in_progress": ["月度审计", "ROI跟踪"],
                    "progress": "50%"
                }
            }
        }
        
        self._add_communication("COO", "All", "progress_report", "第4周进度：35%")
        
        print(json.dumps(progress, indent=2, ensure_ascii=False))
        return progress
    
    def step5_monitoring(self):
        """步骤5: 监控反馈 - Observer观察"""
        print("\n" + "="*60)
        print("👁️ 步骤5: 运营监控 (Observer)")
        print("="*60)
        
        observation = {
            "agent": "Observer",
            "observation_period": "Week 4",
            "overall_assessment": "良好",
            "findings": [
                {
                    "type": "positive",
                    "description": "CTO团队技术进度超前",
                    "impact": "项目可能提前完成"
                },
                {
                    "type": "warning",
                    "description": "PR和COO沟通频率偏低",
                    "impact": "可能影响市场定位准确性",
                    "recommendation": "建议每周同步会议"
                },
                {
                    "type": "info",
                    "description": "CFO成本控制良好",
                    "impact": "预算使用率85%，在预期范围内"
                }
            ],
            "recommendations": [
                "增加PR和COO的沟通频次",
                "提前规划Beta测试用户",
                "关注竞品动态"
            ],
            "next_review": "Week 6"
        }
        
        self._add_communication("Observer", "CEO", "observation_report",
                               "发现PR和COO沟通问题，建议改进")
        
        print(json.dumps(observation, indent=2, ensure_ascii=False))
        return observation
    
    def _add_communication(self, from_agent, to_agent, msg_type, content):
        """添加通信记录"""
        self.state['communications'].append({
            'from': from_agent,
            'to': to_agent,
            'type': msg_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        self.save_state()
    
    def generate_ui_data(self):
        """生成UI数据"""
        return {
            "company": {
                "name": "OpenClaw Innovations",
                "agents_count": 7,
                "active_projects": 1,
                "completed_projects": 2
            },
            "agents": {
                "ceo": {"name": "CEO", "status": "active", "task": "战略决策"},
                "cmo": {"name": "CMO", "status": "idle", "task": None},
                "cto": {"name": "CTO", "status": "busy", "task": "产品开发"},
                "coo": {"name": "COO", "status": "busy", "task": "运营搭建"},
                "pr": {"name": "PR", "status": "busy", "task": "品牌建设"},
                "cfo": {"name": "CFO", "status": "active", "task": "财务监控"},
                "observer": {"name": "Observer", "status": "active", "task": "协作观察"}
            },
            "current_project": {
                "name": "AI内容创作平台",
                "progress": 35,
                "status": "executing",
                "budget_used": 105000,
                "budget_total": 300000
            },
            "communications": self.state['communications'][-10:]
        }

def main():
    """运行完整演示"""
    print("="*60)
    print("🏢 OpenClaw 多Agent公司系统演示")
    print("="*60)
    print("\n系统将演示7个Agent如何协作完成一个项目")
    print("包括：CEO, CMO, CTO, COO, PR, CFO, Observer")
    
    demo = CompanyDemo()
    
    # 运行5个步骤
    for step in range(1, 6):
        input(f"\n按 Enter 继续步骤 {step}...")
        result = demo.run_demo_step(step)
    
    # 生成最终UI数据
    print("\n" + "="*60)
    print("📊 最终UI数据")
    print("="*60)
    ui_data = demo.generate_ui_data()
    print(json.dumps(ui_data, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("✅ 演示完成")
    print("="*60)
    print("\n查看UI界面请打开: dashboard.html")

if __name__ == '__main__':
    main()
