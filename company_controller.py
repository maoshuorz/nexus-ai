#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Company System - 多Agent公司系统
Main Controller - 主控制器
"""

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class CompanySystem:
    """公司系统主控制器"""
    
    def __init__(self, company_name="OpenClaw Innovations"):
        self.company_name = company_name
        self.agents = {}
        self.projects = {}
        self.communications = []
        self.financials = {
            'total_budget': 1000000,  # 初始资金100万
            'spent': 0,
            'revenue': 0,
            'project_budgets': {}
        }
        self.session_ids = {}
        
        # 确保目录存在
        self.data_dir = Path.home() / '.openclaw' / 'company_system'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化Agent配置
        self._init_agents()
    
    def _init_agents(self):
        """初始化所有Agent配置"""
        self.agents = {
            'ceo': {
                'name': 'CEO',
                'title': '首席执行官',
                'role': '战略决策者',
                'status': 'idle',
                'current_task': None,
                'skills': ['战略决策', '资源分配', '团队管理'],
                'model': 'kimi-coding/k2p5',
                'thinking': 'high'
            },
            'cmo': {
                'name': 'CMO',
                'title': '市场总监',
                'role': '市场发现者',
                'status': 'idle',
                'current_task': None,
                'skills': ['市场调研', '竞品分析', '用户洞察'],
                'model': 'kimi-coding/k2p5',
                'thinking': 'medium'
            },
            'cto': {
                'name': 'CTO',
                'title': '研发总监',
                'role': '技术负责人',
                'status': 'idle',
                'current_task': None,
                'skills': ['技术架构', '研发管理', '技术评估'],
                'model': 'kimi-coding/k2p5',
                'thinking': 'high'
            },
            'coo': {
                'name': 'COO',
                'title': '运营总监',
                'role': '运营管理者',
                'status': 'idle',
                'current_task': None,
                'skills': ['运营策略', '流程优化', '执行监督'],
                'model': 'kimi-coding/k2p5',
                'thinking': 'medium'
            },
            'pr': {
                'name': 'PR Director',
                'title': '宣传总监',
                'role': '品牌建设者',
                'status': 'idle',
                'current_task': None,
                'skills': ['品牌营销', '内容创作', '用户获取'],
                'model': 'kimi-coding/k2p5',
                'thinking': 'medium'
            },
            'cfo': {
                'name': 'CFO',
                'title': '财务总监',
                'role': '财务管理者',
                'status': 'idle',
                'current_task': None,
                'skills': ['财务规划', '成本控制', '收益分析'],
                'model': 'kimi-coding/k2p5',
                'thinking': 'medium'
            },
            'observer': {
                'name': 'Observer',
                'title': '运营观察员',
                'role': '协作监督者',
                'status': 'idle',
                'current_task': None,
                'skills': ['协作分析', '问题发现', '优化建议'],
                'model': 'kimi-coding/k2p5',
                'thinking': 'medium'
            }
        }
    
    def spawn_agent(self, agent_id: str, task: str, context: Dict = None) -> str:
        """
        启动一个Agent子进程
        
        Args:
            agent_id: Agent标识
            task: 任务描述
            context: 上下文信息
        
        Returns:
            session_id: 会话ID
        """
        agent = self.agents.get(agent_id)
        if not agent:
            raise ValueError(f"Unknown agent: {agent_id}")
        
        # 构建完整的任务提示
        full_task = self._build_agent_prompt(agent, task, context)
        
        # 使用sessions_spawn启动Agent
        # 注意：这里需要OpenClaw的sessions_spawn功能
        # 在实际环境中调用
        
        session_id = f"{agent_id}_{uuid.uuid4().hex[:8]}"
        self.session_ids[agent_id] = session_id
        
        # 更新Agent状态
        self.agents[agent_id]['status'] = 'busy'
        self.agents[agent_id]['current_task'] = task[:100]
        
        # 记录通信
        self._log_communication(
            from_agent='system',
            to_agent=agent_id,
            msg_type='task_assigned',
            content={'task': task, 'session_id': session_id}
        )
        
        return session_id
    
    def _build_agent_prompt(self, agent: Dict, task: str, context: Dict = None) -> str:
        """构建Agent任务提示"""
        prompt = f"""你是 {agent['name']} ({agent['title']})，{agent['role']}。

你的职责：
{chr(10).join(['- ' + skill for skill in agent['skills']])}

当前任务：
{task}

"""
        if context:
            prompt += f"""
上下文信息：
{json.dumps(context, ensure_ascii=False, indent=2)}
"""
        
        prompt += """
工作要求：
1. 以你的专业角色思考和行动
2. 输出结构化的JSON格式结果
3. 如需协作，明确说明需要哪些Agent配合
4. 评估任务的紧急程度和重要性
5. 识别潜在风险并提出应对方案

