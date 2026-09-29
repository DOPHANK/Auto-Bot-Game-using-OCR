from pathlib import Path

import cv2
import win32gui
import yaml

from vision.window_capture import WindowCapture


GAME_TITLE = "Vua Hải Tặc"

BUTTON_TEMPLATE_DIR = Path(
    "assets/templates/buttons"
)

BUTTON_CONFIG_PATH = Path(
    "config/buttons.yaml"
)


# ============================================================
# FIND GAME WINDOW
# ============================================================

def find_game_window():
    """
    Find the first visible Vua Hải Tặc window.
    """

    windows = []

    def callback(hwnd, extra):
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)

        if title == GAME_TITLE:
            windows.append(hwnd)

    win32gui.EnumWindows(callback, None)

    if not windows:
        raise RuntimeError(
            f'Cannot find game window: "{GAME_TITLE}"'
        )

    hwnd = windows[0]

    print(
        f"[WINDOW] HWND={hwnd}"
    )

    return hwnd


# ============================================================
# REGION SELECTOR
# ============================================================

class RegionSelector:

    def __init__(self, image):

        self.image = image

        self.display = image.copy()

        self.start = None
        self.end = None

        self.dragging = False

        self.window_name = "Select Button ROI"

    def mouse_callback(
        self,
        event,
        x,
        y,
        flags,
        param
    ):

        if event == cv2.EVENT_LBUTTONDOWN:

            self.start = (x, y)
            self.end = (x, y)

            self.dragging = True

        elif event == cv2.EVENT_MOUSEMOVE:

            if self.dragging:

                self.end = (x, y)

        elif event == cv2.EVENT_LBUTTONUP:

            self.end = (x, y)

            self.dragging = False

    def select(self):

        cv2.namedWindow(
            self.window_name,
            cv2.WINDOW_NORMAL
        )

        cv2.setMouseCallback(
            self.window_name,
            self.mouse_callback
        )

        while True:

            self.display = self.image.copy()

            if (
                self.start is not None
                and self.end is not None
            ):

                x1, y1 = self.start
                x2, y2 = self.end

                cv2.rectangle(
                    self.display,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

            cv2.imshow(
                self.window_name,
                self.display
            )

            key = cv2.waitKey(20) & 0xFF

            # ENTER -> confirm
            if key == 13:

                if (
                    self.start is not None
                    and self.end is not None
                ):
                    break

            # ESC -> cancel
            if key == 27:

                self.start = None
                self.end = None

                break

        cv2.destroyWindow(
            self.window_name
        )

        if (
            self.start is None
            or self.end is None
        ):
            return None

        x1, y1 = self.start
        y1 = self.start[1]

        x2, y2 = self.end
        y2 = self.end[1]

        # Normalize coordinates
        left = min(x1, x2)
        right = max(x1, x2)

        top = min(y1, y2)
        bottom = max(y1, y2)

        if right <= left or bottom <= top:
            return None

        return {
            "x1": left,
            "y1": top,
            "x2": right,
            "y2": bottom,
            "width": right - left,
            "height": bottom - top,
        }


# ============================================================
# CONFIG
# ============================================================

def load_config():

    if not BUTTON_CONFIG_PATH.exists():
        return {
            "buttons": {}
        }

    with open(
        BUTTON_CONFIG_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        config = yaml.safe_load(f)

    if not config:
        config = {}

    if "buttons" not in config:
        config["buttons"] = {}

    return config


def save_config(config):

    BUTTON_CONFIG_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        BUTTON_CONFIG_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        yaml.safe_dump(
            config,
            f,
            allow_unicode=True,
            sort_keys=False
        )


# ============================================================
# TEMPLATE NUMBER
# ============================================================

def get_next_number(button_dir):

    button_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    numbers = []

    for file in button_dir.glob("*.png"):

        try:
            number = int(
                file.stem
            )

            numbers.append(number)

        except ValueError:
            pass

    if not numbers:
        return 1

    return max(numbers) + 1


# ============================================================
# SAVE TEMPLATE
# ============================================================

def save_template(
    image,
    button_name
):

    button_dir = (
        BUTTON_TEMPLATE_DIR
        / button_name
    )

    number = get_next_number(
        button_dir
    )

    filename = (
        button_dir
        / f"{number:03d}.png"
    )

    if not cv2.imwrite(
        str(filename),
        image
    ):
        raise RuntimeError(
            f"Cannot save template: {filename}"
        )

    return filename


# ============================================================
# SAVE BUTTON CONFIG
# ============================================================

def save_button_config(
    button_name,
    roi
):

    config = load_config()

    # Keep one ROI for the logical button.
    #
    # Multiple images such as:
    #   select/001.png
    #   select/002.png
    #   select/003.png
    #
    # are template variants of the same button.

    config["buttons"][button_name] = roi

    save_config(config)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("BotVHT - Capture Button Template")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Find game
    # --------------------------------------------------------

    hwnd = find_game_window()

    print(
        "[CAPTURE] Capturing game window..."
    )

    # IMPORTANT:
    # Use the same WindowCapture that is already used
    # successfully by the mission detector.

    capture = WindowCapture(hwnd)

    frame = capture.grab()

    print(
        f"[CAPTURE] Frame size: "
        f"{frame.shape[1]} x {frame.shape[0]}"
    )

    # --------------------------------------------------------
    # 2. Select button ROI
    # --------------------------------------------------------

    print()
    print("Drag around the button.")
    print("Press ENTER to confirm.")
    print("Press ESC to cancel.")

    selector = RegionSelector(frame)

    roi = selector.select()

    if roi is None:

        print(
            "[CANCEL] No ROI selected."
        )

        return

    print()
    print(
        "[ROI]",
        roi
    )

    # --------------------------------------------------------
    # 3. Ask button name
    # --------------------------------------------------------

    button_name = input(
        "Button name: "
    ).strip()

    if not button_name:

        print(
            "[ERROR] Button name is empty."
        )

        return

    # --------------------------------------------------------
    # 4. Crop
    # --------------------------------------------------------

    x1 = roi["x1"]
    y1 = roi["y1"]
    x2 = roi["x2"]
    y2 = roi["y2"]

    cropped = frame[
        y1:y2,
        x1:x2
    ]

    if cropped.size == 0:

        print(
            "[ERROR] Cropped image is empty."
        )

        return

    # --------------------------------------------------------
    # 5. Save template
    # --------------------------------------------------------

    template_path = save_template(
        cropped,
        button_name
    )

    print(
        f"[SAVE] Template: "
        f"{template_path}"
    )

    # --------------------------------------------------------
    # 6. Save YAML position
    # --------------------------------------------------------

    save_button_config(
        button_name,
        roi
    )

    print(
        f"[SAVE] Config: "
        f"{BUTTON_CONFIG_PATH}"
    )

    # --------------------------------------------------------
    # 7. Preview
    # --------------------------------------------------------

    cv2.imshow(
        f"Button - {button_name}",
        cropped
    )

    print()
    print(
        "Press any key to close preview."
    )

    cv2.waitKey(0)

    cv2.destroyAllWindows()

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()