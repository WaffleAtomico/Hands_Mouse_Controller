"""
Actions for hand gesture recognition.

Made by: devpll aka WaffleAtomico
"""

import math
from abc import ABC, abstractmethod
from collections import deque

import pyautogui

from opencvcursorproy.Writer import Writer

pyautogui.PAUSE = 0


MIN_DISTANCE_DRAG = 0.045
MAX_DISTANCE_DRAG = 0.06


class ActionsBase(ABC):
    """
    Abstract base class for actions.

    This class defines the interface for all action classes.
    """

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
    """
    Manages click actions based on finger positions.

    Attributes
    ----------
        fingers_raised (dict): A dictionary indicating which fingers are raised.
        _was_left_clicking (bool): Flag to track the state of left clicking.
        _was_right_clicking (bool): Flag to track the state of right clicking.
        _was_dragging (bool): Flag to track the state of dragging.
        _was_double_clicking (bool): Flag to track the state of double clicking.
        position_history (deque): A deque to store recent cursor positions for smoothing.

    Methods
    -------
        _validate_fingers(correct_fingers, no_fingers): Validates the current finger positions
        _move_cursor(cursor_position): Moves the cursor based on finger positions
        _left_click(): Performs a left click action based on finger positions
        _double_click(): Performs a double click action based on finger positions
        _right_click(): Performs a right click action based on finger positions
        _listen(): Performs a listening action based on finger positions
        update_fingers(fingers_raised): Updates the current finger positions
        execute_actions(cursor_position): Executes all actions based on variables given.
    """

    def __init__(self):
        self.fingers_raised = {}
        self._was_left_clicking = False
        self._was_right_clicking = False
        self._was_dragging = False
        self._was_double_clicking = False
        self.position_history = deque(maxlen=4)

    def _validate_fingers(self, correct_fingers, no_fingers):
        is_valid = all(self.fingers_raised[finger] for finger in correct_fingers)
        return is_valid and not any(self.fingers_raised[finger] for finger in no_fingers)

    def _move_cursor(self, cursor_position):
        correct_fingers = ['index']
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
        correct_fingers = ['index', 'thumb']
        no_fingers = ['middle', 'ring', 'pinky']
        is_valid = self._validate_fingers(correct_fingers, no_fingers)

        if is_valid and not self._was_left_clicking:
            pyautogui.click(button='left')
            self._was_left_clicking = True
        elif not is_valid:
            self._was_left_clicking = False

    def _double_click(self):  # De momento la funcion double click no funciona
        correct_fingers = ['index', 'pinky', 'thumb']
        no_fingers = ['middle', 'ring']
        is_valid = self._validate_fingers(correct_fingers, no_fingers)

        if is_valid and not self._was_double_clicking:
            pyautogui.doubleClick(button='left')
            print('Double click')
            self._was_double_clicking = True
        elif not is_valid:
            self._was_double_clicking = False

    def _right_click(self):
        correct_fingers = ['index', 'middle', 'thumb']
        no_fingers = ['ring', 'pinky']
        is_valid = self._validate_fingers(correct_fingers, no_fingers)

        if is_valid and not self._was_right_clicking:
            pyautogui.click(button='right')
            self._was_right_clicking = True
        elif not is_valid:
            self._was_right_clicking = False

    def _listen(self):
        correct_fingers = ['index', 'middle', 'ring']
        no_fingers = ['thumb', 'pinky']
        is_valid = self._validate_fingers(correct_fingers, no_fingers)
        if is_valid:
            writer = Writer()
            writer.write_text()

    def update_fingers(self, fingers_raised):
        """
        fingers_raised param is updated with the current finger positions.

        Parameters
        ----------
            fingers_raised (list): A list of booleans representing the current finger positions.
        """
        self.fingers_raised = fingers_raised

    def execute_actions(self, cursor_position):
        """
        Execute all actions based on the current finger positions and cursor position.

        Parameters
        ----------
            cursor_position (tuple): A tuple representing the current cursor position (x, y).
        """
        self._move_cursor(cursor_position)
        self._left_click()
        # self._double_click()
        self._right_click()
        self._listen()


