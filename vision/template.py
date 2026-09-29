from pathlib import Path

import cv2
import numpy as np


class TemplateMatcher:
    def __init__(self, threshold=0.80):
        self.threshold = threshold

    def _load_template(self, template_path):
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

        return template

    def find(self, frame, template_path):
        template = self._load_template(template_path)

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

        _, max_value, _, max_location = cv2.minMaxLoc(result)

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

    def find_all(
        self,
        frame,
        template_path,
        threshold=None,
        max_results=20,
        min_distance=10,
    ):
        """
        Find multiple template matches over the entire frame.

        Results are sorted by confidence and nearby overlapping
        detections are suppressed.

        Args:
            frame: BGR image.
            template_path: template image path.
            threshold: minimum matching confidence.
            max_results: maximum number of returned candidates.
            min_distance: minimum distance between candidate centers.
        """

        template = self._load_template(template_path)

        if (
            template.shape[0] > frame.shape[0]
            or template.shape[1] > frame.shape[1]
        ):
            return []

        if threshold is None:
            threshold = self.threshold

        result = cv2.matchTemplate(
            frame,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        locations = np.where(result >= threshold)

        height, width = template.shape[:2]

        raw_candidates = []

        for y, x in zip(*locations):
            confidence = float(result[y, x])

            raw_candidates.append({
                "x": int(x),
                "y": int(y),
                "width": width,
                "height": height,
                "center": (
                    int(x + width // 2),
                    int(y + height // 2)
                ),
                "confidence": confidence,
            })

        # Highest confidence first.
        raw_candidates.sort(
            key=lambda d: d["confidence"],
            reverse=True
        )

        # Remove candidates that are effectively the same match.
        candidates = []

        for candidate in raw_candidates:

            cx, cy = candidate["center"]

            too_close = False

            for selected in candidates:
                sx, sy = selected["center"]

                distance = (
                    (cx - sx) ** 2
                    +
                    (cy - sy) ** 2
                ) ** 0.5

                if distance < min_distance:
                    too_close = True
                    break

            if too_close:
                continue

            candidates.append(candidate)

            if len(candidates) >= max_results:
                break

        return candidates

    def debug_find(self, frame, template_path):
        template = self._load_template(template_path)

        result = cv2.matchTemplate(
            frame,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_value, _, max_location = cv2.minMaxLoc(result)

        return {
            "confidence": float(max_value),
            "position": max_location,
        }