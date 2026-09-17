"""
Main entry point for the Hand Gesture Recognition application.

Made by: WaffleAtomico
"""

from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from opencvcursorproy.Actions import (
    ActivateGesture,
    AdvancedActions,
    ClickActions,
    ScrollAction,
)

pyautogui.PAUSE = 0


class HandGestureRecognition:
    """
    Uses hand gestures to control the mouse cursor and perform various actions.

    Attributes
    ----------
        _full_hand_model (str): Path to the hand landmark model.
        _gesture_model (str): Path to the gesture recognition model.
        base_options (BaseOptions): Base options for the hand landmark model.
        options (HandLandmarkerOptions): Options for the hand landmark model.
        gesture_options (GestureRecognizerOptions): Options for the gesture recognition model.
        detector (HandLandmarker): Hand landmark detector.
        cap (cv2.VideoCapture): Video capture object for accessing the camera.
        screen_width (int): Width of the screen.
        screen_height (int): Height of the screen.
        margin (int): Margin for the detection area.
        click_ctl (ClickActions): Controller for click actions.
        scroll_ctl (ScrollAction): Controller for scroll actions.
        advanced_ctl (AdvancedActions): Controller for advanced actions.
        off_on_ctl (ActivateGesture): Controller for activating/deactivating gestures.

    Methods
    -------
        __init__(): Initializes the HandGestureRecognition class.
        build(): Builds the hand gesture recognition system by loading models.
        _destroy(): Releases resources and cleans up.
        main(): Main loop for capturing video and process gestures and actions.
    """

    def __init__(self):
        self._full_hand_model = ''
        self._gesture_model = ''
        self.base_options = None
        self.options = None
        self.gesture_options = None
        self.detector = None
        self.cap = None
        self.screen_width = 0
        self.screen_height = 0
        self.margin = 170

        self.click_ctl = None
        self.scroll_ctl = None
        self.advanced_ctl = None
        self.off_on_ctl = None

    def build(self):
        """Build the hand gesture recognition system by loading models and setting up options."""
        current_dir = Path(__file__).resolve().parent
        model_path_landmark = current_dir / 'models' / 'hand_landmarker.task'
        self._full_hand_model = str(model_path_landmark)
        model_path_gesture = current_dir / 'models' / 'gesture_recognizer.task'
        self._gesture_model = str(model_path_gesture)

        self.base_options = python.BaseOptions(model_asset_path=self._full_hand_model)
        self.options = vision.HandLandmarkerOptions(
            base_options=self.base_options,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7,
        )
        self.detector = vision.HandLandmarker.create_from_options(self.options)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.screen_width, self.screen_height = pyautogui.size()
        self.click_ctl = ClickActions()
        self.scroll_ctl = ScrollAction()
        self.advanced_ctl = AdvancedActions()
        self.off_on_ctl = ActivateGesture(required_seconds=3, fps=30)

    def _destroy(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def main(self):
        """
        OpenCamera and uses cursor.

        Main function captures video from the default camera, processes
        each frame to detect hand landmarks and recognize gestures, and
        displays the results in a window. The program continues until the
        user presses the 'q' key to quit.
        """
        cap = self.cap
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            margin_x = self.margin
            margin_y = self.margin

            cv2.rectangle(
                frame, (margin_x, margin_y), (w - margin_x, h - margin_y), (255, 0, 255), 2
            )

            results = self.detector.detect(mp_image)
            if results.hand_landmarks and results.handedness:
                for i, hand_landmarks in enumerate(results.hand_landmarks):
                    hand_side = results.handedness[i][0].category_name
                    raised_fingers = _get_raised_fingers(hand_landmarks, hand_side)

                    self.off_on_ctl.update_fingers(raised_fingers)
                    system_is_active = self.off_on_ctl.execute_actions()

                    status_text = 'ACTIVO' if system_is_active else 'PAUSADO'
                    cv2.putText(
                        frame,
                        f'ESTADO: {status_text}',
                        (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 100, 0),
                        2,
                    )

                    if not system_is_active:
                        if hasattr(self.advanced_ctl, 'reset_drag_state'):
                            self.advanced_ctl.reset_drag_state()
                        continue

                    self.click_ctl.update_fingers(raised_fingers)
                    wd = self.advanced_ctl.update_landmarks(hand_landmarks)
                    self.scroll_ctl.update_landmarks(hand_landmarks, wd)

                    index_finger_tip = hand_landmarks[8]
                    x = int(index_finger_tip.x * w)
                    y = int(index_finger_tip.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                    screen_x = np.interp(x, [margin_x, w - margin_x], [0, self.screen_width])
                    screen_y = np.interp(y, [margin_y, h - margin_y], [0, self.screen_height])

                    self.click_ctl.execute_actions((screen_x, screen_y))
                    self.advanced_ctl.execute_actions((screen_x, screen_y))
                    self.scroll_ctl.execute_actions()
            elif hasattr(self, 'advanced_ctl'):
                self.advanced_ctl.reset_drag_state()

            cv2.imshow('Hand Gesture Recognition', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self._destroy()


def _get_raised_fingers(hand_landmarks, handedness_name):
    """
    Count fingers that are raised.

    args:
        hand_landmarks: List of hand landmarks detected by MediaPipe.
        handedness_name: String indicating whether the hand is 'Right' or 'Left'.

    Returns
    -------
        fingers: Dictionary with keys 'thumb', 'index', 'middle', 'ring', 'pinky'.
    """
    fingers = {'thumb': False, 'index': False, 'middle': False, 'ring': False, 'pinky': False}

    # Punta del índice = 8, Nudillo del índice = 6
    fingers['index'] = hand_landmarks[8].y < hand_landmarks[6].y

    # Punta del medio = 12, Nudillo del medio = 10
    fingers['middle'] = hand_landmarks[12].y < hand_landmarks[10].y

    # Punta del anular = 16, Nudillo del anular = 14
    fingers['ring'] = hand_landmarks[16].y < hand_landmarks[14].y

    # Punta del meñique = 20, Nudillo del meñique = 18
    fingers['pinky'] = hand_landmarks[20].y < hand_landmarks[18].y

    is_right_hand = handedness_name == 'Right'

    if is_right_hand:
        fingers['thumb'] = hand_landmarks[4].x < hand_landmarks[3].x
    else:
        fingers['thumb'] = hand_landmarks[4].x > hand_landmarks[3].x

    return fingers
