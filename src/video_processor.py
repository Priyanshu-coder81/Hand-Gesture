import av
import cv2

from streamlit_webrtc import VideoProcessorBase

from .hand_detector import HandDetector

from .guesture_classifier import GestureClassifier

class VideoProcessor(VideoProcessorBase):

    def __init__(self):
        self.hand_detector = HandDetector()
        self.gesture_classifier = GestureClassifier()

    def recv(self, frame):

        # WebRTC frame → OpenCV image
        img = frame.to_ndarray(format="bgr24")

        # Detect hands
        results = self.hand_detector.detect(img)
        img = self.hand_detector.draw_landmarks(img, results)

        # Temporary debug output
        if results.hand_landmarks:
            landmarks = results.hand_landmarks[0]

            gesture = self.gesture_classifier.classify(
                landmarks
            )
            cv2.putText(
                img,
                f"Guesture : {gesture}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )
        else:
            cv2.putText(
                img,
                "No hand detected",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
            )

        return av.VideoFrame.from_ndarray(
            img,
            format="bgr24",
        )