# Nexus AI × Star Office UI 整合文档

_将 Star Office UI 作为 Nexus AI 的官方状态监控面板_

---

## 📋 整合概述

Star Office UI 为 Nexus AI 的 6 个 Agent 提供实时状态监控：

| Agent | 角色 | 专属色 |
|-------|------|--------|
| 宗志 | CEO | #FFE66D 黄 |
| 锦绣 | CMO | #FF6B9D 粉 |
| 匠心 | CTO | #4ECDC4 青 |
| 墨染 | Frontend | #9B59B6 紫 |
| 睿思 | Think | #E74C3C 红 |
| 明镜 | Audit | #3498DB 蓝 |

---

## 🏗️ 架构

```
┌─────────────────────────────────────────┐
│          Nexus AI Agents                │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐       │
│  │宗志 │ │锦绣 │ │匠心 │ │ ... │       │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘       │
│     │       │       │       │           │
│     └───────┴───┬───┴───────┘           │
│                 │                       │
│          StatePublisher                │
│          (star_office_bridge.py)        │
└─────────────────┼───────────────────────┘
                  │ HTTP POST
                  ▼
┌─────────────────────────────────────────┐
│       Star Office UI (Port 18795)       │
│  ┌─────────────────────────────────┐    │
│  │  /agents/:name/state (API)      │    │
│  │  /agents/status (状态墙)         │    │
│  │  /agents/activity-log (日志)    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 1. 启动服务

```bash
cd /Users/maoshu/Desktop/tbms
./scripts/start-nexus-full.sh
```

### 2. 在 Nexus AI Agent 中集成

```python
# 在 Agent 初始化时
from star_office_bridge import StatePublisher

class MyAgent:
    def __init__(self, name: str):
        self.name = name
        self.publisher = StatePublisher(name)
    
    def work(self, task: str):
        # 开始工作
        self.publisher.set_state("writing", f"正在处理：{task}")
        
        # ... 执行任务 ...
        
        # 完成
        self.publisher.set_state("idle", "任务完成")
```

### 3. 访问看板

打开浏览器访问：http://localhost:18795

- **简洁模式**: 显示单一状态
- **Agent 模式**: 显示 6 Agent 状态墙 + 活动日志

---

## 📡 API 文档

### 基础 API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/status` | GET | 当前状态（简洁模式） |
| `/set_state` | POST | 设置状态（简洁模式） |
| `/yesterday-memo` | GET | 读取 MEMORY.md |

### Agent API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/agents/status` | GET | 所有 Agent 状态 |
| `/agents/:name/status` | GET | 单个 Agent 状态 |
| `/agents/:name/state` | POST | 设置 Agent 状态 |
| `/agents/activity-log` | GET | 活动日志（最近 20 条） |
| `/agents/config` | GET | Agent 配置信息 |

### 请求示例

```bash
# 设置宗志状态
curl -X POST http://localhost:18795/agents/宗志/state \
     -H 'Content-Type: application/json' \
     -d '{"state": "writing", "note": "正在分析 Q1 财报"}'

# 获取所有 Agent 状态
curl http://localhost:18795/agents/status

# 获取活动日志
curl http://localhost:18795/agents/activity-log?limit=10
```

---

## 📝 状态值说明

| 状态 | 说明 | 使用场景 |
|------|------|----------|
| `idle` | 空闲 | 等待任务/休息 |
| `writing` | 写作中 | 编写代码/文档/报告 |
| `researching` | 调研中 | 搜索信息/分析数据 |
| `executing` | 执行中 | 运行命令/调用 API |
| `syncing` | 同步中 | 文件同步/数据更新 |
| `error` | 异常 | 任务失败/错误处理 |

---

## 🔧 配置

### Star Office 配置

编辑 `/Users/maoshu/Desktop/tbms/backend/star-office/app.py`:

```python
# 修改端口
app.run(host="0.0.0.0", port=18795, debug=False)

# 添加新 Agent
AGENT_CONFIG = {
    "宗志": {"role": "CEO", "color": "#FFE66D"},
    # 添加新 Agent...
}
```

### Nexus AI 配置

在 Agent 基类中集成：

```python
# advanced_company_v3.py 或类似文件
from star_office_bridge import StatePublisher

# 在 Agent 初始化时
self.state_publisher = StatePublisher(self.name)

# 在关键方法中调用
def execute_task(self, task):
    self.state_publisher.set_state("executing", task.description)
    # ...
```

---

## 📊 前端模式

