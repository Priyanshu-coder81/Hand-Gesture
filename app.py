import streamlit as st


st.set_page_config(
    page_title="Hand Gesture Detector",
    page_icon="",
    layout="wide",
)


st.write(
    "Allow camera access and capture an image from your webcam."
)

camera_image = st.camera_input("Take a picture")

if camera_image is not None:
    st.subheader("Camera Frame")

    st.image(
        camera_image,
        caption="Captured frame",
        use_container_width=True,
    )
else:
    st.info("Please allow camera access and capture an image.")