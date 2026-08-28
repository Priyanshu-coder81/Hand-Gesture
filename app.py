import streamlit as st
from streamlit_webrtc import webrtc_streamer
from src import VideoProcessor


st.set_page_config(
    page_title="Hand Gesture Detector",
    page_icon="",
    layout="wide",
)


st.title("✋ Real-Time Hand Gesture Detector")

st.write(
    "Start the camera to begin receiving video frames."
)


webrtc_streamer(
    key="gesture-detector",
    video_processor_factory=VideoProcessor,
)