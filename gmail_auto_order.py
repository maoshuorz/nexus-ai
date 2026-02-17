#!/usr/bin/env python3
"""
Nexus AI - 智能邮件过滤系统 v2.0
过滤验证码/垃圾邮件，只处理业务咨询
"""

import subprocess
import json
import re
from datetime import datetime
from pathlib import Path

GMAIL_ACCOUNT = "qingziyuezi@gmail.com"
LOG_FILE = Path.home() / ".openclaw/workspace/company_system/logs/gmail_orders.log"
ORDERS_FILE = Path.home() / ".openclaw/workspace/company_system/data/orders.json"

def log(message):
    timestamp = datetime.now().isoformat()
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(log_msg + "\n")

def run_gog_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def is_verification_code_email(subject, body, from_email):
    """检测是否为验证码邮件"""
    verification_keywords = [
        '验证码', 'verification code', '确认码', 'confirmation code',
        '安全码', 'security code', '授权码', 'auth code',
        '一次性密码', 'one-time password', 'otp', 'pin',
        '登录验证', 'login verification', '2fa', 'two-factor',
        '密匙', '密钥', 'access code', 'activation code'
    ]
    
    # 检查主题和内容
    text_to_check = (subject + ' ' + body).lower()
    
    for keyword in verification_keywords:
        if keyword.lower() in text_to_check:
            return True
    
    # 检查常见验证码发送者
    verification_senders = [
        'noreply', 'no-reply', 'verify', 'verification',
        'security', 'secure', 'login', 'signin', 'signup',
        'account', 'auth', '2fa', 'otp', 'steam',
        'github', 'gitlab', 'google', 'microsoft', 'apple',
        'amazon', 'facebook', 'twitter', 'discord', 'slack'
    ]
    
    sender_lower = from_email.lower()
    for sender in verification_senders:
        if sender in sender_lower and any(kw in text_to_check for kw in ['code', 'verify', 'login', 'sign']):
            return True
    
    # 检查6位数字（常见验证码格式）
    if re.search(r'\b\d{4,8}\b', body) and any(kw in text_to_check for kw in ['code', 'verify', 'enter', 'input']):
        return True
    
    return False

def is_spam_email(subject, body, from_email):
    """检测垃圾邮件"""
    spam_keywords = [
        '广告', '促销', '优惠', '打折', 'sale', 'discount', 'promotion',
        '订阅', 'unsubscribe', '取消订阅', '邮件列表', 'newsletter',
        '免费试用', 'free trial', '限时', 'limited time',
        '点击这里', 'click here', '立即购买', 'buy now',
        '赚钱', 'make money', '赚钱机会', 'investment opportunity',
        '贷款', 'loan', 'credit card', '信用卡', '保险', 'insurance'
    ]
    
    text_to_check = (subject + ' ' + body).lower()
    
    spam_score = 0
    for keyword in spam_keywords:
        if keyword.lower() in text_to_check:
            spam_score += 1
    
    # 如果有3个以上垃圾关键词，判定为垃圾邮件
    return spam_score >= 3

def analyze_email(email):
    """分析邮件内容"""
    if isinstance(email, str):
        return {"type": "invalid", "should_reply": False}
    
    subject = email.get('subject', '')
    body = email.get('body', '')
    from_email = email.get('from', '')
    
    # 首先过滤验证码邮件
    if is_verification_code_email(subject, body, from_email):
        log(f"🗑️  过滤验证码邮件: {subject[:50]}")
        return {"type": "verification_code", "should_reply": False}
    
    # 过滤垃圾邮件
    if is_spam_email(subject, body, from_email):
        log(f"🗑️  过滤垃圾邮件: {subject[:50]}")
        return {"type": "spam", "should_reply": False}
    
    # 分析业务类型
    email_type = "unknown"
    confidence = 0
    
    # 项目咨询（高优先级）
    project_keywords = ['开发', '项目', '咨询', 'project', 'development', 'build', 'create', 'app', 'website', 'system', '平台', '定制', 'custom']
    project_score = sum(1 for kw in project_keywords if kw in subject.lower() or kw in body.lower())
    if project_score >= 2:
        email_type = "project_inquiry"
        confidence = min(project_score * 20, 100)
    
    # 报价询问
    price_keywords = ['价格', '报价', '多少钱', 'price', 'cost', 'budget', 'quote', '费用', '收费', '定价']
    price_score = sum(1 for kw in price_keywords if kw in subject.lower() or kw in body.lower())
    if price_score >= 1:
        if email_type == "unknown":
            email_type = "price_inquiry"
        confidence = max(confidence, min(price_score * 30, 100))
    
    # 技术支持
    support_keywords = ['问题', '帮助', '支持', 'help', 'support', 'issue', 'bug', 'error', 'fix', 'repair', '维护']
    support_score = sum(1 for kw in support_keywords if kw in subject.lower() or kw in body.lower())
    if support_score >= 2 and email_type == "unknown":
        email_type = "support"
        confidence = min(support_score * 25, 100)
    
    # 合作/商务
    business_keywords = ['合作', '商务', 'business', 'partnership', 'collaboration', 'opportunity', 'contract']
    business_score = sum(1 for kw in business_keywords if kw in subject.lower() or kw in body.lower())
    if business_score >= 1 and email_type == "unknown":
        email_type = "business_opportunity"
        confidence = min(business_score * 35, 100)
    
    return {
        "type": email_type,
        "confidence": confidence,
        "should_reply": email_type != "unknown" and confidence >= 40,
        "subject": subject,
        "from": from_email,
        "body_preview": body[:300] if body else "",
        "timestamp": email.get('date', ''),
        "message_id": email.get('id', '')
    }

