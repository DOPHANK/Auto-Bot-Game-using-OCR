import sys

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
            'Usage: python -m tools.debug_background "WINDOW TITLE"'
        )
        return

    title = sys.argv[1]

    hwnd = find_window(title)

    print("================================")
    print("   Background Template Debug")
    print("================================")
    print()

    print(f"HWND: {hwnd}")

    capture = WindowCapture(hwnd)

    frame = capture.grab()

    print(
        f"Frame: "
        f"{frame.shape[1]} x {frame.shape[0]}"
    )

    matcher = TemplateMatcher()

    result = matcher.debug_find(
        frame,
        "assets/templates/NVHN.png"
    )

    print()
    print(
        f"Best confidence : "
        f"{result['confidence']:.4f}"
    )

    print(
        f"Best position   : "
        f"{result['position']}"
    )


if __name__ == "__main__":
    main()