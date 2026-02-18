#!/usr/bin/env python3
"""
Nexus AI - 监控数据接口 (For CTO David)
提供orders.json的实时数据供监控系统使用
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

ORDERS_FILE = Path.home() / ".openclaw/workspace/company_system/data/orders.json"

def load_orders_data():
    """加载订单数据"""
    if ORDERS_FILE.exists():
        try:
            with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": str(e), "orders": [], "metadata": {}}
    return {"orders": [], "metadata": {}}

def get_monitor_data():
    """
    获取监控数据 - 用于实时监控系统
    返回格式与现有监控系统兼容
    """
    data = load_orders_data()
    orders = data.get("orders", [])
    metadata = data.get("metadata", {})
    
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    # 统计计算
    new_orders = [o for o in orders if o.get('status', {}).get('current') == 'new']
    pending_response = [o for o in new_orders if not o.get('response', {}).get('auto_replied')]
    
    high_priority = [o for o in orders if o.get('priority') == 'high' and 
                     o.get('status', {}).get('current') == 'new']
    
    today_orders = [o for o in orders if datetime.fromisoformat(
        o['timestamps']['created'].replace('Z', '+00:00')) >= today_start]
    
    # 按类型统计
    by_type = {}
    for order in orders:
        t = order.get('inquiry', {}).get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1
    
    # 按团队统计
    by_team = {}
    for order in orders:
        team = order.get('assignment', {}).get('team', 'general')
        by_team[team] = by_team.get(team, 0) + 1
    
    # 按状态统计
    by_status = {}
    for order in orders:
        status = order.get('status', {}).get('current', 'unknown')
        by_status[status] = by_status.get(status, 0) + 1
    
    # 响应时间分析
    response_times = []
    for order in orders:
        if order.get('response', {}).get('reply_sent_at'):
            received = datetime.fromisoformat(order['timestamps']['received'].replace('Z', '+00:00'))
            replied = datetime.fromisoformat(order['response']['reply_sent_at'].replace('Z', '+00:00'))
            response_times.append((replied - received).total_seconds() / 3600)  # 小时
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # SLA合规率 (2小时内响应)
    sla_compliant = len([t for t in response_times if t <= 2])
    sla_rate = (sla_compliant / len(response_times) * 100) if response_times else 100
    
    # 构建监控数据
    monitor_data = {
        # 核心指标
        "metrics": {
            "total_orders": len(orders),
            "new_orders_today": len(today_orders),
            "pending_response": len(pending_response),
            "high_priority_pending": len(high_priority),
            "avg_response_time_hours": round(avg_response_time, 2),
            "sla_compliance_rate": round(sla_rate, 1),
            "last_sync": metadata.get("last_sync_time"),
            "sync_status": "healthy" if metadata.get("last_sync_time") else "unknown"
        },
        
        # 分布统计
        "distribution": {
            "by_type": by_type,
            "by_team": by_team,
            "by_status": by_status
        },
        
        # 需要关注的订单
        "alerts": {
            "high_priority_orders": high_priority[:5],  # 最近5条高优先级
            "overdue_orders": [o for o in pending_response if 
                datetime.fromisoformat(o['timestamps']['first_response_due'].replace('Z', '+00:00')) < now][:5]
        },
        
        # 实时活动
        "recent_activity": sorted(
            orders, 
            key=lambda x: x['timestamps']['created'], 
            reverse=True
        )[:10],  # 最近10条
        
        # 同步日志
        "sync_log": data.get("sync_log", [])[-20:],  # 最近20条同步日志
        
        # 系统健康
        "health": {
            "status": "healthy" if len(pending_response) < 10 else "warning",
            "orders_processing_rate": len(today_orders),
            "system_version": metadata.get("system", "Nexus AI Order Management"),
            "schema_version": data.get("schema_version", "1.0")
        },
        
        # Agent分配建议
        "agent_assignments": {
            "sales": len([o for o in new_orders if o.get('assignment', {}).get('team') == 'sales']),
            "technical_support": len([o for o in new_orders if o.get('assignment', {}).get('team') == 'technical_support']),
            "business_dev": len([o for o in new_orders if o.get('assignment', {}).get('team') == 'business_dev']),
            "general": len([o for o in new_orders if o.get('assignment', {}).get('team') == 'general'])
        }
    }
    
    return monitor_data

def get_api_response():
    """
    获取API格式响应（用于HTTP API）
    """
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "data": get_monitor_data()
    }

def export_for_agent(agent_name: str):
    """
    导出特定Agent需要的数据
    """
    data = load_orders_data()
    orders = data.get("orders", [])
    
    if agent_name == "CEO":
        # CEO需要：高优先级、待决策、财务相关
        return {
            "high_priority_orders": [o for o in orders if o.get('priority') == 'high'],
            "business_opportunities": [o for o in orders if o.get('inquiry', {}).get('type') == 'business_opportunity'],
            "awaiting_decision": [o for o in orders if o.get('status', {}).get('current') in ['evaluating', 'quoted']]
        }
    
    elif agent_name == "CTO":
        # CTO需要：技术支持、项目评估
        return {
            "support_requests": [o for o in orders if o.get('inquiry', {}).get('type') == 'support_request'],
            "project_evaluations": [o for o in orders if o.get('inquiry', {}).get('type') == 'project_inquiry' and 
                                   o.get('status', {}).get('current') == 'evaluating'],
            "technical_debt": [o for o in orders if o.get('status', {}).get('current') == 'development']
        }
    
    elif agent_name == "COO":
        # COO需要：全部新订单、流程监控
        return {
            "new_orders": [o for o in orders if o.get('status', {}).get('current') == 'new'],
            "in_progress": [o for o in orders if o.get('status', {}).get('current') in ['contract', 'development', 'monitoring']],
            "team_workload": get_monitor_data()["agent_assignments"]
        }
    
    elif agent_name == "CFO":
        # CFO需要：报价、合同、财务相关
        return {
            "price_inquiries": [o for o in orders if o.get('inquiry', {}).get('type') == 'price_inquiry'],
            "awaiting_quote": [o for o in orders if o.get('status', {}).get('current') == 'evaluating'],
            "in_contract": [o for o in orders if o.get('status', {}).get('current') == 'contract']
        }
    
    elif agent_name == "CMO":
        # CMO需要：市场机会、潜在客户
        return {
            "all_leads": orders,
            "project_inquiries": [o for o in orders if o.get('inquiry', {}).get('type') == 'project_inquiry'],
            "conversion_stats": get_monitor_data()["distribution"]["by_type"]
        }
    
    return {"orders": orders}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "api":
            print(json.dumps(get_api_response(), indent=2, ensure_ascii=False))
        elif cmd == "agent" and len(sys.argv) > 2:
            agent = sys.argv[2]
            print(json.dumps(export_for_agent(agent), indent=2, ensure_ascii=False))
        elif cmd == "dashboard":
            print(json.dumps(get_monitor_data(), indent=2, ensure_ascii=False))
        else:
            print("用法: python monitor_api.py [api|dashboard|agent <name>]")
    else:
        print(json.dumps(get_monitor_data(), indent=2, ensure_ascii=False))
