# file: agents/administrator.py
from agents.persona_agent import PersonaAgent
from agents.reviewer_agent import ReviewerAgent
from integrations.ollama_session import OllamaSession as ClaudeConversation
from integrations.shogun_bridge import ShogunBridge

# プロジェクト名 → WSLパスのマッピング（Whisperのミス転写も考慮）
_PROJECT_PATHS = {
    # 正確な表記
    "my-kyudo-app": "~/projects/sample_app/my-kyudo-app",
    "kyudo": "~/projects/sample_app/my-kyudo-app",
    "sample_app": "~/projects/sample_app",
    "kyodoApp": "~/projects/kyodoApp_backend",
    "kyodoapp": "~/projects/kyodoApp_backend",
    # Whisper カタカナ転写ゆれ
    "マイキュード": "~/projects/sample_app/my-kyudo-app",
    "マイキュート": "~/projects/sample_app/my-kyudo-app",
    "mycue": "~/projects/sample_app/my-kyudo-app",
    "キョード": "~/projects/kyodoApp_backend",
}

# コーディングタスクを示すキーワード
_CODING_KEYWORDS = (
    "コード", "実装", "関数", "プログラム", "スクリプト",
    "書いて", "作って", "書く", "作る", "追加して", "修正して", "直して", "変更して",
    "変えて", "変えたい", "書き直し", "書き換え", "日本語に", "翻訳", "リードミー", "README",
    "お願いできる", "してほしい", "やってほしい",
    "python", "Python", "class", "def ",
)

# 実装実行トリガーキーワード
_CONFIRM_YES = ("はい", "yes", "ok", "OK", "進めて", "いいよ", "やって", "お願い", "どうぞ", "承認")

# 計画キャンセルキーワード
_CONFIRM_NO = ("いいえ", "no", "やめ", "キャンセル", "中止", "やっぱり", "やめて")


class Administrator(PersonaAgent):
    """
    Controller agent. すべてのエージェントの提案・結果はここを経由してユーザに届く。

    フロー:
    - 一般入力            → 直接 LLM で返答
    - コーディング検出    → ClaudeConversation で対話的にプランニング開始
    - 会話継続中          → 各ユーザー発言を Claude との会話で深掘り
    - 実行キーワード      → 会話から計画をまとめ → Reviewer → DeveloperAgent
    - キャンセルキーワード → 会話リセット
    - 実装完了           → 会話履歴リセット
    """

    def __init__(self, model: str = None):
        super().__init__("personas/administrator.md", model=model)
        self.developer = ShogunBridge()
        self.reviewer = ReviewerAgent(model=model)
        self._conversation = ClaudeConversation()

        # プランニング会話中フラグ
        self._in_planning: bool = False
        self._pending_task: str = ""
        self._pending_project_path: str = ""

    def _is_coding_task(self, text: str) -> bool:
        return any(kw in text for kw in _CODING_KEYWORDS)

    def _detect_project_path(self, text: str) -> str:
        """発言中のプロジェクト名からWSLパスを返す。見つからなければ空文字。"""
        for keyword, path in _PROJECT_PATHS.items():
            if keyword in text:
                return path
        return ""

    def process(self, user_input: str) -> str:
        """メインエントリポイント。最終返答テキストを返す。"""

        # プランニング中はすべての入力を会話として処理
        if self._in_planning:
            return self._handle_planning(user_input)

        if self._is_coding_task(user_input):
            return self._start_planning(user_input)

        return self.ask(user_input)

    # ------------------------------------------------------------------
    # Step 1: プランニング会話を開始
    # ------------------------------------------------------------------
    def _start_planning(self, user_input: str) -> str:
        print("[Administrator] Claude との実装プランニングを開始")
        self._in_planning = True
        self._pending_task = user_input
        self._pending_project_path = self._detect_project_path(user_input)

        reply = self._conversation.chat(user_input)
        return reply + "\n\n「進めて」と言うと実装を開始します。「キャンセル」でやめられます。"

    # ------------------------------------------------------------------
    # Step 2: プランニング中の会話処理
    # ------------------------------------------------------------------
    def _handle_planning(self, user_input: str) -> str:
        # 実行トリガー
        if any(kw in user_input for kw in _CONFIRM_YES):
            print("[Administrator] 実装を開始します")
            return self._execute_coding()

        # キャンセル
        if any(kw in user_input for kw in _CONFIRM_NO):
            self._reset_planning()
            return "了解しました。実装をキャンセルします。"

        # 通常の会話継続
        return self._conversation.chat(user_input)

    # ------------------------------------------------------------------
    # Step 3: 承認後に実際の実装を実行
    # ------------------------------------------------------------------
    def _execute_coding(self) -> str:
        # 会話から計画をまとめる
        print("[Administrator] 会話から実装計画をまとめています...")
        plan = self._conversation.summarize_plan()
        print(f"[Administrator] 計画:\n{plan}\n")

        # Reviewer が設計観点でレビュー
        print("[Administrator] ReviewerAgent に設計レビューを依頼")
        review_notes = self.reviewer.review_task(self._pending_task)
        print(f"[Reviewer]\n{review_notes}\n")

        # DeveloperAgent が Claude Code CLI で実装
        print("[Administrator] DeveloperAgent に実装を委譲")
        result = self.developer.implement(
            self._pending_task,
            review_notes=review_notes,
            project_path=self._pending_project_path,
        )
        summary = result["summary"]
        skill_proposals = result["skill_proposals"]
        print(f"[Developer]\n{summary}\n")

        # 実装完了 → 会話履歴リセット
        self._reset_planning()

        # Administrator が結果を統合して返答
        final_prompt = (
            "以下の実装結果をユーザへ日本語で簡潔に報告してください。\n\n"
            f"タスク:\n{self._pending_task}\n\n"
            f"実装結果:\n{summary}"
        )
        if skill_proposals:
            proposals_text = "\n".join(f"- {s}" for s in skill_proposals)
            final_prompt += (
                f"\n\n## DeveloperAgent からのスキル提案\n{proposals_text}\n\n"
                "スキルの提案もユーザに伝え、追加するか確認してください。"
            )

        return self.ask(final_prompt)

    # ------------------------------------------------------------------
    # 内部ユーティリティ
    # ------------------------------------------------------------------
    def _reset_planning(self):
        """プランニング状態と会話履歴をリセット。"""
        self._in_planning = False
        self._pending_task = ""
        self._pending_project_path = ""
        self._conversation.reset()
        print("[Administrator] プランニング会話をリセットしました")
