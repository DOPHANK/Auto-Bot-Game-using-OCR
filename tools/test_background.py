import sys

import cv2
import win32gui

from vision.window_capture import WindowCapture
from vision.template import TemplateMatcher


def find_window(title):
    hwnd = win32gui.FindWindow(
        None,
        title
    )

    if not hwnd:
        raise RuntimeError(
            f"Window not found: {title}"
        )

    return hwnd


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:"
        )
        print(
            'python -m tools.test_background "WINDOW TITLE"'
        )
        return

    title = sys.argv[1]

    print("================================")
    print("     Background Capture Test")
    print("================================")
    print()

    hwnd = find_window(title)

    print(f"HWND: {hwnd}")

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    print(
        f"Window: "
        f"{right - left} x {bottom - top}"
    )

    capture = WindowCapture(hwnd)

    frame = capture.grab()

    print(
        f"Client: "
        f"{frame.shape[1]} x {frame.shape[0]}"
    )

    cv2.imwrite(
        "screenshots/window_capture.png",
        frame
    )

    print()
    print(
        "Saved: screenshots/window_capture.png"
    )

    matcher = TemplateMatcher(
        threshold=0.80
    )

    result = matcher.find(
        frame,
        "assets/templates/NVHN.png"
    )

    if result is None:
        print()
        print("NVHN: NOT FOUND")
    else:
        print()
        print("NVHN: FOUND")
        print(f"Position   : ({result['x']}, {result['y']})")
        print(f"Center     : {result['center']}")
        print(f"Confidence : {result['confidence']:.3f}")


if __name__ == "__main__":
    main()