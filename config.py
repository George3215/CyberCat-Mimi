import os

"""
CyberCat 项目配置文件
包含模型设置、路径设置、动作映射以及猫咪行为规则。
"""

# 项目基础根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Ollama 模型配置 ---
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:8b"
LLM_PARAMS = {
    "num_predict": 256,  # 增加预测长度以支持推理模型和完整 JSON
    "temperature": 0.7   # 较高的温度使猫咪回复更具个性
}

# --- 素材路径配置 ---
IMG_PATH = os.path.join(BASE_DIR, "Cats Download/black_2.png")

# --- 界面与缩放配置 ---
SPRITE_FRAME_SIZE = 32  # 原始素材单帧像素尺寸
SPRITE_SCALE = 3.5      # 渲染时的放大倍数

# --- 动作序列映射 ---
# x, y 为素材图中起始坐标，frames 为该动作包含的连续帧数
ACTION_CONFIGS = {
    'sit':  {'x': 0,   'y': 160, 'frames': 4},
    'look': {'x': 128, 'y': 160, 'frames': 4},
    'lay':  {'x': 256, 'y': 160, 'frames': 4},
    'run':  {'x': 512, 'y': 160, 'frames': 4}
}

# --- 定时器配置 (毫秒) ---
PERCEPTION_INTERVAL = 8000  # AI 进行一次决策的时间间隔 (8秒)
ANIMATION_INTERVAL = 100    # 动画刷新间隔 (100ms/帧)

# --- 行为属性规则 (energy, boredom) ---
# 负数代表消耗，正数代表恢复
BEHAVIOR_RULES = {
    'chase': (-10, -15), # 运动：显著消耗能量，显著降低无聊
    'sit':   (2,   5),   # 坐着：极低速恢复能量，缓慢增加无聊
    'lay':   (5,  -5),   # 趴着：中速恢复能量，降低无聊 (休息)
    'look':  (-1,  2)    # 观察：微小能量消耗，微小无聊增加
}

# --- 对话气泡样式 ---
BUBBLE_STYLE = {
    "background": "rgba(40, 40, 40, 220)", # 深色半透明背景
    "text": "white",                       # 白色字体
    "font": "Arial",                       # 字体系列
    "font_size": 13,                       # 字体大小
    "padding": 12,                         # 内边距
    "border_radius": 15,                   # 圆角半径
    "max_width": 220                       # 最大宽度限制
}

# --- AI 逻辑配置 ---
VALID_ACTIONS = ['sit', 'look', 'lay', 'chase']
DEFAULT_ACTION = 'look'  # 默认回退状态
TALK_ON_AUTO_DECISION_PROB = 0.2  # 自动决策时，猫咪开口说话的概率 (20%)
