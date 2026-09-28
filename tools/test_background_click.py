import sys
import time

import win32gui

from vision.window_capture import WindowCapture
from vision.template import TemplateMatcher
from bot.window_controller import WindowController


def main():
    if len(sys.argv) < 2:
        print(
            'Usage: python -m tools.test_background_click "WINDOW TITLE"'
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

    matcher = TemplateMatcher(
        threshold=0.80
    )

    print("Capturing game window...")

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
        f"NVHN found at client coordinates: "
        f"({x}, {y})"
    )

    print(
        f"Confidence: "
        f"{result['confidence']:.3f}"
    )

    print()
    print("Background click in 5 seconds...")
    print("Move your physical mouse normally.")

    time.sleep(5)

    controller = WindowController(hwnd)

    controller.click(
        x,
        y
    )

    print()
    print("Background click sent.")


if __name__ == "__main__":
    main()