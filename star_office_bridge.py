#!/usr/bin/env python3
"""
Star Office Bridge v2 - Nexus AI Agent 状态发布器
支持 WebSocket 实时推送 + 像素风视觉

用法:
    from star_office_bridge import StatePublisher
    
    # 在 Agent 中初始化
    publisher = StatePublisher("宗志")
    
    # 设置状态
    publisher.set_state("writing", "正在分析市场数据")
    publisher.set_state("idle", "休息中")
"""

import requests
import threading
from typing import Optional


class StatePublisher:
    """Agent 状态发布器 - 异步发布状态到 Star Office UI"""
    
    def __init__(self, agent_name: str, star_office_url: str = "http://localhost:18795"):
        """
        初始化状态发布器
        
        Args:
            agent_name: Agent 名称 (宗志/锦绣/匠心/墨染/睿思/明镜)
            star_office_url: Star Office 服务地址
        """
        self.agent_name = agent_name
        self.star_office_url = star_office_url.rstrip("/")
        self._session = requests.Session()
    
    def set_state(self, state: str, note: str = "", async_mode: bool = True) -> bool:
        """
        设置 Agent 状态
        
        Args:
            state: 状态值 (idle/writing/researching/executing/syncing/error)
            note: 状态备注
            async_mode: 是否异步发布 (默认 True，不阻塞主逻辑)
        
        Returns:
            bool: 是否成功
        """
        if async_mode:
            thread = threading.Thread(
                target=self._send_state,
                args=(state, note),
                daemon=True
            )
            thread.start()
            return True
        else:
            return self._send_state(state, note)
    
    def _send_state(self, state: str, note: str = "") -> bool:
        """发送状态到 Star Office"""
        try:
            url = f"{self.star_office_url}/agents/{self.agent_name}/state"
            response = self._session.post(url, json={"state": state, "note": note}, timeout=2)
            return response.status_code == 200
        except Exception as e:
            print(f"[Star Office Bridge] 发送状态失败：{e}")
            return False
    
    def get_status(self) -> Optional[dict]:
        """获取当前 Agent 状态"""
        try:
            url = f"{self.star_office_url}/agents/{self.agent_name}/status"
            response = self._session.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                return data.get("data") if data.get("ok") else None
        except Exception as e:
            print(f"[Star Office Bridge] 获取状态失败：{e}")
        return None
    
    def log_activity(self, note: str = ""):
        """记录活动日志（不改变状态）"""
        self.set_state("executing", note)
    
    # 便捷方法
    def start_work(self, task: str):
        """开始工作"""
        self.set_state("writing", task)
    
    def start_research(self, topic: str):
        """开始调研"""
        self.set_state("researching", topic)
    
    def start_execution(self, action: str):
        """开始执行"""
        self.set_state("executing", action)
    
    def finish(self, note: str = "任务完成"):
        """完成任务"""
        self.set_state("idle", note)
    
    def error(self, msg: str):
        """报告错误"""
        self.set_state("error", msg)


# 便捷函数
def create_publisher(agent_name: str) -> StatePublisher:
    """创建 Agent 状态发布器"""
    return StatePublisher(agent_name)


# 测试
if __name__ == "__main__":
    import time
    
    print("╔════════════════════════════════════════════════════════╗")
    print("║     Star Office Bridge v2 - Phase 2 测试                ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    
    # 测试所有 Agent
    agents = ["宗志", "锦绣", "匠心", "墨染", "睿思", "明镜"]
    
    for i, name in enumerate(agents):
        publisher = StatePublisher(name)
        states = [
            ("writing", "正在处理任务"),
            ("researching", "调研中"),
            ("executing", "执行命令"),
            ("idle", "待命"),
        ]
        for state, note in states:
            publisher.set_state(state, note)
            time.sleep(0.3)
    
    print("\n✓ 测试完成")
    print("\n访问 http://localhost:18795 查看像素风状态看板")
    print("WebSocket 实时推送已启用 ✨")
