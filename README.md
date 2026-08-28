# Real-Time Hand Gesture Detector

Browser app that reads a laptop webcam, recognizes hand gestures in real time, and can POST each new gesture to a webhook URL you configure in the UI.

Built with **Python**, **Streamlit**, and MediaPipe’s Gesture Recognizer. Processing runs on CPU; a dedicated GPU is not required.

## What it does

- Shows the live webcam feed in the browser
- Detects a hand and overlays the recognized gesture
- Supports seven gestures (more than the required five)
- Sends a JSON event to a webhook only when a **new stable** gesture is confirmed
- Survives missing hands, invalid URLs, webhook timeouts/failures, and recognition errors without crashing the camera

## Supported gestures

Hold the pose still and facing the camera:

| On-screen label | How to show it |
|---|---|
| Closed Fist | Make a fist |
| Open Palm | Open hand, fingers together or spread |
| Pointing Up | Index finger up |
| Thumbs Up | Thumb up |
| Thumbs Down | Thumb down |
| Victory | Index and middle fingers in a V (peace) |
| I Love You | Thumb, index, and pinky extended |

Unclear poses show as `UNKNOWN`. No hand shows as `No hand detected`.

A gesture is treated as **stable** only after the same label appears on 5 frames in a row. The same stable gesture is **not** sent to the webhook again until you change to a different one.

## How it is structured

```
webcam (browser)
  → Streamlit + streamlit-webrtc
  → MediaPipe Gesture Recognizer
  → stabilizer (5 matching frames)
  → event manager (emit only on change)
  → background worker
  → HTTP POST to your webhook URL
```

| Path | Role |
|---|---|
| `app.py` | Streamlit UI, camera, webhook form |
| `src/gesture_recognizer.py` | MediaPipe model wrapper |
| `src/video_processor.py` | Per-frame pipeline and overlay |
| `services/gesture_stabilizer.py` | Consecutive-frame confirmation |
| `services/event_manager.py` | One event per gesture change |
| `services/webhook.py` | JSON POST with timeout and error handling |
| `utils/validation.py` | `http`/`https` URL check |
| `models/gesture_recognizer.task` | Official MediaPipe model bundle |

The webhook URL is typed in the UI. It is not hardcoded.

## Local setup

**Requirements:** Python 3.11, a webcam, and a Chromium-based browser (Chrome or Edge work well).

```bash
git clone <your-repo-url>
cd Hand-Gesture

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501), click **START**, and allow camera access.

## Docker

The camera is used by **your browser**, not by a device inside the container. Open the app on `localhost` so the browser can access the webcam (same as the local run).

**Build and run with Docker Compose:**

```bash
docker compose up --build
```

**Or with Docker directly:**

```bash
docker build -t hand-gesture-detector .
docker run --rm -p 8501:8501 hand-gesture-detector
```

Then open [http://localhost:8501](http://localhost:8501) and start the camera.

Stop Compose with `Ctrl+C`, then `docker compose down`.

You share the **Git repository** (source, `Dockerfile`, `docker-compose.yml`), not a built image. An evaluator clones the repo and runs `docker compose up --build`. That command builds the image on **their** machine from the Dockerfile. The image stays in local Docker storage (`docker images`); it is not committed to GitHub.

## Webhook integration

1. Open [https://webhook.site](https://webhook.site) (or use your own endpoint) and copy the unique URL.
2. Paste it into **Webhook URL** under the camera. It must start with `http://` or `https://`.
3. Click **Test Webhook**. The app POSTs:

```json
{
  "gesture": "TEST",
  "timestamp": "2026-08-29T00:20:31.123456+00:00"
}
```

4. Start the camera and hold a gesture until **Event** appears. A live payload looks like:

```json
{
  "gesture": "Open Palm",
  "timestamp": "2026-08-29T00:20:31.123456+00:00",
  "confidence": 0.94
}
```

`confidence` is included only for real detections (MediaPipe’s score). The test payload omits it.

Leave the URL empty to use the camera without sending events.

Failures (invalid URL, timeout after 5 seconds, connection errors, HTTP 4xx/5xx) are shown in the status line. The video stream keeps running.

## Assumptions, limitations, and constraints

- Uses MediaPipe’s canned Gesture Recognizer, not a custom-trained model.
- Best with **one hand**, reasonably well lit, palm roughly toward the camera.
- Fast flickers are ignored on purpose (5-frame stabilizer).
- Webcam access needs a **secure context**: `localhost` or HTTPS. Remote HTTP Docker hosts will not get camera permission in the browser.
- Docker does not need `/dev/video0`. Frames arrive over WebRTC from the browser.
- A STUN server (`stun.l.google.com:19302`) is configured so WebRTC can connect from Docker or another machine. Strict NATs may still need a TURN server.
- CPU-only; first detection can be a little slow while the model loads.
- Overlay labels (`Raw` / `Stable` / `Event`) are for debugging stability, not part of the assignment wording.

## License / model

The Gesture Recognizer `.task` file is Google’s MediaPipe model, used under MediaPipe’s terms.
