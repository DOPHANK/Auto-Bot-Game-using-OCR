import sys
import time

import cv2
import win32gui

from vision.window_capture import WindowCapture
from vision.template import TemplateMatcher
from bot.window_controller import WindowController


def main():
    if len(sys.argv) < 2:
        print(
            'Usage: python -m tools.capture_after_click "WINDOW TITLE"'
        )
        return

    title = sys.argv[1]

    hwnd = win32gui.FindWindow(
        None,
        title
    )

    if not hwnd:
        raise RuntimeError(
            f"Window not found: {title}"
        )

    capture = WindowCapture(hwnd)

    matcher = TemplateMatcher(0.80)

    frame = capture.grab()

    result = matcher.find(
        frame,
        "assets/templates/NVHN_window.png"
    )

    if result is None:
        print("NVHN not found.")
        return

    x, y = result["center"]

    print(
        f"NVHN: ({x}, {y})"
    )

    print(
        "Clicking in 3 seconds..."
    )

    time.sleep(3)

    controller = WindowController(hwnd)

    controller.click(x, y)

    print(
        "Click sent."
    )

    print(
        "Waiting for Daily Mission panel..."
    )

    time.sleep(2)

    frame = capture.grab()

    output = (
        "screenshots/"
        "daily_mission_window.png"
    )

    cv2.imwrite(
        output,
        frame
    )

    print()
    print(
        f"Saved: {output}"
    )


if __name__ == "__main__":
    main()