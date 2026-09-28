import mss
import numpy as np
import cv2


class ScreenCapture:
    def __init__(self, monitor=1):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[monitor]

    def grab(self):
        screenshot = self.sct.grab(self.monitor)

        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        return frame

    def save(self, filename="screenshots/screen.png"):
        frame = self.grab()
        cv2.imwrite(filename, frame)
        return frame