def generate_response(email_analysis):
    """生成专业回复"""
    email_type = email_analysis['type']
    
    templates = {
        "project_inquiry": {
            "subject": "Re: Project Inquiry - Nexus AI Response [Action Required]",
            "body": """Dear Valued Client,

Thank you for reaching out to Nexus AI regarding your project requirements. We have received your inquiry and our team is excited to learn more about your vision.

🎯 NEXT STEPS:
To provide you with an accurate quote and timeline, please reply with:

1. PROJECT OVERVIEW
   - What type of project do you need? (AI Agent system / Workflow automation / Custom development)
   - Brief description of core functionality

2. TECHNICAL REQUIREMENTS
   - Preferred technology stack (if any)
   - Integration requirements
   - Expected user scale

3. TIMELINE & BUDGET
   - Desired launch date
   - Budget range (USD)

4. REFERENCE MATERIALS
   - Similar products/services you like
   - Any existing documentation

⏱️ RESPONSE TIME: Our team will review and respond within 1-2 business hours.

💼 PRICING REFERENCE:
• AI Agent System Development: From $2,000
• Workflow Automation: From $1,000
• Technical Consulting: $50/hour

We look forward to collaborating with you!

Best regards,
Nexus AI Business Team
Emma (COO) & Alex (CEO)

---
🌐 Website: https://maoshuorz.github.io/nexus-ai/
🐦 Twitter: @y36764qing
📧 Business: qingziyuezi@gmail.com
"""
        },
        "price_inquiry": {
            "subject": "Re: Pricing Inquiry - Nexus AI Service Rates",
            "body": """Dear Client,

Thank you for your interest in Nexus AI services. Here is our transparent pricing structure:

💰 SERVICE PRICING:

🤖 AI AGENT SYSTEM DEVELOPMENT
   Starting from: $2,000 USD
   Timeline: 2-4 weeks
   Includes: Multi-agent architecture, API integration, testing & deployment

⚙️ WORKFLOW AUTOMATION
   Starting from: $1,000 USD
   Timeline: 1-2 weeks
   Includes: Process analysis, automation setup, documentation

💡 TECHNICAL CONSULTING
   Rate: $50/hour USD
   Minimum: 2 hours
   Includes: Architecture review, technology selection, implementation guidance

🚀 RAPID PROTOTYPING
   Starting from: $500 USD
   Timeline: 3-7 days
   Perfect for: MVPs, proof-of-concept, demo systems

📋 CUSTOM ENTERPRISE SOLUTIONS
   Pricing: Project-based
   Contact us for detailed quote

🎯 TO GET A CUSTOM QUOTE:
Please provide:
1. Project description
2. Technical requirements
3. Timeline expectations
4. Budget range

We will analyze your needs and respond within 1 hour with a detailed proposal.

Best regards,
Nexus AI Team
Lisa (CFO) & Emma (COO)

---
🌐 https://maoshuorz.github.io/nexus-ai/
📧 qingziyuezi@gmail.com
"""
        },
        "support": {
            "subject": "Re: Technical Support - Nexus AI Assistance",
            "body": """Hello,

Thank you for contacting Nexus AI Technical Support. We have received your inquiry and assigned it to our engineering team.

🎫 TICKET INFORMATION:
• Status: Under Review
• Priority: Standard
• Estimated Response: Within 2 hours

🔧 TO HELP US ASSIST YOU BETTER:
Please provide the following details (if applicable):

1. ERROR DETAILS
   - Error messages or screenshots
   - When did the issue start?
   - Steps to reproduce

2. ENVIRONMENT
   - Operating system
   - Browser/version (if web-related)
   - Relevant software versions

3. IMPACT
   - How many users affected?
   - Business impact level
   - Workarounds attempted

📞 URGENT ISSUES?
For critical production issues, please:
• Mark email subject with [URGENT]
• Include your phone number
• Our CTO (David) will prioritize

🔍 RESOURCES:
While waiting, you may find helpful information:
• Documentation: https://maoshuorz.github.io/nexus-ai/
• GitHub: https://github.com/maoshuorz/nexus-ai
• FAQ: Check our website

We are committed to resolving your issue promptly.

Best regards,
Nexus AI Technical Support
David (CTO) & Michael (CPO)

---
📧 qingziyuezi@gmail.com
🐦 @y36764qing
"""
        },
        "business_opportunity": {
            "subject": "Re: Business Opportunity - Nexus AI Partnership",
            "body": """Dear Partner,

Thank you for reaching out regarding business collaboration. Nexus AI is always open to exploring strategic partnerships.

🤝 PARTNERSHIP AREAS:
• Technology Integration
• Joint Product Development
• Referral Partnerships
• White-label Solutions
• Enterprise Reselling

📋 TO MOVE FORWARD:
Please share:
1. Company/Organization overview
2. Partnership proposal
3. Expected mutual benefits
4. Timeline expectations

Our CEO (Alex) and CMO (Sarah) will review and schedule a call within 24 hours.

Best regards,
Nexus AI Business Development
Alex (CEO) & Sarah (CMO)

---
🌐 https://maoshuorz.github.io/nexus-ai/
📧 qingziyuezi@gmail.com
"""
        },
        "unknown": {
            "subject": "Re: Your Inquiry - Nexus AI Response",
            "body": """Hello,

Thank you for contacting Nexus AI. We have received your message.

To better assist you, could you please clarify:

• Are you looking for AI Agent development services?
• Do you need workflow automation solutions?
• Are you requesting technical consulting?
• Or is this regarding business partnership?

Please reply with more details, and our team will route your inquiry to the appropriate department.

⏱️ We typically respond within 1 hour during business hours.

Best regards,
Nexus AI Team

---
🌐 https://maoshuorz.github.io/nexus-ai/
📧 qingziyuezi@gmail.com
🐦 @y36764qing
"""
        }
    }
    
    return templates.get(email_type, templates["unknown"])

