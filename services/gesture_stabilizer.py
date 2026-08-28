from collections import deque


class GestureStabilizer:

    def __init__(self, required_frames=5):
        self.required_frames = required_frames
        self._history = deque(maxlen=required_frames)

    def update(self, gesture):
        """
        Add the latest gesture and return the stable gesture
        if the same gesture has been detected consistently.
        """
        self._history.append(gesture)

        if len(self._history) < self.required_frames:
            return None

        if all(item == gesture for item in self._history):
            return gesture

        return None

    def reset(self):
        self._history.clear()
