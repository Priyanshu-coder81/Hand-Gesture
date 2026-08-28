from pathlib import Path
import time

import cv2
import mediapipe as mp
import numpy as np

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "gesture_recognizer.task"
)

GESTURE_LABELS = {
    "Closed_Fist": "Closed Fist",
    "Open_Palm": "Open Palm",
    "Pointing_Up": "Pointing Up",
    "Thumb_Down": "Thumbs Down",
    "Thumb_Up": "Thumbs Up",
    "Victory": "Victory",
    "ILoveYou": "I Love You",
}


class GestureDetector:
    """MediaPipe Gesture Recognizer wrapper for live video frames."""

    def __init__(
        self,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        min_gesture_confidence=0.5,
    ):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Gesture recognizer model not found at {MODEL_PATH}"
            )

        self._timestamp_ms = 0

        options = mp.tasks.vision.GestureRecognizerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(MODEL_PATH),
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            canned_gesture_classifier_options=(
                mp.tasks.components.processors.ClassifierOptions(
                    score_threshold=min_gesture_confidence,
                )
            ),
        )
        self._recognizer = (
            mp.tasks.vision.GestureRecognizer.create_from_options(
                options,
            )
        )

        self.mp_draw = mp.tasks.vision.drawing_utils
        self.mp_draw_styles = mp.tasks.vision.drawing_styles
        self.hand_connections = (
            mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS
        )

    def recognize(self, frame):
        """
        Recognize gestures in an OpenCV BGR frame.

        Returns MediaPipe GestureRecognizerResult.
        """
        rgb_frame = np.ascontiguousarray(
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        )
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame,
        )

        timestamp_ms = time.time_ns() // 1_000_000
        if timestamp_ms <= self._timestamp_ms:
            timestamp_ms = self._timestamp_ms + 1
        self._timestamp_ms = timestamp_ms

        return self._recognizer.recognize_for_video(
            mp_image,
            timestamp_ms,
        )

    def get_top_gesture(self, results):
        """
        Return (label, score) for the first detected hand, or None
        when no hand / unrecognized pose is present.
        """
        if not results.gestures or not results.gestures[0]:
            return None

        category = results.gestures[0][0]
        name = category.category_name or "None"
        if name in ("None", ""):
            return None

        label = GESTURE_LABELS.get(name, name)
        return label, category.score

    def draw_landmarks(self, frame, results):
        if not results.hand_landmarks:
            return frame

        for hand_landmarks in results.hand_landmarks:
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.hand_connections,
                self.mp_draw_styles.get_default_hand_landmarks_style(),
                self.mp_draw_styles.get_default_hand_connections_style(),
            )

        return frame
