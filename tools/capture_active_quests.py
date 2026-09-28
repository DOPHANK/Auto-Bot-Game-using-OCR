import sys
from pathlib import Path

import cv2
import yaml
import win32gui

from vision.window_capture import WindowCapture


CONFIG_FILE = Path("config/active_quests.yaml")
OUTPUT_DIR = Path("screenshots/active_quests")


selection = None
start_point = None
drawing = False
current_frame = None


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

            cv2.imshow(
                "Select Active Quest Area",
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


def setup_config(frame):
    global current_frame

    current_frame = frame

    print("======================================")
    print("       SETUP ACTIVE QUEST AREA")
    print("======================================")
    print()
    print(
        f"Captured client: "
        f"{frame.shape[1]} x {frame.shape[0]}"
    )
    print()
    print("Hướng dẫn:")
    print("  1. Kéo chọn TOÀN BỘ vùng Active Quest.")
    print("  2. Bao gồm Quest 1, Quest 2, Quest 3.")
    print("  3. ENTER để xác nhận.")
    print("  4. ESC để hủy.")
    print()

    window_name = "Select Active Quest Area"

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
        mouse_callback
    )

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
        raise RuntimeError(
            "No Active Quest area selected."
        )

    x1, y1, x2, y2 = selection

    width = x2 - x1
    height = y2 - y1

    if width < 10 or height < 10:
        raise RuntimeError(
            "Active Quest area is too small."
        )

    print()
    print("Now define Quest 1, Quest 2, Quest 3.")
    print()

    quest_boxes = {}

    # Crop full Active Quest area
    area = frame[y1:y2, x1:x2]

    quest_boxes = select_quest_boxes(
        area
    )

    config = {
        "active_quests": {
            "area": {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "width": width,
                "height": height,
            },

            "quest_1": quest_boxes["quest_1"],
            "quest_2": quest_boxes["quest_2"],
            "quest_3": quest_boxes["quest_3"],
        }
    }

    CONFIG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CONFIG_FILE,
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
        f"Config saved: {CONFIG_FILE}"
    )

    return config


def select_quest_boxes(area):
    """
    One-time setup:
    manually select Quest 1, Quest 2, Quest 3
    inside the already selected Active Quest area.
    """

    boxes = {}

    for quest_number in range(1, 4):

        window_name = (
            f"Select Quest {quest_number}"
        )

        print(
            f"Select Quest {quest_number}"
        )
        print(
            "  Kéo chọn vùng image của quest."
        )
        print(
            "  ENTER để xác nhận."
        )
        print()

        local_selection = None
        local_start = None
        local_drawing = False

        def callback(
            event,
            x,
            y,
            flags,
            param
        ):
            nonlocal local_selection
            nonlocal local_start
            nonlocal local_drawing

            if event == cv2.EVENT_LBUTTONDOWN:

                local_start = (x, y)
                local_drawing = True

            elif event == cv2.EVENT_MOUSEMOVE:

                if (
                    local_drawing
                    and local_start is not None
                ):

                    display = area.copy()

                    cv2.rectangle(
                        display,
                        local_start,
                        (x, y),
                        (0, 255, 0),
                        2
                    )

                    cv2.imshow(
                        window_name,
                        display
                    )

            elif event == cv2.EVENT_LBUTTONUP:

                if local_start is None:
                    return

                local_drawing = False

                x1, y1 = local_start
                x2, y2 = x, y

                x1, x2 = sorted(
                    (x1, x2)
                )

                y1, y2 = sorted(
                    (y1, y2)
                )

                local_selection = (
                    x1,
                    y1,
                    x2,
                    y2
                )

                local_start = None

        cv2.namedWindow(
            window_name,
            cv2.WINDOW_NORMAL
        )

        cv2.imshow(
            window_name,
            area
        )

        cv2.setMouseCallback(
            window_name,
            callback
        )

        while True:

            key = cv2.waitKey(30) & 0xFF

            if key == 13:
                break

            if key == 27:

                cv2.destroyAllWindows()

                raise RuntimeError(
                    "Quest selection cancelled."
                )

        cv2.destroyWindow(
            window_name
        )

        if local_selection is None:
            raise RuntimeError(
                f"Quest {quest_number} "
                "was not selected."
            )

        qx1, qy1, qx2, qy2 = (
            local_selection
        )

        boxes[
            f"quest_{quest_number}"
        ] = {
            "x1": qx1,
            "y1": qy1,
            "x2": qx2,
            "y2": qy2,
        }

    return boxes


