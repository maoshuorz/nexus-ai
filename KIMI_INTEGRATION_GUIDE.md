# Kimi AI Agent 集成指南
# Integration Guide for Real AI Agents

## 🎯 目标

将模拟的多Agent公司系统升级为使用真实 **Kimi K2.5** 模型的AI Agent系统，实现真正的自主决策和智能协作。

---

## 📋 前置条件

- ✅ Kimi API Key: `sk-kimi-I6opLore8BAYYOXt7B8zufYTBIG9VCSY7aR4cddqUxszmpVqA4tQEwZpSFlczkYq`
- ✅ Python 3.8+
- ✅ 已安装依赖: `aiohttp`

```bash
pip install aiohttp
```

---

## 🏗️ 集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Company System (原有系统)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Agent Manager (agent_manager.py)                   │   │
│  │  - 管理Agent生命周期                                 │   │
│  │  - 协调Agent间通信                                   │   │
│  │  - 分配任务和收集决策                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Kimi Agent Runner (kimi_agent_runner.py)           │   │
│  │  - 调用Kimi API                                      │   │
│  │  - 解析AI决策                                        │   │
│  │  - 管理对话历史                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Kimi API (kimi-coding/k2p5)                        │   │
│  │  - 真实AI模型推理                                    │   │
│  │  - 生成决策和建议                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 步骤1: 配置环境

```bash
# 设置API Key环境变量
export KIMI_API_KEY="sk-kimi-I6opLore8BAYYOXt7B8zufYTBIG9VCSY7aR4cddqUxszmpVqA4tQEwZpSFlczkYq"

# 验证配置
echo $KIMI_API_KEY
```

### 步骤2: 测试单个Agent

```bash
cd ~/.openclaw/workspace/company_system
python3 -c "
import asyncio
import os
from kimi_agent_runner import KimiAgentRunner, KimiAgentFactory

async def test():
    api_key = os.getenv('KIMI_API_KEY')
    
    # 创建CEO Agent
    config = KimiAgentFactory.create_ceo_agent(api_key)
    
    async with KimiAgentRunner(config) as agent:
        decision = await agent.think(
            task='评估是否投资一个AI写作工具项目，预算50万',
            context={'market_size': '10亿美元', 'competitors': ['Jasper', 'Copy.ai']}
        )
        print('决策:', decision['decision'])
        print('推理:', decision['reasoning'][:200])

asyncio.run(test())
"
```

### 步骤3: 运行完整演示

```bash
python3 kimi_agent_runner.py
```

---

## 🔧 核心组件详解

### 1. KimiAgentConfig - Agent配置

```python
from kimi_agent_runner import KimiAgentConfig

config = KimiAgentConfig(
    agent_id="ceo",           # Agent唯一标识
    name="Alex Chen",         # Agent姓名
    role="CEO",               # 职位
    system_prompt="...",      # 系统提示词（定义角色和行为）
    api_key="sk-...",         # API Key
    model="kimi-coding/k2p5", # 模型选择
    thinking="high",          # 思考深度 (low/medium/high)
    temperature=0.7,          # 创造性 (0-1)
    max_tokens=4000           # 最大输出长度
)
```

### 2. KimiAgentRunner - Agent运行器

```python
from kimi_agent_runner import KimiAgentRunner

# 方式1: 使用上下文管理器（推荐）
async with KimiAgentRunner(config) as agent:
    decision = await agent.think(task="...", context={...})

# 方式2: 手动管理生命周期
agent = KimiAgentRunner(config)
# ... 初始化session ...
decision = await agent.think(task="...")
```

### 3. KimiAgentFactory - Agent工厂

```python
from kimi_agent_runner import KimiAgentFactory

# 创建预配置的Agent
ceo = KimiAgentFactory.create_ceo_agent(api_key)
cmo = KimiAgentFactory.create_cmo_agent(api_key)
cto = KimiAgentFactory.create_cto_agent(api_key)
cfo = KimiAgentFactory.create_cfo_agent(api_key)
cpo = KimiAgentFactory.create_cpo_agent(api_key)
coo = KimiAgentFactory.create_coo_agent(api_key)
chro = KimiAgentFactory.create_chro_agent(api_key)
```

---

## 💡 使用示例

### 示例1: CMO市场分析

```python
import asyncio
import os
from kimi_agent_runner import KimiAgentRunner, KimiAgentFactory

async def cmo_analysis():
    api_key = os.getenv("KIMI_API_KEY")
    cmo_config = KimiAgentFactory.create_cmo_agent(api_key)
    
    opportunity = {
        "name": "AI客服平台",
        "description": "智能客服自动化解决方案",
        "market_size": "200亿美元",
        "growth_rate": "35%",
        "target_customers": "电商、SaaS企业"
    }
    
    async with KimiAgentRunner(cmo_config) as cmo:
        result = await cmo.think(
            task="分析这个市场机会，评估进入策略",
            context={"opportunity": opportunity}
        )
        
        print(f"📊 CMO分析结果:")
        print(f"   决策: {result['decision']}")
        print(f"   信心度: {result['confidence']}")
        print(f"   建议: {result['recommendations']}")
        print(f"   风险: {result['risks']}")

asyncio.run(cmo_analysis())
```

