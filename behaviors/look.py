import random
from behaviors.base import BaseBehavior

class LookBehavior(BaseBehavior):
    """
    环顾观察行为逻辑
    """
    def __init__(self, cat):
        super().__init__(cat)
        self.wait_counter = 0
        self.is_waiting = False

    def start(self):
        self.cat.state = 'look'
        self.cat.frame = 0
        self.is_waiting = False
        self.wait_counter = 0

    def stop(self):
        pass

    def update(self):
        # 如果处于发呆等待状态
        if self.is_waiting:
            self.wait_counter -= 1
            if self.wait_counter <= 0:
                self.is_waiting = False
            return

        # 正常播放观察动画
        self.cat.frame = (self.cat.frame + 1) % 4
        
        # 25% 概率进入发呆状态（暂停动画帧）
        if random.random() < 0.25:
            self.is_waiting = True
            self.wait_counter = random.randint(5, 25)
