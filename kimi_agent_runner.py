#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kimi AI Agent Integration - Kimi AI Agent集成模块
使用真实的 kimi-coding/k2p5 模型实现Agent自主决策
"""

import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import os

@dataclass
class KimiAgentConfig:
    """Kimi Agent配置"""
    agent_id: str
    name: str
    role: str
    system_prompt: str
    api_key: str
    model: str = "kimi-coding/k2p5"
    thinking: str = "medium"  # low, medium, high
    temperature: float = 0.7
    max_tokens: int = 4000

class KimiAgentRunner:
    """Kimi AI Agent运行器 - 调用真实的Kimi K2.5模型"""
    
    API_BASE_URL = "https://api.moonshot.cn/v1"
    
    def __init__(self, config: KimiAgentConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.conversation_history: List[Dict] = []
        self.decision_log: List[Dict] = []
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def think(self, task: str, context: Dict = None) -> Dict[str, Any]:
        """
        Agent思考并做出决策
        
        Args:
            task: 任务描述
            context: 上下文信息（公司状态、市场数据等）
            
        Returns:
            决策结果字典
        """
        # 构建提示词
        prompt = self._build_prompt(task, context)
        
        # 调用Kimi API
        response = await self._call_kimi_api(prompt)
        
        # 解析决策
        decision = self._parse_decision(response)
        
        # 记录决策
        self.decision_log.append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "decision": decision,
            "raw_response": response
        })
        
        return decision
    
    def _build_prompt(self, task: str, context: Dict = None) -> str:
        """构建提示词"""
        base_prompt = f"""{self.config.system_prompt}

## 当前任务
{task}

## 角色信息
- 姓名: {self.config.name}
- 职位: {self.config.role}
- Agent ID: {self.config.agent_id}

## 决策格式
请使用以下JSON格式返回你的决策：
```json
{{
    "decision": "你的决策（批准/拒绝/需要更多信息）",
    "confidence": 0.85,
    "reasoning": "详细的推理过程",
    "action_items": ["具体行动项1", "行动项2"],
    "risks": ["风险1", "风险2"],
    "recommendations": ["建议1", "建议2"],
    "budget_request": 0,
    "timeline_days": 30,
    "team_requirements": ["需要的团队成员"]
}}
```

请确保你的决策符合你的角色职责和专业领域。"""

        if context:
            base_prompt += f"\n\n## 上下文信息\n{json.dumps(context, ensure_ascii=False, indent=2)}"
        
        return base_prompt
    
    async def _call_kimi_api(self, prompt: str) -> str:
        """调用Kimi API"""
        if not self.session:
            raise RuntimeError("Agent not initialized. Use 'async with' context manager.")
        
        url = f"{self.API_BASE_URL}/chat/completions"
        
        payload = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "stream": False
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    raise Exception(f"Kimi API Error: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ API调用失败: {e}")
            # 返回模拟响应作为fallback
            return self._generate_fallback_response(prompt)
    
    def _parse_decision(self, response: str) -> Dict:
        """解析AI响应为结构化决策"""
        try:
            # 尝试提取JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response
            
            decision = json.loads(json_str)
            return decision
        except json.JSONDecodeError:
            # 如果解析失败，返回文本决策
            return {
                "decision": "需要讨论",
                "confidence": 0.5,
                "reasoning": response[:500],
                "action_items": [],
                "risks": [],
                "recommendations": ["请重新格式化决策"],
                "budget_request": 0,
                "timeline_days": 0,
                "team_requirements": []
            }
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """生成fallback响应（当API调用失败时）"""
        return """```json
{
    "decision": "需要更多信息",
    "confidence": 0.6,
    "reasoning": "API暂时不可用，需要等待恢复后重新评估",
    "action_items": ["等待系统恢复", "收集更多数据"],
    "risks": ["API连接不稳定"],
    "recommendations": ["稍后重试"],
    "budget_request": 0,
    "timeline_days": 1,
    "team_requirements": ["技术团队"]
}
```"""


class KimiAgentFactory:
    """Kimi Agent工厂 - 创建预配置的Agent"""
    
    @staticmethod
    def create_ceo_agent(api_key: str) -> KimiAgentConfig:
        """创建CEO Agent"""
        return KimiAgentConfig(
            agent_id="ceo",
            name="Alex Chen",
            role="CEO",
            system_prompt="""你是Nexus AI Technologies的首席执行官(CEO)。

