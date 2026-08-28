import queue

import av
import cv2

from streamlit_webrtc import VideoProcessorBase

from services.event_manager import GestureEventManager
from services.gesture_stabilizer import GestureStabilizer

from .gesture_recognizer import GestureDetector


class VideoProcessor(VideoProcessorBase):

    def __init__(self, event_queue=None):
        self.gesture_detector = GestureDetector()
        self.stabilizer = GestureStabilizer(required_frames=5)
        self.event_manager = GestureEventManager()
        self.event_queue = event_queue
        self._last_event = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        try:
            results = self.gesture_detector.recognize(img)
        except Exception:
            self.stabilizer.reset()
            cv2.putText(
                img,
                "Recognition error",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        img = self.gesture_detector.draw_landmarks(img, results)

        gesture_data = self.gesture_detector.get_top_gesture(results)
        stable_gesture = None
        should_emit = False

        if gesture_data is not None:
            gesture, score = gesture_data
            raw_text = f"Raw: {gesture} ({score:.0%})"
            raw_color = (0, 255, 0)

            stable_gesture = self.stabilizer.update(gesture)

            if stable_gesture is not None:
                should_emit = self.event_manager.should_emit(stable_gesture)
                if should_emit:
                    self._last_event = stable_gesture
                    self._enqueue_event(stable_gesture, score)
        else:
            self.stabilizer.reset()
            if results.hand_landmarks:
                raw_text = "Raw: UNKNOWN"
                raw_color = (0, 255, 255)
            else:
                raw_text = "No hand detected"
                raw_color = (0, 0, 255)

        cv2.putText(
            img,
            raw_text,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            raw_color,
            2,
        )

        stable_text = (
            f"Stable: {stable_gesture}"
            if stable_gesture is not None
            else "Stable: waiting"
        )
        cv2.putText(
            img,
            stable_text,
            (30, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 0) if stable_gesture is not None else (180, 180, 180),
            2,
        )

        if self._last_event is not None:
            event_text = (
                f"Event: {self._last_event}"
                if should_emit
                else f"Last event: {self._last_event}"
            )
            cv2.putText(
                img,
                event_text,
                (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255) if should_emit else (200, 200, 200),
                2,
            )

        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24",
        )

    def _enqueue_event(self, gesture, confidence):
        if self.event_queue is None:
            return

        try:
            self.event_queue.put_nowait(
                {
                    "gesture": gesture,
                    "confidence": confidence,
                }
            )
        except queue.Full:
            pass
