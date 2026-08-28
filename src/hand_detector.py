from pathlib import Path
import time

import cv2
import mediapipe as mp
import numpy as np

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"


class HandDetector:

    def __init__(
        self,
        max_num_hands=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        self.max_num_hands = max_num_hands
        self._timestamp_ms = 0

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(MODEL_PATH),
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(
            options,
        )

        self.mp_draw = mp.tasks.vision.drawing_utils
        self.mp_draw_styles = mp.tasks.vision.drawing_styles
        self.hand_connections = (
            mp.tasks.vision.HandLandmarksConnections.HAND_CONNECTIONS
        )

    def detect(self, frame):
        """
        Detect hands in an OpenCV BGR frame.

        Returns MediaPipe HandLandmarkerResult.
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

        return self.landmarker.detect_for_video(mp_image, timestamp_ms)

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
