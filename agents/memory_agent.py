# file: agents/memory_agent.py
import json
from agents.persona_agent import PersonaAgent
from core.memory.memory_store import MemoryStore


class MemoryAgent(PersonaAgent):
    """
    会話を分析してユーザのパーソナルデータを長期記憶に保存するエージェント。
    AIが自ら「これは覚えるべきか」を判断する。
    """

    def __init__(self, memory_store: MemoryStore, model: str = None):
        super().__init__("personas/memory_agent.md", model=model)
        self.memory_store = memory_store

    def process(self, user_input: str, ai_reply: str) -> dict | None:
        """
        会話を渡してLLMに判断させ、必要なら記憶に保存する。
        保存した場合は {"key": ..., "value": ...} を返す。保存しない場合は None。
        """
        prompt = (
            f"ユーザの発言: {user_input}\n"
            f"AIの返答: {ai_reply}\n\n"
            "この会話にユーザのパーソナルデータが含まれているか判断し、JSONで回答してください。"
        )

        raw = self.ask(prompt)

        # LLMの出力からJSONを抽出
        try:
            # コードブロックや余分なテキストを除去
            start = raw.find("{")
            end = raw.rfind("}") + 1
            result = json.loads(raw[start:end])
        except (ValueError, json.JSONDecodeError):
            print(f"[MemoryAgent] JSON解析失敗: {raw}")
            return None

        if result.get("should_save"):
            entry = {"key": result.get("key", "情報"), "value": result.get("value", "")}
            self.memory_store.add(entry)
            print(f"[MemoryAgent] 記憶に保存: {entry}")
            return entry

        print("[MemoryAgent] 記憶不要と判断")
        return None
