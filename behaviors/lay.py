from behaviors.base import BaseBehavior

class LayBehavior(BaseBehavior):
    """
    躺下休息行为逻辑
    """
    def start(self):
        self.cat.state = 'lay'
        self.cat.frame = 0

    def stop(self):
        pass

    def update(self):
        # 播放躺下动画
        if self.cat.frame < 3:
            self.cat.frame += 1
        # 躺下后保持最后一帧
