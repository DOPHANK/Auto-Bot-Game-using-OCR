from pathlib import Path

import cv2
import yaml

from vision.template import TemplateMatcher


class GameDetector:

    def __init__(self, threshold=0.80):
        self.matcher = TemplateMatcher(threshold)

        self.active_quests_dir = Path(
            "assets/templates/active_quests"
        )

        self.missions_dir = Path(
            "assets/templates/missions"
        )

        self.active_quests_config = self._load_yaml(
            "config/active_quests.yaml"
        )

        self.missions_config = self._load_yaml(
            "config/missions.yaml"
        )

    # ============================================================
    # YAML
    # ============================================================

    def _load_yaml(self, path):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Config not found: {path}"
            )

        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    # ============================================================
    # ROI
    # ============================================================

    def _crop_roi(self, frame, roi):
        x1 = roi["x1"]
        y1 = roi["y1"]
        x2 = roi["x2"]
        y2 = roi["y2"]

        return frame[y1:y2, x1:x2]

    def _offset_detection(
        self,
        detection,
        offset_x,
        offset_y
    ):
        detection["x"] += offset_x
        detection["y"] += offset_y

        cx, cy = detection["center"]

        detection["center"] = (
            cx + offset_x,
            cy + offset_y
        )

        return detection

    # ============================================================
    # NVHN
    # ============================================================

    def detect_nvhn(self, frame):
        return self.matcher.find(
            frame,
            "assets/templates/buttons/NVHN/001.png"
        )

    # ============================================================
    # ACTIVE QUESTS
    # ============================================================

    def detect_active_quests(self, frame):

        config = self.active_quests_config["active_quests"]

        detections = []

        # Chỉ kiểm tra đúng 3 slot được định nghĩa trong YAML
        for slot_name in (
            "quest_1",
            "quest_2",
            "quest_3",
        ):

            if slot_name not in config:
                continue

            roi = config[slot_name]

            crop = self._crop_roi(
                frame,
                roi
            )

            best_detection = None

            # Mỗi slot có thể match với nhiều template variant
            for category_dir in sorted(
                self.active_quests_dir.iterdir()
            ):

                if not category_dir.is_dir():
                    continue

                category = category_dir.name

                for template_path in sorted(
                    category_dir.glob("*.png")
                ):

                    detection = self.matcher.find(
                        crop,
                        template_path
                    )

                    if detection is None:
                        continue

                    if (
                        best_detection is None
                        or detection["confidence"]
                        > best_detection["confidence"]
                    ):
                        best_detection = detection.copy()

                        best_detection["type"] = category
                        best_detection["template"] = (
                            template_path.stem
                        )

            if best_detection is None:
                continue

            best_detection = self._offset_detection(
                best_detection,
                roi["x1"],
                roi["y1"]
            )

            best_detection["slot"] = slot_name

            detections.append(
                best_detection
            )

        return detections

    # ============================================================
    # MISSIONS
    # ============================================================

    def detect_missions(self, frame):

        config = self.missions_config["missions"]

        row = config["row"]
        slots = config["slots"]

        detections = []

        for slot_name, slot_config in slots.items():

            # --------------------------------------------------------
            # Slot coordinates are relative to missions.row
            # --------------------------------------------------------

            x1 = row["x1"] + slot_config["x1"]
            y1 = row["y1"]

            x2 = row["x1"] + slot_config["x2"]
            y2 = row["y2"]

            roi = {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
            }

            crop = self._crop_roi(
                frame,
                roi
            )

            best_detection = None

            # --------------------------------------------------------
            # Try every mission category/template in this slot
            # --------------------------------------------------------

            for category_dir in sorted(
                self.missions_dir.iterdir()
            ):

                if not category_dir.is_dir():
                    continue

                category = category_dir.name

                for template_path in sorted(
                    category_dir.glob("*.png")
                ):

                    detection = self.matcher.find(
                        crop,
                        template_path
                    )

                    if detection is None:
                        continue

                    if (
                        best_detection is None
                        or detection["confidence"]
                        > best_detection["confidence"]
                    ):
                        best_detection = detection.copy()

                        best_detection["type"] = category
                        best_detection["template"] = (
                            template_path.stem
                        )

            # --------------------------------------------------------
            # No mission in this slot
            # --------------------------------------------------------

            if best_detection is None:
                continue

            # --------------------------------------------------------
            # Convert slot-local coordinates back to game coordinates
            # --------------------------------------------------------

            best_detection = self._offset_detection(
                best_detection,
                x1,
                y1
            )

            best_detection["slot"] = slot_name

            detections.append(
                best_detection
            )

        return detections

    # ============================================================
    # DETECT
    # ============================================================

    def detect(self, frame):

        return {
            "nvhn": self.detect_nvhn(frame),

            "active_quests":
                self.detect_active_quests(frame),

            "missions":
                self.detect_missions(frame),
        }