## 核心职责
1. 制定公司战略方向
2. 审批重大项目投资
3. 协调高管团队
4. 对外代表公司形象

## 决策原则
- 以公司长远利益为首要考虑
- 平衡风险与回报
- 重视团队协作和人才发展
- 保持对技术趋势的敏感度

## 性格特点
- 果断但不鲁莽
- 善于倾听不同意见
- 有远见卓识
- 重视数据驱动决策

请用专业、战略性的思维来分析和决策。""",
            api_key=api_key,
            thinking="high"
        )
    
    @staticmethod
    def create_cmo_agent(api_key: str) -> KimiAgentConfig:
        """创建CMO Agent"""
        return KimiAgentConfig(
            agent_id="cmo",
            name="Sarah Miller",
            role="CMO",
            system_prompt="""你是Nexus AI Technologies的首席营销官(CMO)。

## 核心职责
1. 市场趋势分析和机会发现
2. 品牌建设和推广策略
3. 用户洞察和需求分析
4. 竞品分析和定位

## 专业能力
- 深度理解AI和SaaS市场
- 擅长数据分析和用户研究
- 熟悉数字营销策略
- 具备创意和执行力

## 分析框架
1. 市场规模(TAM/SAM/SOM)
2. 增长率和趋势
3. 竞争格局
4. 用户需求痛点
5. 进入壁垒

请提供详细的市场分析和营销建议。""",
            api_key=api_key,
            thinking="medium"
        )
    
    @staticmethod
    def create_cto_agent(api_key: str) -> KimiAgentConfig:
        """创建CTO Agent"""
        return KimiAgentConfig(
            agent_id="cto",
            name="David Kim",
            role="CTO",
            system_prompt="""你是Nexus AI Technologies的首席技术官(CTO)。

## 核心职责
1. 技术架构规划和设计
2. 技术选型和技术栈决策
3. 研发团队管理
4. 技术风险评估

## 技术专长
- AI/ML系统架构
- 分布式系统设计
- 云原生技术
- 安全性和可扩展性

## 评估维度
1. 技术可行性
2. 架构复杂度
3. 开发周期
4. 维护成本
5. 技术风险
6. 团队技能匹配

请从技术角度提供专业评估和建议。""",
            api_key=api_key,
            thinking="high"
        )
    
    @staticmethod
    def create_cfo_agent(api_key: str) -> KimiAgentConfig:
        """创建CFO Agent"""
        return KimiAgentConfig(
            agent_id="cfo",
            name="Lisa Wang",
            role="CFO",
            system_prompt="""你是Nexus AI Technologies的首席财务官(CFO)。

## 核心职责
1. 财务规划和预算管理
2. 投资回报率分析
3. 风险评估和风控
4. 融资和资本运作

## 专业能力
- 财务建模和分析
- 投资评估(NPV/IRR/ROI)
- 风险管理
- 合规和审计

## 分析框架
1. 成本效益分析
2. 现金流影响
3. 投资回报期
4. 风险调整收益
5. 财务可持续性

请提供严谨的财务分析和投资建议。""",
            api_key=api_key,
            thinking="medium"
        )
    
    @staticmethod
    def create_cpo_agent(api_key: str) -> KimiAgentConfig:
        """创建CPO Agent"""
        return KimiAgentConfig(
            agent_id="cpo",
            name="Michael Zhang",
            role="CPO",
            system_prompt="""你是Nexus AI Technologies的首席产品官(CPO)。

## 核心职责
1. 产品战略和路线图
2. 用户体验设计
3. 产品需求分析
4. 产品创新和优化

## 专业能力
- 产品设计和UX
- 用户研究和测试
- 敏捷开发流程
- 数据驱动产品决策

## 评估维度
1. 用户需求匹配度
2. 市场差异化
3. 产品可行性
4. 用户体验
5. 创新程度

请从产品角度提供专业评估和建议。""",
            api_key=api_key,
            thinking="medium"
        )
    
    @staticmethod
    def create_coo_agent(api_key: str) -> KimiAgentConfig:
        """创建COO Agent"""
        return KimiAgentConfig(
            agent_id="coo",
            name="Emma Wilson",
            role="COO",
            system_prompt="""你是Nexus AI Technologies的首席运营官(COO)。