### 简洁模式
- 单状态显示
- 适合个人使用
- 快速查看当前状态

### Agent 模式
- 6 Agent 状态墙
- 专属颜色标识
- 活动日志时间轴
- 适合团队协作监控

---

## ⚠️ 注意事项

1. **端口占用**: 默认端口 18795，如被占用请修改 `app.py`
2. **虚拟环境**: Star Office 使用独立 `.venv`，确保已安装依赖
3. **异步发布**: `set_state(async_mode=True)` 不阻塞主逻辑
4. **日志轮转**: 活动日志保留最近 100 条，自动轮转

---

## 🛠️ 故障排查

### Star Office 无法启动

```bash
# 查看日志
cat /tmp/star-office.log

# 检查端口占用
lsof -i :18795

# 重启服务
kill $(cat backend/star-office/.pid)
./scripts/start-nexus-full.sh
```

### Agent 状态不更新

1. 检查网络连接：`curl http://localhost:18795/health`
2. 检查 Agent 名称是否正确（中文名称需精确匹配）
3. 查看活动日志：`curl http://localhost:18795/agents/activity-log`

---

## 📄 文件结构

```
tbms/
├── backend/star-office/
│   ├── app.py              # Flask 服务（支持 Agent API）
│   ├── agents_state.json   # Agent 状态存储
│   ├── activity_log.json   # 活动日志
│   └── frontend/
│       └── index.html      # 支持双模式看板

nexus-ai/
├── star_office_bridge.py   # Agent 状态发布器
└── INTEGRATION_STAR_OFFICE.md  # 本文档

scripts/
├── start-office.sh         # 仅启动 Star Office
└── start-nexus-full.sh     # 启动全套服务
```

---

## 🎯 后续优化（阶段 2/3）

- [ ] 像素风视觉升级（六艺智团头像）
- [ ] WebSocket 实时推送（替代轮询）
- [ ] 状态统计报表（每日/每周）
- [ ] Telegram 通知集成
- [ ] 状态 - 任务关联（绑定具体任务 ID）

---

_最后更新：2026-03-01_

---

## 🎨 Phase 2 更新 (2026-03-01)

### 新增功能

#### 1. WebSocket 实时推送
- 状态变更即时同步到前端（无需轮询）
- 事件：`connect` → `agents_init`, `agent_update`, `status_update`
- 断线自动重连

#### 2. 像素风视觉升级
- 字体：Press Start 2P（像素游戏风格）
- 霓虹灯效果：文字阴影 + 边框发光
- Agent 头像表情符号：
  - 宗志 🐲 (CEO)
  - 锦绣 🦊 (CMO)
  - 匠心 🤖 (CTO)
  - 墨染 🎨 (Frontend)
  - 睿思 🦉 (Think)
  - 明镜 ⚖️ (Audit)

#### 3. 状态动画
- 状态指示灯闪烁
- Agent 卡片更新脉冲效果
- WebSocket 连接状态指示

#### 4. 桥接模块增强
```python
publisher.start_work("任务描述")      # writing 状态
publisher.start_research("调研主题")  # researching 状态
publisher.start_execution("命令")     # executing 状态
publisher.finish("完成")              # idle 状态
publisher.error("错误信息")           # error 状态
```

### 技术栈更新

```
flask==3.0.3
flask-cors==4.0.1
flask-socketio==5.3.6
python-socketio==5.10.0
# async_mode=threading (兼容 Python 3.14)
```

### 视觉效果

```
╔════════════════════════════════════════════════════════╗
║     STAR OFFICE UI - Pixel Style                       ║
╚════════════════════════════════════════════════════════╝

[🐲 宗志] [CEO]
┌────────────────────────────┐
│    ⚡ 执行中                │
│  正在执行 Phase 2 部署       │
│  UPDATED: 2026-03-01 18:42 │
└────────────────────────────┘
```

### 访问

- HTTP: http://localhost:18795
- WebSocket: ws://localhost:18795

---


---

## 🎯 Phase 3 更新 (2026-03-01)

### 深度一体化功能

#### 1. 任务管理系统

**API**:
| 端点 | 方法 | 说明 |
|------|------|------|
| `GET /tasks` | 获取 | 活动任务列表 |
| `POST /tasks` | 创建 | 创建新任务 |
| `PUT /tasks/<id>` | 更新 | 更新任务状态 |

**请求示例**:
```bash
# 创建任务
curl -X POST http://localhost:18795/tasks \
     -H 'Content-Type: application/json' \
     -d '{"agent": "宗志", "description": "Q1 战略规划"}'

# 获取任务列表
curl http://localhost:18795/tasks
```

