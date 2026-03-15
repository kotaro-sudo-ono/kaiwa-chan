# file: integrations/llm_interface.py
from dotenv import load_dotenv
import subprocess
import os
import anthropic  # Claude用

load_dotenv()  # .env を読み込む

LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "ollama")  # "ollama" or "claude"
OLLAMA_MODEL = "llama2"   # Ollama用モデル名
CLAUDE_MODEL = "claude-3" # Claude用モデル名
DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LLM_LANGUAGE", "ja")  # デフォルト日本語

# Claudeクライアント
anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
client = anthropic.Client(api_key=anthropic_api_key) if anthropic_api_key else None

def get_response(prompt: str) -> str:
    # 環境変数に応じて先頭に言語指示を追加
    prompt_lang = f"以下の文章に {DEFAULT_LANGUAGE} で答えてください:\n{prompt}"

    if LLM_PROVIDER == "ollama":
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL, prompt_lang],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return (result.stdout or "").strip()

    elif LLM_PROVIDER == "claude":
        if not client:
            return "Claude APIキーが設定されていません"
        resp = client.completions.create(
            model=CLAUDE_MODEL,
            prompt=prompt_lang,
            max_tokens_to_sample=300
        )
        return resp.completion
    else:
        return "不明な LLM プロバイダです"