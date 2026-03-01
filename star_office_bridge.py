#!/usr/bin/env python3
"""
四智团 - 状态发布器 v4
"""

import requests
import threading
from typing import Optional


class StatePublisher:
    """四智团状态发布器"""
    
    # 四智团配置
    QUARTET = {
        "宗志": {"role": "决策者", "avatar": "🧠", "color": "#FF6B6B"},
        "码匠": {"role": "工程师", "avatar": "💻", "color": "#4ECDC4"},
        "研析": {"role": "研究员", "avatar": "🔬", "color": "#A78BFA"},
        "家助": {"role": "协调员", "avatar": "🏠", "color": "#F59E0B"},
    }
    
    def __init__(self, agent_name: str, star_office_url: str = "http://localhost:18795"):
        if agent_name not in self.QUARTET:
            raise ValueError(f"未知 Agent: {agent_name}\n可选：{list(self.QUARTET.keys())}")
        
        self.agent_name = agent_name
        self.agent_info = self.QUARTET[agent_name]
        self.star_office_url = star_office_url.rstrip("/")
        self._session = requests.Session()
    
    def set_state(self, state: str, note: str = "", async_mode: bool = True) -> bool:
        """设置状态"""
        if async_mode:
            threading.Thread(target=self._send_state, args=(state, note), daemon=True).start()
            return True
        return self._send_state(state, note)
    
    def _send_state(self, state: str, note: str = "") -> bool:
        try:
            url = f"{self.star_office_url}/quartet/{self.agent_name}/state"
            resp = self._session.post(url, json={"state": state, "note": note}, timeout=2)
            return resp.status_code == 200
        except Exception as e:
            print(f"[{self.agent_name}] 状态发送失败：{e}")
            return False
    
    def send_message(self, to_agent: str, content: str, msg_type: str = "task") -> bool:
        """发送消息给其他 Agent"""
        try:
            url = f"{self.star_office_url}/quartet/message"
            resp = self._session.post(url, json={
                "from": self.agent_name,
                "to": to_agent,
                "content": content,
                "type": msg_type
            }, timeout=2)
            return resp.status_code == 200
        except Exception as e:
            print(f"[{self.agent_name}] 消息发送失败：{e}")
            return False
    
    # 便捷方法
    def thinking(self, note: str = "思考中"):
        self.set_state("thinking", note)
    
    def deciding(self, note: str = "决策中"):
        self.set_state("deciding", note)
    
    def coding(self, note: str = "编码中"):
        self.set_state("coding", note)
    
    def building(self, note: str = "构建中"):
        self.set_state("building", note)
    
    def researching(self, note: str = "研究中"):
        self.set_state("researching", note)
    
    def analyzing(self, note: str = "分析中"):
        self.set_state("analyzing", note)
    
    def coordinating(self, note: str = "协调中"):
        self.set_state("coordinating", note)
    
    def idle(self, note: str = "待命"):
        self.set_state("idle", note)
    
    def delegate(self, to_agent: str, task: str):
        """委派任务"""
        self.send_message(to_agent, task)
        self.set_state("coordinating", f"委派任务给 {to_agent}")


# 便捷函数
def create(agent_name: str) -> StatePublisher:
    return StatePublisher(agent_name)


# 测试
if __name__ == "__main__":
    import time
    
    print("╔══════════════════════════════════════════════════════╗")
    print("║           四智团 - 状态发布器测试                      ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    
    # 测试所有 Agent
    for name in StatePublisher.QUARTET:
        pub = StatePublisher(name)
        print(f"{pub.agent_info['avatar']} {name} ({pub.agent_info['role']})")
        
        # 模拟活动
        pub.set_state("thinking", "思考任务...")
        time.sleep(0.3)
        pub.set_state("executing", "执行中...")
        time.sleep(0.3)
        pub.set_state("idle", "待命")
        print()
    
    # 测试消息
    print("测试 Agent 间消息:")
    zong = StatePublisher("宗志")
    zong.delegate("码匠", "实现新功能")
    time.sleep(0.5)
    
    print("\n✅ 测试完成")
    print("访问：http://localhost:18795")
