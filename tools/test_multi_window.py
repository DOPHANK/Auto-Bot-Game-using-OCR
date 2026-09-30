import time
from pathlib import Path

import cv2
import win32api
import win32con
import win32gui

from vision.window_capture import WindowCapture
from vision.template import TemplateMatcher


# ============================================================
# CONFIG
# ============================================================

GAME_TITLE = "Vua Hải Tặc"

NVHN_TEMPLATE = Path(
    "assets/templates/buttons/NVHN/001.png"
)

DEBUG_DIR = Path(
    "debug/multi_window"
)

THRESHOLD = 0.80
CLICK_WAIT = 3.0


# ============================================================
# FIND ALL GAME WINDOWS
# ============================================================

def find_all_game_windows():
    windows = []

    def enum_callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)

        if title == GAME_TITLE:
            windows.append(hwnd)

    win32gui.EnumWindows(
        enum_callback,
        None
    )

    return windows


# ============================================================
# WINDOW INFO
# ============================================================

def print_window_info(index, hwnd):
    title = win32gui.GetWindowText(hwnd)

    left, top, right, bottom = (
        win32gui.GetWindowRect(hwnd)
    )

    client_left, client_top, client_right, client_bottom = (
        win32gui.GetClientRect(hwnd)
    )

    width = client_right - client_left
    height = client_bottom - client_top

    foreground = win32gui.GetForegroundWindow()

    print()
    print("-" * 70)
    print(f"[BOT {index}]")
    print(f"[BOT {index}] HWND       = {hwnd}")
    print(f"[BOT {index}] Title      = {title}")
    print(
        f"[BOT {index}] Window     = "
        f"({left},{top}) -> ({right},{bottom})"
    )
    print(
        f"[BOT {index}] Client     = "
        f"{width}x{height}"
    )

    if foreground == hwnd:
        print(
            f"[BOT {index}] Foreground = YES"
        )
    else:
        print(
            f"[BOT {index}] Foreground = NO"
        )


# ============================================================
# CAPTURE
# ============================================================

def capture_game(index, hwnd):
    capture = WindowCapture(hwnd)

    frame = capture.grab()

    print(
        f"[BOT {index}] Capture = "
        f"{frame.shape[1]}x{frame.shape[0]}"
    )

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    path = (
        DEBUG_DIR /
        f"bot_{index}_before.png"
    )

    cv2.imwrite(
        str(path),
        frame
    )

    print(
        f"[BOT {index}] Saved = {path}"
    )

    return frame


# ============================================================
# NVHN DETECTION
# ============================================================

def detect_nvhn(index, frame):
    matcher = TemplateMatcher(
        threshold=THRESHOLD
    )

    detection = matcher.find(
        frame,
        NVHN_TEMPLATE
    )

    if detection is None:
        print(
            f"[BOT {index}] NVHN = NOT FOUND"
        )
        return None

    print(
        f"[BOT {index}] NVHN = FOUND"
    )

    print(
        f"[BOT {index}] confidence = "
        f"{detection['confidence']:.4f}"
    )

    print(
        f"[BOT {index}] center = "
        f"{detection['center']}"
    )

    return detection


# ============================================================
# BACKGROUND CLICK
# ============================================================

def background_click(index, hwnd, x, y):
    x = int(x)
    y = int(y)

    lparam = win32api.MAKELONG(
        x,
        y
    )

    foreground_before = (
        win32gui.GetForegroundWindow()
    )

    mouse_before = (
        win32api.GetCursorPos()
    )

    print()
    print(
        f"[BOT {index}] Background click"
    )

    print(
        f"[BOT {index}] HWND = {hwnd}"
    )

    print(
        f"[BOT {index}] client = "
        f"({x},{y})"
    )

    print(
        f"[BOT {index}] foreground before = "
        f"{foreground_before}"
    )

    print(
        f"[BOT {index}] mouse before = "
        f"{mouse_before}"
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # No SetForegroundWindow()
    # No BringWindowToTop()
    # No pyautogui
    # --------------------------------------------------------

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        lparam
    )

    time.sleep(0.05)

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONUP,
        0,
        lparam
    )

    time.sleep(CLICK_WAIT)

    foreground_after = (
        win32gui.GetForegroundWindow()
    )

    mouse_after = (
        win32api.GetCursorPos()
    )

    print(
        f"[BOT {index}] foreground after = "
        f"{foreground_after}"
    )

    print(
        f"[BOT {index}] mouse after = "
        f"{mouse_after}"
    )

    if mouse_before == mouse_after:
        print(
            f"[BOT {index}] Physical mouse: OK"
        )
    else:
        print(
            f"[BOT {index}] WARNING: "
            f"physical mouse moved!"
        )

    if foreground_before == foreground_after:
        print(
            f"[BOT {index}] Foreground unchanged: OK"
        )
    else:
        print(
            f"[BOT {index}] WARNING: "
            f"foreground changed!"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("BOTVHT - MULTI WINDOW TEST")
    print("=" * 70)

    windows = find_all_game_windows()

    print()
    print(
        f"[MANAGER] Found "
        f"{len(windows)} game window(s)"
    )

    if not windows:
        print(
            "[STOP] No Vua Hải Tặc windows found."
        )
        return

    # --------------------------------------------------------
    # List all windows
    # --------------------------------------------------------

    for index, hwnd in enumerate(
        windows,
        start=1
    ):
        print_window_info(
            index,
            hwnd
        )

    # --------------------------------------------------------
    # Process each bot
    # --------------------------------------------------------

    for index, hwnd in enumerate(
        windows,
        start=1
    ):

        print()
        print("=" * 70)
        print(
            f"[BOT {index}] START"
        )
        print("=" * 70)

        # ----------------------------------------------------
        # Capture
        # ----------------------------------------------------

        frame = capture_game(
            index,
            hwnd
        )

        # ----------------------------------------------------
        # Detect NVHN
        # ----------------------------------------------------

        detection = detect_nvhn(
            index,
            frame
        )

        if detection is None:
            print(
                f"[BOT {index}] "
                f"Skipping click."
            )
            continue

        # ----------------------------------------------------
        # Verify background
        # ----------------------------------------------------

        foreground = (
            win32gui.GetForegroundWindow()
        )

        if foreground == hwnd:
            print(
                f"[BOT {index}] WARNING:"
                f" game is foreground."
            )

            print(
                "[MANAGER] Put another window "
                "in foreground before test."
            )

            input(
                "Press ENTER to continue..."
            )

        # ----------------------------------------------------
        # Click NVHN
        # ----------------------------------------------------

        x, y = detection["center"]

        background_click(
            index,
            hwnd,
            x,
            y
        )

        print()
        print(
            f"[BOT {index}] COMPLETE"
        )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("MULTI WINDOW TEST COMPLETE")
    print("=" * 70)

    print(
        f"[MANAGER] Total windows = "
        f"{len(windows)}"
    )


if __name__ == "__main__":
    main()