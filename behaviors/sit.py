import random
from behaviors.base import BaseBehavior

class SitBehavior(BaseBehavior):
    """
    坐下行为逻辑
    """
    def start(self):
        self.cat.state = 'sit'
        self.cat.frame = 0
        # 换个方向坐
        if random.random() > 0.5:
            self.cat.direction *= -1

    def stop(self):
        pass

    def update(self):
        # 播放坐下动画（前3帧为坐下动作，最后一帧保持）
        if self.cat.frame < 3:
            self.cat.frame += 1
        else:
            # 极小概率中途换方向
            if random.random() < 0.01:
                self.cat.direction *= -1
