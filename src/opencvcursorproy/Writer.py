import string

import pyautogui

from opencvcursorproy.voice2text_tool.Voice2Text import Voice2Text

pyautogui.PAUSE = 0


class Writer:
    def __init__(self):
        self.voice2text = Voice2Text()

    def write_text(self):
        txt = self.voice2text.speak_text()
        for char in txt:
            if (char not in string.ascii_letters
                and char not in "ñáéíóúüÑÁÉÍÓÚÜ "):

                continue
            pyautogui.typewrite(char)
        print("Dejamos de escribir...")
