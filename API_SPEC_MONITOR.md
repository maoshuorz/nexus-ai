# Nexus AI 监控模块 API 规范

> **版本**: v1.0  
> **创建者**: CPO Michael  
> **日期**: 2026-02-18  
> **状态**: 待CTO确认

---

## 1. 接口概览

### 1.1 基础信息

| 项目 | 值 |
|------|-----|
| 基础URL | `https://api.nexus-ai.com/v1` |
| 认证方式 | Bearer Token |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |

### 1.2 认证头

```http
Authorization: Bearer {token}
Content-Type: application/json
```

---

## 2. 核心接口

### 2.1 获取监控仪表盘数据

**公开版和管理版共用此接口，返回数据根据用户权限自动过滤**

```http
GET /monitor/dashboard
```

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `version` | string | 否 | `public` 或 `full`，默认根据token权限 |
| `timestamp` | number | 否 | 客户端时间戳，用于缓存控制 |

#### 响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "timestamp": 1709876543210,
    "summary": {
      "revenue": {
        "current": 128500,
        "target": 150000,
        "currency": "CNY",
        "month_over_month": 12.5,
        "history": [85000, 92000, 88000, 105000, 115000, 122000, 128500]
      },
      "projects": {
        "active": 12,
        "discussing": 3,
        "review": 2,
        "completed": 28
      },
      "agents": {
        "total": 6,
        "online": 6,
        "busy": 2,
        "average_load": 68
      }
    },
    "agents": [
      {
        "id": "ceo",
        "name": "Alex",
        "title": "CEO",
        "role": "战略决策",
        "status": "active",
        "activity": "评估新项目",
        "load": 65,
        "last_seen": "2026-02-18T08:30:00Z",
        "tasks_count": 3
      }
    ],
    "projects": {
      "discussing": [...],
      "progress": [...],
      "review": [...],
      "completed": [...]
    },
    "system": {
      "uptime_seconds": 1228800,
      "version": "2.0.1",
      "api_status": {
        "gmail": "healthy",
        "twitter": "healthy",
        "openai": "degraded",
        "feishu": "healthy"
      }
    }
  }
}
```

#### 公开版 vs 完整版数据差异

| 数据字段 | 公开版 | 完整版 |
|----------|--------|--------|
| 收入总额 | ✅ | ✅ |
| 收入历史 | ✅ (7天) | ✅ (30天/自定义) |
| 收入目标 | ❌ | ✅ |
| 项目数量 | ✅ | ✅ |
| 项目预算 | ❌ | ✅ |
| 项目详细描述 | 简化 | 完整 |
| Agent状态 | ✅ | ✅ |
| Agent负载 | 简化显示 | 完整数值 |
| Agent操作按钮 | ❌ | ✅ |
| 系统日志 | ❌ | ✅ |
| API状态 | ❌ | ✅ |

---

### 2.2 获取Agent详情

```http
GET /monitor/agents/{agent_id}
```

#### 响应

```json
{
  "code": 200,
  "data": {
    "id": "cto",
    "name": "David",
    "status": "busy",
    "current_task": {
      "id": "task_123",
      "title": "开发Gmail系统",
      "progress": 85,
      "started_at": "2026-02-10T09:00:00Z"
    },
    "recent_logs": [...],
    "performance": {
      "tasks_completed_7d": 15,
      "average_response_time": 2.3,
      "success_rate": 98.5
    }
  }
}
```

---

### 2.3 Agent控制操作

```http
POST /monitor/agents/{agent_id}/control
```

#### 请求体

```json
{
  "action": "restart",
  "reason": "手动重启"
}
```

#### 支持的操作

| 操作 | 说明 | 权限 |
|------|------|------|
| `restart` | 重启Agent | admin |
| `pause` | 暂停Agent | admin |
| `resume` | 恢复Agent | admin |
| `stop` | 停止Agent | admin |

---

### 2.4 项目操作

#### 创建项目
```http
POST /monitor/projects
```

```json
{
  "title": "新项目",
  "description": "项目描述",
  "client": "客户名称",
  "budget": 50000,
  "priority": "high",
  "assigned_agents": ["cto", "cpo"]
}
```

#### 更新项目
```http
PUT /monitor/projects/{project_id}
```

#### 删除项目
```http
DELETE /monitor/projects/{project_id}
```

#### 更新项目状态
```http
PATCH /monitor/projects/{project_id}/status
```

```json
{
  "status": "completed",
  "progress": 100
}
```

---

### 2.5 系统日志

```http
GET /monitor/logs
```

#### 请求参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `limit` | number | 返回条数，默认 50，最大 200 |
| `offset` | number | 分页偏移 |
| `level` | string | 过滤级别: info, warning, error, success |
| `agent_id` | string | 过滤特定Agent |
| `start_time` | string | ISO 8601 开始时间 |
| `end_time` | string | ISO 8601 结束时间 |

#### 响应

```json
{
  "code": 200,
  "data": {
    "total": 1250,
    "logs": [
      {
        "id": "log_123",
        "timestamp": "2026-02-18T08:30:00Z",
        "level": "info",
        "agent_id": "cto",
        "message": "任务完成: 代码审查",
        "metadata": {}
      }
    ]
  }
}
```

---

### 2.6 执行系统操作

```http
POST /monitor/system/action
```

```json
{
  "action": "backup",
  "params": {}
}
```

#### 支持的操作

| 操作 | 说明 | 响应 |
|------|------|------|
| `backup` | 数据备份 | `{ "backup_id": "bak_123", "status": "pending" }` |
| `export_report` | 导出报告 | `{ "download_url": "..." }` |
| `notify_all` | 发送全员通知 | `{ "sent": 6 }` |

---

## 3. WebSocket 实时推送 (可选)

### 3.1 连接地址

```
wss://api.nexus-ai.com/v1/monitor/ws
```

### 3.2 订阅消息

```json
{
  "type": "subscribe",
  "channels": ["agent_status", "project_updates", "system_logs"]
}
```

### 3.3 推送消息格式

```json
{
  "channel": "agent_status",
  "timestamp": 1709876543210,
  "data": {
    "agent_id": "cto",
    "status": "busy",
    "activity": "开发新功能"
  }
}
```

---

## 4. 错误处理

### 4.1 错误响应格式

```json
{
  "code": 400,
  "message": "请求参数错误",
  "details": {
    "field": "budget",
    "error": "预算必须为正数"
  }
}
```

### 4.2 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

---

## 5. 前端轮询逻辑

### 5.1 轮询配置

```javascript
const CONFIG = {
  refreshInterval: 30000,  // 30秒
  retryInterval: 5000,     // 失败重试间隔
  maxRetries: 3            // 最大重试次数
};
```

### 5.2 轮询逻辑

```javascript
async function startPolling() {
  const poll = async () => {
    try {
      const response = await fetch('/api/monitor/dashboard');
      const data = await response.json();
      updateUI(data);
      scheduleNextPoll(CONFIG.refreshInterval);
    } catch (error) {
      console.error('Poll failed:', error);
      scheduleNextPoll(CONFIG.retryInterval);
    }
  };
  
  poll();
}
```

---

## 6. 数据缓存策略

### 6.1 客户端缓存

| 数据类型 | 缓存时间 | 说明 |
|----------|----------|------|
| 仪表盘数据 | 30秒 | 与轮询周期一致 |
| Agent列表 | 60秒 | 状态变化不频繁 |
| 项目列表 | 30秒 | 根据tab不同 |
| 日志数据 | 不缓存 | 实时性要求高 |

### 6.2 ETag 支持

```http
GET /monitor/dashboard
If-None-Match: "abc123"

