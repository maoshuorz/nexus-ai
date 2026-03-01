# 🎭 Nexus AI - 四智团协同系统

> 🧠 宗志 (CEO) · 💻 码匠 (工程师) · 🔬 研析 (研究员) · 🏠 家助 (协调员)  
> 📅 版本：V4.0 Quartet Edition  
> 🌐 官网：https://maoshuorz.github.io/nexus-ai/

---

## 📋 项目概述

Nexus AI 是一个**四智团协同作战系统**，通过 4 个专业 AI Agent 的分工协作，实现高效的任务执行和决策支持。

### 核心理念
- **精简高效**：4 人团队，职责清晰
- **实时协同**：状态实时同步，可视化监控
- **安全可控**：本地运行，数据隔离
- **开源开放**：MIT 许可，自由扩展

---

## 👥 四智团成员

| 名字 | 角色 | 职责 | 表情 | 颜色 |
|------|------|------|------|------|
| **宗志** | 决策者 (CEO) | 战略规划、任务分配 | 🧠💡 | #FF6B6B |
| **码匠** | 工程师 | 编码实现、技术构建 | 💻🔨 | #4ECDC4 |
| **研析** | 研究员 | 信息收集、数据分析 | 🔬📊 | #A78BFA |
| **家助** | 协调员 | 日程管理、资源协调 | 🏠📋 | #F59E0B |

---

## 🌐 在线演示

### 官网
- **主页**: https://maoshuorz.github.io/nexus-ai/
- **四智团监控**: https://maoshuorz.github.io/nexus-ai/quartet.html

### 功能
- 实时 Agent 状态展示
- 活动日志（每 3 秒刷新）
- WebSocket 实时推送
- 响应式设计（支持移动端）

---

## 🚀 快速开始

### 前置要求
- Python 3.14+
- Node.js 18+
- OpenClaw

### 安装

```bash
# 1. 克隆项目
git clone https://github.com/maoshuorz/nexus-ai.git
cd nexus-ai

# 2. 安装后端依赖
cd backend/star-office
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. 启动服务
cd ../../scripts
./start-star-office-auto.sh
```

### 访问

```bash
open http://localhost:18795
```

---

## 📁 项目结构

```
nexus-ai/
├── index.html                 # 官网主页
├── quartet.html               # 四智团监控页面
├── star_office_bridge.py      # Agent 桥接模块
├── agent_runner.py            # Agent 运行器
├── README.md                  # 本文档
├── docs/                      # 文档目录
│   ├── API.md                 # API 文档
│   └── DEPLOYMENT.md          # 部署指南
└── backend/star-office/       # Star Office 后端
    ├── app.py                 # Flask 服务
    ├── auto_sync.py           # 自动同步脚本
    ├── frontend/              # 前端文件
    └── scripts/               # 启动脚本
```

---

## 🔌 API 文档

### 基础端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/quartet/status` | GET | 所有 Agent 状态 |
| `/quartet/:name/state` | POST | 设置 Agent 状态 |
| `/quartet/activity` | GET | 活动日志 |
| `/quartet/stats` | GET | 统计数据 |

### 使用示例

```bash
# 设置 Agent 状态
curl -X POST http://localhost:18795/quartet/宗志/state \
     -H 'Content-Type: application/json' \
     -d '{"state": "thinking", "note": "战略规划"}'

# 获取活动日志
curl http://localhost:18795/quartet/activity?limit=10

# 获取统计
curl http://localhost:18795/quartet/stats?days=7
```

### Python SDK

```python
from star_office_bridge import StatePublisher

# 创建 Agent
zong = StatePublisher("宗志")

# 设置状态
zong.thinking("战略规划中")

# 委派任务
zong.delegate("码匠", "实现新功能")
```

---

## 🔄 自动同步

系统支持从 OpenClaw sessions 自动同步 Agent 活动：

```bash
# 启动自动同步
python auto_sync.py
```

**同步频率**: 每 30 秒  
**数据来源**: OpenClaw sessions（只读）  
**安全保证**: 不修改任何 Agent 代码

---

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | HTML5, CSS3, JavaScript, Socket.IO |
| 后端 | Python 3.14, Flask, Flask-SocketIO |
| 通信 | WebSocket, REST API |
| 部署 | GitHub Pages, 本地服务 |

---

## 📊 系统架构

```
┌─────────────────────────────────────────────┐
│              Nexus AI                        │
│  ┌─────────────────────────────────────┐   │
│  │  四智团 (Quartet)                    │   │
│  │  🧠宗志  💻码匠  🔬研析  🏠家助      │   │
│  └─────────────────────────────────────┘   │
│                    ↓                         │
│  ┌─────────────────────────────────────┐   │
│  │  star_office_bridge.py              │   │
│  └─────────────────────────────────────┘   │
└────────────────────┬───────────────────────┘
                     │ HTTP + WebSocket
                     ↓
┌─────────────────────────────────────────────┐
│           Star Office UI                     │
│  ┌─────────────────────────────────────┐   │
│  │  Flask + SocketIO (Port 18795)      │   │
│  └─────────────────────────────────────┘   │
│  ┌─────────────────────────────────────┐   │
│  │  实时监控面板                        │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## 🔐 安全说明

- 服务仅监听 `localhost:18795`（不开放外网）
- 自动同步只读访问 OpenClaw sessions
- 所有数据本地存储
- 无外部 API 调用
- 可随时停止服务或删除数据

详见：[SECURITY_GUIDE.md](backend/star-office/SECURITY_GUIDE.md)

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [README_QUARTET.md](README_QUARTET.md) | 四智团使用说明 |
| [DESIGN_QUARTET.md](backend/star-office/DESIGN_QUARTET.md) | 设计文档 |
| [SECURITY_GUIDE.md](backend/star-office/SECURITY_GUIDE.md) | 安全指南 |
| [INTEGRATION_STAR_OFFICE.md](INTEGRATION_STAR_OFFICE.md) | Star Office 集成 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 📞 联系方式

- **GitHub**: [@maoshuorz](https://github.com/maoshuorz)
- **项目地址**: https://github.com/maoshuorz/nexus-ai

---

_最后更新：2026-03-01 · V4.0 Quartet Edition_