### 示例2: 多Agent协作决策

```python
import asyncio
import os
from kimi_agent_runner import KimiAgentRunner, KimiAgentFactory

async def collaborative_decision():
    api_key = os.getenv("KIMI_API_KEY")
    
    # 项目提案
    project = {
        "name": "AI代码助手",
        "budget": 1000000,
        "timeline": "6个月",
        "team_size": 8
    }
    
    # 并行收集各Agent评估
    async def evaluate_agent(agent_config, task):
        async with KimiAgentRunner(agent_config) as agent:
            return await agent.think(task, context={"project": project})
    
    # 创建Agent配置
    cto_config = KimiAgentFactory.create_cto_agent(api_key)
    cfo_config = KimiAgentFactory.create_cfo_agent(api_key)
    cpo_config = KimiAgentFactory.create_cpo_agent(api_key)
    
    # 并行执行
    cto_result, cfo_result, cpo_result = await asyncio.gather(
        evaluate_agent(cto_config, "评估技术可行性和架构方案"),
        evaluate_agent(cfo_config, "评估财务可行性和ROI"),
        evaluate_agent(cpo_config, "评估产品可行性和市场定位")
    )
    
    # CEO综合决策
    ceo_config = KimiAgentFactory.create_ceo_agent(api_key)
    async with KimiAgentRunner(ceo_config) as ceo:
        final_decision = await ceo.think(
            task="基于各部门评估，做出最终投资决策",
            context={
                "project": project,
                "cto_assessment": cto_result,
                "cfo_assessment": cfo_result,
                "cpo_assessment": cpo_result
            }
        )
    
    print(f"\n👔 CEO最终决策: {final_decision['decision']}")
    print(f"   预算批准: ¥{final_decision.get('budget_request', 0):,}")
    print(f"   执行团队: {final_decision.get('team_requirements', [])}")

asyncio.run(collaborative_decision())
```

### 示例3: 与现有系统集成

```python
# company_with_kimi.py
import asyncio
import os
from advanced_company_v3 import AdvancedCompanySystem
from kimi_agent_runner import KimiAgentRunner, KimiAgentFactory

class RealAICompanySystem(AdvancedCompanySystem):
    """使用真实AI的增强版公司系统"""
    
    def __init__(self, company_name: str = "Nexus AI"):
        super().__init__(company_name)
        self.api_key = os.getenv("KIMI_API_KEY")
        self.agent_runners = {}
        self._init_kimi_agents()
    
    def _init_kimi_agents(self):
        """初始化Kimi AI Agents"""
        factory = KimiAgentFactory
        
        self.agent_configs = {
            "ceo": factory.create_ceo_agent(self.api_key),
            "cmo": factory.create_cmo_agent(self.api_key),
            "cto": factory.create_cto_agent(self.api_key),
            "cfo": factory.create_cfo_agent(self.api_key),
            "cpo": factory.create_cpo_agent(self.api_key),
            "coo": factory.create_coo_agent(self.api_key),
            "chro": factory.create_chro_agent(self.api_key),
        }
    
    async def _cmo_market_scan(self):
        """使用真实AI进行市场扫描"""
        print("\n📊 CMO (AI) 正在分析市场...")
        
        config = self.agent_configs["cmo"]
        async with KimiAgentRunner(config) as cmo:
            result = await cmo.think(
                task="分析当前AI市场趋势，识别3个最有潜力的创业机会",
                context={
                    "current_projects": [p.name for p in self.projects.values()],
                    "cash_flow": self.financials["cash_flow"]
                }
            )
            
            print(f"   AI分析完成: {result['decision']}")
            print(f"   发现机会: {result.get('recommendations', [])}")
            
            # 根据AI建议创建机会
            opportunities = []
            for rec in result.get('recommendations', [])[:3]:
                opp = {
                    "id": f"opp_{len(opportunities)}",
                    "name": rec,
                    "description": f"基于AI分析的{rec}机会",
                    "confidence": result.get('confidence', 0.7)
                }
                opportunities.append(opp)
            
            return opportunities
    
    async def _ceo_decision(self, project, eval_results):
        """使用真实AI做CEO决策"""
        print("\n👔 CEO (AI) 正在做出决策...")
        
        config = self.agent_configs["ceo"]
        async with KimiAgentRunner(config) as ceo:
            result = await ceo.think(
                task=f"评估项目'{project.name}'是否值得投资",
                context={
                    "project": {
                        "name": project.name,
                        "description": project.description,
                        "budget_request": project.budget
                    },
                    "evaluations": eval_results,
                    "company_cash": self.financials["cash_flow"]
                }
            )
            
            print(f"   AI决策: {result['decision']}")
            print(f"   推理: {result.get('reasoning', '')[:100]}...")
            
            return {
                "approved": result['decision'] in ['批准', '通过', 'approved'],
                "budget": result.get('budget_request', 0),
                "reason": result.get('reasoning', ''),
                "confidence": result.get('confidence', 0.5)
            }

# 运行
async def main():
    company = RealAICompanySystem("Nexus AI with Real Agents")
    await company.run_daily_simulation()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🎨 系统提示词设计

每个Agent的系统提示词决定了其行为和决策风格：

### CEO提示词关键元素
```
1. 角色定义 - 明确职责和权限
2. 决策原则 - 如何权衡利弊
3. 性格特点 - 决策风格
4. 输出格式 - JSON结构
5. 约束条件 - 预算限制、时间限制
```

### 自定义提示词

```python
custom_ceo_prompt = """你是{company_name}的CEO。

## 背景
- 公司阶段: {stage}
- 现金: ${cash}
- 团队: {team_size}人

## 当前挑战
{challenges}

## 决策原则
1. 优先保证现金流健康
2. 技术债务不能超过X
3. 每个决策必须有ROI分析

请基于以上信息做出决策。
"""

