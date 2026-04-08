from collections import deque

class CatMemory:
    """
    电子猫行为记忆模块
    使用双向队列记录最近的 N 次行为，为 AI 提供上下文参考。
    """
    def __init__(self, max_size=5):
        """
        初始化记忆模块
        :param max_size: 记忆的最大步数，默认为 5 步
        """
        self.history = deque(maxlen=max_size)

    def add_action(self, action):
        """记录一个新的动作"""
        self.history.append(action)

    def get_history(self):
        """获取所有动作历史列表"""
        return list(self.history)

    def get_history_summary(self):
        """获取以箭头连接的历史记录字符串"""
        if not self.history:
            return "尚无行为历史。"
        return " -> ".join(self.history)
