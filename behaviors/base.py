from abc import ABC, abstractmethod

class BaseBehavior(ABC):
    """
    猫咪行为基类 (接口定义)
    所有具体行为（如追逐、坐下）都必须继承此类并实现其方法。
    """
    def __init__(self, cat):
        """
        初始化行为
        :param cat: DesktopCat 对象实例，用于控制猫咪属性
        """
        self.cat = cat

    @abstractmethod
    def start(self):
        """行为开始时的逻辑（如重置帧数）"""
        pass

    @abstractmethod
    def stop(self):
        """行为结束时的清理逻辑"""
        pass

    @abstractmethod
    def update(self):
        """每帧调用的更新逻辑（动画、位移等）"""
        pass
