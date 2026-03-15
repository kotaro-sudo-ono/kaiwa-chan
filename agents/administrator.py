# file: agents/administrator.py
from agents.persona_agent import PersonaAgent
from agents.coder_agent import CoderAgent
from agents.reviewer_agent import ReviewerAgent

# Keywords that indicate a coding task (Japanese + English)
_CODING_KEYWORDS = (
    "コード", "実装", "関数", "プログラム", "スクリプト",
    "書いて", "作って", "ください", "書く", "作る",
    "python", "Python", "class", "def ",
)


class Administrator(PersonaAgent):
    """
    Controller agent.

    - General input  → answers directly via Ollama
    - Coding request → CoderAgent generates code → ReviewerAgent reviews
                       → Administrator summarises into a final reply
    """

    def __init__(self, model: str = None):
        super().__init__("personas/administrator.md", model=model)
        self.coder = CoderAgent(model=model)
        self.reviewer = ReviewerAgent(model=model)

    def _is_coding_task(self, text: str) -> bool:
        return any(kw in text for kw in _CODING_KEYWORDS)

    def process(self, user_input: str) -> str:
        """Main entry point. Returns the final text response."""
        if self._is_coding_task(user_input):
            return self._handle_coding(user_input)
        return self.ask(user_input)

    def _handle_coding(self, user_input: str) -> str:
        print("[Administrator] コーディングタスクを検出 → CoderAgent に委譲")
        code = self.coder.generate_code(user_input)
        print(f"[Coder]\n{code}\n")

        print("[Administrator] ReviewerAgent にレビューを依頼")
        review = self.reviewer.review(code, user_input)
        print(f"[Reviewer]\n{review}\n")

        summary_prompt = (
            "以下のコード生成結果とレビューを統合し、"
            "ユーザへの最終回答を日本語で簡潔にまとめてください。\n\n"
            f"生成されたコード:\n{code}\n\n"
            f"レビュー:\n{review}"
        )
        return self.ask(summary_prompt)
