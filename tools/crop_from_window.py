import sys
from pathlib import Path

import cv2
import win32gui

from vision.window_capture import WindowCapture


selection = None
start_point = None
drawing = False


def find_window(title):
    hwnd = win32gui.FindWindow(None, title)

    if not hwnd:
        raise RuntimeError(
            f"Window not found: {title}"
        )

    return hwnd


def mouse_callback(event, x, y, flags, param):
    global selection
    global start_point
    global drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            frame = param.copy()

            cv2.rectangle(
                frame,
                start_point,
                (x, y),
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "Crop Window Capture",
                frame
            )

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

        x1, y1 = start_point
        x2, y2 = x, y

        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        selection = (
            x1,
            y1,
            x2,
            y2
        )


def main():
    if len(sys.argv) < 2:
        print(
            'Usage: python -m tools.crop_from_window "WINDOW TITLE"'
        )
        return

    title = sys.argv[1]

    hwnd = find_window(title)

    capture = WindowCapture(hwnd)

    frame = capture.grab()

    print("================================")
    print("     Crop Window Template")
    print("================================")
    print()

    print(
        f"Captured client: "
        f"{frame.shape[1]} x {frame.shape[0]}"
    )

    print()
    print("Cách sử dụng:")
    print("  1. Cửa sổ capture sẽ hiện ra.")
    print("  2. Kéo chuột quanh icon NVHN.")
    print("  3. Nhấn ENTER để lưu.")
    print("  4. Nhấn ESC để hủy.")

    window_name = "Crop Window Capture"

    cv2.namedWindow(
        window_name,
        cv2.WINDOW_NORMAL
    )

    cv2.imshow(
        window_name,
        frame
    )

    cv2.setMouseCallback(
        window_name,
        mouse_callback,
        frame
    )

    while True:
        key = cv2.waitKey(30) & 0xFF

        if key == 13:  # ENTER
            break

        if key == 27:  # ESC
            print("Cancelled.")
            cv2.destroyAllWindows()
            return

    cv2.destroyAllWindows()

    if selection is None:
        raise RuntimeError(
            "No region selected."
        )

    x1, y1, x2, y2 = selection

    width = x2 - x1
    height = y2 - y1

    print()
    print(
        f"Selected: "
        f"({x1}, {y1}) -> ({x2}, {y2})"
    )

    print(
        f"Size: {width} x {height}"
    )

    if width < 5 or height < 5:
        raise RuntimeError(
            "Selected region is too small."
        )

    crop = frame[
        y1:y2,
        x1:x2
    ]

    output = Path(
        "assets/templates/NVHN_window.png"
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not cv2.imwrite(
        str(output),
        crop
    ):
        raise RuntimeError(
            f"Unable to save: {output}"
        )

    print()
    print(
        f"Saved: {output}"
    )

    print(
        f"Template size: "
        f"{crop.shape[1]} x {crop.shape[0]}"
    )


if __name__ == "__main__":
    main()