config = KimiAgentConfig(
    agent_id="ceo",
    name="CEO",
    role="CEO",
    system_prompt=custom_ceo_prompt.format(
        company_name="My Startup",
        stage="Pre-Series A",
        cash="2M",
        team_size=8,
        challenges="需要找到PMF"
    ),
    api_key=api_key
)
```

---

## 📊 成本估算

| 操作 | Token消耗 | 预估成本 |
|------|-----------|----------|
| 单次决策 | 2K-4K tokens | ¥0.02-0.04 |
| 完整项目评估 (6 Agents) | 12K-24K tokens | ¥0.12-0.24 |
| 每日模拟 (7天) | 84K-168K tokens | ¥0.84-1.68 |

*基于Kimi API定价估算*

---

## ⚠️ 注意事项

### 1. API限流
- 建议添加请求间隔（0.5-1秒）
- 使用asyncio.gather()进行并行请求时注意并发数

### 2. 错误处理
```python
async with KimiAgentRunner(config) as agent:
    try:
        result = await agent.think(task, context)
    except Exception as e:
        print(f"API调用失败: {e}")
        # 使用fallback决策
        result = {"decision": "需要讨论", "confidence": 0.5}
```

### 3. 对话历史管理
- 每个Agent实例维护独立的对话历史
- 长时间运行建议定期清理历史
- 重要决策可以保存到文件

### 4. 安全性
- API Key不要硬编码，使用环境变量
- 不要在前端暴露API Key
- 定期轮换API Key

---

## 🔮 高级功能

### 1. 记忆持久化

```python
import json

class PersistentAgent(KimiAgentRunner):
    async def save_memory(self, filepath: str):
        """保存Agent记忆"""
        memory = {
            "conversation_history": self.conversation_history,
            "decision_log": self.decision_log,
            "config": self.config.__dict__
        }
        with open(filepath, 'w') as f:
            json.dump(memory, f, indent=2)
    
    async def load_memory(self, filepath: str):
        """加载Agent记忆"""
        with open(filepath, 'r') as f:
            memory = json.load(f)
        self.conversation_history = memory["conversation_history"]
        self.decision_log = memory["decision_log"]
```

### 2. Agent间通信

```python
async def agent_communication(sender_id: str, receiver_id: str, message: str):
    """模拟Agent间消息传递"""
    sender_config = agent_configs[sender_id]
    receiver_config = agent_configs[receiver_id]
    
    # Sender发送消息
    async with KimiAgentRunner(sender_config) as sender:
        response = await sender.think(
            task=f"向{receiver_config.name}发送消息: {message}",
            context={"communication": True}
        )
    
    # Receiver接收并回复
    async with KimiAgentRunner(receiver_config) as receiver:
        reply = await receiver.think(
            task=f"回复{sender_config.name}的消息",
            context={"received_message": response}
        )
    
    return reply
```

### 3. 决策审计

```python
def generate_decision_report(agent: KimiAgentRunner) -> str:
    """生成决策审计报告"""
    report = f"# {agent.config.name} 决策报告\n\n"
    
    for i, log in enumerate(agent.decision_log, 1):
        report += f"## 决策 #{i}\n"
        report += f"- 时间: {log['timestamp']}\n"
        report += f"- 任务: {log['task'][:100]}...\n"
        report += f"- 决策: {log['decision']['decision']}\n"
        report += f"- 信心度: {log['decision']['confidence']}\n\n"
    
    return report
```

---

## 📚 扩展阅读

- Kimi API文档: https://platform.moonshot.cn/docs
- 多Agent协作论文: https://arxiv.org/abs/2306.08530
- Prompt Engineering Guide: https://www.promptingguide.ai/

---

**创建时间**: 2026-02-17  
**版本**: v1.0  
**作者**: OpenClaw Agent
