import numpy as np
import sounddevice as sd
import queue
import threading

class AudioPlayer:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_playing = False
        self.thread = None

    def __enter__(self):
        self.stream = sd.OutputStream(
            samplerate=24000,
            channels=1,
            dtype=np.int16,
            callback=self._audio_callback
        )
        self.stream.start()
        self.is_playing = True
        self.thread = threading.Thread(target=self._play_audio)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.is_playing = False
        if self.thread:
            self.thread.join()
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def add_audio(self, audio_data):
        self.audio_queue.put(audio_data)

    def _audio_callback(self, outdata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        try:
            data = self.audio_queue.get_nowait()
            outdata[:len(data), 0] = data
            outdata[len(data):, 0] = 0
        except queue.Empty:
            outdata.fill(0)

    def _play_audio(self):
        while self.is_playing:
            try:
                audio_data = self.audio_queue.get(timeout=0.1)
                self.stream.write(audio_data)
            except queue.Empty:
                continue

def record_audio(duration=5, sample_rate=24000):
    """Record audio from the microphone."""
    print(f"Recording for {duration} seconds...")
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.int16
    )
    sd.wait()
    print("Recording finished.")
    return recording.flatten() 