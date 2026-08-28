import queue
import threading

import streamlit as st
from streamlit_webrtc import webrtc_streamer

from services.webhook import (
    SharedWebhookState,
    WebhookService,
    run_webhook_worker,
)
from src import VideoProcessor


st.set_page_config(
    page_title="Hand Gesture Detector",
    page_icon="",
    layout="wide",
)


if "event_queue" not in st.session_state:
    st.session_state.event_queue = queue.Queue(maxsize=32)
    st.session_state.webhook_state = SharedWebhookState()
    worker = threading.Thread(
        target=run_webhook_worker,
        args=(
            st.session_state.event_queue,
            st.session_state.webhook_state,
        ),
        daemon=True,
    )
    worker.start()
    st.session_state.webhook_worker = worker


st.title("✋ Real-Time Hand Gesture Detector")

st.write(
    "Start the camera to begin receiving video frames."
)

# Bind the queue here (Streamlit thread). The WebRTC worker
# calls the factory later and has no access to session_state.
event_queue = st.session_state.event_queue


def processor_factory(event_queue=event_queue):
    return VideoProcessor(event_queue=event_queue)


_, camera_col, _ = st.columns([1, 2, 1])

with camera_col:
    webrtc_streamer(
        key="gesture-detector",
        video_processor_factory=processor_factory,
        video_html_attrs={
            "autoPlay": True,
            "controls": False,
            "style": {"width": "100%", "maxWidth": "900px"},
        },
    )

    st.subheader("Webhook")

    webhook_url = st.text_input(
        "Webhook URL",
        placeholder="https://example.com/webhook",
    )
    st.session_state.webhook_state.set_url(webhook_url)

    if st.button("Test Webhook"):
        result = WebhookService().send_gesture(webhook_url, "TEST")
        if result["ok"]:
            st.success(result["message"])
            st.session_state.webhook_state.set_status(
                "Test webhook successful"
            )
        else:
            st.error(result["message"])
            st.session_state.webhook_state.set_status(result["message"])

    st.caption(f"Status: {st.session_state.webhook_state.get_status()}")