def load_config():
    if not CONFIG_FILE.exists():
        return None

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return yaml.safe_load(f)


def crop_from_config(frame, config):
    active = config["active_quests"]

    area_config = active["area"]

    ax1 = int(area_config["x1"])
    ay1 = int(area_config["y1"])
    ax2 = int(area_config["x2"])
    ay2 = int(area_config["y2"])

    # ==========================================
    # CROP FULL ACTIVE QUEST AREA
    # ==========================================

    area = frame[
        ay1:ay2,
        ax1:ax2
    ]

    if area.size == 0:
        raise RuntimeError(
            "Active Quest area is empty."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    active_file = (
        OUTPUT_DIR / "active_quests.png"
    )

    if not cv2.imwrite(
        str(active_file),
        area
    ):
        raise RuntimeError(
            f"Unable to save {active_file}"
        )

    print()
    print("Active Quest area:")
    print(
        f"  Position: "
        f"({ax1}, {ay1}) -> "
        f"({ax2}, {ay2})"
    )

    print(
        f"  Size: "
        f"{area.shape[1]} x "
        f"{area.shape[0]}"
    )

    print()

    # ==========================================
    # QUEST 1 / 2 / 3
    #
    # YAML stores coordinates relative
    # to the FULL CLIENT.
    #
    # Convert them to local coordinates
    # inside 'area'.
    # ==========================================

    for quest_number in range(1, 4):

        quest_name = f"quest_{quest_number}"

        quest_config = active[quest_name]

        qx1 = int(quest_config["x1"])
        qy1 = int(quest_config["y1"])
        qx2 = int(quest_config["x2"])
        qy2 = int(quest_config["y2"])

        # Convert client coordinates
        # -> coordinates relative to area

        local_x1 = qx1 - ax1
        local_y1 = qy1 - ay1
        local_x2 = qx2 - ax1
        local_y2 = qy2 - ay1

        print(
            f"{quest_name}: "
            f"client "
            f"({qx1}, {qy1}) -> "
            f"({qx2}, {qy2})"
        )

        print(
            f"  local "
            f"({local_x1}, {local_y1}) -> "
            f"({local_x2}, {local_y2})"
        )

        # Validate coordinates

        if (
            local_x1 < 0
            or local_y1 < 0
            or local_x2 > area.shape[1]
            or local_y2 > area.shape[0]
            or local_x2 <= local_x1
            or local_y2 <= local_y1
        ):
            raise RuntimeError(
                f"{quest_name} coordinates are "
                f"outside Active Quest area."
            )

        quest = area[
            local_y1:local_y2,
            local_x1:local_x2
        ]

        if quest.size == 0:
            raise RuntimeError(
                f"{quest_name} crop is empty."
            )

        filename = (
            OUTPUT_DIR
            / f"{quest_name}.png"
        )

        if not cv2.imwrite(
            str(filename),
            quest
        ):
            raise RuntimeError(
                f"Unable to save {filename}"
            )

        print(
            f"  saved: {filename}"
        )

        print(
            f"  size: "
            f"{quest.shape[1]} x "
            f"{quest.shape[0]}"
        )

        print()

    print(
        "Active Quest capture completed."
    )


def main():

    if len(sys.argv) < 2:

        print(
            'Usage: '
            'python -m tools.capture_active_quests '
            '"Vua Hải Tặc"'
        )

        return

    title = sys.argv[1]

    hwnd = find_window(title)

    capture = WindowCapture(hwnd)

    frame = capture.grab()

    config = load_config()

    # ==========================================
    # FIRST RUN
    # ==========================================

    if config is None:

        print(
            "active_quests.yaml not found."
        )

        print(
            "Starting one-time setup..."
        )

        config = setup_config(
            frame
        )

        if config is None:
            return

    # ==========================================
    # NORMAL RUN
    # ==========================================

    else:

        print(
            "active_quests.yaml found."
        )

        print(
            "Using saved coordinates."
        )

        print()

    # ==========================================
    # AUTOMATIC CAPTURE
    # ==========================================

    crop_from_config(
        frame,
        config
    )


if __name__ == "__main__":
    main()