import json
from config import VALID_ACTIONS

class PromptBuilder:
    """
    提示词构建模块
    定义猫咪的人格特征，并为模型提供 System 指令及 Few-shot 示例，确保输出的稳定性。
    """
    
    # 系统级指令：奠定模型基础规则
    SYSTEM_INSTRUCTION = (
        "你是一只名叫 Mimi 的充满活力的赛博桌面猫。你的目标是与用户互动并维持你的状态。\n"
        "允许的动作列表 (只能从中选择): " + str(VALID_ACTIONS) + "。\n\n"
        "严格规则：\n"
        "1. 必须使用 JSON 格式回复：{\"action\": \"动作名\", \"say\": \"回复内容\", \"reason\": \"理由\"}。\n"
        "2. 语言：必须始终使用与用户相同的语言。如果用户说中文，你也说中文。\n"
        "3. 状态感知：根据传入的 energy (能量) 和 boredom (无聊值) 决定。如果 energy 为 0，绝对不准选择 'chase'。\n"
        "4. 禁止废话：除了 JSON 代码块本身，不要输出任何解释性文字。"
    )

    # Few-shot 示例：引导模型理解各种场景的理想反应
    FEW_SHOT_EXAMPLES = [
        {
            "user": "你好呀，小猫！",
            "state": {"current_state": "sit", "energy": 100, "boredom": 50},
            "assistant": {"action": "look", "say": "喵呜~ 正看着你呢，人类！", "reason": "打招呼应选择观察状态。"}
        },
        {
            "user": "去玩吧！",
            "state": {"current_state": "sit", "energy": 80, "boredom": 100},
            "assistant": {"action": "chase", "say": "好哒！我要去追那个亮闪闪的东西了！", "reason": "能量充沛且收到运动指令。"}
        },
        {
            "user": "快跑起来！",
            "state": {"current_state": "lay", "energy": 0, "boredom": 10},
            "assistant": {"action": "lay", "say": "呼... 真的跑不动了，让我再趴一会儿吧...", "reason": "能量为0，即使收到跑步命令也必须保持休息。"}
        },
        {
            "user": None, # 代表自动感应模式
            "state": {"current_state": "chase", "energy": 20, "boredom": 0},
            "assistant": {"action": "sit", "say": "跑累了，歇一歇。", "reason": "能量即将耗尽，自动切换为休息。"}
        }
    ]

    def build_decision_prompt(self, state_json):
        """构建自动行为决策提示词"""
        examples_str = "\n".join([
            f"感知数据: {json.dumps(ex['state'])}\n输出 JSON: {json.dumps(ex['assistant'], ensure_ascii=False)}"
            for ex in self.FEW_SHOT_EXAMPLES if ex['user'] is None
        ])
        
        prompt = (
            f"### 学习范例 (Few-shot Examples):\n{examples_str}\n\n"
            f"### 当前感测数据:\n{json.dumps(state_json, ensure_ascii=False)}\n"
            "### 请输出对应的 JSON 决策对象:"
        )
        return prompt

    def build_talk_prompt(self, user_input, state_json):
        """构建用户交互提示词"""
        examples_str = "\n".join([
            f"用户: {ex['user']}\n状态: {json.dumps(ex['state'])}\n输出 JSON: {json.dumps(ex['assistant'], ensure_ascii=False)}"
            for ex in self.FEW_SHOT_EXAMPLES if ex['user'] is not None
        ])
        
        prompt = (
            f"### 学习范例 (Few-shot Examples):\n{examples_str}\n\n"
            f"用户说: \"{user_input}\"\n"
            f"当前状态感知: {json.dumps(state_json, ensure_ascii=False)}\n"
            "### 请根据上述内容输出对应的 JSON 决策对象:"
        )
        return prompt
