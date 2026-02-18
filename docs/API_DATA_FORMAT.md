# Nexus AI - 订单数据API文档
## For: CTO David (技术架构)

**文档版本**: v1.0  
**创建时间**: 2026-02-18 08:55  
**负责人**: Emma (COO)  
**审核状态**: 待CTO确认

---

## 1. 数据架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                      Data Flow Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐     ┌──────────────┐     ┌────────────────────┐  │
│  │  Gmail   │────▶│ gmail_sync   │────▶│   orders.json      │  │
│  │  API     │     │   (Python)   │     │  (Single Source)   │  │
│  └──────────┘     └──────────────┘     └────────────────────┘  │
│                                               │                  │
│                                               ▼                  │
│                                      ┌────────────────────┐     │
│                                      │  Monitor Dashboard │     │
│                                      │   (Real-time)      │     │
│                                      └────────────────────┘     │
│                                               │                  │
│                                               ▼                  │
│                                      ┌────────────────────┐     │
│                                      │   Agent System     │     │
│                                      │ (CTO/COO/CEO...)   │     │
│                                      └────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 核心数据文件

### 2.1 orders.json 结构

**文件路径**: `company_system/data/orders.json`  
**更新频率**: 每5分钟  
**编码**: UTF-8

```json
{
  "schema_version": "2.0",
  "last_updated": "2026-02-18T08:55:00+08:00",
  "metadata": {
    "system": "Nexus AI Order Management",
    "total_orders": 0,
    "pending_sync": 0,
    "last_sync_time": "2026-02-18T08:50:00+08:00",
    "gmail_account": "qingziyuezi@gmail.com",
    "sync_interval_minutes": 5
  },
  "orders": [OrderObject],
  "sync_log": [SyncEvent]
}
```

### 2.2 Order Object Schema

| 字段 | 类型 | 描述 | 示例 |
|------|------|------|------|
| `order_id` | string | 唯一订单ID (MD12) | "A3F7B9C2D1E4" |
| `gmail_message_id` | string | Gmail消息ID | "18f3a2b4c5d6e7f8" |
| `thread_id` | string | Gmail线程ID | "18f3a2b4c5d6e7f9" |
| **customer** | object | 客户信息 | - |
| `customer.email` | string | 客户邮箱 | "client@company.com" |
| `customer.name` | string | 客户姓名 | "John Smith" |
| `customer.first_contact` | string | 首次联系时间 (ISO8601) | "2026-02-18T08:30:00+08:00" |
| **inquiry** | object | 咨询内容 | - |
| `inquiry.type` | string | 咨询类型 | "project_inquiry" |
| `inquiry.subject` | string | 邮件主题 | "AI Development Project" |
| `inquiry.body_preview` | string | 内容预览 (500字符) | "We need an AI agent..." |
| `inquiry.confidence` | number | AI分类置信度 | 85 |
| **status** | object | 订单状态 | - |
| `status.current` | string | 当前状态 | "new" / "evaluating" / "quoted" / "contract" / "development" / "completed" |
| `status.history` | array | 状态变更历史 | [{"status": "new", "timestamp": "...", "note": "..."}] |
| `priority` | string | 优先级 | "high" / "medium" / "low" |
| **timestamps** | object | 时间戳 | - |
| `timestamps.created` | string | 订单创建时间 | "2026-02-18T08:30:00+08:00" |
| `timestamps.received` | string | 邮件接收时间 | "2026-02-18T08:25:00+08:00" |
| `timestamps.last_updated` | string | 最后更新时间 | "2026-02-18T08:30:00+08:00" |
| `timestamps.first_response_due` | string | 首次回复截止时间 | "2026-02-18T10:30:00+08:00" |
| `tags` | array | 标签 | ["project_inquiry", "high_value"] |
| **assignment** | object | 分配信息 | - |
| `assignment.team` | string | 负责团队 | "sales" / "technical_support" / "business_dev" / "general" |
| `assignment.agent` | string | 分配的Agent | "CEO" / "CTO" / "COO" / null |
| `assignment.assigned_at` | string | 分配时间 | "2026-02-18T08:35:00+08:00" |
| **response** | object | 响应状态 | - |
| `response.auto_replied` | boolean | 是否自动回复 | false |
| `response.reply_template` | string | 使用的模板 | "project_inquiry" |
| `response.manual_reply_required` | boolean | 是否需要人工回复 | true |
| `response.reply_sent_at` | string | 回复发送时间 | null |
| **metadata** | object | 元数据 | - |
| `metadata.source` | string | 数据来源 | "gmail_auto_sync" |
| `metadata.version` | string | 版本 | "3.0" |
| `metadata.sync_batch_id` | string | 同步批次ID | "20260218_085500" |