## 核心职责
1. 运营流程设计和优化
2. 团队管理和协调
3. 项目执行监督
4. 资源分配和调度

## 专业能力
- 运营管理和优化
- 项目管理和执行
- 团队协作和沟通
- 流程自动化

## 评估维度
1. 运营可行性
2. 资源需求
3. 执行风险
4. 效率提升
5. 团队协作

请从运营角度提供专业评估和执行建议。""",
            api_key=api_key,
            thinking="medium"
        )
    
    @staticmethod
    def create_chro_agent(api_key: str) -> KimiAgentConfig:
        """创建CHRO Agent"""
        return KimiAgentConfig(
            agent_id="chro",
            name="James Brown",
            role="CHRO",
            system_prompt="""你是Nexus AI Technologies的首席人力资源官(CHRO)。

## 核心职责
1. 人才招聘和培养
2. 企业文化建设
3. 员工发展和福利
4. 组织效能提升

## 专业能力
- 人才管理和发展
- 组织设计和优化
- 员工关系和沟通
- 绩效管理和激励

## 关注重点
1. 团队健康度
2. 员工满意度
3. 人才保留
4. 文化契合度
5. 技能发展

请从人力资源角度提供专业建议和团队管理方案。""",
            api_key=api_key,
            thinking="low"
        )


# ============== 集成示例 ==============

async def demo_kimi_agents():
    """演示：使用真实Kimi模型的多Agent协作"""
    
    # 从环境变量或配置文件读取API key
    api_key = os.getenv("KIMI_API_KEY", "your-api-key-here")
    
    print("🚀 启动真实Kimi AI Agent系统")
    print("=" * 60)
    
    # 创建Agent配置
    ceo_config = KimiAgentFactory.create_ceo_agent(api_key)
    cmo_config = KimiAgentFactory.create_cmo_agent(api_key)
    cto_config = KimiAgentFactory.create_cto_agent(api_key)
    
    # 模拟市场机会
    opportunity = {
        "name": "AI内容创作平台",
        "description": "基于大语言模型的自动化内容创作工具",
        "market_size": "50亿美元",
        "target_users": "内容创作者、营销团队",
        "competitors": ["Jasper", "Copy.ai", "ChatGPT"]
    }
    
    # CMO分析市场机会
    print("\n📊 CMO分析市场机会...")
    async with KimiAgentRunner(cmo_config) as cmo:
        cmo_decision = await cmo.think(
            task="分析以下市场机会，评估其潜力和可行性",
            context={"opportunity": opportunity}
        )
        print(f"CMO决策: {cmo_decision.get('decision')}")
        print(f"信心度: {cmo_decision.get('confidence')}")
        print(f"建议: {cmo_decision.get('recommendations', [])}")
    
    # CTO技术评估
    print("\n💻 CTO技术评估...")
    async with KimiAgentRunner(cto_config) as cto:
        cto_decision = await cto.think(
            task="评估构建AI内容创作平台的技术可行性和挑战",
            context={"opportunity": opportunity, "cmo_analysis": cmo_decision}
        )
        print(f"CTO决策: {cto_decision.get('decision')}")
        print(f"技术风险: {cto_decision.get('risks', [])}")
    
    # CEO最终决策
    print("\n👔 CEO最终决策...")
    async with KimiAgentRunner(ceo_config) as ceo:
        ceo_decision = await ceo.think(
            task="基于CMO和CTO的评估，做出是否投资该项目的最终决策",
            context={
                "opportunity": opportunity,
                "cmo_analysis": cmo_decision,
                "cto_analysis": cto_decision
            }
        )
        print(f"CEO决策: {ceo_decision.get('decision')}")
        print(f"投资预算: ¥{ceo_decision.get('budget_request', 0):,}")
        print(f"时间线: {ceo_decision.get('timeline_days')}天")
        print(f"执行团队: {ceo_decision.get('team_requirements', [])}")


if __name__ == "__main__":
    # 设置API key（实际使用时从环境变量读取）
    # os.environ["KIMI_API_KEY"] = "your-api-key"
    
    print("Kimi AI Agent Integration Module")
    print("Usage: Import this module in your company system")
    print("\nTo run demo:")
    print("  export KIMI_API_KEY='your-key'")
    print("  python3 kimi_agent_runner.py")
