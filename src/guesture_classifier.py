import math


class GestureClassifier:

    WRIST = 0

    THUMB_MCP = 1
    THUMB_TIP = 4

    INDEX_MCP = 5
    INDEX_TIP = 8

    MIDDLE_MCP = 9
    MIDDLE_TIP = 12

    RING_MCP = 13
    RING_TIP = 16

    PINKY_MCP = 17
    PINKY_TIP = 20

    def _distance(self, a, b):
        return math.sqrt(
            (a.x - b.x) ** 2 +
            (a.y - b.y) ** 2
        )

    def _is_finger_extended(
        self,
        landmarks,
        base_index,
        tip_index,
    ):
        wrist = landmarks[self.WRIST]
        base = landmarks[base_index]
        tip = landmarks[tip_index]

        wrist_to_tip = self._distance(
            wrist,
            tip,
        )

        wrist_to_base = self._distance(
            wrist,
            base,
        )

        return wrist_to_tip > wrist_to_base

    def _is_thumb_extended(self, landmarks):

        wrist = landmarks[self.WRIST]

        thumb_mcp = landmarks[self.THUMB_MCP]
        thumb_tip = landmarks[self.THUMB_TIP]

        wrist_to_tip = self._distance(
            wrist,
            thumb_tip,
        )

        wrist_to_mcp = self._distance(
            wrist,
            thumb_mcp,
        )

        return wrist_to_tip > wrist_to_mcp

    def get_finger_states(self, landmarks):

        return {
            "thumb": self._is_thumb_extended(
                landmarks
            ),
            "index": self._is_finger_extended(
                landmarks,
                self.INDEX_MCP,
                self.INDEX_TIP,
            ),
            "middle": self._is_finger_extended(
                landmarks,
                self.MIDDLE_MCP,
                self.MIDDLE_TIP,
            ),
            "ring": self._is_finger_extended(
                landmarks,
                self.RING_MCP,
                self.RING_TIP,
            ),
            "pinky": self._is_finger_extended(
                landmarks,
                self.PINKY_MCP,
                self.PINKY_TIP,
            ),
        }

    def classify(self, landmarks):

        fingers = self.get_finger_states(
            landmarks
        )

        thumb = fingers["thumb"]
        index = fingers["index"]
        middle = fingers["middle"]
        ring = fingers["ring"]
        pinky = fingers["pinky"]

        if (
            thumb
            and index
            and middle
            and ring
            and pinky
        ):
            return "OPEN_PALM"

        if not any([
            thumb,
            index,
            middle,
            ring,
            pinky,
        ]):
            return "FIST"

        if (
            thumb
            and not index
            and not middle
            and not ring
            and not pinky
        ):
            return "THUMBS_UP"

        if (
            index
            and middle
            and not ring
            and not pinky
        ):
            return "PEACE"

        if (
            index
            and not middle
            and not ring
            and not pinky
        ):
            return "POINTING"

        return "UNKNOWN"