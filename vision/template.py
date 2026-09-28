from pathlib import Path

import cv2
import numpy as np


class TemplateMatcher:
    def __init__(self, threshold=0.80):
        self.threshold = threshold

    def find(self, frame, template_path):
        template_path = Path(template_path)

        if not template_path.exists():
            raise FileNotFoundError(
                f"Template not found: {template_path}"
            )

        template = cv2.imread(
            str(template_path),
            cv2.IMREAD_COLOR
        )

        if template is None:
            raise ValueError(
                f"Unable to read template: {template_path}"
            )

        # Nếu template lớn hơn frame thì không thể match
        if (
            template.shape[0] > frame.shape[0]
            or template.shape[1] > frame.shape[1]
        ):
            return None

        result = cv2.matchTemplate(
            frame,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_value, _, max_location = cv2.minMaxLoc(
            result
        )

        if max_value < self.threshold:
            return None

        height, width = template.shape[:2]

        x, y = max_location

        return {
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "center": (
                x + width // 2,
                y + height // 2
            ),
            "confidence": float(max_value),
        }

    def debug_find(self, frame, template_path):
        template = cv2.imread(
            str(template_path),
            cv2.IMREAD_COLOR
        )

        if template is None:
            raise ValueError(
                f"Unable to read template: {template_path}"
            )

        result = cv2.matchTemplate(
            frame,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_value, _, max_location = cv2.minMaxLoc(
            result
        )

        return {
            "confidence": float(max_value),
            "position": max_location,
        }