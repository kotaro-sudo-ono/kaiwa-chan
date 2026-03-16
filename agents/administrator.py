# file: agents/administrator.py
from agents.persona_agent import PersonaAgent
from agents.developer_agent import DeveloperAgent
from agents.reviewer_agent import ReviewerAgent

# コーディングタスクを示すキーワード
_CODING_KEYWORDS = (
    "コード", "実装", "関数", "プログラム", "スクリプト",
    "書いて", "作って", "書く", "作る", "追加して", "修正して", "直して", "変更して",
    "python", "Python", "class", "def ",
)

# ユーザが計画を承認したと判断するキーワード
_CONFIRM_YES = ("はい", "yes", "ok", "OK", "進めて", "いいよ", "やって", "お願い", "どうぞ", "承認")

# ユーザが計画を拒否したと判断するキーワード
_CONFIRM_NO = ("いいえ", "no", "やめ", "キャンセル", "中止", "やっぱり", "やめて")


class Administrator(PersonaAgent):
    """
    Controller agent. すべてのエージェントの提案・結果はここを経由してユーザに届く。

    フロー:
    - 一般入力        → 直接 LLM で返答
    - コーディング    → ① 計画生成 → ② ユーザ確認待ち
                        → ③ 承認後: Reviewer（設計レビュー）→ DeveloperAgent（Claude Code CLI）
                        → ④ Administrator が結果 + スキル提案を統合して返答
    """

    def __init__(self, model: str = None):
        super().__init__("personas/administrator.md", model=model)
        self.developer = DeveloperAgent()
        self.reviewer = ReviewerAgent(model=model)

        # 確認待ち状態
        self._awaiting_confirmation: bool = False
        self._pending_task: str = ""
        self._pending_plan: str = ""

    def _is_coding_task(self, text: str) -> bool:
        return any(kw in text for kw in _CODING_KEYWORDS)

    def process(self, user_input: str) -> str:
        """メインエントリポイント。最終返答テキストを返す。"""
        if self._awaiting_confirmation:
            return self._handle_confirmation(user_input)

        if self._is_coding_task(user_input):
            return self._propose_plan(user_input)

        return self.ask(user_input)

    # ------------------------------------------------------------------
    # Step 1: 計画を生成してユーザに提案
    # ------------------------------------------------------------------
    def _propose_plan(self, user_input: str) -> str:
        print("[Administrator] 実装計画を生成中...")
        plan_prompt = (
            "以下のコーディングタスクについて、実装計画を日本語で作成してください。\n"
            "変更予定のファイル、追加する機能、注意点を箇条書きで簡潔にまとめてください:\n\n"
            f"{user_input}"
        )
        plan = self.ask(plan_prompt)
        print(f"[Administrator] 計画:\n{plan}\n")

        # 確認待ち状態に移行
        self._awaiting_confirmation = True
        self._pending_task = user_input
        self._pending_plan = plan

        return f"以下の実装計画を提案します。\n\n{plan}\n\nこの計画で進めてよいですか？"

    # ------------------------------------------------------------------
    # Step 2: ユーザの承認・拒否を処理
    # ------------------------------------------------------------------
    def _handle_confirmation(self, user_input: str) -> str:
        if any(kw in user_input for kw in _CONFIRM_YES):
            self._awaiting_confirmation = False
            return self._execute_coding(self._pending_task, self._pending_plan)

        if any(kw in user_input for kw in _CONFIRM_NO):
            self._awaiting_confirmation = False
            self._pending_task = ""
            self._pending_plan = ""
            return "了解しました。実装をキャンセルします。"

        # 判断できない場合は再確認
        return "承認する場合は「はい」、キャンセルする場合は「いいえ」とお答えください。"

    # ------------------------------------------------------------------
    # Step 3: 承認後に実際の実装を実行
    # ------------------------------------------------------------------
    def _execute_coding(self, user_input: str, plan: str) -> str:
        # Reviewer が設計観点でレビュー
        print("[Administrator] ReviewerAgent に設計レビューを依頼")
        review_notes = self.reviewer.review_task(user_input)
        print(f"[Reviewer]\n{review_notes}\n")

        # DeveloperAgent が Claude Code CLI で実際に実装
        print("[Administrator] DeveloperAgent に実装を委譲")
        result = self.developer.implement(user_input, review_notes=review_notes)
        summary = result["summary"]
        skill_proposals = result["skill_proposals"]
        print(f"[Developer]\n{summary}\n")

        # Administrator が結果を統合して最終返答を生成
        final_prompt = (
            "以下の実装結果をユーザへ日本語で簡潔に報告してください。\n\n"
            f"タスク:\n{user_input}\n\n"
            f"実装結果:\n{summary}"
        )
        if skill_proposals:
            proposals_text = "\n".join(f"- {s}" for s in skill_proposals)
            final_prompt += (
                f"\n\n## DeveloperAgent からのスキル提案\n{proposals_text}\n\n"
                "スキルの提案もユーザに伝え、追加するか確認してください。"
            )

        return self.ask(final_prompt)
