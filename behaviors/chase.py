import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor
from behaviors.base import BaseBehavior

class Butterfly(QWidget):
    """
    辅助窗口：独立的蝴蝶动画窗口
    """
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        self.resize(50, 50)
        self.wing_scale = 1.0
        self.wing_dir = 1
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(100, 200, 255))
        painter.setPen(Qt.PenStyle.NoPen)
        w = 12 * self.wing_scale
        painter.drawEllipse(25 - int(w), 15, int(w), 15)
        painter.drawEllipse(25, 15, int(w), 15)
        painter.setBrush(QColor(40, 40, 40))
        painter.drawRect(24, 12, 2, 20)

class ChaseBehavior(BaseBehavior):
    """
    追逐蝴蝶行为逻辑
    """
    def __init__(self, cat):
        super().__init__(cat)
        self.butterfly = Butterfly()
        self.is_active = False
        self.rel_pos = QPointF(0, 0)

    def start(self):
        self.is_active = True
        self.cat.state = 'run'
        self.cat.frame = 0 
        # 设置蝴蝶相对于猫咪的起始位置
        self.rel_pos = QPointF(200 * self.cat.direction, -100)
        self.butterfly.show()

    def stop(self):
        self.is_active = False
        self.butterfly.hide()

    def update(self):
        if not self.is_active: return
        
        # 更新猫咪世界坐标位移
        self.cat.cat_pos += QPointF(12 * self.cat.direction, 0)
        self.cat.frame = (self.cat.frame + 1) % 4
        
        # 蝴蝶动力学逻辑
        current_x = self.rel_pos.x()
        if abs(current_x) > 50:
            reduction = 3.0 * self.cat.direction
            self.rel_pos.setX(current_x - reduction)
        
        # 蝴蝶上下波动
        self.rel_pos.setY(-100 + math.sin(self.cat.frame * 0.8) * 12)
        # 将蝴蝶移动到猫咪坐标 + 相对坐标处
        self.butterfly.move((self.cat.cat_pos + self.rel_pos).toPoint())
        
        # 蝴蝶煽动翅膀动画
        self.butterfly.wing_scale += 0.3 * self.butterfly.wing_dir
        if self.butterfly.wing_scale > 1.2 or self.butterfly.wing_scale < 0.3:
            self.butterfly.wing_dir *= -1
        self.butterfly.update()
