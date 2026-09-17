"""
Main entry point for the Hand Gesture Recognition application.

Made by: WaffleAtomico
"""

from opencvcursorproy.HandGestureRecognition import HandGestureRecognition

if __name__ == '__main__':
    print('hello')
    hand_gesture_recognition = HandGestureRecognition()
    hand_gesture_recognition.build()
    hand_gesture_recognition.main()
    print('bye')
