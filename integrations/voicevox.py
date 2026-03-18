import requests
import simpleaudio as sa

VOICEVOX_URL = "http://localhost:50021"
SPEAKER_ID = 8  # 春日部つむぎ ノーマル

def speak(text: str):
    print("SPEAK CALLED")
    # 音声クエリ生成
    query_res = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": SPEAKER_ID},
    )
    if query_res.status_code != 200:
        print(f"[VoiceVox] audio_query エラー ({query_res.status_code}): {query_res.text}")
        return

    query = query_res.json()
    query["outputSamplingRate"] = 44100
    query["outputStereo"] = True
    query["intonationScale"] = 1.1
    query["pitchScale"] = -0.02
    query["speedScale"] = 1.1

    # 音声合成
    audio_res = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": SPEAKER_ID},
        json=query,
    )
    if audio_res.status_code != 200:
        print(f"[VoiceVox] synthesis エラー ({audio_res.status_code}): {audio_res.text}")
        return

    wav_path = "voice.wav"
    with open(wav_path, "wb") as f:
        f.write(audio_res.content)

    # 再生（simpleaudio 使用）
    wave_obj = sa.WaveObject.from_wave_file(wav_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # 再生完了まで待つ