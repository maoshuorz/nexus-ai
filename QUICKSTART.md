# 🚀 快速开始 - 真实AI多Agent公司系统

## 系统概述

已创建完整的**混合AI多Agent公司系统**，支持：
- ✅ **模拟AI模式** - 无需API Key，立即可用
- ✅ **真实AI模式** - 接入Kimi K2.5模型（需要有效API Key）
- ✅ **无缝切换** - 两种模式随时切换

---

## 📁 文件结构

```
company_system/
├── advanced_company_v3.py      # 基础模拟系统（8-Agent）
├── voxyz_company_v2.py         # Voxyz风格系统（7-Agent）
├── hybrid_ai_company.py        # 混合AI系统 ⭐推荐
├── kimi_agent_runner.py        # Kimi AI Agent模块
├── real_ai_company.py          # 纯真实AI系统
├── test_kimi_connection.py     # API连接测试
├── KIMI_INTEGRATION_GUIDE.md   # 完整集成指南
└── QUICKSTART.md              # 本文件
```

---

## 🎮 快速开始

### 方式1: 立即体验（模拟AI模式）

```bash
cd ~/.openclaw/workspace/company_system
python3 hybrid_ai_company.py
```

**预期输出：**
- 7个AI Agent自动协作
- 3天公司运营模拟
- 市场分析 → 项目评估 → CEO决策 → 项目执行
- 完整的财务报表和决策记录

### 方式2: 可视化界面

```bash
open advanced_dashboard.html
```

**功能：**
- 实时Agent状态监控
- 财务仪表盘（Chart.js图表）
- 项目进度追踪
- 活动日志流

---

## 🔌 接入真实AI（Kimi K2.5）

### 步骤1: 获取有效API Key

你的API Key: `sk-kimi-I6opLore8BAYYOXt7B8zufYTBIG9VCSY7aR4cddqUxszmpVqA4tQEwZpSFlczkYq`

⚠️ **注意**: 当前API Key可能已过期或无效。请确认：
1. 从Kimi/Moonshot官网获取最新API Key
2. 确保账户有足够余额

### 步骤2: 设置环境变量

```bash
# 临时设置（当前终端）
export KIMI_API_KEY="your-valid-api-key"

# 永久设置（添加到 ~/.zshrc）
echo 'export KIMI_API_KEY="your-valid-api-key"' >> ~/.zshrc
source ~/.zshrc
```

### 步骤3: 测试连接

```bash
python3 test_kimi_connection.py
```

**成功输出：**
```
✅ API连接成功!
🤖 AI响应: 作为Nexus AI Technologies的CEO，我负责制定...
📊 Token用量: 输入 45 tokens / 输出 28 tokens
```

### 步骤4: 运行真实AI系统

```bash
# 混合模式（推荐）
python3 hybrid_ai_company.py

# 纯真实AI模式
python3 real_ai_company.py
```

---

## 🎯 系统特性

### 8个AI Agent角色

| Agent | 角色 | 职责 | 头像 |
|-------|------|------|------|
| CEO | 首席执行官 | 战略决策、资源分配 | 👨‍💼 |
| CMO | 市场总监 | 市场扫描、机会发现 | 👩‍💼 |
| CTO | 技术总监 | 技术评估、架构设计 | 👨‍💻 |
| COO | 运营总监 | 运营评估、流程优化 | 👩‍💻 |
| CPO | 产品总监 | 产品设计、用户体验 | 👨‍🎨 |
| CFO | 财务总监 | 财务规划、投资分析 | 👩‍💼 |
| CHRO | 人力资源总监 | 人才招聘、团队管理 | 👨‍💼 |
| Observer | 系统观察员 | 监控分析、优化建议 | 🤖 |

### 工作流程

```
Day N:
  ├─ 🌅 晨会 (所有Agent)
  ├─ 📊 CMO市场扫描 → 发现机会
  ├─ 🔍 并行评估 (CTO+CFO+CPO+COO)
  ├─ 👔 CEO综合决策 → 批准/拒绝
  ├─ 🚀 项目执行 (团队协作)
  ├─ 👥 HR团队管理
  └─ 📋 生成日报
```

### AI决策格式

每个Agent返回结构化决策：
```json
{
    "decision": "批准",
    "confidence": 0.85,
    "reasoning": "详细推理过程...",
    "action_items": ["行动1", "行动2"],
    "risks": ["风险1"],
    "recommendations": ["建议1"],
    "budget_request": 500000,
    "timeline_days": 90,
    "team_requirements": ["AI工程师", "产品经理"]
}
```

