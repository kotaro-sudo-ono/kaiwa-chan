# file: agents/developer_agent.py
import subprocess
from pathlib import Path

# Claude Code に許可するツール（Bash を除外することでファイル削除を防ぐ）
_ALLOWED_TOOLS = "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch"


class DeveloperAgent:
    """
    Claude Code CLI を使って実際にファイルを編集するエージェント。
    - Bash ツールを禁止することでファイル削除・破壊的操作を防ぐ
    - 実装後、変更概要とスキル提案を Administrator に返す
    """

    PROJECT_ROOT = Path(__file__).parent.parent

    def implement(self, task: str, review_notes: str = "") -> dict:
        """
        Claude Code CLI でタスクを実装する。

        Returns:
            {
                "summary": str,           # 実装概要（Administrator に渡す）
                "skill_proposals": list   # 提案スキルのリスト
            }
        """
        prompt = self._build_prompt(task, review_notes)
        print("[DeveloperAgent] claude CLI を起動して実装中...")
        output = self._run_claude(prompt)
        return self._parse_result(output)

    def _build_prompt(self, task: str, review_notes: str) -> str:
        prompt = f"以下のタスクをこのリポジトリ内で実装してください:\n\n{task}"
        if review_notes:
            prompt += f"\n\n## 設計上の考慮事項（Reviewerより）\n{review_notes}"
        prompt += (
            "\n\n## 報告形式"
            "\n実装後、以下の形式で日本語で報告してください:"
            "\n1. 変更したファイルと内容の概要"
            "\n2. 動作確認方法"
            "\n3. この機能に関連してClaude Codeスキル（スラッシュコマンド）の追加が有効なら"
            "\n   「SKILL_PROPOSAL: <スキル名> - <説明>」の形式で追記してください"
        )
        return prompt

    def _run_claude(self, prompt: str) -> str:
        try:
            result = subprocess.run(
                [
                    "claude", "-p", prompt,
                    "--allowedTools", _ALLOWED_TOOLS,
                    "--dangerously-skip-permissions",
                ],
                cwd=str(self.PROJECT_ROOT),
                capture_output=True,
                text=True,
                timeout=300,
                encoding="utf-8",
            )
            return result.stdout or result.stderr or "（出力なし）"
        except subprocess.TimeoutExpired:
            return "タイムアウト: 処理が5分を超えました"
        except FileNotFoundError:
            return "エラー: claude コマンドが見つかりません。Claude Code がインストールされているか確認してください"

    def _parse_result(self, output: str) -> dict:
        skill_proposals = []
        summary_lines = []

        for line in output.splitlines():
            if line.startswith("SKILL_PROPOSAL:"):
                skill_proposals.append(line.replace("SKILL_PROPOSAL:", "").strip())
            else:
                summary_lines.append(line)

        return {
            "summary": "\n".join(summary_lines).strip(),
            "skill_proposals": skill_proposals,
        }
