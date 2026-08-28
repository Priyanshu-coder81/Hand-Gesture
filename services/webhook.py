from datetime import datetime, timezone
import threading

import requests

from utils.validation import is_valid_webhook_url


class WebhookService:

    def __init__(self, timeout=5):
        self.timeout = timeout

    def send_gesture(self, webhook_url, gesture, confidence=None):
        """
        POST a gesture event as JSON. Never raises to the caller.
        Returns {"ok", "message", "status_code"}.
        """
        if not webhook_url or not is_valid_webhook_url(webhook_url):
            return {
                "ok": False,
                "message": "Invalid webhook URL",
                "status_code": None,
            }

        payload = {
            "gesture": gesture,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if confidence is not None:
            payload["confidence"] = confidence

        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return {
                "ok": True,
                "message": "Webhook successful",
                "status_code": response.status_code,
            }
        except requests.Timeout:
            return {
                "ok": False,
                "message": "Webhook timed out",
                "status_code": None,
            }
        except requests.ConnectionError:
            return {
                "ok": False,
                "message": "Could not connect to webhook",
                "status_code": None,
            }
        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code if exc.response is not None else None
            )
            return {
                "ok": False,
                "message": f"Webhook returned HTTP {status_code}",
                "status_code": status_code,
            }
        except requests.RequestException:
            return {
                "ok": False,
                "message": "Webhook request failed",
                "status_code": None,
            }


class SharedWebhookState:

    def __init__(self):
        self._lock = threading.Lock()
        self._webhook_url = ""
        self._last_status = "Idle"

    def set_url(self, url):
        with self._lock:
            self._webhook_url = (url or "").strip()

    def get_url(self):
        with self._lock:
            return self._webhook_url

    def set_status(self, status):
        with self._lock:
            self._last_status = status

    def get_status(self):
        with self._lock:
            return self._last_status


def run_webhook_worker(event_queue, shared_state, webhook_service=None):
    service = webhook_service or WebhookService()

    while True:
        event = event_queue.get()
        url = shared_state.get_url()

        if not url:
            shared_state.set_status("No webhook URL configured")
            continue

        if not is_valid_webhook_url(url):
            shared_state.set_status("No valid webhook URL")
            continue

        result = service.send_gesture(
            url,
            event["gesture"],
            confidence=event.get("confidence"),
        )

        if result["ok"]:
            shared_state.set_status(f"Sent {event['gesture']}")
        else:
            shared_state.set_status(result["message"])
