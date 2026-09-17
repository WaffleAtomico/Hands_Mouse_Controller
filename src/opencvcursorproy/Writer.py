"""
Actions related to write in the screen using voice recognition.

Made by: devpll aka WaffleAtomico
"""

import string

import pyautogui

from opencvcursorproy.voice2text_tool.Voice2Text import Voice2Text

pyautogui.PAUSE = 0


class Writer:
    """
    A class for writing text on the screen using voice recognition.

    Attributes
    ----------
        voice2text (Voice2Text): An instance of the Voice2Text class for voice-to-text conversion.
    """

    def __init__(self):
        self.voice2text = Voice2Text()

    def write_text(self):
        """
        Capture voice input and write the recognized text on the screen.

        This method uses the Voice2Text class to capture voice input,
        convert it to text, and then type the text on the screen using pyautogui.
        """
        txt = self.voice2text.speak_text()
        for char in txt:
            if char not in string.ascii_letters and char not in 'ñáéíóúüÑÁÉÍÓÚÜ ':
                continue
            pyautogui.typewrite(char)
        print('Dejamos de escribir...')
