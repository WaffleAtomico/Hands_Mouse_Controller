import queue

import sounddevice as sd
from faster_whisper import WhisperModel


class Voice2Text:
    def __init__(self):
        self.model_size = "tiny"
        self.model = WhisperModel(self.model_size,
                                  device="cpu",
                                  compute_type="int8")

    def speak_text(self, duration=4):
        samplerate = 16000
        print("Escuchando...")
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate,
                       channels=1, dtype='float32')
        sd.wait()
        segments, _ = self.model.transcribe(audio.flatten(),
                                            beam_size=1,
                                            language="es")
        text = " ".join([segment.text for segment in segments])
        return text.strip()
