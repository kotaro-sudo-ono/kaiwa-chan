# file: agents/persona_agent.py
import re
from pathlib import Path
from integrations.ollama import OllamaClient


class PersonaAgent:
    """Base agent that loads a persona from a Markdown file and talks to Ollama."""

    def __init__(self, persona_path: str, model: str = None):
        self.persona_path = Path(persona_path)
        self.ollama = OllamaClient(model=model)
        self.persona = self._load_persona()
        self.system_prompt = self._build_system_prompt()

    def _load_persona(self) -> dict:
        text = self.persona_path.read_text(encoding="utf-8")
        persona = {}

        # Extract "# Persona: <name>"
        name_match = re.search(r"^#\s*Persona:\s*(.+)$", text, re.MULTILINE)
        if name_match:
            persona["name"] = name_match.group(1).strip()

        # Extract "key: value" lines (skip headings)
        for line in text.splitlines():
            if line.startswith("#") or ":" not in line:
                continue
            key, _, value = line.partition(":")
            persona[key.strip()] = value.strip()

        return persona

    def _build_system_prompt(self) -> str:
        name = self.persona.get("name", "AI")
        lines = [f"あなたは {name} です。"]
        for key in ("性格", "口調", "役割", "言語"):
            if key in self.persona:
                lines.append(f"{key}: {self.persona[key]}")
        return "\n".join(lines)

    def ask(self, prompt: str) -> str:
        """Send a prompt with this agent's system prompt and return the response."""
        return self.ollama.generate(prompt, system=self.system_prompt)
