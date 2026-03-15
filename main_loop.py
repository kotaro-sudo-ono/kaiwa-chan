# file: main_loop.py
import re
import time
import threading
import keyboard

from integrations.whisper_integration import transcribe_audio
from integrations.voicevox import speak
from agents.administrator import Administrator
from agents.memory_agent import MemoryAgent

from core.memory.memory_manager import MemoryManager
from core.memory.memory_store import MemoryStore
from core.task.task_manager import TaskManager
from core.task.task_queue import TaskQueue
from core.event.event_bus import EventBus
from core.cognition.observe import Observer


RESET_KEYWORDS = ["リセット", "タスクリセット", "クリア", "全部消して", "キャンセル"]


def strip_code_blocks(text: str) -> str:
    """コードブロック(``` ... ```)とインラインコード(` ... `)をTTS前に除去する"""
    text = re.sub(r"```[\s\S]*?```", "コードは省略します。", text)
    text = re.sub(r"`[^`]+`", "", text)
    return text.strip()


def record_and_process(observer, shogun: Administrator, memory_agent: MemoryAgent, task_queue: TaskQueue, is_speaking: threading.Event):
    """
    録音→文字起こし→Administrator（マルチエージェント）→Observer→TaskQueue
    スレッドで回す
    """
    while True:
        if keyboard.is_pressed("esc"):
            print("終了キー押下 → 録音スレッド停止")
            break

        # 再生中は録音しない
        if is_speaking.is_set():
            time.sleep(0.1)
            continue

        # 録音 & 文字起こし
        user_text = transcribe_audio()
        if not user_text:
            continue

        print(f"ユーザ入力: {user_text}")

        # リセットキーワードチェック
        if any(kw in user_text for kw in RESET_KEYWORDS):
            task_queue.clear()
            print("[リセット] タスクキューをクリアしました")
            speak("タスクをリセットしました")
            continue

        # Administrator（マルチエージェント）で返答生成
        llm_reply = shogun.process(user_text)
        print(f"Administrator 返答: {llm_reply}")

        # MemoryAgent が非同期でパーソナルデータを判断・保存（TTS再生を遅延させない）
        threading.Thread(target=memory_agent.process, args=(user_text, llm_reply), daemon=True).start()

        # Observer に渡してタスク生成（TaskManager が task_queue に直接 push）
        context = observer.observe(user_text, llm_reply=llm_reply)
        print(f"Observer Context: {context}")

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
    memory_agent = MemoryAgent(memory_store)
    is_speaking = threading.Event()

    print("=== Kaiwa-chan AI 常駐ループ 起動 ===")
    print("'space'で録音開始・離すと終了、'esc'で全体終了")

    # 録音＆文字起こしスレッド開始
    t = threading.Thread(target=record_and_process, args=(observer, shogun, memory_agent, task_queue, is_speaking), daemon=True)
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
                    # VoiceVoxで音声出力（コードブロック除去後、再生中フラグを立てる）
                    message = strip_code_blocks(task.payload.get("message", ""))
                    is_speaking.set()
                    speak(message)
                    is_speaking.clear()

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n=== 強制終了 ===")


if __name__ == "__main__":
    main_loop()