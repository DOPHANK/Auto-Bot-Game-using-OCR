import sys
from pathlib import Path

import cv2
import yaml
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
        if drawing and start_point is not None:
            display = param.copy()

            cv2.rectangle(
                display,
                start_point,
                (x, y),
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "Select Refresh Button",
                display
            )

    elif event == cv2.EVENT_LBUTTONUP:
        if start_point is None:
            return

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

        start_point = None


def main():

    if len(sys.argv) < 2:
        print(
            'Usage: python -m tools.capture_refresh '
            '"WINDOW TITLE"'
        )
        return

    title = sys.argv[1]

    hwnd = find_window(title)

    capture = WindowCapture(hwnd)

    frame = capture.grab()

    print("================================")
    print("       Capture Refresh")
    print("================================")
    print()

    print(
        f"Client: "
        f"{frame.shape[1]} x "
        f"{frame.shape[0]}"
    )

    print()
    print("Hướng dẫn:")
    print("  1. Kéo quanh NÚT LÀM MỚI.")
    print("  2. Chỉ chọn vùng nút.")
    print("  3. ENTER để xác nhận.")
    print("  4. ESC để hủy.")

    window_name = "Select Refresh Button"

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

        if key == 13:
            break

        if key == 27:
            print("Cancelled.")
            cv2.destroyAllWindows()
            return

    cv2.destroyAllWindows()

    if selection is None:
        raise RuntimeError(
            "No refresh button selected."
        )

    x1, y1, x2, y2 = selection

    width = x2 - x1
    height = y2 - y1

    print()
    print("Refresh button:")
    print(
        f"  Position : "
        f"({x1}, {y1}) -> ({x2}, {y2})"
    )
    print(
        f"  Size     : "
        f"{width} x {height}"
    )

    # ========================================================
    # Save button crop
    # ========================================================

    crop = frame[
        y1:y2,
        x1:x2
    ]

    image_path = Path(
        "assets/templates/refresh.png"
    )

    image_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not cv2.imwrite(
        str(image_path),
        crop
    ):
        raise RuntimeError(
            f"Unable to save {image_path}"
        )

    # ========================================================
    # Save configuration
    # ========================================================

    config_path = Path(
        "config/refresh.yaml"
    )

    config_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    config = {
        "refresh": {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "center": {
                "x": x1 + width // 2,
                "y": y1 + height // 2
            },
            "width": width,
            "height": height
        }
    }

    with open(
        config_path,
        "w",
        encoding="utf-8"
    ) as f:
        yaml.safe_dump(
            config,
            f,
            allow_unicode=True,
            sort_keys=False
        )

    print()
    print(
        f"Template saved: {image_path}"
    )

    print(
        f"Config saved: {config_path}"
    )

    print()
    print("Done.")


if __name__ == "__main__":
    main()