### 2.3 咨询类型 (inquiry.type)

| 类型 | 描述 | 自动分配团队 | 响应SLA |
|------|------|--------------|---------|
| `project_inquiry` | 项目开发咨询 | sales | 2小时 |
| `price_inquiry` | 报价询问 | sales | 2小时 |
| `support_request` | 技术支持请求 | technical_support | 4小时 |
| `business_opportunity` | 商务合作机会 | business_dev | 4小时 |
| `unknown` | 未分类咨询 | general | 8小时 |

### 2.4 订单状态 (status.current)

```
new → evaluating → quoted → contract → development → monitoring → completed
            ↓
        rejected
```

| 状态 | 描述 | 负责角色 |
|------|------|----------|
| `new` | 新订单，待分配 | COO |
| `evaluating` | 评估中 | CTO + CMO + CFO |
| `quoted` | 已报价 | CFO |
| `contract` | 合同阶段 | CEO + CFO |
| `development` | 开发中 | CTO + 开发团队 |
| `monitoring` | 监控交付 | COO |
| `completed` | 已完成 | COO |
| `rejected` | 已拒绝 | CEO |

---

## 3. API接口

### 3.1 执行同步

```bash
# 执行一次同步
python gmail_sync.py once

# 启动定时服务（每5分钟）
python gmail_sync.py daemon

# 获取仪表板数据
python gmail_sync.py dashboard
```

### 3.2 获取订单数据 (Python)

```python
import json
from pathlib import Path

def load_orders():
    """加载所有订单"""
    orders_file = Path("company_system/data/orders.json")
    with open(orders_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['orders']

def get_pending_orders():
    """获取待处理订单"""
    orders = load_orders()
    return [o for o in orders if o['status']['current'] == 'new']

def get_high_priority_orders():
    """获取高优先级订单"""
    orders = load_orders()
    return [o for o in orders if o['priority'] == 'high' and o['status']['current'] == 'new']

def get_orders_by_type(inquiry_type: str):
    """按类型获取订单"""
    orders = load_orders()
    return [o for o in orders if o['inquiry']['type'] == inquiry_type]

def update_order_status(order_id: str, new_status: str, note: str = ""):
    """更新订单状态"""
    orders_file = Path("company_system/data/orders.json")
    with open(orders_file, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        for order in data['orders']:
            if order['order_id'] == order_id:
                order['status']['current'] = new_status
                order['status']['history'].append({
                    "status": new_status,
                    "timestamp": datetime.now().isoformat(),
                    "note": note
                })
                order['timestamps']['last_updated'] = datetime.now().isoformat()
                break
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()
```

### 3.3 实时监控数据 (JSON)

```bash
$ python gmail_sync.py dashboard
```

输出：
```json
{
  "total_orders": 42,
  "new_today": 5,
  "pending_response": 3,
  "high_priority": 1,
  "by_type": {
    "project_inquiry": 18,
    "price_inquiry": 12,
    "support_request": 7,
    "business_opportunity": 3,
    "unknown": 2
  },
  "last_sync": "2026-02-18T08:55:00+08:00"
}
```

---

## 4. 数据流时序

```
时间轴: 0min    5min    10min   15min   20min   25min   30min
         │       │       │       │       │       │       │
Gmail    │   ◆   │   ◆   │   ◆   │   ◆   │   ◆   │   ◆   │  ◆
收到邮件 │       │       │       │       │       │       │
         │       │       │       │       │       │       │
Sync     │   ◆   │   ◆   │   ◆   │   ◆   │   ◆   │   ◆   │  ◆
每5分钟  │       │       │       │       │       │       │
         │       │       │       │       │       │       │
Monitor  │   ◆   │   ◆   │   ◆   │   ◆   │   ◆   │   ◆   │  ◆
实时更新 │       │       │       │       │       │       │
         │       │       │       │       │       │       │
最大延迟: ◄─────── 5分钟 ───────►
```