---

## 💡 使用示例

### 示例1: 基础模拟

```python
from hybrid_ai_company import HybridAICompanySystem, AIMode

# 创建系统（模拟模式）
mode = AIMode(use_real_ai=False)
company = HybridAICompanySystem("My Startup", mode)

# 运行3天模拟
import asyncio
asyncio.run(company.run_hybrid_simulation(days=3))
```

### 示例2: 真实AI模式

```python
import os
from hybrid_ai_company import HybridAICompanySystem, AIMode

# 创建系统（真实AI模式）
api_key = os.getenv("KIMI_API_KEY")
mode = AIMode(use_real_ai=True, api_key=api_key)
company = HybridAICompanySystem("My Startup", mode)

# 运行模拟
import asyncio
asyncio.run(company.run_hybrid_simulation(days=3))
```

### 示例3: 自定义Agent行为

```python
from kimi_agent_runner import KimiAgentConfig, KimiAgentFactory

# 自定义CEO提示词
custom_ceo_prompt = """你是{company_name}的CEO。

## 特殊约束
- 每次投资不能超过现金的30%
- 优先投资AI基础设施
- 重视长期价值而非短期收益

请做出符合这些约束的决策。"""

config = KimiAgentConfig(
    agent_id="ceo",
    name="Custom CEO",
    role="CEO",
    system_prompt=custom_ceo_prompt.format(company_name="My AI Startup"),
    api_key=api_key,
    thinking="high"
)
```

---

## 📊 成本估算

### 模拟AI模式
- **成本**: 免费
- **速度**: 快（0.5秒/决策）
- **适合**: 快速测试、演示

### 真实AI模式（Kimi K2.5）

| 操作 | Token消耗 | 预估成本 |
|------|-----------|----------|
| 单次决策 | 2K-4K | ¥0.02-0.04 |
| 完整评估（6 Agents） | 12K-24K | ¥0.12-0.24 |
| 每日模拟（20决策） | 40K-80K | ¥0.40-0.80 |
| 月度运行（30天） | 1.2M-2.4M | ¥12-24 |

*基于Kimi API定价：¥10/1M tokens*

---

## 🔧 故障排除

### 问题1: API Key无效

**症状**: 
```
❌ 错误: API Key无效或已过期
```

**解决**:
1. 访问 https://platform.moonshot.cn 获取新Key
2. 确认账户余额充足
3. 检查Key格式：`sk-kimi-...`

### 问题2: 网络连接失败

**症状**:
```
❌ 网络错误: Cannot connect to host
```

**解决**:
```bash
# 检查网络
curl -I https://api.moonshot.cn

# 使用代理（如需要）
export HTTPS_PROXY=http://proxy:port
```

### 问题3: 模拟AI不工作

**症状**: 程序卡住或无输出

**解决**:
```bash
# 检查Python版本
python3 --version  # 需要 3.8+

# 安装依赖
pip3 install aiohttp
```

---

## 🎨 可视化界面功能

### advanced_dashboard.html

- **实时状态**: Agent头像 + 状态指示器
- **财务图表**: Chart.js动态图表
- **项目看板**: 进度条 + 团队信息
- **活动日志**: 实时消息流
- **交互控制**: 开始/暂停模拟

### 使用方式

```bash
# macOS
open advanced_dashboard.html

# 或使用HTTP服务器
python3 -m http.server 8080
# 访问 http://localhost:8080/advanced_dashboard.html
```

---

## 🚀 下一步

### 短期
- [ ] 获取有效Kimi API Key
- [ ] 测试真实AI模式
- [ ] 调整Agent提示词

### 中期
- [ ] 接入更多数据源（市场数据、竞品信息）
- [ ] 添加记忆持久化
- [ ] 实现Agent间实时通信

### 长期
- [ ] 接入股票/加密货币市场
- [ ] 与其他AI公司竞争模拟
- [ ] 真实业务场景验证

---

## 📚 相关文档

- `KIMI_INTEGRATION_GUIDE.md` - 完整集成指南
- `VOXYZ_README.md` - 系统架构文档
- `advanced_company_v3.py` - 源代码注释

---

## 💬 支持

如有问题：
1. 检查 `test_kimi_connection.py` 输出
2. 查看 `KIMI_INTEGRATION_GUIDE.md`
3. 检查API Key有效性和余额

---

**版本**: v1.0  
**创建**: 2026-02-17  
**作者**: OpenClaw Agent
