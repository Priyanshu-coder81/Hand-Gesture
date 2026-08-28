import av
import cv2

from streamlit_webrtc import VideoProcessorBase

from .gesture_recognizer import GestureDetector


class VideoProcessor(VideoProcessorBase):

    def __init__(self):
        self.gesture_detector = GestureDetector()

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        try:
            results = self.gesture_detector.recognize(img)
        except Exception:
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

        if results.hand_landmarks:
            gesture = self.gesture_detector.get_top_gesture(results)
            if gesture:
                label, score = gesture
                text = f"Gesture: {label} ({score:.0%})"
                color = (0, 255, 0)
            else:
                text = "Gesture: UNKNOWN"
                color = (0, 255, 255)
        else:
            text = "No hand detected"
            color = (0, 0, 255)

        cv2.putText(
            img,
            text,
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2,
        )

        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24",
        )
