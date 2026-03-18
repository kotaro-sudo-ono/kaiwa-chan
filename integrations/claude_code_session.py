# file: integrations/claude_code_session.py
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

_SYSTEM_PROMPT = (
    "あなたは実装プランニングの専門家です。"
    "ユーザーが話しかけてくる実装タスクについて、一緒に設計を練り上げてください。"
    "変更するファイル、実装方針、注意点などを対話的に確認・提案する。"
    "不明点はユーザーに質問して明確にする。"
    "会話は日本語で行う。"
    "実際のファイル編集は行わず、プランニングのみ行う。"
)

# プランニング中は読み取り系ツールのみ許可（ファイル編集を防ぐ）
_PLANNING_TOOLS = "Read,Glob,Grep"


class ClaudeCodeSession:
    """
    Claude Code CLI を使ったマルチターン会話セッション。
    ClaudeConversation の drop-in 置き換え。API キー不要。

    - 初回: claude -p "message" --system-prompt ...
    - 2回目以降: claude --continue -p "message"
    - reset(): 次回を新規会話として扱う
    """

    def __init__(self):
        self._started = False

    def chat(self, user_message: str) -> str:
        """ユーザーメッセージを送り、Claude Code CLI の返答を返す。"""
        if not self._started:
            cmd = [
                "claude", "-p", user_message,
                "--system-prompt", _SYSTEM_PROMPT,
                "--allowedTools", _PLANNING_TOOLS,
                "--dangerously-skip-permissions",
            ]
            self._started = True
        else:
            cmd = [
                "claude", "--continue", "-p", user_message,
                "--dangerously-skip-permissions",
            ]

        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
            encoding="utf-8",
        )
        return (result.stdout or result.stderr or "（応答なし）").strip()

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
        """次回呼び出しを新規会話として扱う。"""
        self._started = False
