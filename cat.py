import random
from PyQt6.QtWidgets import QWidget, QApplication, QMenu, QInputDialog, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QPointF, QSize
from PyQt6.QtGui import QPixmap, QPainter, QAction, QColor, QFont, QPolygon, QFontMetrics

from config import (
    IMG_PATH, SPRITE_FRAME_SIZE, SPRITE_SCALE, 
    ACTION_CONFIGS, PERCEPTION_INTERVAL, ANIMATION_INTERVAL,
    BEHAVIOR_RULES, BUBBLE_STYLE
)
from behaviors.sit import SitBehavior
from behaviors.look import LookBehavior
from behaviors.lay import LayBehavior
from behaviors.chase import ChaseBehavior
from memory.memory import CatMemory
from brain.decision import DecisionWorker

class SpeechBubble(QWidget):
    """
    对话气泡窗口组件
    位于猫咪头顶，用于实时展示 AI 生成的对话内容。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 文本标签
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 应用样式配置
        style = BUBBLE_STYLE
        self.label.setStyleSheet(
            f"color: {style['text']}; "
            f"font-family: {style['font']}; "
            f"font-size: {style['font_size']}px;"
        )
        
        # 布局管理
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            style["padding"], style["padding"], 
            style["padding"], style["padding"] + 10 # 为底部箭头留出空间
        )
        self.layout.addWidget(self.label)
        
        self.hide()

    def setText(self, text):
        """设置文本并根据内容自动调整气泡大小"""
        self.label.setText(text)
        metrics = QFontMetrics(self.font())
        max_w = BUBBLE_STYLE["max_width"]
        rect = metrics.boundingRect(0, 0, max_w, 1000, Qt.TextFlag.TextWordWrap, text)
        
        w = max(60, rect.width() + BUBBLE_STYLE["padding"] * 2)
        h = max(40, rect.height() + BUBBLE_STYLE["padding"] * 2 + 10)
        self.resize(w, h)

    def paintEvent(self, event):
        """绘制气泡背景与小箭头"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        bubble_rect = QRect(0, 0, rect.width(), rect.height() - 10)
        
        # 绘制圆角矩形背景
        painter.setBrush(QColor(BUBBLE_STYLE["background"]))
        painter.setPen(Qt.PenStyle.NoPen)
        radius = BUBBLE_STYLE["border_radius"]
        painter.drawRoundedRect(bubble_rect, radius, radius)
        
        # 绘制指向猫咪的小三角形箭头
        arrow = QPolygon([
            QPoint(rect.width() // 2 - 10, rect.height() - 10),
            QPoint(rect.width() // 2 + 10, rect.height() - 10),
            QPoint(rect.width() // 2, rect.height())
        ])
        painter.drawPolygon(arrow)


class DesktopCat(QWidget):
    """
    DesktopCat 主窗口类
    负责整合动画渲染、行为管理、AI 决策及 UI 交互。
    """
    def __init__(self):
        super().__init__()
        
        # 1. 资源加载
        self.sprite = QPixmap(IMG_PATH)
        self.fw, self.fh = SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE
        self.scale = SPRITE_SCALE
        
        # 2. 核心状态初始化
        self.state = 'sit'
        self.frame = 0
        self.direction = 1 
        self.cat_pos = QPointF(100, 100) # 初始坐标
        self.energy = 100
        self.boredom = 0
        self.log_counter = 0

        # 3. 基础组件初始化
        self.memory = CatMemory()
        self.behaviors = {
            'sit': SitBehavior(self),
            'look': LookBehavior(self),
            'lay': LayBehavior(self),
            'chase': ChaseBehavior(self),
            'run': ChaseBehavior(self) # run 与 chase 使用相同的动作序列
        }
        self.current_behavior = self.behaviors['sit']
        self.current_behavior.start()

        # 4. UI 窗口标志设置
        self.setWindowTitle("CyberCat Mimi")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool 
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        self.resize(int(self.fw * self.scale), int(self.fh * self.scale))

        # 5. 对话气泡与 AI 引擎
        self.speech_bubble = SpeechBubble()
        self.bubble_timer = QTimer(self)
        self.bubble_timer.setSingleShot(True)
        self.bubble_timer.timeout.connect(self.speech_bubble.hide)

        self.brain = DecisionWorker()
        self.brain.decision_made.connect(self.apply_decision)
        self.brain.talk_response.connect(self.handle_talk_response)
        self.brain.start()

        # 6. 定时器启动
        # 动画循环
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(ANIMATION_INTERVAL)
        
        # AI 决策周期
        self.decision_timer = QTimer(self)
        self.decision_timer.timeout.connect(self.trigger_decision)
        self.decision_timer.start(PERCEPTION_INTERVAL)

        self.show()

    def trigger_decision(self):
        """构建环境感知 JSON 并请求 AI 进行行为决策"""
        screen = QApplication.primaryScreen().availableGeometry()
        state_json = {
            "current_state": self.state,
            "pos": {"x": int(self.cat_pos.x()), "y": int(self.cat_pos.y())},
            "energy": self.energy,
            "boredom": self.boredom,
            "near_edge": self.cat_pos.x() > screen.right() - 200 or self.cat_pos.x() < screen.left() + 100,
            "history": self.memory.get_history()
        }
        self.brain.request_decision(state_json)

    def apply_decision(self, action):
        """主线程槽：根据 AI 决策切换猫咪行为"""
        if action == self.state:
            return
        
        print(f"[视觉系统] 行为切换: {self.state} -> {action}")
        self.memory.add_action(self.state)
        self.current_behavior.stop()
        self.current_behavior = self.behaviors.get(action, self.behaviors['sit'])
        self.current_behavior.start()

    def update_loop(self):
        """主逻辑循环：更新数值状态、播放动画、同步气泡位置"""
        # A. 更新能量与无聊值数值
        e_change, b_change = BEHAVIOR_RULES.get(self.state, (0, 0))
        self.energy = max(0, min(100, self.energy + e_change))
        self.boredom = max(0, min(100, self.boredom + b_change))

        # B. 执行当前行为的动作跟进
        self.current_behavior.update()

        # C. 定时记录后台状态日志 (每 10 秒)
        self.log_counter += 1
        if self.log_counter >= 100:
            self.log_counter = 0
            print(f"[状态监控] 能量: {self.energy:3d} | 无聊度: {self.boredom:3d} | 位置: ({int(self.cat_pos.x())}, {int(self.cat_pos.y())})")

        # D. 碰撞检测与屏幕边缘逻辑
        screen = QApplication.primaryScreen().availableGeometry()
        if self.state == 'run':
            if (self.direction == 1 and self.cat_pos.x() > screen.right() - 150) or \
               (self.direction == -1 and self.cat_pos.x() < screen.left() + 50):
                self.direction *= -1
                self.current_behavior.start() # 转身重新重置行为

        # E. UI 位置同步与重绘
        self.move(self.cat_pos.toPoint())
        self.reposition_bubble() # 同步气泡位置
        self.update()

    def reposition_bubble(self):
        """实时将气泡定位在猫咪头顶，并处理屏幕边缘溢出"""
        if not hasattr(self, 'speech_bubble') or not self.speech_bubble.isVisible():
            return
            
        bw = self.speech_bubble.width()
        bh = self.speech_bubble.height()
        
        # 目标位置：猫咪水平中心上方
        bx = int(self.cat_pos.x()) + (self.width() // 2) - (bw // 2)
        by = int(self.cat_pos.y()) - bh
        
        # 屏幕边缘检测：如果上方空间不足，气泡显示在猫咪下方
        if by < 50:
            by = int(self.cat_pos.y()) + self.height()
            
        self.speech_bubble.move(bx, by)

    def display_message(self, text, duration=5000):
        """显示一段对话气泡"""
        self.speech_bubble.setText(text)
        self.reposition_bubble()
        self.speech_bubble.show()
        self.bubble_timer.start(duration)

    def handle_talk_response(self, response):
        """处理来自 AI 的对话内容"""
        self.display_message(response)

    def paintEvent(self, event):
        """根据当前状态与帧数绘制素材"""
        painter = QPainter(self)
        if self.sprite.isNull(): return
        
        config = ACTION_CONFIGS.get(self.state, ACTION_CONFIGS['sit'])
        # 计算素材图中的矩形区域
        rect = QRect(config['x'] + self.frame * self.fw, config['y'], self.fw, self.fh)
        
        if self.direction == 1:
            # 镜像翻转图片以支持双向移动
            img = self.sprite.copy(rect).toImage().mirrored(True, False)
            painter.drawPixmap(self.rect(), QPixmap.fromImage(img))
        else:
            painter.drawPixmap(self.rect(), self.sprite, rect)

    def contextMenuEvent(self, event):
        """右键菜单"""
        menu = QMenu(self)
        talk_action = QAction("与猫对话 (Talk)", self)
        talk_action.triggered.connect(self.show_talk_dialog)
        exit_action = QAction("退出程序 (Exit)", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        
        menu.addAction(talk_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        menu.exec(event.globalPos())

    def show_talk_dialog(self):
        """打开输入对话框"""
        text, ok = QInputDialog.getText(self, 'CyberCat 对话', '输入你想对 Mimi 说的话:')
        if ok and text:
            # 立即反馈思考状态
            self.display_message("...", duration=20000) 
            state_json = { "energy": self.energy, "boredom": self.boredom, "state": self.state }
            self.brain.request_talk(text, state_json)

    def moveEvent(self, event):
        """手动拖拽猫咪时同步气泡"""
        self.reposition_bubble()
        super().moveEvent(event)

    def closeEvent(self, event):
        """退出时的清理工作"""
        self.speech_bubble.close()
        self.brain.stop()
        super().closeEvent(event)
