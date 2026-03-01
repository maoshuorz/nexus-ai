# 🎭 四智团 (Quartet)

_Nexus AI 实时活动监控系统_

---

## 👥 四智团成员

| 名字 | 角色 | 职责 | 表情 |
|------|------|------|------|
| **宗志** | 决策者 (CEO) | 战略规划、任务分配 | 🧠💡 |
| **码匠** | 工程师 | 编码实现、技术构建 | 💻🔨 |
| **研析** | 研究员 | 信息收集、数据分析 | 🔬📊 |
| **家助** | 协调员 | 日程管理、资源协调 | 🏠📋 |

---

## 🌐 访问方式

### 在线官网
- **主页**: https://maoshuorz.github.io/nexus-ai/
- **四智团监控**: https://maoshuorz.github.io/nexus-ai/quartet.html

### 本地服务
- **Star Office**: http://localhost:18795

---

## 🚀 快速启动

### 方式 1: 一键启动（推荐）

```bash
cd /Users/maoshu/Desktop/tbms
./scripts/start-star-office-auto.sh
```

### 方式 2: 手动启动

```bash
# 启动 Star Office 服务
cd /Users/maoshu/Desktop/tbms/backend/star-office
source .venv/bin/activate
python app.py

# 启动自动同步（可选）
python auto_sync.py
```

### 停止服务

```bash
./scripts/stop-star-office.sh
```

---

## 🔄 自动同步

系统每 30 秒自动从 OpenClaw sessions 读取 Agent 活动：

```
OpenClaw Sessions → auto_sync.py → Star Office UI
     (只读)           (同步)         (展示)
```

**安全保证**:
- ✅ 只读 sessions，不修改任何代码
- ✅ 本地运行，数据不出本机
- ✅ 可随时停止

---

## 📊 功能特性

| 功能 | 说明 |
|------|------|
| 实时状态 | 4 Agent 当前活动状态 |
| 活动日志 | 最近活动记录（每 3 秒刷新） |
| WebSocket | 状态变更实时推送 |
| 自动同步 | 从 OpenClaw sessions 自动读取 |
| 手动记录 | 支持 API/脚本手动记录 |

---

## 🛠️ API 端点

```
GET  /quartet/status          - 所有 Agent 状态
POST /quartet/:name/state     - 设置 Agent 状态
GET  /quartet/activity        - 活动日志
```

### 使用示例

```bash
# 设置 Agent 状态
curl -X POST http://localhost:18795/quartet/宗志/state \
     -H 'Content-Type: application/json' \
     -d '{"state": "thinking", "note": "战略规划"}'

# 获取活动日志
curl http://localhost:18795/quartet/activity?limit=10
```

---

## 📁 项目结构

```
nexus-ai/
├── quartet.html              # 四智团监控页面
├── index.html                # 主页（含入口）
└── README_QUARTET.md         # 本文档

tbms/backend/star-office/
├── app.py                    # Flask 服务
├── auto_sync.py              # 自动同步脚本
├── frontend/index.html       # 本地 UI
└── scripts/
    ├── start-star-office-auto.sh
    └── stop-star-office.sh
```

---

## 🔐 安全说明

- 服务仅监听 `localhost:18795`（不开放外网）
- 自动同步只读访问 OpenClaw sessions
- 所有数据本地存储
- 可随时停止服务或删除数据

详见：`SECURITY_GUIDE.md`

---

## 📞 相关文档

- [DESIGN_QUARTET.md](../../tbms/backend/star-office/DESIGN_QUARTET.md) - 设计文档
- [SECURITY_GUIDE.md](../../tbms/backend/star-office/SECURITY_GUIDE.md) - 安全指南

---

_最后更新：2026-03-01_
