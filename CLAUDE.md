# CLAUDE.md

このファイルは、リポジトリ内のコードを操作する際に Claude Code (claude.ai/code) へのガイダンスを提供します。

## プロジェクト概要

Kaiwa-chan は「Agent OS」— 音声で会話し、タスクを実行できる常駐型 AI です。コアループは以下の通り：

```
User speaks → Whisper (STT) → LLM → Observer → TaskQueue → VoiceVox (TTS)
```

## 実行方法

```bash
# メイン音声会話ループ（現在のアクティブなエントリーポイント）
python main_loop.py

# VoiceVox TTS 出力のテスト
python tests/test_voice.py

# マイク入力と Whisper 文字起こしのテスト
python tests/test_mic_input.py

# 基本的なシステム統合テスト（音声ループなし）
python main.py
```

**実行前に必要な外部サービス：**
- **VoiceVox** が `http://localhost:50021` でローカル起動していること
- **Ollama** がローカル起動していること（`LLM_PROVIDER=ollama` の場合）

## 環境設定

環境変数は`.env` に置く：

```env
LLM_PROVIDER=ollama   # "ollama" or "claude"
ANTHROPIC_API_KEY=xxxxxxx
DEFAULT_LLM_LANGUAGE=ja
```

## 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

注意：`requirements.txt` にはすべての依存パッケージが含まれていない。以下は手動でインストールが必要：
- `keyboard`
- `anthropic`
- `simpleaudio`
- `python-dotenv`
- `requests`

## アーキテクチャ

### データフロー

```
main_loop.py
  ├─ whisper_integration.py   # Space key → record mic → faster-whisper STT
  ├─ llm_interface.py         # Send text to Ollama or Claude API
  ├─ core/cognition/observe.py # Store to memory, create tasks from LLM reply
  ├─ core/task/task_queue.py  # FIFO queue of Task objects
  └─ voicevox.py              # POST to VoiceVox API → play WAV
```

### コアレイヤー (`core/`)

Agent OS のカーネル。すべてのレイヤーは `main_loop.py` で初期化される：

- **`core/memory/`** — `MemoryStore`（生ストレージ）+ `MemoryManager`（add/search/get_all）。現在はインメモリのみ。将来的に SQLite・VectorDB・Redis を検討。
- **`core/task/`** — `TaskModel`（uuid, type, payload, status）+ `TaskQueue`（FIFO）+ `TaskManager`（タスクの作成・更新・取得、イベント発行）。
- **`core/event/`** — エージェント間通信用の `EventBus`。イベント種別：`task_created`、`task_completed`、`agent_spawned`、`tool_called`。
- **`core/cognition/`** — 認知ループ：`observe → think → plan → act → reflect`。現在はメインループに `Observer` のみ組み込み済み。
- **`core/security/`** — `PermissionManager`（low/medium/high リスク）+ `RiskScanner`（`rm -rf` などの危険操作を検出）。
- **`core/tools/`** — `name`・`description`・`capability`・`risk_level` を持つ `Tool` モデル。`ToolRegistry` で登録・検索。ケーパビリティ：`filesystem`、`browser`、`code_execution`、`git_operation`。

### 外部連携 (`integrations/`)

外部ツールのラッパー：
- `whisper_integration.py` — `transcribe_audio()`：スペースキー長押しで録音し、`faster-whisper`（small モデル、CPU、日本語）で文字起こし
- `voicevox.py` — `speak(text)`：VoiceVox REST API を呼び出し、`voice.wav` を保存して `simpleaudio` で再生
- `llm_interface.py` — `get_response(prompt)`：`LLM_PROVIDER` に応じて Ollama（`subprocess`）または Claude（`anthropic` SDK）にルーティング

### エージェント (`agents/`)

- `BaseAgent` — メモリ・ツール・タスクにアクセスできる基底クラス
- `AgentManager` — エージェントのスポーン・登録・停止。将来：Developer・Research・Reviewer エージェント

### ランタイム (`runtime/`)

- `AgentRuntime` — エージェントのライフサイクルおよびイベント・タスク処理
- `Scheduler` — エージェントへのタスク振り分け

## 開発ロードマップ

- Step0 ✅ Agent OS コア（memory, tools, task, event, security）
- Step1 ✅ PC 操作連携（filesystem, browser, python, git）
- Step2 ✅ エージェントシステム（manager, scheduler）
- Step3 — AI エージェントチーム（developer/research/reviewer エージェント）
- Step4 — ペルソナ AI（Kaiwa-chan ペルソナ、フル認知ループ、会話システム）
