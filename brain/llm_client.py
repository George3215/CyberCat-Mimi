import httpx
import json
import asyncio
import re
from config import OLLAMA_URL, OLLAMA_MODEL, LLM_PARAMS, DEFAULT_ACTION

class LLMClient:
    """
    Ollama 客户端模块
    负责与本地大语言模型进行异步通信，处理请求载体并解析结构化 JSON。
    """
    def __init__(self):
        self.url = OLLAMA_URL
        self.model = OLLAMA_MODEL

    async def generate_response(self, prompt, system=None):
        """
        向 Ollama 发送请求并获取回复
        :param prompt: 用户提示词
        :param system: 系统指令 (用于强化规则遵循)
        :return: 解析后的字典 {action, say, reason} 或默认回退字典
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "format": "json", # 强制模型返回 JSON 格式
            "options": LLM_PARAMS
        }
        
        if not system:
            del payload["system"]
        
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(self.url, json=payload)
                response.raise_for_status()
                data = response.json()
                raw_text = data.get("response", "").strip()
                
                # 情况处理：部分模型可能在 JSON 外层包裹 <think> 推理块
                clean_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL).strip()
                
                # 使用正则表达式从回复中提取第一个完整的 JSON 对象 {...}
                json_match = re.search(r'(\{.*\})', clean_text, re.DOTALL)
                if json_match:
                    clean_text = json_match.group(1)
                
                try:
                    res_dict = json.loads(clean_text)
                    # 鲁棒性：将键名统一转为小写，处理模型可能返回的 Action/Say 等变体
                    res_dict = {k.lower(): v for k, v in res_dict.items()}
                    
                    if "action" in res_dict:
                        return res_dict
                except json.JSONDecodeError:
                    print(f"JSON 解析失败，原始文本: {clean_text}")
                
                # 如果解析彻底失败，返回默认的安全回退结构
                return {"action": DEFAULT_ACTION, "say": "喵呜？(信号干扰中...)", "reason": "parsing failed"}
                
        except Exception as e:
            print(f"调用 Ollama 时发生通信错误: {e}")
            return {"action": DEFAULT_ACTION, "say": "喵... (好像掉线了)", "reason": str(e)}
