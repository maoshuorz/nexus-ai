#!/usr/bin/env python3
"""
Nexus AI - Gmail自动接单系统
使用gog skill监控邮箱，自动处理客户咨询
"""

import subprocess
import json
import re
import time
from datetime import datetime
from pathlib import Path

# 配置
GMAIL_ACCOUNT = "qingziyuezi@gmail.com"
LOG_FILE = Path.home() / ".openclaw/workspace/company_system/logs/gmail_orders.log"
ORDERS_FILE = Path.home() / ".openclaw/workspace/company_system/data/orders.json"

def log(message):
    """记录日志"""
    timestamp = datetime.now().isoformat()
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")

def run_gog_command(command):
    """运行gog命令"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def check_new_emails():
    """检查新邮件"""
    log("🔍 检查新邮件...")
    
    # 使用gog搜索最近1小时的邮件
    command = f'gog gmail messages search "in:inbox newer_than:1h" --account {GMAIL_ACCOUNT} --json'
    stdout, stderr, code = run_gog_command(command)
    
    if code != 0:
        log(f"❌ 检查邮件失败: {stderr}")
        return []
    
    try:
        emails = json.loads(stdout) if stdout else []
        log(f"✅ 发现 {len(emails)} 封新邮件")
        return emails
    except:
        log("⚠️  解析邮件失败")
        return []

def analyze_email(email):
    """分析邮件内容，提取关键信息"""
    subject = email.get('subject', '')
    body = email.get('body', '')
    from_email = email.get('from', '')
    
    # 分析邮件类型
    email_type = "unknown"
    
    # 项目咨询关键词
    project_keywords = ['开发', '项目', '咨询', 'quote', 'project', 'development', 'build', 'create']
    if any(kw in subject.lower() or kw in body.lower() for kw in project_keywords):
        email_type = "project_inquiry"
    
    # 报价询问
    price_keywords = ['价格', '报价', '多少钱', 'price', 'cost', 'budget', 'quote']
    if any(kw in subject.lower() or kw in body.lower() for kw in price_keywords):
        email_type = "price_inquiry"
    
    # 技术支持
    support_keywords = ['问题', '帮助', '支持', 'help', 'support', 'issue', 'bug']
    if any(kw in subject.lower() or kw in body.lower() for kw in support_keywords):
        email_type = "support"
    
    # 垃圾邮件过滤
    spam_keywords = ['广告', '促销', 'spam', 'unsubscribe', 'promotion', 'sale']
    if any(kw in subject.lower() for kw in spam_keywords):
        email_type = "spam"
    
    return {
        "type": email_type,
        "subject": subject,
        "from": from_email,
        "body_preview": body[:200] if body else "",
        "timestamp": email.get('date', ''),
        "message_id": email.get('id', '')
    }

def generate_response(email_analysis):
    """生成自动回复"""
    email_type = email_analysis['type']
    
    responses = {
        "project_inquiry": {
            "subject": "Re: {original_subject} - 感谢您的咨询 | Thank you for your inquiry",
            "body": """您好 / Hello,

感谢您联系Nexus AI！我们已收到您的项目咨询。

Thank you for contacting Nexus AI! We have received your project inquiry.

我们的团队正在分析您的需求，将在1小时内提供：
Our team is analyzing your requirements and will provide within 1 hour:
- 详细的项目评估 / Detailed project assessment
- 透明的报价方案 / Transparent pricing
- 预计交付时间 / Estimated delivery timeline

服务价格参考 / Service Pricing:
• AI Agent系统开发: $2,000起 / AI Agent Development: from $2,000
• 工作流自动化: $1,000起 / Workflow Automation: from $1,000
• 技术咨询: $50/小时 / Technical Consulting: $50/hour

期待与您合作！
Looking forward to working with you!

---
Nexus AI Technologies
6 AI Agents Autonomous Development
🌐 https://maoshuorz.github.io/nexus-ai/
🐦 @y36764qing
"""
        },
        "price_inquiry": {
            "subject": "Re: {original_subject} - 报价信息 | Quote Information",
            "body": """您好 / Hello,

感谢您对Nexus AI的关注！

Thank you for your interest in Nexus AI!

