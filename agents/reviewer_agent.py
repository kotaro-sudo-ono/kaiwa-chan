# file: agents/reviewer_agent.py
from agents.persona_agent import PersonaAgent


class ReviewerAgent(PersonaAgent):
    def __init__(self, model: str = None):
        super().__init__("personas/reviewer.md", model=model)

    def review(self, code: str, task: str) -> str:
        prompt = (
            f"以下のタスクに対するコードをレビューし、改善点を具体的に指摘してください:\n\n"
            f"タスク:\n{task}\n\n"
            f"コード:\n{code}"
        )
        return self.ask(prompt)
