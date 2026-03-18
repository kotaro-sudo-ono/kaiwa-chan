# file: integrations/claude_conversation.py
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

CLAUDE_MODEL = os.getenv("CLAUDE_PLANNING_MODEL", "claude-sonnet-4-6")

_SYSTEM_PROMPT = """\
あなたは実装プランニングの専門家です。
ユーザーが話しかけてくる実装タスクについて、一緒に設計を練り上げてください。

- 変更するファイル、実装方針、注意点などを対話的に確認・提案する
- 不明点はユーザーに質問して明確にする
- 実装が決まってきたら、ポイントを整理して伝える
- 会話は日本語で行う
"""


class ClaudeConversation:
    """
    Anthropic Messages API を使ったマルチターン会話セッション。
    会話履歴を保持し、reset() で初期化できる。
    """

    def __init__(self, model: str = CLAUDE_MODEL):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self._history: list[dict] = []

    def chat(self, user_message: str) -> str:
        """ユーザーメッセージを送り、アシスタントの返答を返す。履歴に両方追記。"""
        self._history.append({"role": "user", "content": user_message})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=_SYSTEM_PROMPT,
            messages=self._history,
        )
        reply = response.content[0].text
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def summarize_plan(self) -> str:
        """会話履歴から合意した実装計画を箇条書きでまとめる。"""
        summary_prompt = (
            "これまでの会話で合意した実装計画を、以下の形式で日本語でまとめてください:\n"
            "- 変更・追加するファイル\n"
            "- 実装内容の要点\n"
            "- 注意事項\n"
        )
        return self.chat(summary_prompt)

    def reset(self):
        """会話履歴をリセットする。"""
        self._history = []