输出格式：
{
  "analysis": "任务分析",
  "plan": "执行计划",
  "output": "具体输出内容",
  "collaboration": ["需要协作的Agent列表"],
  "risks": ["风险点"],
  "next_steps": "下一步行动建议"
}
"""
        return prompt
    
    def _log_communication(self, from_agent: str, to_agent: str, 
                          msg_type: str, content: Dict):
        """记录Agent间通信"""
        comm = {
            'id': str(uuid.uuid4()),
            'from': from_agent,
            'to': to_agent,
            'type': msg_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.communications.append(comm)
        self._save_communications()
    
    def create_project(self, name: str, description: str, 
                      proposed_by: str = 'cmo') -> str:
        """创建新项目"""
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        
        project = {
            'id': project_id,
            'name': name,
            'description': description,
            'status': 'discovered',  # discovered/evaluating/executing/monitoring/completed
            'proposed_by': proposed_by,
            'created_at': datetime.now().isoformat(),
            'team': {},
            'progress': 0,
            'budget': 0,
            'expected_revenue': 0,
            'phases': {
                'discovery': {'status': 'completed', 'output': {}},
                'evaluation': {'status': 'pending', 'output': {}},
                'execution': {'status': 'pending', 'output': {}},
                'monitoring': {'status': 'pending', 'output': {}}
            }
        }
        
        self.projects[project_id] = project
        self._save_projects()
        
        # 通知CEO有新项目提案
        self._log_communication(
            from_agent=proposed_by,
            to_agent='ceo',
            msg_type='project_proposal',
            content={'project_id': project_id, 'name': name, 'description': description}
        )
        
        return project_id
    
    def evaluate_project(self, project_id: str):
        """评估项目 - 启动CMO、CTO、CFO、COO并行评估"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        project['status'] = 'evaluating'
        project['phases']['evaluation']['status'] = 'in_progress'
        
        # 启动并行评估
        context = {
            'project': project,
            'company_budget': self.financials['total_budget'] - self.financials['spent']
        }
        
        # CMO - 市场评估
        self.spawn_agent('cmo', 
            f"评估项目市场前景: {project['name']}\n{project['description']}",
            context)
        
        # CTO - 技术评估
        self.spawn_agent('cto',
            f"评估技术可行性: {project['name']}\n{project['description']}",
            context)
        
        # CFO - 财务评估
        self.spawn_agent('cfo',
            f"评估财务可行性: {project['name']}\n{project['description']}",
            context)
        
        # COO - 运营评估
        self.spawn_agent('coo',
            f"评估运营可行性: {project['name']}\n{project['description']}",
            context)
        
        self._save_projects()
    
    def execute_project(self, project_id: str):
        """执行项目 - 分配团队并启动"""
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        project['status'] = 'executing'
        project['phases']['execution']['status'] = 'in_progress'
        
        # 分配团队
        project['team'] = {
            'cto': {'role': '技术研发', 'tasks': ['架构设计', '产品开发']},
            'coo': {'role': '运营执行', 'tasks': ['流程搭建', '团队管理']},
            'pr': {'role': '宣传推广', 'tasks': ['品牌建设', '用户获取']},
            'cfo': {'role': '财务监控', 'tasks': ['成本控制', '收益跟踪']}
        }
        
        # 启动Observer监控
        self.spawn_agent('observer',
            f"开始监控项目执行: {project['name']}",
            {'project': project, 'agents': self.agents})
        
        self._save_projects()
    
    def get_ui_data(self) -> Dict:
        """获取UI展示数据"""
        return {
            'company': {
                'name': self.company_name,
                'total_agents': len(self.agents),
                'active_projects': len([p for p in self.projects.values() if p['status'] != 'completed']),
                'completed_projects': len([p for p in self.projects.values() if p['status'] == 'completed'])
            },
            'agents': {
                agent_id: {
                    'name': info['name'],
                    'title': info['title'],
                    'status': info['status'],
                    'current_task': info['current_task'],
                    'skills': info['skills']
                }
                for agent_id, info in self.agents.items()
            },
            'projects': {
                proj_id: {
                    'name': proj['name'],
                    'status': proj['status'],
                    'progress': proj['progress'],
                    'team': list(proj['team'].keys())
                }
                for proj_id, proj in self.projects.items()
            },
            'financials': self.financials,
            'recent_communications': self.communications[-10:]  # 最近10条通信
        }
    
    def _save_communications(self):
        """保存通信记录"""
        file_path = self.data_dir / 'communications.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.communications, f, ensure_ascii=False, indent=2)
    
    def _save_projects(self):
        """保存项目数据"""
        file_path = self.data_dir / 'projects.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.projects, f, ensure_ascii=False, indent=2)
    
    def _save_financials(self):
        """保存财务数据"""
        file_path = self.data_dir / 'financials.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.financials, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        """加载保存的数据"""
        # 加载通信记录
        comm_file = self.data_dir / 'communications.json'
        if comm_file.exists():
            with open(comm_file, 'r', encoding='utf-8') as f:
                self.communications = json.load(f)
        
        # 加载项目数据
        proj_file = self.data_dir / 'projects.json'
        if proj_file.exists():
            with open(proj_file, 'r', encoding='utf-8') as f:
                self.projects = json.load(f)
        
        # 加载财务数据
        fin_file = self.data_dir / 'financials.json'
        if fin_file.exists():
            with open(fin_file, 'r', encoding='utf-8') as f:
                self.financials = json.load(f)

# 全局实例
company = CompanySystem()

if __name__ == '__main__':
    # 测试运行
    company.load_data()
    print("="*60)
    print(f"🚀 {company.company_name} - 多Agent公司系统")
    print("="*60)
    
    # 显示UI数据
    ui_data = company.get_ui_data()
    print("\n公司状态:")
    print(json.dumps(ui_data['company'], indent=2, ensure_ascii=False))
    
    print("\nAgent团队:")
    for agent_id, info in ui_data['agents'].items():
        print(f"  {info['name']} ({info['title']}): {info['status']}")
