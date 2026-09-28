from vision.template import TemplateMatcher


class GameDetector:
    def __init__(self, threshold=0.80):
        self.matcher = TemplateMatcher(threshold)

    def detect_nvhn(self, frame):
        return self.matcher.find(
            frame,
            "assets/templates/NVHN.png"
        )

    def detect(self, frame):
        return {
            "nvhn": self.detect_nvhn(frame)
        }