#!/usr/bin/env python3
"""
Nexus AI - 订单数据同步系统 v3.0 (COO Emma)
功能：Gmail自动接单 + 数据同步 + 5分钟定时检查
"""

import subprocess
import json
import re
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# === 配置 ===
GMAIL_ACCOUNT = "qingziyuezi@gmail.com"
BASE_DIR = Path.home() / ".openclaw/workspace/company_system"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
ORDERS_FILE = DATA_DIR / "orders.json"
LOG_FILE = LOG_DIR / "gmail_sync.log"
LOCK_FILE = DATA_DIR / ".sync_lock"

# 确保目录存在
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# === 日志系统 ===
def log(message: str, level: str = "INFO"):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] [{level}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def log_sync_event(event_type: str, details: Dict):
    """记录同步事件到orders.json"""
    try:
        data = load_orders()
        sync_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        if "sync_log" not in data:
            data["sync_log"] = []
        data["sync_log"].append(sync_entry)
        # 只保留最近100条日志
        data["sync_log"] = data["sync_log"][-100:]
        save_orders(data)
    except Exception as e:
        log(f"记录同步事件失败: {e}", "ERROR")

# === 订单数据管理 ===
def load_orders() -> Dict:
    """加载订单数据"""
    if ORDERS_FILE.exists():
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"加载orders.json失败: {e}", "ERROR")
    return {
        "schema_version": "2.0",
        "last_updated": datetime.now().isoformat(),
        "metadata": {
            "system": "Nexus AI Order Management",
            "total_orders": 0,
            "pending_sync": 0,
            "last_sync_time": None,
            "gmail_account": GMAIL_ACCOUNT,
            "sync_interval_minutes": 5
        },
        "orders": [],
        "sync_log": []
    }