---

## 5. 技术实现

### 5.1 核心模块

| 文件 | 功能 | 依赖 |
|------|------|------|
| `gmail_sync.py` | 主同步脚本 | Python 3.8+, gog CLI |
| `sync_cron.sh` | 定时任务脚本 | bash, cron |
| `orders.json` | 数据存储 | JSON, UTF-8 |

### 5.2 邮件过滤逻辑

```python
# 1. 验证码检测
if is_verification_code(subject, body, from_email):
    return FILTERED

# 2. 垃圾邮件检测
if is_spam(subject, body, from_email):
    return FILTERED

# 3. 业务分类
email_type = classify_business_type(text)
confidence = calculate_confidence_score(text, email_type)

# 4. 优先级判定
priority = assign_priority(email_type, confidence)

# 5. 创建订单
order = create_order(email_data, email_type, priority)
```

### 5.3 并发控制

- **文件锁**: 使用 `.sync_lock` 文件防止并发写入
- **超时机制**: 单次同步最大30秒
- **PID管理**: Cron任务使用PID文件防止重复执行

---

## 6. 监控与告警

### 6.1 日志文件

| 日志 | 路径 | 保留策略 |
|------|------|----------|
| 同步日志 | `logs/gmail_sync.log` | 7天轮转 |
| Cron日志 | `logs/cron_sync.log` | 7天轮转 |
| 订单历史 | `orders.json:sync_log` | 最近100条 |

### 6.2 关键指标

```json
{
  "sync_latency_seconds": 15,
  "emails_per_sync": 12,
  "conversion_rate": 0.65,
  "avg_confidence": 78,
  "error_rate": 0.02
}
```

---

## 7. 部署指南

### 7.1 添加到Crontab

```bash
# 编辑crontab
crontab -e

# 添加每5分钟执行
*/5 * * * * /Users/yueqingsong/.openclaw/workspace/company_system/sync_cron.sh

# 查看cron日志
tail -f /Users/yueqingsong/.openclaw/workspace/company_system/logs/cron_sync.log
```

### 7.2 手动启动守护进程

```bash
cd /Users/yueqingsong/.openclaw/workspace/company_system
python3 gmail_sync.py daemon
```

### 7.3 验证部署

```bash
# 检查定时任务
crontab -l | grep sync_cron

# 检查日志
tail -20 logs/cron_sync.log

# 检查订单数据
python3 gmail_sync.py dashboard
```

---

## 8. 集成建议

### 8.1 与监控系统集成

```python
# monitor.py 添加以下代码
def load_orders_for_display():
    data = load_orders()
    return {
        "orders": data['orders'][:10],  # 最近10条
        "stats": get_dashboard_data(),
        "last_sync": data['metadata']['last_sync_time']
    }
```

### 8.2 与Agent系统集成

```python
# 在 full_company_system.py 中添加
from gmail_sync import load_orders, get_high_priority_orders

class CompanySystem:
    def check_new_orders(self):
        """CEO/CFO/CTO等Agent调用"""
        high_priority = get_high_priority_orders()
        if high_priority:
            self.notify_agents("NEW_HIGH_PRIORITY_ORDERS", high_priority)
```

---

## 9. 注意事项

1. **数据一致性**: 所有写入必须通过 `gmail_sync.py`，避免直接修改 `orders.json`
2. **备份策略**: 建议每日备份 `orders.json` 到版本控制或云存储
3. **隐私保护**: 订单数据包含客户邮箱，注意访问权限控制
4. **性能优化**: 当订单数 > 1000时，考虑分页加载

---

## 10. 联系方式

- **数据层负责人**: Emma (COO)
- **技术对接**: David (CTO) - 请确认此文档
- **业务需求**: Michael (CPO) - 确认展示需求

---

**下次评审**: 2026-02-25  
**文档状态**: ✅ 初版完成，待审核
