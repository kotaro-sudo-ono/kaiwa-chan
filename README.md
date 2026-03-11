# Kaiwa-chan
- Kaiwa-chan は
「会話できて仕事もできる人格AI」 を目指した Agent OS プロジェクトです。

## 目的
- 常駐型AI（会話）
- PC操作AI
- AIエージェントチーム
- セキュアなツール実行

##　最終構成

```sh
User
 ↓
Kaiwa-chan (Persona AI)
 ↓
Cognitive System
 ↓
Task Manager
 ↓
Agent Manager
 ↓
Security Layer
 ↓
Tools
```

## アーキテクチャ
- Kaiwa-chanは Agent OS構造 を採用しています。
```sh
User
 ↓
Conversation Layer
 ↓
Persona Agent
 ↓
Cognitive System
 ↓
Agent System
 ↓
Tool Execution Layer
```

## 使用するAIツール
- このプロジェクトでは以下のOSSを活用予定です。

| 用途                  | ツール                |
| ------------------- | ------------------ |
| 人格AI                | OpenClaw           |
| PC操作                | Open Interpreter   |
| LLM                 | OpenAI / Local LLM |
| Agent orchestration | LangGraph（予定）      |

## ディレクトリ構造

```sh
kaiwa-chan/
 ├ core/                         # Agent OS カーネル
 │
 │   ├ memory/                   # AI記憶システム
 │   │   ├ memory_manager.py
 │   │   ├ models.py
 │   │   └ memory_store.py
 │   │
 │   ├ tools/                    # ツール管理
 │   │   ├ tool.py
 │   │   ├ registry.py
 │   │   └ capability.py
 │   │
 │   ├ task/                     # AIの仕事システム
 │   │   ├ task_model.py
 │   │   ├ task_manager.py
 │   │   └ task_queue.py
 │   │
 │   ├ event/                    # AI通信
 │   │   ├ event_bus.py
 │   │   └ event_types.py
 │   │
 │   ├ security/                 # セキュリティ
 │   │   ├ permission_manager.py
 │   │   └ risk_scanner.py
 │   │
 │   └ cognition/                # 思考システム（Step4）
 │       ├ observe.py
 │       ├ think.py
 │       ├ plan.py
 │       ├ act.py
 │       └ reflect.py
 │
 ├ agents/                       # AIエージェント
 │   ├ base_agent.py
 │   └ agent_manager.py
 │
 ├ integrations/                 # 外部ツール
 │   ├ python_runner.py
 │   ├ browser.py
 │   ├ filesystem.py
 │   └ git_tools.py
 │
 ├ runtime/                      # 実行環境
 │   ├ agent_runtime.py
 │   └ scheduler.py
 │
 ├ config/                       # 設定
 │   └ settings.py
 │
 ├ tests/                        # テスト
 │
 └ main.py                       # 起動
 ```

### core/
- AIの OSカーネル部分。すべてのエージェントがこのレイヤーを利用します。
#### 含まれる機能
- memory
- tools
- task
- event
- security
- cognition
### core/memory
- AIの 記憶管理システム。人格と知識の基盤になります。
#### memory_manager.py
- 記憶の管理クラス。
##### 機能
- 記憶追加
- 記憶検索
- 記憶更新

##### 例
```sh
memory_manager.add(memory)
memory_manager.search(keyword)
```
#### models.py
- 記憶のデータ構造。
```sh
Memory
 ├ content
 ├ type
 └ timestamp
 ```

#### memory_store.py
- 記憶保存層。
- 将来的に対応予定
- SQLite
- VectorDB
- Redis

### core/tools
- AIが使用するツール管理。
- AIは ToolRegistry経由 でツールを実行します。

#### tool.py
- ツールの基本モデル。
```sh
Tool(
 name="run_python",
 description="execute python code",
 capability="code_execution",
 risk_level="medium"
)
```
#### registry.py
- ツール登録システム。
##### 機能
- ツール登録
- ツール取得
- ツール一覧

##### 例
```sh
registry.register(tool)
registry.get("run_python")
```
#### capability.py
- ツール能力定義。
```sh
filesystem
browser
code_execution
git_operation
```

### core/task
- AIの 仕事管理システム。
- AIはすべて Task単位 で動作します。

#### task_model.py
- タスクモデル。
```sh
{
 "task_id": "uuid",
 "type": "code_generation",
 "payload": {},
 "status": "pending"
}
```

#### task_manager.py
- タスク管理。

##### 機能
- タスク作成
- タスク更新
- タスク取得

#### task_queue.py
- タスク実行キュー。
- AIエージェントがここからタスクを取得します。

### core/event
- AI間通信システム。
- エージェント同士は イベントベース通信 を行います。

#### event_bus.py
- イベント配信。

```sh
event_bus.emit("task_created", task)
```

#### event_types.py
- イベント種類。

```sh
task_created
task_completed
agent_spawned
tool_called
```

### core/security
- ツール実行の セキュリティレイヤー。
- OpenClawのセキュリティ思想を参考にしています。

#### permission_manager.py
- AI権限管理。
```sh
low risk
medium risk
high risk
```

#### risk_scanner.py
- 危険操作の検知。
```sh
rm -rf
curl unknown script
filesystem deletion
```

### core/cognition
- AI思考システム。
- Step4で実装予定。
- 思考ループ
```sh
observe
think
plan
act
reflect
```

### agents/
- AIエージェント実装。

#### base_agent.py
- すべてのエージェントの基底クラス。

##### 機能
- memory access
- tool access
- task handling

#### agent_manager.py
- エージェント管理。

##### 機能
- エージェント生成
- エージェント登録
- エージェント停止

##### 将来
```sh
Developer Agent
Research Agent
Reviewer Agent
```
などを生成。

### integrations/
- 外部ツール。

#### python_runner.py
- Pythonコード実行。

##### 用途
- データ処理
- スクリプト実行
- 自動化

#### browser.py
- ブラウザ操作。

#### 用途
- web search
- scraping
- 情報取得

#### filesystem.py
- ファイル操作。
```sh
read file
write file
create directory
git_tools.py
```
- Git操作。
```sh
git clone
git commit
git push
```

### runtime/
- AIシステム実行管理。

#### agent_runtime.py
- AI実行環境。

##### 機能
- エージェント起動
- タスク処理
- イベント処理

#### scheduler.py
- タスクスケジューラ。
- AIエージェントへの仕事分配。

### config/
- システム設定。

#### settings.py
- 設定管理。

##### 例
```sh
LLM設定
APIキー
実行設定
```

### tests/
- ユニットテスト。

#### main.py
- システム起動。
```sh
python main.py
```

## 開発ロードマップ
### Step0
- Agent OS Core
```sh
memory
tools
task
event
security
```

### Step1
- PC操作AI
```sh
filesystem
browser
python
git
```

### Step2
- Agent System
```sh
agent manager
task scheduler
```

### Step3
- AIエージェントチーム
```sh
developer agent
research agent
reviewer agent
```

### Step4
- 人格AI
```sh
Kaiwa-chan persona
cognitive loop
conversation system
```




