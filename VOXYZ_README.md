# Voxyz-Style Multi-Agent Company System
# Voxyz风格多Agent公司模拟系统

## 🎮 系统概览

参考 Voxyz AI Agent Platform 设计的多Agent公司模拟系统，实现7个AI Agent自主协作运营一家公司。

### 核心特性

- 🤖 **7个AI Agent** - CEO, CMO, CTO, COO, PR, CFO, Observer
- 🔄 **自主决策** - Agent根据市场数据自主做出商业决策
- 📊 **实时协作** - Agent间通过消息系统实时通信
- 💰 **财务管理** - 完整的资金、收入、支出追踪
- 📈 **项目全生命周期** - 发现→评估→决策→执行→监控
- 🎨 **可视化界面** - 现代化的Web Dashboard

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Voxyz Company System                  │
├─────────────────────────────────────────────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │
│  │ CEO │ │ CMO │ │ CTO │ │ COO │ │ PR  │ │ CFO │     │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘     │
│     │       │       │       │       │       │          │
│     └───────┴───────┴───────┴───────┴───────┘          │
│                      │                                   │
│               ┌──────┴──────┐                           │
│               │  Observer   │  ← 监控与优化              │
│               └─────────────┘                           │
└─────────────────────────────────────────────────────────┘
```

---

## 👥 Agent角色定义

| Agent | 角色 | 核心职责 | 技能 |
|-------|------|----------|------|
| **CEO** | 首席执行官 | 战略决策、资源分配、最终审批 | 战略决策、领导力、资源分配 |
| **CMO** | 市场总监 | 市场扫描、机会发现、用户洞察 | 市场分析、竞品研究、用户画像 |
| **CTO** | 技术总监 | 技术评估、架构设计、研发规划 | 技术架构、研发管理、创新 |
| **COO** | 运营总监 | 运营评估、流程优化、执行监督 | 运营管理、流程优化、执行 |
| **PR** | 品牌总监 | 品牌建设、营销推广、公关策略 | 品牌建设、内容营销、公关 |
| **CFO** | 财务总监 | 财务规划、成本控制、投资分析 | 财务规划、投资分析、风控 |
| **Observer** | 运营观察员 | 协作监控、问题发现、优化建议 | 监控分析、问题识别、优化 |

---

## 🔄 工作流程

### 阶段1: 市场发现 (CMO主导)
```
CMO扫描市场趋势 → 识别机会 → 提交项目提案
```

### 阶段2: 并行评估 (多Agent协作)
```
         ┌──────────┐
         │  项目提案  │
         └────┬─────┘
              │
    ┌─────────┼─────────┐
    │         │         │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐
│  CTO  │ │ CFO  │ │ COO  │
│技术评估│ │财务评估│ │运营评估│
└───┬───┘ └──┬───┘ └──┬───┘
    │        │        │
    └────────┼────────┘
             │
        ┌────▼────┐
        │ 评估报告  │
        └─────────┘
```

### 阶段3: 战略决策 (CEO决策)
```
CEO综合评估 → 做出决策 → 分配预算和团队
```

### 阶段4: 项目执行 (团队协作)
```
CTO: 技术研发
COO: 运营搭建  
PR:  市场推广
CFO: 财务监控
```

### 阶段5: 持续监控 (Observer)
```
Observer监控系统 → 发现问题 → 提出优化建议
```

---

## 📁 文件结构

```
company_system/
├── ARCHITECTURE.md              # 原始架构文档
├── README.md                     # 本文件
├── voxyz_company_v2.py          # Voxyz风格公司系统核心
├── voxyz_dashboard.html         # 可视化Dashboard
├── company_controller.py        # 基础版公司控制器
├── agent_runner.py              # Agent启动器
├── demo.py                      # 演示脚本
├── dashboard.html               # 基础版Dashboard
└── README.md                    # 项目说明
```

---

## 🚀 快速开始

### 1. 运行核心系统

```bash
cd ~/.openclaw/workspace/company_system
python3 voxyz_company_v2.py
```

### 2. 打开可视化界面

```bash
open voxyz_dashboard.html  # macOS
# 或
python3 -m http.server 8080  # 然后访问 localhost:8080/voxyz_dashboard.html
```

### 3. 运行演示

```bash
python3 demo.py
```

---

## 💡 使用示例

### 创建公司实例

```python
from voxyz_company_v2 import VoxyzCompanySystem

# 创建公司
company = VoxyzCompanySystem(company_name="My Startup")

# 运行一轮模拟
import asyncio
asyncio.run(company.run_simulation_round())

# 获取仪表盘数据
dashboard = company.get_dashboard_data()
print(json.dumps(dashboard, indent=2))
```

### 查看Agent状态

```python
# 查看所有Agent
for agent_id, agent in company.agents.items():
    print(f"{agent.name}: {agent.status}")

# 查看项目
for project_id, project in company.projects.items():
    print(f"{project.name}: {project.status.value}")

# 查看财务
print(f"Balance: ¥{company.financials['current_balance']}")
```

---

## 🎨 Dashboard功能

### 实时面板
- **Agent状态** - 实时显示7个Agent的工作状态
- **项目看板** - 追踪所有项目的进度和ROI
- **财务仪表盘** - 收入、支出、余额实时更新
- **市场趋势** - 显示当前市场机会和趋势
- **活动日志** - Agent间通信和操作记录

### 交互功能
- ▶️ Start Simulation - 开始新一轮模拟
- 👁️ 实时更新 - Agent状态实时刷新
- 📊 数据可视化 - 图表展示财务和项目数据

---

## 🔧 核心组件

### Agent系统
- 每个Agent有独立的状态、技能、任务
- Agent间通过Message系统通信
- Observer监控所有Agent的协作效率

### 项目系统
- 完整的项目生命周期管理
- 自动团队分配
- 进度追踪和ROI计算

### 财务系统
- 初始资金管理
- 收入和支出追踪
- 投资回报计算

### 市场系统
- 趋势分析
- 竞品监控
- 机会评分

---

## 🚀 与OpenClaw集成

当前版本是模拟系统，可以扩展为使用真实的`kimi-coding/k2p5`模型：

```python
# 在agent_runner.py中使用sessions_spawn
from openclaw import sessions_spawn

# 启动真实Agent
sessions_spawn(
    agent_id="cmo",
    task="扫描市场发现机会",
    model="kimi-coding/k2p5",
    thinking="medium"
)
```

这样可以实现：
- 真实的AI Agent决策
- 并行Agent执行
- 真实的商业分析和建议

---

## 📊 性能指标

当前模拟版本：
- **响应时间**: < 1秒/轮
- **并发Agent**: 7个
- **项目处理能力**: 多项目并行
- **内存占用**: < 50MB

---

## 🎯 未来扩展

- [ ] 接入真实AI模型 (Kimi K2.5)
- [ ] 添加更多Agent角色 (HR, 法务等)
- [ ] 市场竞争模拟
- [ ] 真实数据源集成
- [ ] WebSocket实时通信
- [ ] 历史数据分析

---

## 📄 许可

MIT License

---

**参考设计**: Voxyz AI Agent Platform  
**创建日期**: 2026-02-17  
**版本**: v2.0
