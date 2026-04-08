import asyncio
import random
from PyQt6.QtCore import QThread, pyqtSignal
from brain.llm_client import LLMClient
from brain.prompt_builder import PromptBuilder
from brain.vision import get_active_window_info
from config import VALID_ACTIONS, DEFAULT_ACTION, TALK_ON_AUTO_DECISION_PROB

class DecisionWorker(QThread):
    """
    AI 决策后台工作线程
    使用 QThread 避免阻塞主 UI 线程。它负责轮询 LLM 并将结果通过信号传回主窗口。
    """
    decision_made = pyqtSignal(str)  # 发射动作切换指令信号
    talk_response = pyqtSignal(str) # 发射猫咪对话内容信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = LLMClient()
        self.builder = PromptBuilder()
        self.pending_state = None  # 待处理的状态感知请求
        self.pending_talk = None   # 待处理的用户对话请求
        self._running = True

    def request_decision(self, state_json):
        """主线程调用：请求一次自动行为决策"""
        self.pending_state = state_json

    def request_talk(self, user_input, state_json):
        """主线程调用：请求一次主动对话决策"""
        self.pending_talk = (user_input, state_json)

    def run(self):
        """线程主运行循环"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        while self._running:
            # 优先处理用户的对话请求
            if self.pending_talk:
                user_input, state_json = self.pending_talk
                self.pending_talk = None
                
                # 在后台线程探测活动窗口
                state_json["active_window"] = get_active_window_info()
                
                prompt = self.builder.build_talk_prompt(user_input, state_json)
                print(f"\n[猫咪思维中心] 收到人类发言: {user_input}")
                
                res_dict = loop.run_until_complete(
                    self.client.generate_response(prompt, system=self.builder.SYSTEM_INSTRUCTION)
                )
                
                if res_dict and isinstance(res_dict, dict):
                    action = res_dict.get("action", DEFAULT_ACTION)
                    say = res_dict.get("say") or res_dict.get("response") or ""
                    inner_voice = res_dict.get("inner_voice", "")
                    mood = res_dict.get("mood_sync", {})
                    
                    if inner_voice:
                        print(f"🕯️ [Mimi 的内心独白] {inner_voice}")
                    if mood:
                        print(f"📊 [情感同步] 眷恋: {mood.get('love_index', 0)} | 孤独: {mood.get('loneliness', 0)} | 心情: {mood.get('current_feeling', '---')}")
                    
                    if say:
                        self.talk_response.emit(say)
                    
                    # 对话可能会改变猫咪当前的动作状态
                    final_action = action if action in VALID_ACTIONS else DEFAULT_ACTION
                    self.decision_made.emit(final_action)

            # 处理定时触发的自动行为决策
            if self.pending_state:
                state_json = self.pending_state
                self.pending_state = None
                
                # 在后台线程探测活动窗口
                state_json["active_window"] = get_active_window_info()
                
                prompt = self.builder.build_decision_prompt(state_json)
                print(f"\n[猫咪思维中心] 定时感知环境: {state_json}")
                
                res_dict = loop.run_until_complete(
                    self.client.generate_response(prompt, system=self.builder.SYSTEM_INSTRUCTION)
                )
                print(f"[猫咪思维中心] 决策结果: {res_dict}")
                
                if res_dict and isinstance(res_dict, dict):
                    action = res_dict.get("action", DEFAULT_ACTION)
                    say = res_dict.get("say") or res_dict.get("response") or ""
                    inner_voice = res_dict.get("inner_voice", "")
                    mood = res_dict.get("mood_sync", {})
                    
                    if inner_voice:
                        print(f"🕯️ [Mimi 的内心独白] {inner_voice}")
                    if mood:
                        print(f"📊 [情感同步] 眷恋: {mood.get('love_index', 0)} | 孤独: {mood.get('loneliness', 0)} | 心情: {mood.get('current_feeling', '---')}")
                    
                    # 自动行为时有一定概率开口说话，增强“活着”的感觉
                    if say and random.random() < TAL_ON_AUTO_DECISION_PROB:
                        self.talk_response.emit(say)
                    
                    # 过滤动作，防止模型幻觉
                    final_action = action if action in VALID_ACTIONS else DEFAULT_ACTION
                    self.decision_made.emit(final_action)
                else:
                    self.decision_made.emit(DEFAULT_ACTION)
            
            self.msleep(100) # 每 100ms 检查一次任务队列

    def stop(self):
        """优雅停止线程"""
        self._running = False
        self.wait()
