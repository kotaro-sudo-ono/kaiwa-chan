# file: autonomous_loop.py
import time
import threading

PROMPT_TEMPLATE = """\
あなたは常駐型AIアシスタントです。
以下の状況を見て、今ユーザーに話しかける必要があるか判断してください。

【最近の会話メモリ（最大5件）】
{memories}

【最後にユーザーが話してから経過した時間】
{idle_seconds}秒

判断ルール:
- 話しかける必要があるなら、日本語で一言メッセージを返してください。
- 必要なければ「NONE」とだけ返してください。
- メッセージは短く自然な日本語にしてください（1〜2文）。
"""


class AutonomousLoop:
    def __init__(self, memory_manager, administrator, task_manager,
                 is_speaking: threading.Event, interval: int = 60):
        self.memory_manager = memory_manager
        self.administrator = administrator
        self.task_manager = task_manager
        self.is_speaking = is_speaking
        self.interval = interval
        self._stop_event = threading.Event()
        self._last_user_time = time.time()

    def update_last_user_time(self):
        """ユーザーが話したとき呼び出す。アイドル時間をリセット。"""
        self._last_user_time = time.time()

    def start(self):
        t = threading.Thread(target=self._run, daemon=True)
        t.start()
        return t

    def stop(self):
        self._stop_event.set()

    def _build_prompt(self) -> str:
        memories = self.memory_manager.recall_latest(5)
        memory_text = "\n".join(f"- {m}" for m in memories) if memories else "（なし）"
        idle = int(time.time() - self._last_user_time)
        return PROMPT_TEMPLATE.format(memories=memory_text, idle_seconds=idle)

    def _run(self):
        print("[AutonomousLoop] 自律ループ開始")
        while not self._stop_event.is_set():
            time.sleep(self.interval)

            if self.is_speaking.is_set():
                continue

            prompt = self._build_prompt()
            decision = self.administrator.ask(prompt).strip()
            print(f"[AutonomousLoop] 判断: {decision[:80]}")

            if decision and decision.upper() != "NONE":
                self.task_manager.create_task(
                    task_type="print_message",
                    payload={"message": decision},
                )
