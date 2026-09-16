from abc import ABC, abstractmethod
import math
from collections import deque

import pyautogui

from opencvcursorproy.Writer import Writer

pyautogui.PAUSE = 0

class ActionsBase(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def execute_actions(self):
        """
        Usted to execute all actions in class.

        This method should be implemented in subclasses to define the specific actions
        """
        pass

class ClickActions(ActionsBase):
    def __init__(self):
        self.fingers_raised = {}
        self._was_left_clicking = False
        self._was_right_clicking = False
        self._was_dragging = False
        self._was_double_clicking = False
        self.position_history = deque(maxlen=4)

    def _validate_fingers(self, correct_fingers, no_fingers):
        is_valid = all(self.fingers_raised[finger] for finger
                       in correct_fingers)
        is_valid = is_valid and not any(self.fingers_raised[finger] for finger
                                        in no_fingers)
        return is_valid

    def _move_cursor(self, cursor_position):
        correct_fingers = ["index"]
        no_fingers = []
        is_valid = self._validate_fingers(correct_fingers, no_fingers)
        if is_valid:
            self.position_history.append(cursor_position)
            len_history = len(self.position_history)
            avg_x = sum(pos[0] for pos in self.position_history) / len_history
            avg_y = sum(pos[1] for pos in self.position_history) / len_history

            pyautogui.moveTo(avg_x, avg_y)
        else:
            self.position_history.clear()

    def _left_click(self):
        correct_fingers = ["index", "thumb"]
        no_fingers = ["middle", "ring", "pinky"]
        is_valid = self._validate_fingers(correct_fingers, no_fingers)

        if is_valid and not self._was_left_clicking:
            pyautogui.click(button='left')
            self._was_left_clicking = True
        elif not is_valid:
            self._was_left_clicking = False

    def _double_click(self): #De momento la funcion double click no funciona
        correct_fingers = ["index", "pinky", "thumb"]
        no_fingers = ["middle", "ring"]
        is_valid = self._validate_fingers(correct_fingers, no_fingers)

        if is_valid and not self._was_double_clicking:
            pyautogui.doubleClick(button='left')
            print("Double click")
            self._was_double_clicking = True
        elif not is_valid:
            self._was_double_clicking = False

    def _right_click(self):
        correct_fingers = ["index", "middle", "thumb"]
        no_fingers = ["ring", "pinky"]
        is_valid = self._validate_fingers(correct_fingers, no_fingers)

        if is_valid and not self._was_right_clicking:
            pyautogui.click(button='right')
            self._was_right_clicking = True
        elif not is_valid:
            self._was_right_clicking = False

    def _listen(self):
        correct_fingers = ["index", "middle", "ring"]
        no_fingers = ["thumb", "pinky"]
        is_valid = self._validate_fingers(correct_fingers, no_fingers)
        if is_valid:
            writer = Writer()
            writer.write_text()

    def update_fingers(self, fingers_raised):
        self.fingers_raised = fingers_raised

    def execute_actions(self, cursor_position):
        self._move_cursor(cursor_position)
        self._left_click()
        # self._double_click()
        self._right_click()
        self._listen()

class ScrollAction(ClickActions):
    def __init__(self):
        super().__init__()
        self.hand_landmarks = None
        self._was_dragging = False

    def update_landmarks(self, hand_landmarks, was_dragging=False):
        self.hand_landmarks = hand_landmarks
        self._was_dragging = was_dragging

    def _scroll(self):
        if not self.hand_landmarks and self._was_dragging:
            return

        tips = [8, 12, 16, 20]
        knuckles = [6, 10, 14, 18]

        is_up = all(self.hand_landmarks[tip].y < self.hand_landmarks[knuckle].y
                    for tip, knuckle in zip(tips, knuckles))

        is_down = all(self.hand_landmarks[tip].y > self.hand_landmarks[knuckle].y
                      for tip, knuckle in zip(tips, knuckles))

        scroll_amount = 1

        if is_up:
            pyautogui.scroll(scroll_amount)
        elif is_down:
            pyautogui.scroll(scroll_amount * -1)

    def execute_actions(self):
        self._scroll()

class AdvancedActions(ActionsBase):
    def __init__(self):
        self.hand_landmarks = None
        self._was_dragging = False
        self.position_history = deque(maxlen=4)

    def update_landmarks(self, hand_landmarks):
        self.hand_landmarks = hand_landmarks
        return self._was_dragging

    def reset_drag_state(self):
        if self._was_dragging:
            pyautogui.mouseUp(button='left')
            self._was_dragging = False
        self.hand_landmarks = None

    def _drag(self, cursor_position):
        if not self.hand_landmarks:
            self.reset_drag_state()
            return

        thumb = self.hand_landmarks[4]
        index = self.hand_landmarks[8]
        distance = math.hypot(thumb.x - index.x, thumb.y - index.y)
        self.position_history.append(cursor_position)

        len_history = len(self.position_history)
        avg_x = sum(pos[0] for pos in self.position_history) / len_history
        avg_y = sum(pos[1] for pos in self.position_history) / len_history

        # Histéresis: Activación estricta (< 0.045), Soltado con margen (> 0.06)
        if not self._was_dragging and distance < 0.045:
            pyautogui.mouseDown(button='left', 
                                x=avg_x,
                                y=avg_y)
            self._was_dragging = True
        elif self._was_dragging and distance > 0.06:
            pyautogui.mouseUp(button='left', 
                              x=avg_x,
                              y=avg_y)
            self._was_dragging = False

        if self._was_dragging:
            pyautogui.moveTo(avg_x, avg_y)

    def execute_actions(self, cursor_position):
        self._drag(cursor_position)

class ActivateGesture(ActionsBase):
    def __init__(self, required_seconds=2, fps=30):
        self.is_active = True
        self.fingers_raised = {}
        self.fist_frame_counter = 0
        self.required_frames = required_seconds * fps
        self.cooldown = 0

    def update_fingers(self, fingers_raised):
        self.fingers_raised = fingers_raised

    def _is_fist(self):
        if not self.fingers_raised:
            return False

        fingers_to_check = ["index", "middle", "ring", "pinky"]
        return all(not self.fingers_raised.get(f, True)
                   for f in fingers_to_check)

    def _check_toggle(self):
        """
        Mock function to start or stop completely all gestures.

        This fuctions will recognize when you close your fist and put it in
        front of the camera, and will deactivate all gestures until you
        make the same gesture again.
        """
        if self.cooldown > 0:
            self.cooldown -= 1
            return self.is_active

        if self._is_fist():
            self.fist_frame_counter += 1
            if self.fist_frame_counter >= self.required_frames:
                self.is_active = not self.is_active
                self.fist_frame_counter = 0
                self.cooldown = 45
        else:
            self.fist_frame_counter = max(0, self.fist_frame_counter - 2)

        return self.is_active

    def execute_actions(self):
        return self._check_toggle()