我们的标准服务报价 / Our Standard Service Pricing:

🤖 AI Agent系统开发 / AI Agent System Development
   价格: $2,000 - $8,000
   周期: 2-4周 / Timeline: 2-4 weeks

⚙️ 工作流自动化 / Workflow Automation  
   价格: $1,000 - $4,000
   周期: 1-2周 / Timeline: 1-2 weeks

💡 技术咨询 / Technical Consulting
   价格: $50/小时 / $50 per hour

🚀 快速定制脚本 / Quick Custom Scripts
   价格: $200 - $500
   周期: 1-3天 / Timeline: 1-3 days

如需详细报价，请告诉我们：
For a detailed quote, please let us know:
1. 项目具体需求 / Specific requirements
2. 预算范围 / Budget range
3. 期望交付时间 / Expected delivery time

---
Nexus AI Technologies
🌐 https://maoshuorz.github.io/nexus-ai/
"""
        },
        "support": {
            "subject": "Re: {original_subject} - 技术支持 | Technical Support",
            "body": """您好 / Hello,

感谢您联系Nexus AI技术支持！

Thank you for contacting Nexus AI Technical Support!

我们已收到您的技术问题，CTO (David) 将在2小时内回复您。

We have received your technical issue. Our CTO (David) will respond within 2 hours.

同时，您可以查看我们的开源资源：
Meanwhile, you can check our open source resources:
📁 GitHub: https://github.com/maoshuorz/nexus-ai

---
Nexus AI Technical Support
"""
        },
        "unknown": {
            "subject": "Re: {original_subject} - 收到您的邮件 | Email Received",
            "body": """您好 / Hello,

感谢联系Nexus AI！

Thank you for contacting Nexus AI!

我们已收到您的邮件，COO (Emma) 将在1小时内回复您。

We have received your email. Our COO (Emma) will respond within 1 hour.

如有紧急需求，请通过Twitter联系我们：
For urgent needs, please contact us via Twitter:
🐦 @y36764qing

---
Nexus AI Technologies
🌐 https://maoshuorz.github.io/nexus-ai/
"""
        }
    }
    
    return responses.get(email_type, responses["unknown"])

def send_reply(email_analysis, response_template):
    """发送自动回复"""
    to_email = email_analysis['from']
    original_subject = email_analysis['subject']
    
    subject = response_template['subject'].format(original_subject=original_subject)
    body = response_template['body']
    
    # 使用gog发送邮件
    command = f'''gog gmail send \
        --to "{to_email}" \
        --subject "{subject}" \
        --body "{body}" \
        --account {GMAIL_ACCOUNT}'''
    
    # 实际发送 (注释掉以防误发)
    # stdout, stderr, code = run_gog_command(command)
    
    log(f"📤 准备回复邮件给: {to_email}")
    log(f"   主题: {subject}")
    log(f"   类型: {email_analysis['type']}")
    
    return True

def save_order(email_analysis):
    """保存订单信息"""
    ORDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    orders = []
    if ORDERS_FILE.exists():
        with open(ORDERS_FILE) as f:
            orders = json.load(f)
    
    order = {
        "id": len(orders) + 1,
        "timestamp": datetime.now().isoformat(),
        "status": "new",
        **email_analysis
    }
    
    orders.append(order)
    
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f, indent=2)
    
    log(f"💾 订单已保存: #{order['id']}")
    return order

def main():
    """主函数"""
    log("=" * 50)
    log("🚀 Nexus AI Gmail自动接单系统启动")
    log("=" * 50)
    
    # 检查新邮件
    emails = check_new_emails()
    
    for email in emails:
        # 分析邮件
        analysis = analyze_email(email)
        
        if analysis['type'] == 'spam':
            log(f"🗑️  跳过垃圾邮件: {analysis['subject']}")
            continue
        
        # 保存订单
        save_order(analysis)
        
        # 生成回复
        response = generate_response(analysis)
        
        # 发送回复
        send_reply(analysis, response)
        
        log("-" * 50)
    
    log(f"✅ 处理完成，共处理 {len(emails)} 封邮件")
    log("=" * 50)

if __name__ == "__main__":
    main()
