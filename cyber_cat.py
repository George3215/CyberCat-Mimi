import sys
import os
import math
import random
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor

# 提示：确保黑猫素材路径正确（推荐使用相对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_DIR, "Cats Download/black_2.png")

class Butterfly(QWidget):
    """独立的蝴蝶窗口"""
    def __init__(self):
        super().__init__()
        # 设置：无边框 | 永久置顶 | 工具窗口 | 忽略点击
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 针对 macOS 的关键设置：确保在所有虚拟桌面（Spaces）都可见
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

class ChaseBehavior:
    """封装：追蝴蝶的行为"""
    def __init__(self, cat_widget):
        self.cat = cat_widget
        self.butterfly = Butterfly()
        self.is_active = False
        self.rel_pos = QPointF(0, 0)

    def start(self):
        self.is_active = True
        self.cat.state = 'run'
        self.cat.frame = 0 
        self.rel_pos = QPointF(200 * self.cat.direction, -100)
        self.butterfly.show()

    def stop(self):
        self.is_active = False
        self.butterfly.hide()

    def update(self):
        if not self.is_active: return
        self.cat.cat_pos += QPointF(12 * self.cat.direction, 0)
        self.cat.frame = (self.cat.frame + 1) % 4
        current_x = self.rel_pos.x()
        if abs(current_x) > 50:
            reduction = 3.0 * self.cat.direction
            self.rel_pos.setX(current_x - reduction)
        self.rel_pos.setY(-100 + math.sin(self.cat.frame * 0.8) * 12)
        self.butterfly.move((self.cat.cat_pos + self.rel_pos).toPoint())
        self.butterfly.wing_scale += 0.3 * self.butterfly.wing_dir
        if self.butterfly.wing_scale > 1.2 or self.butterfly.wing_scale < 0.3:
            self.butterfly.wing_dir *= -1
        self.butterfly.update()

class SitBehavior:
    """封装：坐下的行为"""
    def __init__(self, cat_widget):
        self.cat = cat_widget

    def start(self):
        self.cat.state = 'sit'
        self.cat.frame = 0 
        if random.random() > 0.8:
            self.cat.direction *= -1

    def stop(self):
        pass

    def update(self):
        if self.cat.frame < 3:
            self.cat.frame += 1
        else:
            self.cat.frame = 3 

class DesktopCat(QWidget):
    def __init__(self, path):
        super().__init__()
        self.sprite = QPixmap(path)
        self.fw, self.fh = 32, 32
        self.scale = 3.5
        
        # --- 窗口置顶核心设置 ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |       # 无边框
            Qt.WindowType.WindowStaysOnTopHint |      # 永久置顶
            Qt.WindowType.Tool |                      # 隐藏任务栏图标
            Qt.WindowType.WindowTransparentForInput | # 点击穿透（不干扰后面窗口的操作）
            Qt.WindowType.WindowDoesNotAcceptFocus    # 不抢占输入焦点
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 针对 macOS 的特殊设置：切换全屏页面/桌面时猫咪依然存在
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        
        self.resize(int(self.fw * self.scale), int(self.fh * self.scale))

        self.actions = {'run': [512, 160, 4], 'sit': [0, 160, 4]} 
        self.state = 'sit'
        self.frame = 0
        self.direction = 1 
        self.cat_pos = QPointF(200, 600)

        self.behaviors = {
            'chase': ChaseBehavior(self),
            'sit': SitBehavior(self)
        }
        self.current_behavior = self.behaviors['sit']
        self.current_behavior.start()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(100)
        
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.random_switch_behavior)
        self.behavior_timer.start(4000)

        self.show()

    def random_switch_behavior(self):
        new_key = 'chase' if random.random() < 0.4 else 'sit'
        if (new_key == 'chase' and self.state == 'sit') or (new_key == 'sit' and self.state == 'run'):
            self.current_behavior.stop()
            self.current_behavior = self.behaviors[new_key]
            self.current_behavior.start()

    def main_loop(self):
        self.current_behavior.update()
        screen = QApplication.primaryScreen().availableGeometry()
        if (self.direction == 1 and self.cat_pos.x() > screen.right() - 150) or \
           (self.direction == -1 and self.cat_pos.x() < screen.left() + 50):
            self.direction *= -1
            if isinstance(self.current_behavior, ChaseBehavior):
                self.current_behavior.start()

        self.move(self.cat_pos.toPoint())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.sprite.isNull(): return
        info = self.actions[self.state]
        rect = QRect(info[0] + self.frame * self.fw, info[1], self.fw, self.fh)
        if self.direction == 1:
            img = self.sprite.copy(rect).toImage().mirrored(True, False)
            painter.drawPixmap(self.rect(), QPixmap.fromImage(img))
        else:
            painter.drawPixmap(self.rect(), self.sprite, rect)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cat = DesktopCat(IMG_PATH)
    sys.exit(app.exec())