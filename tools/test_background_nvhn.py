import sys

import win32gui

from vision.window_capture import WindowCapture
from vision.template import TemplateMatcher


def main():
    if len(sys.argv) < 2:
        print(
            'Usage: python -m tools.test_background_nvhn "WINDOW TITLE"'
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

    print("================================")
    print(" Background NVHN Detection")
    print("================================")
    print()

    capture = WindowCapture(hwnd)

    frame = capture.grab()

    print(
        f"Frame: "
        f"{frame.shape[1]} x {frame.shape[0]}"
    )

    matcher = TemplateMatcher(
        threshold=0.80
    )

    result = matcher.find(
        frame,
        "assets/templates/NVHN_window.png"
    )

    if result is None:
        print()
        print("NVHN: NOT FOUND")
        return

    print()
    print("NVHN: FOUND")
    print(
        f"Position   : "
        f"({result['x']}, {result['y']})"
    )
    print(
        f"Center     : "
        f"{result['center']}"
    )
    print(
        f"Size       : "
        f"{result['width']} x {result['height']}"
    )
    print(
        f"Confidence : "
        f"{result['confidence']:.3f}"
    )


if __name__ == "__main__":
    main()