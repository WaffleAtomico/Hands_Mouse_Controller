"""
Voice2Text is a class that converts voice input to text using the Whisper model.

Made by: devpll aka WaffleAtomico
"""
import sounddevice as sd
from faster_whisper import WhisperModel


class Voice2Text:
    """
    A class that converts voice input to text using the Whisper model.

    Attributes
    ----------
        model_size (str): The size of the Whisper model to use.
        model (WhisperModel): An instance of the WhisperModel class for speech recognition.
    """

    def __init__(self):
        self.model_size = 'tiny'
        self.model = WhisperModel(self.model_size, device='cpu', compute_type='int8')

    def speak_text(self, duration=4):
        """
        Convert voice input to text using the Whisper model.

        Args:
            duration (int): The duration of the audio recording in seconds.

        Returns
        -------
            str: The transcribed text.
        """
        samplerate = 16000
        print('Escuchando...')
        audio = sd.rec(
            int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32'
        )
        sd.wait()
        segments, _ = self.model.transcribe(audio.flatten(), beam_size=1, language='es')
        text = ' '.join([segment.text for segment in segments])
        return text.strip()
