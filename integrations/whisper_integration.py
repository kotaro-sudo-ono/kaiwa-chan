import sounddevice as sd
import numpy as np
import keyboard
from faster_whisper import WhisperModel
import time

model = WhisperModel("small", device="cpu")
fs = 16000

def record_until_key_release(record_key="space"):
    frames = []
    recording = False
    stream = sd.InputStream(samplerate=fs, channels=1)
    stream.start()
    print(f"'{record_key}'を押すと録音開始、離すと録音停止")
    print("'esc'で終了")

    try:
        while True:
            if keyboard.is_pressed("esc"):
                return None
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

def transcribe_audio(audio=None):
    """
    audio=None ならマイク録音から文字起こし
    audio が渡されたらそれを文字起こし
    """
    if audio is None:
        audio = record_until_key_release("space")
    if audio is None or audio.size == 0:
        return ""
    segments, _ = model.transcribe(audio, beam_size=5, language="ja")
    return "".join([s.text for s in segments])