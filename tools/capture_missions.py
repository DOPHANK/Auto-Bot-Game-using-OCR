import sys
from pathlib import Path

import cv2
import yaml
import win32gui

from vision.window_capture import WindowCapture


CONFIG_FILE = Path("config/missions.yaml")
OUTPUT_DIR = Path("screenshots/missions")

selection = None
start_point = None
drawing = False
current_frame = None


def find_window(title):
    hwnd = win32gui.FindWindow(None, title)

    if not hwnd:
        raise RuntimeError(f"Window not found: {title}")

    return hwnd


def mouse_callback(event, x, y, flags, param):
    global selection
    global start_point
    global drawing
    global current_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        start_point = (x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing and start_point is not None:
            display = current_frame.copy()

            cv2.rectangle(
                display,
                start_point,
                (x, y),
                (0, 255, 0),
                2
            )

            cv2.imshow("Select Mission Row", display)

    elif event == cv2.EVENT_LBUTTONUP:
        if start_point is None:
            return

        drawing = False

        x1, y1 = start_point
        x2, y2 = x, y

        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        selection = (x1, y1, x2, y2)
        start_point = None


def save_config(selection):
    x1, y1, x2, y2 = selection

    width = x2 - x1
    height = y2 - y1

    if width < 5 or height < 5:
        raise RuntimeError("Mission row is too small.")

    slot_width = width / 5.0

    slots = {}

    for i in range(5):
        sx1 = round(i * slot_width)
        sx2 = round((i + 1) * slot_width)

        slots[f"slot_{i + 1}"] = {
            "x1": sx1,
            "x2": sx2,
        }

    config = {
        "missions": {
            "row": {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": width,
                "height": height,
            },
            "slots": slots,
        }
    }

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            config,
            f,
            allow_unicode=True,
            sort_keys=False,
        )

    print()
    print(f"Config saved: {CONFIG_FILE}")


def load_config():
    if not CONFIG_FILE.exists():
        return None

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def capture_slots(frame, config):
    missions = config["missions"]
    row_config = missions["row"]

    x1 = row_config["x1"]
    y1 = row_config["y1"]
    x2 = row_config["x2"]
    y2 = row_config["y2"]

    row = frame[y1:y2, x1:x2]

    if row.size == 0:
        raise RuntimeError("Mission row crop is empty.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    row_file = OUTPUT_DIR / "mission_row.png"

    if not cv2.imwrite(str(row_file), row):
        raise RuntimeError(f"Unable to save {row_file}")

    print()
    print("Mission row:")
    print(f"  Position : ({x1}, {y1}) -> ({x2}, {y2})")
    print(f"  Size     : {row.shape[1]} x {row.shape[0]}")
    print()

    for i in range(1, 6):
        slot_config = missions["slots"][f"slot_{i}"]

        sx1 = slot_config["x1"]
        sx2 = slot_config["x2"]

        slot = row[:, sx1:sx2]

        filename = OUTPUT_DIR / f"slot_{i}.png"

        if not cv2.imwrite(str(filename), slot):
            raise RuntimeError(f"Unable to save {filename}")

        print(
            f"Slot {i}: "
            f"{slot.shape[1]} x {slot.shape[0]} "
            f"-> {filename}"
        )

    print()
    print(f"Full row saved: {row_file}")


def setup_mode(frame):
    global current_frame

    current_frame = frame

    print("================================")
    print("      Setup Mission Row")
    print("================================")
    print()
    print(f"Captured client: {frame.shape[1]} x {frame.shape[0]}")
    print()
    print("Hướng dẫn:")
    print("  1. Kéo chuột chọn TOÀN BỘ hàng 5 nhiệm vụ.")
    print("  2. ENTER để xác nhận.")
    print("  3. ESC để hủy.")
    print()

    window_name = "Select Mission Row"

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, frame)
    cv2.setMouseCallback(window_name, mouse_callback)

    while True:
        key = cv2.waitKey(30) & 0xFF

        if key == 13:
            break

        if key == 27:
            print("Cancelled.")
            cv2.destroyAllWindows()
            return None

    cv2.destroyAllWindows()

    if selection is None:
        raise RuntimeError("No mission row selected.")

    save_config(selection)

    return load_config()


def main():
    if len(sys.argv) < 2:
        print('Usage:')
        print('  python -m tools.capture_missions "Vua Hải Tặc"')
        return

    title = sys.argv[1]

    hwnd = find_window(title)
    capture = WindowCapture(hwnd)
    frame = capture.grab()

    config = load_config()

    if config is None:
        print("missions.yaml not found.")
        print("Starting SETUP mode...")
        print()

        config = setup_mode(frame)

        if config is None:
            return

    else:
        print("missions.yaml found.")
        print("Using saved mission coordinates.")
        print()

    capture_slots(frame, config)


if __name__ == "__main__":
    main()
