# file: integrations/ollama.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


class OllamaClient:
    def __init__(self, model: str = None, base_url: str = OLLAMA_BASE_URL):
        self.model = model or DEFAULT_MODEL
        self.base_url = base_url

    def chat(self, messages: list[dict], model: str = None) -> str:
        """Send a list of messages and return the assistant reply."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model or self.model,
            "messages": messages,
            "stream": False,
        }
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["message"]["content"].strip()
        except requests.exceptions.ConnectionError:
            return "Ollama に接続できません。Ollama が起動しているか確認してください。"
        except Exception as e:
            return f"Ollama エラー: {e}"

    def generate(self, prompt: str, system: str = None, model: str = None) -> str:
        """Convenience wrapper: optional system prompt + user prompt."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, model=model)
