# file: key_record_whisper_ja.py
import sounddevice as sd
import numpy as np
import keyboard
from faster_whisper import WhisperModel
import time

# Whisperモデル準備（CPU）
model = WhisperModel("small", device="cpu")
fs = 16000  # サンプリング周波数

def record_until_key_release(record_key="space"):
    """
    指定キーが押されている間録音し、離されたら停止して numpy 配列を返す
    """
    frames = []
    recording = False

    # InputStreamの準備
    stream = sd.InputStream(samplerate=fs, channels=1)
    stream.start()

    print(f"'{record_key}'を押すと録音開始、離すと録音停止")
    print("'esc'で終了")

    try:
        while True:
            if keyboard.is_pressed("esc"):
                print("終了します")
                return None  # mainで終了処理
            if keyboard.is_pressed(record_key):
                if not recording:
                    print("録音開始")
                    recording = True
                audio_chunk, _ = stream.read(1024)
                frames.append(audio_chunk)
            else:
                if recording:
                    print("録音終了")
                    break
            time.sleep(0.01)
    finally:
        stream.stop()

    if frames:
        audio = np.concatenate(frames, axis=0)
        audio = np.squeeze(audio)
        return audio
    else:
        return np.array([])

def transcribe(audio):
    """
    Whisperで日本語固定文字起こし
    """
    segments, _ = model.transcribe(audio, beam_size=5, language="ja")  # 日本語固定
    return "".join([s.text for s in segments])

def main():
    while True:
        audio_data = record_until_key_release("space")
        if audio_data is None:  # Escで終了
            break
        if audio_data.size == 0:
            continue
        text = transcribe(audio_data)
        print("文字起こし:", text)

if __name__ == "__main__":
    main()