def save_order(email_analysis):
    """保存订单"""
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
    
    log(f"💾 订单已保存: #{order['id']} | 类型: {order['type']} | 置信度: {order.get('confidence', 0)}%")
    return order

def main():
    log("=" * 60)
    log("🚀 Nexus AI 智能邮件过滤系统 v2.0")
    log("=" * 60)
    
    # 检查新邮件
    log("🔍 检查新邮件...")
    command = f'gog gmail messages search "in:inbox newer_than:1h" --account {GMAIL_ACCOUNT} --json'
    stdout, stderr, code = run_gog_command(command)
    
    if code != 0:
        log(f"❌ 检查邮件失败: {stderr}")
        return
    
    try:
        emails = json.loads(stdout) if stdout else []
        log(f"📨 发现 {len(emails)} 封新邮件")
    except:
        log("⚠️ 解析邮件失败")
        return
    
    # 统计
    stats = {"total": len(emails), "filtered": 0, "orders": 0, "replies": 0}
    
    for email in emails:
        analysis = analyze_email(email)
        
        if analysis["type"] in ["verification_code", "spam", "invalid"]:
            stats["filtered"] += 1
            continue
        
        if analysis["should_reply"]:
            save_order(analysis)
            response = generate_response(analysis)
            stats["orders"] += 1
            stats["replies"] += 1
            
            log(f"📤 准备回复: {analysis['type']} | 来自: {analysis['from'][:30]}...")
        else:
            log(f"⚠️  置信度不足: {analysis['type']} ({analysis.get('confidence', 0)}%)")
        
        log("-" * 60)
    
    log(f"✅ 处理完成: 总计{stats['total']} | 过滤{stats['filtered']} | 订单{stats['orders']}")
    log("=" * 60)

if __name__ == "__main__":
    main()
