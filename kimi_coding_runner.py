#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kimi Coding API (Anthropic Compatible) Runner
支持 Anthropic API 格式的 Kimi Coding 接入
"""

import json
import asyncio
import aiohttp
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class KimiCodingConfig:
    """Kimi Coding 配置 - Anthropic兼容格式"""
    agent_id: str
    name: str
    role: str
    system_prompt: str
    api_key: str
    base_url: str = "https://api.kimi.com/coding"
    model: str = "kimi-coding/k2p5"
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60


class KimiCodingRunner:
    """
    Kimi Coding Agent运行器
    使用 Anthropic API 兼容格式
    """
    
    def __init__(self, config: KimiCodingConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.decision_log: List[Dict] = []
        
    async def __aenter__(self):
        """异步上下文管理器入口"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers={
                "x-api-key": self.config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def think(self, task: str, context: Dict = None) -> Dict[str, Any]:
        """Agent思考并做出决策"""
        prompt = self._build_prompt(task, context)
        
        try:
            response = await self._call_anthropic_api(prompt)
            decision = self._parse_response(response)
            
            # 记录决策
            self.decision_log.append({
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "decision": decision,
                "mode": "real_ai",
                "model": self.config.model,
                "api_type": "anthropic_compatible"
            })
            
            return decision
            
        except Exception as e:
            print(f"⚠️ API调用失败: {e}")
            return self._generate_fallback_decision(task, str(e))
    
    def _build_prompt(self, task: str, context: Dict = None) -> str:
        """构建提示词"""
        prompt = f"""{self.config.system_prompt}

## 当前任务
{task}

## 角色信息
- 姓名: {self.config.name}
- 职位: {self.config.role}

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
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            prompt += f"\n\n## 上下文信息\n{context_str}"
        
        return prompt
    
    async def _call_anthropic_api(self, prompt: str) -> str:
        """调用Anthropic兼容API"""
        if not self.session:
            raise RuntimeError("Agent not initialized")
        
        url = f"{self.config.base_url}/v1/messages"
        
        # Anthropic格式
        payload = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "system": self.config.system_prompt,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                # Anthropic返回格式
                return data["content"][0]["text"]
            else:
                error_text = await response.text()
                raise Exception(f"API Error {response.status}: {error_text}")
    
    def _parse_response(self, response: str) -> Dict:
        """解析API响应"""
        try:
            # 尝试提取JSON
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].strip()
            else:
                json_str = response
            
            decision = json.loads(json_str)
            
            # 确保必要字段
            required = ["decision", "confidence", "reasoning"]
            for field in required:
                if field not in decision:
                    decision[field] = "未知" if field == "decision" else 0.5
            
            return decision
            
        except json.JSONDecodeError:
            return {
                "decision": "需要讨论",
                "confidence": 0.5,
                "reasoning": response[:500] if response else "无法解析",
                "action_items": [],
                "risks": [],
                "recommendations": ["重新格式化"],
                "budget_request": 0,
                "timeline_days": 0,
                "team_requirements": [],
                "raw_response": response
            }
    
    def _generate_fallback_decision(self, task: str, error: str) -> Dict:
        """生成fallback决策"""
        return {
            "decision": "需要更多信息",
            "confidence": 0.6,
            "reasoning": f"API调用失败: {error}",
            "action_items": ["检查API配置", "验证API Key"],
            "risks": ["API连接不稳定"],
            "recommendations": ["使用模拟模式"],
            "budget_request": 0,
            "timeline_days": 1,
            "team_requirements": [],
            "mode": "fallback"
        }


class KimiCodingFactory:
    """Kimi Coding Agent工厂"""
    
    @staticmethod
    def _get_config() -> Dict:
        """从环境变量获取配置"""
        return {
            "api_key": os.getenv("ANTHROPIC_API_KEY") or os.getenv("KIMI_API_KEY"),
            "base_url": os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding"),
            "model": os.getenv("KIMI_MODEL", "kimi-coding/k2p5")
        }
    
    @staticmethod
    def create_ceo_agent(api_key: str = None) -> KimiCodingConfig:
        """创建CEO Agent"""
        base = KimiCodingFactory._get_config()
        
        return KimiCodingConfig(
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

请用专业、战略性的思维来分析和决策。""",
            api_key=api_key or base["api_key"],
            base_url=base["base_url"],
            model=base["model"]
        )
    
    @staticmethod
    def create_cmo_agent(api_key: str = None) -> KimiCodingConfig:
        """创建CMO Agent"""
        base = KimiCodingFactory._get_config()
        
        return KimiCodingConfig(
            agent_id="cmo",
            name="Sarah Miller",
            role="CMO",
            system_prompt="""你是Nexus AI Technologies的首席营销官(CMO)。

## 核心职责
1. 市场趋势分析和机会发现
2. 品牌建设和推广策略
3. 用户洞察和需求分析

请提供详细的市场分析和营销建议。""",
            api_key=api_key or base["api_key"],
            base_url=base["base_url"],
            model=base["model"]
        )
    
    @staticmethod
    def create_cto_agent(api_key: str = None) -> KimiCodingConfig:
        """创建CTO Agent"""
        base = KimiCodingFactory._get_config()
        
        return KimiCodingConfig(
            agent_id="cto",
            name="David Kim",
            role="CTO",
            system_prompt="""你是Nexus AI Technologies的首席技术官(CTO)。

## 核心职责
1. 技术架构规划和设计
2. 技术选型和技术栈决策
3. 研发团队管理
4. 技术风险评估

请从技术角度提供专业评估和建议。""",
            api_key=api_key or base["api_key"],
            base_url=base["base_url"],
            model=base["model"]
        )


# ============== 测试代码 ==============

async def test_kimi_coding():
    """测试Kimi Coding连接"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("KIMI_API_KEY")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.kimi.com/coding")
    
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     Kimi Coding API 测试 (Anthropic兼容模式)                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    print(f"\n📝 配置信息:")
    print(f"   Base URL: {base_url}")
    print(f"   API Key: {api_key[:20]}..." if api_key else "   API Key: 未设置")
    print(f"   Model: kimi-coding/k2p5")
    
    if not api_key:
        print("\n❌ 错误: 未设置API Key")
        print("\n请设置环境变量:")
        print("   export ANTHROPIC_API_KEY='your-api-key'")
        print("   export ANTHROPIC_BASE_URL='https://api.kimi.com/coding'")
        return
    
    print("\n🔍 测试API连接...")
    
    try:
        # 创建CEO Agent
        config = KimiCodingFactory.create_ceo_agent(api_key)
        config.base_url = base_url
        
        async with KimiCodingRunner(config) as agent:
            print("   ✅ Agent初始化成功")
            
            # 测试决策
            print("\n🧠 测试CEO决策...")
            result = await agent.think(
                task="评估是否投资一个AI写作工具项目，预算50万元",
                context={"market_size": "10亿美元", "competitors": ["Jasper", "Copy.ai"]}
            )
            
            print(f"\n📊 决策结果:")
            print(f"   决策: {result['decision']}")
            print(f"   信心度: {result.get('confidence', 0)}")
            print(f"   推理: {result.get('reasoning', '')[:150]}...")
            
            print("\n✅ 测试成功!")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_kimi_coding())
