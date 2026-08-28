import av
import cv2

from streamlit_webrtc import VideoProcessorBase

from .hand_detector import HandDetector


class VideoProcessor(VideoProcessorBase):

    def __init__(self):
        self.hand_detector = HandDetector()

    def recv(self, frame):

        # WebRTC frame → OpenCV image
        img = frame.to_ndarray(format="bgr24")

        # Detect hands
        results = self.hand_detector.detect(img)

        # Temporary debug output
        if results.hand_landmarks:
            cv2.putText(
                img,
                "Hand detected",
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