def save_orders(data: Dict):
    """保存订单数据"""
    data["last_updated"] = datetime.now().isoformat()
    data["metadata"]["total_orders"] = len(data.get("orders", []))
    with open(ORDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def generate_order_id(email_data: Dict) -> str:
    """生成唯一订单ID"""
    content = f"{email_data.get('from', '')}_{email_data.get('subject', '')}_{email_data.get('date', '')}"
    return hashlib.md5(content.encode()).hexdigest()[:12].upper()

# === Gmail命令执行 ===
def run_gog_command(command: str, timeout: int = 30) -> tuple:
    """执行gog命令"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def fetch_recent_emails(minutes: int = 10) -> List[Dict]:
    """获取最近N分钟的邮件"""
    log(f"📧 获取最近{minutes}分钟的邮件...")
    
    # 使用 newer_than 查询（以小时为单位，向上取整）
    hours = max(1, (minutes + 59) // 60)
    command = f'gog gmail messages search "in:inbox newer_than:{hours}h" --account {GMAIL_ACCOUNT} --json'
    
    stdout, stderr, code = run_gog_command(command)
    
    if code != 0:
        log(f"❌ 获取邮件失败: {stderr}", "ERROR")
        return []
    
    try:
        emails = json.loads(stdout) if stdout else []
        # 过滤出指定时间范围内的邮件
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_emails = []
        
        for email in emails:
            if isinstance(email, dict):
                email_date = email.get('date', '')
                try:
                    # 尝试解析邮件日期
                    from email.utils import parsedate_to_datetime
                    parsed_date = parsedate_to_datetime(email_date)
                    if parsed_date >= cutoff_time:
                        recent_emails.append(email)
                except:
                    # 如果无法解析日期，默认包含
                    recent_emails.append(email)
        
        log(f"✅ 发现 {len(recent_emails)} 封新邮件")
        return recent_emails
    except Exception as e:
        log(f"❌ 解析邮件失败: {e}", "ERROR")
        return []

# === 邮件分析引擎 ===
class EmailAnalyzer:
    """邮件分析器"""
    
    # 验证码关键词
    VERIFICATION_KEYWORDS = [
        '验证码', 'verification code', '确认码', 'confirmation code',
        '安全码', 'security code', '授权码', 'auth code',
        '一次性密码', 'one-time password', 'otp', 'pin',
        '登录验证', 'login verification', '2fa', 'two-factor',
        '密匙', '密钥', 'access code', 'activation code'
    ]
    
    # 验证码发送者
    VERIFICATION_SENDERS = [
        'noreply', 'no-reply', 'verify', 'verification',
        'security', 'secure', 'login', 'signin', 'signup',
        'account', 'auth', '2fa', 'otp'
    ]
    
    # 垃圾邮件关键词
    SPAM_KEYWORDS = [
        '广告', '促销', '优惠', '打折', 'sale', 'discount', 'promotion',
        '订阅', 'unsubscribe', '取消订阅', 'newsletter',
        '免费试用', 'free trial', '限时', 'limited time',
        '点击这里', 'click here', '立即购买', 'buy now',
        '赚钱', 'make money', '赚钱机会', 'investment opportunity',
        '贷款', 'loan', 'credit card', '信用卡', '保险', 'insurance'
    ]
    
    # 业务类型关键词
    PROJECT_KEYWORDS = ['开发', '项目', '咨询', 'project', 'development', 'build', 'create', 'app', 'website', 'system', '平台', '定制', 'custom', 'software']
    PRICE_KEYWORDS = ['价格', '报价', '多少钱', 'price', 'cost', 'budget', 'quote', '费用', '收费', '定价', 'how much']
    SUPPORT_KEYWORDS = ['问题', '帮助', '支持', 'help', 'support', 'issue', 'bug', 'error', 'fix', 'repair', '维护', 'troubleshoot']
    BUSINESS_KEYWORDS = ['合作', '商务', 'business', 'partnership', 'collaboration', 'opportunity', 'contract', 'reseller', 'distributor']
    
    @classmethod
    def is_verification_code(cls, subject: str, body: str, from_email: str) -> bool:
        """检测是否为验证码邮件"""
        text = (subject + ' ' + body).lower()
        
        # 检查关键词
        for keyword in cls.VERIFICATION_KEYWORDS:
            if keyword.lower() in text:
                return True
        
        # 检查发送者
        sender_lower = from_email.lower()
        for sender in cls.VERIFICATION_SENDERS:
            if sender in sender_lower and any(kw in text for kw in ['code', 'verify', 'login', 'sign']):
                return True
        
        # 检查4-8位数字（常见验证码格式）
        if re.search(r'\b\d{4,8}\b', body) and any(kw in text for kw in ['code', 'verify', 'enter', 'input', '验证']):
            return True
        
        return False
    
    @classmethod
    def is_spam(cls, subject: str, body: str, from_email: str) -> bool:
        """检测垃圾邮件"""
        text = (subject + ' ' + body).lower()
        score = sum(1 for kw in cls.SPAM_KEYWORDS if kw.lower() in text)
        return score >= 3
    
    @classmethod
    def analyze(cls, email: Dict) -> Dict:
        """分析邮件类型和优先级"""
        if not isinstance(email, dict):
            return {"type": "invalid", "priority": "low", "should_process": False}
        
        subject = email.get('subject', '')
        body = email.get('body', '')
        from_email = email.get('from', '')
        
        # 过滤验证码
        if cls.is_verification_code(subject, body, from_email):
            return {"type": "verification_code", "priority": "low", "should_process": False}
        
        # 过滤垃圾邮件
        if cls.is_spam(subject, body, from_email):
            return {"type": "spam", "priority": "low", "should_process": False}
        
        text = (subject + ' ' + body).lower()
        
        # 分析业务类型
        email_type = "unknown"
        confidence = 0
        priority = "medium"
        
        # 项目咨询
        project_score = sum(1 for kw in cls.PROJECT_KEYWORDS if kw in text)
        if project_score >= 2:
            email_type = "project_inquiry"
            confidence = min(project_score * 15, 100)
            priority = "high"
        
        # 报价询问
        price_score = sum(1 for kw in cls.PRICE_KEYWORDS if kw in text)
        if price_score >= 1 and email_type == "unknown":
            email_type = "price_inquiry"
            confidence = min(price_score * 25, 100)
            priority = "high"
        
        # 技术支持
        support_score = sum(1 for kw in cls.SUPPORT_KEYWORDS if kw in text)
        if support_score >= 2 and email_type == "unknown":
            email_type = "support_request"
            confidence = min(support_score * 20, 100)
            priority = "medium"
        
        # 商务合作
        business_score = sum(1 for kw in cls.BUSINESS_KEYWORDS if kw in text)
        if business_score >= 1 and email_type == "unknown":
            email_type = "business_opportunity"
            confidence = min(business_score * 30, 100)
            priority = "high"
        
        return {
            "type": email_type,
            "priority": priority,
            "confidence": confidence,
            "should_process": confidence >= 30,
            "subject": subject,
            "from": from_email,
            "body_preview": body[:500] if body else "",
            "full_body": body,
            "timestamp": email.get('date', datetime.now().isoformat()),
            "gmail_message_id": email.get('id', ''),
            "thread_id": email.get('threadId', '')
        }

# === 订单处理 ===
def create_order(email_analysis: Dict) -> Dict:
    """创建标准化订单"""
    order_id = generate_order_id(email_analysis)
    
    order = {
        "order_id": order_id,
        "gmail_message_id": email_analysis.get("gmail_message_id", ""),
        "thread_id": email_analysis.get("thread_id", ""),
        
        # 客户信息
        "customer": {
            "email": email_analysis.get("from", ""),
            "name": extract_name_from_email(email_analysis.get("from", "")),
            "first_contact": datetime.now().isoformat()
        },
        
        # 订单内容
        "inquiry": {
            "type": email_analysis.get("type", "unknown"),
            "subject": email_analysis.get("subject", ""),
            "body_preview": email_analysis.get("body_preview", ""),
            "confidence": email_analysis.get("confidence", 0)
        },
        
        # 状态追踪
        "status": {
            "current": "new",
            "history": [
                {
                    "status": "new",
                    "timestamp": datetime.now().isoformat(),
                    "note": "从Gmail自动同步"
                }
            ]
        },
        
        # 优先级
        "priority": email_analysis.get("priority", "medium"),
        
        # 时间戳
        "timestamps": {
            "created": datetime.now().isoformat(),
            "received": email_analysis.get("timestamp", datetime.now().isoformat()),
            "last_updated": datetime.now().isoformat(),
            "first_response_due": (datetime.now() + timedelta(hours=2)).isoformat()
        },
        
        # 标签
        "tags": [email_analysis.get("type", "unknown")],
        
        # 分配
        "assignment": {
            "team": determine_team(email_analysis.get("type", "unknown")),
            "agent": None,
            "assigned_at": None
        },
        
        # 响应状态
        "response": {
            "auto_replied": False,
            "reply_template": None,
            "manual_reply_required": True,
            "reply_sent_at": None
        },
        
        # 元数据
        "metadata": {
            "source": "gmail_auto_sync",
            "version": "3.0",
            "sync_batch_id": datetime.now().strftime("%Y%m%d_%H%M%S")
        }
    }
    
    return order

def extract_name_from_email(email: str) -> str:
    """从邮箱地址提取姓名"""
    if '<' in email and '>' in email:
        name_part = email.split('<')[0].strip()
        if name_part:
            return name_part.strip('"')
    return email.split('@')[0] if '@' in email else email

def determine_team(inquiry_type: str) -> str:
    """根据咨询类型确定负责团队"""
    team_map = {
        "project_inquiry": "sales",
        "price_inquiry": "sales",
        "support_request": "technical_support",
        "business_opportunity": "business_dev",
        "unknown": "general"
    }
    return team_map.get(inquiry_type, "general")

def order_exists(order_id: str, existing_orders: List[Dict]) -> bool:
    """检查订单是否已存在"""
    return any(o.get("order_id") == order_id or o.get("gmail_message_id") == order_id for o in existing_orders)

# === 主同步流程 ===
def sync_gmail_to_orders():
    """主同步函数"""
    log("=" * 70)
    log("🚀 Nexus AI 订单同步系统 v3.0 - 开始同步")
    log("=" * 70)
    
    # 检查锁（防止并发）
    if LOCK_FILE.exists():
        lock_time = datetime.fromtimestamp(LOCK_FILE.stat().st_mtime)
        if datetime.now() - lock_time < timedelta(minutes=5):
            log("⚠️ 同步正在进行中，跳过本次执行")
            return
    
    # 创建锁文件
    LOCK_FILE.touch()
    
    try:
        # 加载现有订单
        data = load_orders()
        existing_orders = data.get("orders", [])
        initial_count = len(existing_orders)
        
        # 获取新邮件
        emails = fetch_recent_emails(minutes=10)  # 检查最近10分钟（覆盖5分钟间隔）
        
        stats = {
            "total_emails": len(emails),
            "filtered": 0,
            "processed": 0,
            "new_orders": 0,
            "skipped": 0
        }
        
        for email in emails:
            # 分析邮件
            analysis = EmailAnalyzer.analyze(email)
            
            if not analysis["should_process"]:
                stats["filtered"] += 1
                log(f"🗑️  过滤: {analysis['type']} | {analysis.get('subject', '')[:50]}...")
                continue
            
            # 生成订单ID
            order_id = generate_order_id(analysis)
            
            # 检查是否已存在
            if order_exists(analysis.get("gmail_message_id", ""), existing_orders) or \
               order_exists(order_id, existing_orders):
                stats["skipped"] += 1
                log(f"⏭️  跳过已存在: {analysis['type']} | {analysis.get('subject', '')[:50]}...")
                continue
            
            # 创建新订单
            order = create_order(analysis)
            existing_orders.append(order)
            stats["new_orders"] += 1
            stats["processed"] += 1
            
            log(f"✅ 新订单: #{order['order_id']} | 类型: {order['inquiry']['type']} | 优先级: {order['priority']}")
            
            # 高优先级订单额外标记
            if order['priority'] == 'high':
                log(f"🔴 高优先级订单需要立即处理: {order['order_id']}")
        
        # 更新数据
        data["orders"] = existing_orders
        data["metadata"]["last_sync_time"] = datetime.now().isoformat()
        data["metadata"]["pending_sync"] = 0
        save_orders(data)
        
        # 记录同步事件
        log_sync_event("sync_completed", {
            "emails_checked": stats["total_emails"],
            "filtered": stats["filtered"],
            "processed": stats["processed"],
            "new_orders": stats["new_orders"],
            "total_orders": len(existing_orders)
        })
        
        log("-" * 70)
        log(f"📊 同步完成: 检查{stats['total_emails']}封邮件 | 过滤{stats['filtered']} | 新增{stats['new_orders']}订单")
        log(f"📁 总订单数: {len(existing_orders)} | 数据文件: {ORDERS_FILE}")
        log("=" * 70)
        
    except Exception as e:
        log(f"❌ 同步失败: {e}", "ERROR")
        log_sync_event("sync_failed", {"error": str(e)})
    finally:
        # 删除锁文件
        if LOCK_FILE.exists():
            LOCK_FILE.unlink()

def get_dashboard_data() -> Dict:
    """获取仪表板数据（供监控使用）"""
    data = load_orders()
    orders = data.get("orders", [])
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return {
        "total_orders": len(orders),
        "new_today": len([o for o in orders if datetime.fromisoformat(o['timestamps']['created']) >= today_start]),
        "pending_response": len([o for o in orders if o['status']['current'] == 'new']),
        "high_priority": len([o for o in orders if o['priority'] == 'high' and o['status']['current'] == 'new']),
        "by_type": {
            "project_inquiry": len([o for o in orders if o['inquiry']['type'] == 'project_inquiry']),
            "price_inquiry": len([o for o in orders if o['inquiry']['type'] == 'price_inquiry']),
            "support_request": len([o for o in orders if o['inquiry']['type'] == 'support_request']),
            "business_opportunity": len([o for o in orders if o['inquiry']['type'] == 'business_opportunity']),
            "unknown": len([o for o in orders if o['inquiry']['type'] == 'unknown'])
        },
        "last_sync": data.get("metadata", {}).get("last_sync_time")
    }

# === 定时任务模式 ===
def run_scheduler():
    """运行定时同步（每5分钟）"""
    log("🕐 启动定时同步服务（每5分钟）")
    log("按 Ctrl+C 停止")
    
    try:
        while True:
            sync_gmail_to_orders()
            log("💤 等待5分钟...")
            time.sleep(300)  # 5分钟 = 300秒
    except KeyboardInterrupt:
        log("👋 定时服务已停止")

# === CLI入口 ===
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "daemon":
            run_scheduler()
        elif cmd == "dashboard":
            print(json.dumps(get_dashboard_data(), indent=2))
        elif cmd == "once":
            sync_gmail_to_orders()
        else:
            print("用法: python gmail_sync.py [daemon|once|dashboard]")
            print("  daemon   - 启动定时服务（每5分钟）")
            print("  once     - 执行一次同步")
            print("  dashboard - 显示仪表板数据")
    else:
        sync_gmail_to_orders()
