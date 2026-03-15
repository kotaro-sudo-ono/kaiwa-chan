# file: agents/coder_agent.py
from agents.persona_agent import PersonaAgent


class CoderAgent(PersonaAgent):
    def __init__(self, model: str = None):
        super().__init__("personas/coder.md", model=model)

    def generate_code(self, task: str) -> str:
        prompt = f"以下のタスクに対してコードを生成してください:\n\n{task}"
        return self.ask(prompt)