HTTP/1.1 304 Not Modified
```

---

## 7. 安全要求

### 7.1 访问控制

| 接口 | 公开访问 | 用户访问 | 管理员访问 |
|------|----------|----------|------------|
| GET /dashboard | ✅ (public版本) | ✅ | ✅ |
| GET /dashboard?version=full | ❌ | ❌ | ✅ |
| POST /agents/{id}/control | ❌ | ❌ | ✅ |
| POST /projects | ❌ | ✅ | ✅ |
| DELETE /projects/{id} | ❌ | ❌ | ✅ |

### 7.2 速率限制

| 用户类型 | 限制 |
|----------|------|
| 公开访问 | 10 req/min |
| 普通用户 | 60 req/min |
| 管理员 | 300 req/min |

---

## 8. 待确认事项

- [ ] API基础URL确定
- [ ] 认证方式确认（JWT / API Key）
- [ ] 数据库Schema设计
- [ ] WebSocket是否需要
- [ ] 日志存储策略
- [ ] 数据保留期限

---

## 附录：Mock 数据

开发阶段可使用以下Mock数据：

```bash
# 启动本地Mock服务器
cd company_system
python3 -m http.server 8080

# 访问
open http://localhost:8080/monitor_v5_dual.html
```

**注意**: 当前前端已实现完整的静态原型，数据更新为模拟实现，等待后端API完成后替换。
