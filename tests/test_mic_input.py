# file: test_mic_input.py
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

# CPUモードでモデル準備（GPU不要）
model = WhisperModel("small", device="cpu")  # small / medium / large

def list_microphones():
    """使用可能なマイクを表示"""
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            print(f"{i}: {dev['name']} ({dev['hostapi']})")
    return devices

def record(duration=5, fs=16000, device=None):
    """
    マイクから録音して numpy 配列で返す
    duration: 録音秒数
    fs: サンプリング周波数
    device: マイク番号
    """
    print("録音開始...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=device)
    sd.wait()
    audio = np.squeeze(audio)
    print("録音終了")
    return audio

def transcribe(audio):
    """
    Whisperで文字起こし
    audio: numpy配列
    """
    segments, info = model.transcribe(audio, beam_size=5)
    text = "".join(segment.text for segment in segments)
    return text

def main():
    print("使用可能なマイク")
    list_microphones()

    # 使いたいマイクの番号を指定（デフォルト None はシステム既定）
    device_index = None  # 例: 1 とか指定可能

    # 録音
    audio_data = record(duration=5, device=device_index)

    # 文字起こし
    text = transcribe(audio_data)
    print("文字起こし結果:", text)

if __name__ == "__main__":
    main()