**数据结构**:
```json
{
  "id": "task_20260301184632_宗志",
  "agent": "宗志",
  "description": "Q1 战略规划",
  "status": "active",
  "created_at": "2026-03-01T18:46:32",
  "updated_at": "2026-03-01T18:46:32"
}
```

#### 2. 统计报表系统

**API**: `GET /stats?days=7`

**响应**:
```json
{
  "daily": { "2026-03-01": { "writing": 5, "executing": 3 } },
  "agents": { "宗志": { "writing": 2, "idle": 1 } },
  "total": { "writing": 5, "executing": 3, "idle": 2 },
  "period": "最近 7 天"
}
```

**前端展示**:
- 今日概览：6 状态汇总
- Agent 统计：每人状态分布
- 主要状态：最频繁状态

#### 3. 状态 - 任务关联

设置 Agent 状态时可绑定任务 ID：
```python
publisher.set_state("writing", "撰写报告", task_id="task_123")
```

API:
```bash
curl -X POST http://localhost:18795/agents/宗志/state \
     -H 'Content-Type: application/json' \
     -d '{"state": "writing", "note": "撰写报告", "task_id": "task_123"}'
```

#### 4. 活动日志扩展

- 容量：200 条（Phase 2 为 100 条）
- 字段：agent, state, note, task_id, timestamp
- API: `GET /agents/activity-log?limit=20`

### 前端三板块

| 板块 | 功能 |
|------|------|
| Agent 墙 | 6 Agent 实时状态 + 活动日志 |
| 统计 | 今日概览 + Agent 统计 |
| 任务 | 活动任务列表 |

### 文件结构

```
backend/star-office/
├── app.py              # Phase 3 服务
├── state.json          # 简洁模式状态
├── agents_state.json   # Agent 状态
├── activity_log.json   # 活动日志 (200 条)
├── tasks.json          # 任务管理 (新增)
├── stats.json          # 统计数据 (新增)
└── frontend/
    └── index.html      # 三板块 UI
```

### 桥接模块 Phase 3

```python
from star_office_bridge import StatePublisher

publisher = StatePublisher("宗志")

# 创建任务并绑定
task = requests.post('http://localhost:18795/tasks', json={
    'agent': '宗志',
    'description': 'Q1 战略规划'
}).json()['task']

# 设置状态时绑定任务
publisher.set_state("writing", "撰写战略报告", task_id=task['id'])

# 完成任务
publisher.finish("Q1 战略完成")
requests.put(f"http://localhost:18795/tasks/{task['id']}", json={'status': 'completed'})
```

### 统计数据自动累积

每次状态变更自动记录：
- 按天统计：`stats.days["2026-03-01"]["writing"] += 1`
- 按 Agent 统计：`stats.agents["宗志"]["writing"] += 1`

---

## 📊 三阶段对比

| 功能 | Phase 1 | Phase 2 | Phase 3 |
|------|---------|---------|---------|
| HTTP API | ✅ | ✅ | ✅ |
| WebSocket | ❌ | ✅ | ✅ |
| 像素风视觉 | ❌ | ✅ | ✅ |
| Agent 头像 | ❌ | ✅ | ✅ |
| 任务管理 | ❌ | ❌ | ✅ |
| 统计报表 | ❌ | ❌ | ✅ |
| 状态 - 任务关联 | ❌ | ❌ | ✅ |
| 活动日志 | 100 条 | 100 条 | 200 条 |
| 前端板块 | 2 | 2 | 3 |

---

## 🎉 完整功能清单

### API (13 个端点)

**基础**:
- `GET /health`
- `GET /status`
- `POST /set_state`
- `GET /yesterday-memo`

**Agent**:
- `GET /agents/status`
- `GET /agents/:name/status`
- `POST /agents/:name/state`
- `GET /agents/activity-log`
- `GET /agents/config`

**任务**:
- `GET /tasks`
- `POST /tasks`
- `PUT /tasks/:id`

**统计**:
- `GET /stats`

### WebSocket 事件

- `connect` → `agents_init`
- `agent_update`
- `status_update`

### 前端功能

- 实时状态墙（6 Agent）
- 活动日志时间轴
- 今日概览统计
- Agent 个人统计
- 活动任务列表
- WebSocket 连接状态

---

_Phase 3 完成日期：2026-03-01_
_GitHub: https://github.com/maoshuorz/nexus-ai_
