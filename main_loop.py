# file: main_loop.py
import time
import threading
import keyboard

from integrations.whisper_integration import transcribe_audio
from integrations.voicevox import speak
from agents.administrator import Administrator

from core.memory.memory_manager import MemoryManager
from core.memory.memory_store import MemoryStore
from core.task.task_manager import TaskManager
from core.task.task_queue import TaskQueue
from core.event.event_bus import EventBus
from core.cognition.observe import Observer


def record_and_process(observer, task_queue, shogun: Administrator):
    """
    録音→文字起こし→Administrator（マルチエージェント）→Observer→TaskQueue
    スレッドで回す
    """
    while True:
        if keyboard.is_pressed("esc"):
            print("終了キー押下 → 録音スレッド停止")
            break

        # 録音 & 文字起こし
        user_text = transcribe_audio()
        if not user_text:
            continue

        print(f"ユーザ入力: {user_text}")

        # Administrator（マルチエージェント）で返答生成
        llm_reply = shogun.process(user_text)
        print(f"Administrator 返答: {llm_reply}")

        # Observer に渡してタスク生成
        context = observer.observe(user_text, llm_reply=llm_reply)
        print(f"Observer Context: {context}")

        # TaskQueue にタスク追加
        for task in context.get("tasks", []):
            task_queue.push(task)

        time.sleep(0.1)


def main_loop():
    # --- 初期化 ---
    event_bus = EventBus()
    memory_store = MemoryStore()
    memory_manager = MemoryManager(memory_store)
    task_queue = TaskQueue()
    task_manager = TaskManager(event_bus, task_queue)
    observer = Observer(memory_manager, task_manager)
    shogun = Administrator()  # マルチエージェントコントローラ

    print("=== Kaiwa-chan AI 常駐ループ 起動 ===")
    print("'space'で録音開始・離すと終了、'esc'で全体終了")

    # 録音＆文字起こしスレッド開始
    t = threading.Thread(target=record_and_process, args=(observer, task_queue, shogun), daemon=True)
    t.start()

    try:
        while True:
            if keyboard.is_pressed("esc"):
                print("終了キー押下 → メインループ終了")
                break

            # TaskQueue からタスクを取得して実行
            while not task_queue.is_empty():
                task = task_queue.pop()
                print(f"タスク実行: {task.type}, payload={task.payload}")
                if task.type == "print_message":
                    # VoiceVoxで音声出力
                    speak(task.payload.get("message", ""))

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n=== 強制終了 ===")


if __name__ == "__main__":
    main_loop()