class ScrollAction(ClickActions):
    """
    Manages scroll actions based on finger positions.

    Attributes
    ----------
        hand_landmarks (list): A list of hand landmarks detected by MediaPipe.
        _was_dragging (bool): Flag to track the state of dragging.

    Methods
    -------
        update_landmarks(hand_landmarks, was_dragging): Updates the current variables
        _scroll(): Performs a scroll action based on finger positions
        execute_actions(): Executes the scroll action based on the current h-landmardk and d-state
    """

    def __init__(self):
        super().__init__()
        self.hand_landmarks = None
        self._was_dragging = False

    def update_landmarks(self, hand_landmarks, was_dragging=False):
        """
        Update the current hand landmarks and dragging state.

        Parameters
        ----------
            hand_landmarks (list): A list of hand landmarks detected by MediaPipe.
            was_dragging (bool): Flag to indicate if the hand is currently dragging.
        """
        self.hand_landmarks = hand_landmarks
        self._was_dragging = was_dragging

    def _scroll(self):
        if not self.hand_landmarks and self._was_dragging:
            return

        tips = [8, 12, 16, 20]
        knuckles = [6, 10, 14, 18]

        is_up = all(
            self.hand_landmarks[tip].y < self.hand_landmarks[knuckle].y
            for tip, knuckle in zip(tips, knuckles)
        )

        is_down = all(
            self.hand_landmarks[tip].y > self.hand_landmarks[knuckle].y
            for tip, knuckle in zip(tips, knuckles)
        )

        scroll_amount = 1

        if is_up:
            pyautogui.scroll(scroll_amount)
        elif is_down:
            pyautogui.scroll(scroll_amount * -1)

    def execute_actions(self):
        """
        Execute all actions related to scrolling.

        Parameters
        ----------
            N/A
        """
        self._scroll()


class AdvancedActions(ActionsBase):
    """
    Manages advanced actions based on finger positions and hand landmarks.

    Attributes
    ----------
        hand_landmarks (list): A list of hand landmarks detected by MediaPipe.
        _was_dragging (bool): Flag to track the state of dragging.
    """

    def __init__(self):
        self.hand_landmarks = None
        self._was_dragging = False
        self.position_history = deque(maxlen=4)

    def update_landmarks(self, hand_landmarks):
        """
        Update the current hand landmarks and dragging state.

        Parameters
        ----------
            hand_landmarks (list): A list of hand landmarks detected by MediaPipe.

        Returns
        -------
            _was_dragging (bool): Flag indicating if the hand was previously dragging.
        """
        self.hand_landmarks = hand_landmarks
        return self._was_dragging

    def reset_drag_state(self):
        """
        Reset the dragging state and release the mouse button if it was previously pressed.

        Parameters
        ----------
        N/A
        """
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

        if not self._was_dragging and distance < MIN_DISTANCE_DRAG:
            pyautogui.mouseDown(button='left', x=avg_x, y=avg_y)
            self._was_dragging = True
        elif self._was_dragging and distance > MAX_DISTANCE_DRAG:
            pyautogui.mouseUp(button='left', x=avg_x, y=avg_y)
            self._was_dragging = False

        if self._was_dragging:
            pyautogui.moveTo(avg_x, avg_y)

    def execute_actions(self, cursor_position):
        """Execute all actions related to advanced gestures."""
        self._drag(cursor_position)


class ActivateGesture(ActionsBase):
    """
    Manages the activation and deactivation of gestures based on a fist gesture.

    Attributes
    ----------
        is_active (bool): Flag indicating if gestures are currently active.
        fingers_raised (dict): A dictionary indicating which fingers are raised.
        fist_frame_counter (int): Counter for consecutive frames with a fist gesture.
        required_frames (int): Number of consecutive frames required to toggle activation.
        cooldown (int): Cooldown period to prevent rapid toggling of activation.
    """

    def __init__(self, required_seconds=2, fps=30):
        self.is_active = True
        self.fingers_raised = {}
        self.fist_frame_counter = 0
        self.required_frames = required_seconds * fps
        self.cooldown = 0

    def update_fingers(self, fingers_raised):
        """
        fingers_raised param is updated with the current finger positions.

        Parameters
        ----------
            fingers_raised (list): A list of booleans representing the current finger positions.
        """
        self.fingers_raised = fingers_raised  # TODO: Make this related to hand landmarks

    def _is_fist(self):
        if not self.fingers_raised:
            return False

        fingers_to_check = ['index', 'middle', 'ring', 'pinky']
        return all(not self.fingers_raised.get(f, True) for f in fingers_to_check)

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
        """Execute the activation/deactivation of gestures based on the fist gesture."""
        return self._check_toggle()
