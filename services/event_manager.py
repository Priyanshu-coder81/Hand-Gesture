class GestureEventManager:

    def __init__(self):
        self._last_emitted_gesture = None

    def should_emit(self, gesture):
        """
        Return True only when the stable gesture
        is different from the last emitted gesture.
        """
        if gesture is None:
            return False

        if gesture == self._last_emitted_gesture:
            return False

        self._last_emitted_gesture = gesture
        return True

    def reset(self):
        self._last_emitted_gesture = None
