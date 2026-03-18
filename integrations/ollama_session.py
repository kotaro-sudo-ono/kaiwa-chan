# file: integrations/ollama_session.py
from integrations.ollama import OllamaClient

_SYSTEM_PROMPT = """\
あなたは実装プランニングの専門家です。
ユーザーが話しかけてくる実装タスクについて、一緒に設計を練り上げてください。

- 変更するファイル、実装方針、注意点などを対話的に確認・提案する
- 不明点はユーザーに質問して明確にする
- 実装が決まってきたら、ポイントを整理して伝える
- 会話は日本語で行う
- 実際のファイル編集は行わず、プランニングのみ行う
"""


class OllamaSession:
    """
    Ollama を使ったマルチターン会話セッション。
    ClaudeConversation / ClaudeCodeSession の drop-in 置き換え。
    APIキー不要。
    """

    def __init__(self):
        self.ollama = OllamaClient()
        self._history: list[dict] = [
            {"role": "system", "content": _SYSTEM_PROMPT}
        ]

    def chat(self, user_message: str) -> str:
        self._history.append({"role": "user", "content": user_message})
        reply = self.ollama.chat(self._history)
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def summarize_plan(self) -> str:
        summary_prompt = (
            "これまでの会話で合意した実装計画を、以下の形式で日本語でまとめてください:\n"
            "- 変更・追加するファイル\n"
            "- 実装内容の要点\n"
            "- 注意事項\n"
        )
        return self.chat(summary_prompt)

    def reset(self):
        self._history = [{"role": "system", "content": _SYSTEM_PROMPT}]
