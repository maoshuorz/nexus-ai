# 🏢 OpenClaw Multi-Agent Company System

基于 OpenClaw 智能体的多Agent公司模拟系统，使用 Kimi K2.5 Code 实现并行协作。

## 📁 项目结构

```
company_system/
├── ARCHITECTURE.md          # 系统架构文档
├── README.md               # 本文件
├── company_controller.py   # 公司主控制器
├── agent_runner.py         # Agent启动器
├── demo.py                 # 演示脚本
├── dashboard.html          # Web UI界面
└── agents/                 # Agent配置文件(可选)
```

## 🎯 系统架构

### 核心团队 (7个Agent)

| Agent | 角色 | 职责 |
|-------|------|------|
| **CEO** | 首席执行官 | 战略决策、资源分配、最终审批 |
| **CMO** | 市场总监 | 市场发现、用户需求、竞品分析 |
| **CTO** | 研发总监 | 技术架构、研发规划、技术评估 |
| **COO** | 运营总监 | 运营策略、流程优化、执行监督 |
| **PR** | 宣传总监 | 品牌建设、营销推广、用户获取 |
| **CFO** | 财务总监 | 财务规划、成本控制、收益分析 |
| **Observer** | 运营观察员 | 协作监控、问题发现、优化建议 |

### 工作流程

```
阶段1: 市场发现 → CMO发现机会
    ↓
阶段2: 并行评估 → CTO+CFO+COO同时评估
    ↓
阶段3: 战略决策 → CEO做最终决策
    ↓
阶段4: 项目执行 → 团队协作执行
    ↓
阶段5: 持续监控 → Observer监督优化
```

## 🚀 快速开始

### 1. 查看架构设计

```bash
cat company_system/ARCHITECTURE.md
```

### 2. 运行演示

```bash
cd company_system
python3 demo.py
```

### 3. 查看UI界面

打开 `dashboard.html` 文件查看公司运营仪表盘。

## 📊 系统特性

### 多Agent协作
- **并行评估**: CTO、CFO、COO同时评估项目
- **角色分工**: 每个Agent有明确的职责和技能
- **通信机制**: Agent间通过JSON消息通信

### 项目全生命周期管理
- **发现**: CMO自动寻找市场机会
- **评估**: 多维度可行性分析
- **决策**: CEO基于数据做决策
- **执行**: 团队协作推进项目
- **监控**: Observer持续优化

### 财务与资源管理
- 预算分配与控制
- 成本跟踪与ROI分析
- 风险评估与应对

### UI监控面板
- 实时Agent状态
- 项目进度追踪
- 团队通信记录
- 财务仪表盘

## 🔧 核心组件

### CompanyController
主控制器，管理所有Agent和项目：
- Agent生命周期管理
- 项目创建与状态跟踪
- 通信记录存储
- UI数据生成

### AgentRunner
Agent启动器，使用 OpenClaw 的 `sessions_spawn`：
- 并行启动多个Agent
- 分配任务和上下文
- 收集Agent输出

### Observer
运营观察员，持续监控系统：
- 分析Agent协作效率
- 识别沟通问题
- 提出优化建议

## 💡 使用场景

1. **创业项目模拟**: 模拟从0到1的创业过程
2. **团队协作训练**: 训练多Agent协作能力
3. **决策流程优化**: 优化公司决策流程
4. **项目管理实验**: 测试不同管理策略

## 🔮 未来扩展

- [ ] 接入真实的 OpenClaw sessions_spawn
- [ ] 添加更多Agent角色（HR、法务等）
- [ ] 实现Agent间的自主协商
- [ ] 添加竞争市场环境模拟
- [ ] 集成真实的市场数据源

## 📄 许可

MIT License
