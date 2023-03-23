#!/usr/bin/env python
import pyaudio
import wave


def record_audio_to_wav_file(output_filename, duration, format, channels, rate, chunk):
    audio = pyaudio.PyAudio()

    # 録音ストリームを開く
    stream = audio.open(
        format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk
    )

    print("Recording...")
    frames = []

    # 録音を行う
    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    # 録音ストリームを閉じる
    print("Finished recording")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 録音データをWAVファイルに保存する
    with wave.open(output_filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b"".join(frames))


if __name__ == "__main__":
    output_filename = "output.wav"
    duration = 5  # 録音時間（秒）
    format = pyaudio.paInt16
    channels = 1
    rate = 44100
    chunk = 1024

    record_audio_to_wav_file(output_filename, duration, format, channels, rate, chunk)
