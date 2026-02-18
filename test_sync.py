#!/usr/bin/env python3
"""
Nexus AI - 数据同步测试脚本
验证orders.json数据结构和同步功能
"""

import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from gmail_sync import (
    load_orders, save_orders, generate_order_id, 
    EmailAnalyzer, create_order, get_dashboard_data
)

def test_schema():
    """测试数据结构完整性"""
    print("=" * 60)
    print("🧪 测试1: 数据结构完整性")
    print("=" * 60)
    
    data = load_orders()
    
    required_fields = [
        "schema_version",
        "last_updated", 
        "metadata",
        "orders",
        "sync_log"
    ]
    
    missing = [f for f in required_fields if f not in data]
    if missing:
        print(f"❌ 缺少字段: {missing}")
        return False
    
    print(f"✅ schema_version: {data['schema_version']}")
    print(f"✅ metadata.system: {data['metadata']['system']}")
    print(f"✅ sync_interval: {data['metadata']['sync_interval_minutes']}分钟")
    print("✅ 数据结构测试通过")
    return True

def test_email_analyzer():
    """测试邮件分析器"""
    print("\n" + "=" * 60)
    print("🧪 测试2: 邮件分析引擎")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "项目咨询",
            "email": {
                "subject": "AI Agent Development Project Inquiry",
                "body": "We need to develop a custom AI agent system for our business. Can you help?",
                "from": "client@company.com",
                "date": datetime.now().isoformat(),
                "id": "test1"
            },
            "expected_type": "project_inquiry",
            "expected_priority": "high"
        },
        {
            "name": "验证码过滤",
            "email": {
                "subject": "Your verification code is 123456",
                "body": "Please use code 123456 to verify your account.",
                "from": "noreply@service.com",
                "date": datetime.now().isoformat(),
                "id": "test2"
            },
            "expected_type": "verification_code",
            "expected_should_process": False
        },
        {
            "name": "报价询问",
            "email": {
                "subject": "How much does it cost?",
                "body": "What is the price for your consulting service?",
                "from": "buyer@business.com",
                "date": datetime.now().isoformat(),
                "id": "test3"
            },
            "expected_type": "price_inquiry",
            "expected_priority": "high"
        },
        {
            "name": "技术支持",
            "email": {
                "subject": "Need help with AI integration",
                "body": "We are experiencing issues with our current AI system. Can you provide technical support?",
                "from": "tech@company.com",
                "date": datetime.now().isoformat(),
                "id": "test4"
            },
            "expected_type": "support_request"
        }
    ]
    
    passed = 0
    for test in test_cases:
        result = EmailAnalyzer.analyze(test["email"])
        
        type_match = result["type"] == test["expected_type"]
        process_match = result.get("should_process", True) == test.get("expected_should_process", True)
        
        if type_match and process_match:
            print(f"✅ {test['name']}: 类型={result['type']}, 置信度={result.get('confidence', 0)}%")
            passed += 1
        else:
            print(f"❌ {test['name']}: 期望={test['expected_type']}, 实际={result['type']}")
    
    print(f"\n测试结果: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)

def test_order_creation():
    """测试订单创建"""
    print("\n" + "=" * 60)
    print("🧪 测试3: 订单创建")
    print("=" * 60)
    
    analysis = {
        "type": "project_inquiry",
        "priority": "high",
        "confidence": 85,
        "subject": "Test Project",
        "from": "test@example.com",
        "body_preview": "Test body preview",
        "full_body": "Full test body content",
        "timestamp": datetime.now().isoformat(),
        "gmail_message_id": "test_msg_123",
        "thread_id": "test_thread_456"
    }
    
    order = create_order(analysis)
    
    required_order_fields = [
        "order_id", "customer", "inquiry", "status", 
        "priority", "timestamps", "assignment", "response", "metadata"
    ]
    
    missing = [f for f in required_order_fields if f not in order]
    if missing:
        print(f"❌ 订单缺少字段: {missing}")
        return False
    
    print(f"✅ 订单ID: {order['order_id']}")
    print(f"✅ 客户邮箱: {order['customer']['email']}")
    print(f"✅ 咨询类型: {order['inquiry']['type']}")
    print(f"✅ 分配团队: {order['assignment']['team']}")
    print(f"✅ 状态历史: {len(order['status']['history'])} 条记录")
    print("✅ 订单创建测试通过")
    return True

def test_dashboard():
    """测试仪表板数据"""
    print("\n" + "=" * 60)
    print("🧪 测试4: 仪表板数据")
    print("=" * 60)
    
    try:
        dashboard = get_dashboard_data()
        
        required_metrics = [
            "total_orders", "new_today", "pending_response", 
            "high_priority", "by_type", "last_sync"
        ]
        
        missing = [m for m in required_metrics if m not in dashboard]
        if missing:
            print(f"❌ 仪表板缺少指标: {missing}")
            return False
        
        print(f"✅ 总订单数: {dashboard['total_orders']}")
        print(f"✅ 今日新订单: {dashboard['new_today']}")
        print(f"✅ 待回复: {dashboard['pending_response']}")
        print(f"✅ 高优先级: {dashboard['high_priority']}")
        print(f"✅ 类型分布: {list(dashboard['by_type'].keys())}")
        print("✅ 仪表板测试通过")
        return True
    except Exception as e:
        print(f"❌ 仪表板测试失败: {e}")
        return False

def test_data_persistence():
    """测试数据持久化"""
    print("\n" + "=" * 60)
    print("🧪 测试5: 数据持久化")
    print("=" * 60)
    
    try:
        # 保存测试数据
        data = load_orders()
        original_count = len(data.get("orders", []))
        
        # 添加测试订单
        test_order = {
            "order_id": "TEST_001",
            "customer": {"email": "test@test.com", "name": "Test"},
            "inquiry": {"type": "test", "subject": "Test", "body_preview": "Test", "confidence": 100},
            "status": {"current": "test", "history": []},
            "priority": "low",
            "timestamps": {"created": datetime.now().isoformat(), "received": datetime.now().isoformat(), "last_updated": datetime.now().isoformat()},
            "assignment": {"team": "test"},
            "response": {},
            "metadata": {"source": "test"}
        }
        
        data["orders"].append(test_order)
        save_orders(data)
        
        # 重新加载验证
        data2 = load_orders()
        new_count = len(data2.get("orders", []))
        
        if new_count == original_count + 1:
            print(f"✅ 数据持久化成功: {original_count} -> {new_count}")
            
            # 清理测试数据
            data2["orders"] = [o for o in data2["orders"] if o.get("order_id") != "TEST_001"]
            save_orders(data2)
            
            print("✅ 测试数据已清理")
            return True
        else:
            print(f"❌ 数据持久化失败: {original_count} -> {new_count}")
            return False
    except Exception as e:
        print(f"❌ 数据持久化测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print("Nexus AI - 数据同步系统测试套件")
    print("测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🚀" * 30 + "\n")
    
    results = []
    
    results.append(("数据结构", test_schema()))
    results.append(("邮件分析", test_email_analyzer()))
    results.append(("订单创建", test_order_creation()))
    results.append(("仪表板", test_dashboard()))
    results.append(("数据持久化", test_data_persistence()))
    
    print("\n" + "=" * 60)
    print("📊 测试汇总")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print("-" * 60)
    print(f"总计: {passed}/{total} 测试通过 ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常运行。")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
