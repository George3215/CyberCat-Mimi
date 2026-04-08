import sys
import os
import math
import random
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QRect, QPoint, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QColor

# 确保路径指向你的素材
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_DIR, "Cats Download/black_2.png")

class Butterfly(QWidget):
    """独立的蝴蝶窗口"""
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

# --- 行为类封装 ---

class LookBehavior:
    """环顾四周：增加发呆逻辑，不再鬼畜"""
    def __init__(self, cat_widget):
        self.cat = cat_widget
        self.wait_counter = 0
        self.is_waiting = False

    def start(self):
        self.cat.state = 'look'
        self.cat.frame = 0
        self.is_waiting = False
        self.wait_counter = 0

    def stop(self): pass

    def update(self):
        if self.is_waiting:
            self.wait_counter -= 1
            if self.wait_counter <= 0:
                self.is_waiting = False
            return

        # 正常播放动画
        self.cat.frame = (self.cat.frame + 1) % 4
        
        # 每一帧播完有 25% 概率进入“发呆”状态，停在当前帧
        if random.random() < 0.25:
            self.is_waiting = True
            # 随机停顿 0.5 到 2.5 秒 (5 到 25 帧)
            self.wait_counter = random.randint(5, 25)

class LayBehavior:
    """趴下休息"""
    def __init__(self, cat_widget):
        self.cat = cat_widget
    def start(self):
        self.cat.state = 'lay'
        self.cat.frame = 0
    def stop(self): pass
    def update(self):
        if self.cat.frame < 3:
            self.cat.frame += 1

class ChaseBehavior:
    """追蝴蝶"""
    def __init__(self, cat_widget):
        self.cat = cat_widget
        self.butterfly = Butterfly()
        self.is_active = False

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
        
        # 蝴蝶逻辑
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
    """坐下：静止状态"""
    def __init__(self, cat_widget):
        self.cat = cat_widget
    def start(self):
        self.cat.state = 'sit'
        self.cat.frame = 0 
        if random.random() > 0.5:
            self.cat.direction *= -1
    def stop(self): pass
    def update(self):
        if self.cat.frame < 3:
            self.cat.frame += 1
        else:
            # 坐稳后有极小概率偶尔换个方向坐
            if random.random() < 0.01:
                self.cat.direction *= -1

# --- 主窗口 ---

class DesktopCat(QWidget):
    def __init__(self, path):
        super().__init__()
        self.sprite = QPixmap(path)
        self.fw, self.fh = 32, 32
        self.scale = 3.5
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        
        self.resize(int(self.fw * self.scale), int(self.fh * self.scale))

        # 坐标映射 (Y=160 为侧面视角)
        self.actions = {
            'sit':  [0, 160, 4],
            'look': [128, 160, 4],
            'lay':  [256, 160, 4],
            'run':  [512, 160, 4]
        } 
        
        self.state = 'sit'
        self.frame = 0
        self.direction = 1 
        self.cat_pos = QPointF(200, 600)

        self.behaviors = {
            'chase': ChaseBehavior(self),
            'sit': SitBehavior(self),
            'look': LookBehavior(self),
            'lay': LayBehavior(self)
        }
        self.current_behavior = self.behaviors['sit']
        self.current_behavior.start()
        
        # 动画主计时器 (100ms 一帧)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(100)
        
        # 行为切换计时器：使用 SingleShot 实现随机时长
        self.behavior_timer = QTimer(self)
        self.behavior_timer.setSingleShot(True)
        self.behavior_timer.timeout.connect(self.random_switch_behavior)
        self.behavior_timer.start(random.randint(3000, 7000))

        self.show()

    def random_switch_behavior(self):
        self.current_behavior.stop()
        
        # 设置行为权重：让猫咪更多处于坐着和张望状态
        # 权重顺序对应：sit(坐), look(看), lay(躺), chase(跑)
        keys = ['sit', 'look', 'lay', 'chase']
        weights = [0.1, 0.2, 0.2, 0.5] 
        
        new_key = random.choices(keys, weights=weights)[0]
        self.current_behavior = self.behaviors[new_key]
        self.current_behavior.start()
        
        # 随机设置下一次切换的时间 (3-10秒)
        self.behavior_timer.start(random.randint(3000, 10000))

    def main_loop(self):
        self.current_behavior.update()
        screen = QApplication.primaryScreen().availableGeometry()
        
        if self.state == 'run':
            if (self.direction == 1 and self.cat_pos.x() > screen.right() - 150) or \
               (self.direction == -1 and self.cat_pos.x() < screen.left() + 50):
                self.direction *= -1
                self.current_behavior.start() # 转身后重置蝴蝶

        self.move(self.cat_pos.toPoint())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.sprite.isNull(): return
        
        info = self.actions.get(self.state, [0, 160, 4])
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