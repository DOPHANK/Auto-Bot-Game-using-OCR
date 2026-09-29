import time
from pathlib import Path

import cv2
import win32api
import win32con
import win32gui
import yaml

from vision.window_capture import WindowCapture
from vision.template import TemplateMatcher


# ============================================================
# CONFIG
# ============================================================

GAME_TITLE = "Vua Hải Tặc"

NVHN_TEMPLATE = Path(
    "assets/templates/buttons/NVHN/001.png"
)

BUTTON_CONFIG_PATH = Path(
    "config/buttons.yaml"
)

DEBUG_DIR = Path(
    "debug/background_input"
)

THRESHOLD = 0.80

# Chờ để quan sát game trước/sau click
WAIT_BEFORE_CLICK = 2.0
WAIT_AFTER_CLICK = 3.0


# ============================================================
# YAML
# ============================================================

def load_yaml(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"Config not found: {path}"
        )

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:
        return yaml.safe_load(f)


# ============================================================
# WINDOW
# ============================================================

def find_game_window():
    hwnd = win32gui.FindWindow(
        None,
        GAME_TITLE
    )

    if not hwnd:
        raise RuntimeError(
            f"Game window not found: {GAME_TITLE}"
        )

    return hwnd


def print_window_info(hwnd):
    print()
    print("=" * 70)
    print("[WINDOW]")
    print(f"[WINDOW] HWND       = {hwnd}")
    print(
        f"[WINDOW] Title      = "
        f"{win32gui.GetWindowText(hwnd)}"
    )

    foreground = win32gui.GetForegroundWindow()

    print(
        f"[WINDOW] Foreground = "
        f"{foreground}"
    )

    if foreground == hwnd:
        print(
            "[WINDOW] WARNING: Game is currently "
            "foreground."
        )
    else:
        print(
            "[WINDOW] Game is currently "
            "BACKGROUND."
        )

    left, top, right, bottom = (
        win32gui.GetWindowRect(hwnd)
    )

    print(
        f"[WINDOW] Window rect = "
        f"({left},{top}) -> ({right},{bottom})"
    )

    client_left, client_top, client_right, client_bottom = (
        win32gui.GetClientRect(hwnd)
    )

    print(
        f"[WINDOW] Client size = "
        f"{client_right - client_left}x"
        f"{client_bottom - client_top}"
    )

    print("=" * 70)


# ============================================================
# CAPTURE
# ============================================================

def save_capture(frame, filename):
    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    path = DEBUG_DIR / filename

    if not cv2.imwrite(
        str(path),
        frame
    ):
        raise RuntimeError(
            f"Unable to save capture: {path}"
        )

    print(
        f"[CAPTURE] Saved: {path}"
    )


# ============================================================
# NVHN DETECTION
# ============================================================

def detect_nvhn(frame):
    print()
    print("=" * 70)
    print("[NVHN] Searching NVHN...")
    print(
        f"[NVHN] Template = {NVHN_TEMPLATE}"
    )

    matcher = TemplateMatcher(
        threshold=THRESHOLD
    )

    detection = matcher.find(
        frame,
        NVHN_TEMPLATE
    )

    if detection is None:
        print(
            "[NVHN] NOT FOUND"
        )
        return None

    print(
        f"[NVHN] confidence = "
        f"{detection['confidence']:.4f}"
    )

    print(
        f"[NVHN] center = "
        f"{detection['center']}"
    )

    print(
        f"[NVHN] bbox = "
        f"x={detection['x']} "
        f"y={detection['y']} "
        f"w={detection['width']} "
        f"h={detection['height']}"
    )

    print("=" * 70)

    return detection


# ============================================================
# BACKGROUND CLICK
# ============================================================

def background_click(hwnd, x, y):
    """
    Send mouse messages directly to HWND.

    IMPORTANT:
    - Does NOT move physical mouse.
    - Does NOT call SetForegroundWindow.
    - Does NOT call BringWindowToTop.
    """

    x = int(x)
    y = int(y)

    lparam = win32api.MAKELONG(
        x,
        y
    )

    print()
    print("=" * 70)
    print("[INPUT] BACKGROUND CLICK")
    print(
        f"[INPUT] HWND   = {hwnd}"
    )
    print(
        f"[INPUT] client = ({x},{y})"
    )
    print(
        f"[INPUT] LPARAM = {lparam}"
    )

    # --------------------------------------------------------
    # Verify game is still background
    # --------------------------------------------------------

    foreground = (
        win32gui.GetForegroundWindow()
    )

    print(
        f"[INPUT] Foreground HWND = "
        f"{foreground}"
    )

    if foreground == hwnd:
        print(
            "[INPUT] WARNING: Game is foreground "
            "before click."
        )
        print(
            "[INPUT] Please put another window "
            "in front before continuing."
        )

        input(
            "[INPUT] Press ENTER after "
            "putting another window in front..."
        )

        foreground = (
            win32gui.GetForegroundWindow()
        )

        print(
            f"[INPUT] New foreground HWND = "
            f"{foreground}"
        )

    if foreground == hwnd:
        raise RuntimeError(
            "Game is still foreground. "
            "Background test cannot continue."
        )

    # --------------------------------------------------------
    # Check physical mouse before
    # --------------------------------------------------------

    mouse_before = win32api.GetCursorPos()

    print(
        f"[INPUT] Physical mouse BEFORE = "
        f"{mouse_before}"
    )

    # --------------------------------------------------------
    # Send DOWN
    # --------------------------------------------------------

    try:
        result_down = win32gui.PostMessage(
            hwnd,
            win32con.WM_LBUTTONDOWN,
            win32con.MK_LBUTTON,
            lparam
        )

        print(
            f"[INPUT] WM_LBUTTONDOWN "
            f"PostMessage returned = "
            f"{result_down}"
        )

    except Exception as e:
        print(
            f"[INPUT] WM_LBUTTONDOWN ERROR: "
            f"{e}"
        )
        raise

    time.sleep(0.05)

    # --------------------------------------------------------
    # Send UP
    # --------------------------------------------------------

    try:
        result_up = win32gui.PostMessage(
            hwnd,
            win32con.WM_LBUTTONUP,
            0,
            lparam
        )

        print(
            f"[INPUT] WM_LBUTTONUP "
            f"PostMessage returned = "
            f"{result_up}"
        )

    except Exception as e:
        print(
            f"[INPUT] WM_LBUTTONUP ERROR: "
            f"{e}"
        )
        raise

    # --------------------------------------------------------
    # Check physical mouse after
    # --------------------------------------------------------

    mouse_after = win32api.GetCursorPos()

    print(
        f"[INPUT] Physical mouse AFTER  = "
        f"{mouse_after}"
    )

    if mouse_before == mouse_after:
        print(
            "[INPUT] Physical mouse: "
            "UNCHANGED"
        )
    else:
        print(
            "[INPUT] WARNING: Physical mouse "
            "MOVED!"
        )

    # --------------------------------------------------------
    # Check foreground after
    # --------------------------------------------------------

    foreground_after = (
        win32gui.GetForegroundWindow()
    )

    print(
        f"[INPUT] Foreground AFTER = "
        f"{foreground_after}"
    )

    if foreground_after == hwnd:
        print(
            "[INPUT] WARNING: Game became "
            "foreground."
        )
    else:
        print(
            "[INPUT] Game remained "
            "background."
        )

    print("=" * 70)


# ============================================================
# IMAGE DIFFERENCE
# ============================================================

def calculate_difference(
    frame_before,
    frame_after
):
    if frame_before.shape != frame_after.shape:
        print(
            "[RESULT] Capture dimensions changed:"
        )

        print(
            f"  BEFORE = {frame_before.shape}"
        )

        print(
            f"  AFTER  = {frame_after.shape}"
        )

        return None

    diff = cv2.absdiff(
        frame_before,
        frame_after
    )

    gray = cv2.cvtColor(
        diff,
        cv2.COLOR_BGR2GRAY
    )

    changed_pixels = cv2.countNonZero(
        gray
    )

    total_pixels = (
        gray.shape[0] *
        gray.shape[1]
    )

    percentage = (
        changed_pixels /
        total_pixels *
        100
    )

    return percentage


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("BOTVHT - BACKGROUND INPUT TEST")
    print("=" * 70)

    print()
    print("[TEST] This test will:")
    print("  1. Capture the game while background")
    print("  2. Detect NVHN")
    print("  3. Send PostMessage click")
    print("  4. NEVER move physical mouse")
    print("  5. NEVER call SetForegroundWindow")
    print("  6. Capture again")
    print("  7. Compare before/after")
    print("=" * 70)

    # --------------------------------------------------------
    # Find game
    # --------------------------------------------------------

    hwnd = find_game_window()

    print_window_info(hwnd)

    # --------------------------------------------------------
    # Create capture
    # --------------------------------------------------------

    capture = WindowCapture(hwnd)

    # --------------------------------------------------------
    # First capture
    # --------------------------------------------------------

    print()
    print("[STEP 1] Background capture")

    frame_before = capture.grab()

    print(
        f"[CAPTURE] Size = "
        f"{frame_before.shape[1]}x"
        f"{frame_before.shape[0]}"
    )

    save_capture(
        frame_before,
        "before_click.png"
    )

    # --------------------------------------------------------
    # Detect NVHN
    # --------------------------------------------------------

    print()
    print("[STEP 2] Detect NVHN")

    detection = detect_nvhn(
        frame_before
    )

    if detection is None:
        print()
        print(
            "[STOP] NVHN not detected."
        )
        return

    x, y = detection["center"]

    # --------------------------------------------------------
    # Wait
    # --------------------------------------------------------

    print()
    print(
        f"[STEP 3] Waiting "
        f"{WAIT_BEFORE_CLICK:.1f}s"
    )

    print(
        "[STEP 3] Put another window "
        "in front of the game now."
    )

    time.sleep(
        WAIT_BEFORE_CLICK
    )

    # --------------------------------------------------------
    # Confirm background
    # --------------------------------------------------------

    print()
    print(
        "[STEP 4] Checking background state"
    )

    print_window_info(hwnd)

    if (
        win32gui.GetForegroundWindow()
        == hwnd
    ):
        print()
        print(
            "[STOP] Game is still foreground."
        )

        print(
            "[STOP] Put Chrome/VS Code/etc. "
            "in front and run again."
        )

        return

    # --------------------------------------------------------
    # Background click
    # --------------------------------------------------------

    print()
    print("[STEP 5] Background click")

    background_click(
        hwnd,
        x,
        y
    )

    # --------------------------------------------------------
    # Wait
    # --------------------------------------------------------

    print()
    print(
        f"[STEP 6] Waiting "
        f"{WAIT_AFTER_CLICK:.1f}s "
        "for game reaction..."
    )

    time.sleep(
        WAIT_AFTER_CLICK
    )

    # --------------------------------------------------------
    # Second capture
    # --------------------------------------------------------

    print()
    print(
        "[STEP 7] Capture after click"
    )

    frame_after = capture.grab()

    print(
        f"[CAPTURE] Size = "
        f"{frame_after.shape[1]}x"
        f"{frame_after.shape[0]}"
    )

    save_capture(
        frame_after,
        "after_click.png"
    )

    # --------------------------------------------------------
    # Compare
    # --------------------------------------------------------

    print()
    print(
        "[STEP 8] Comparing captures"
    )

    difference = calculate_difference(
        frame_before,
        frame_after
    )

    if difference is None:
        print(
            "[RESULT] Unable to compare."
        )

    else:
        print(
            f"[RESULT] Changed pixels = "
            f"{difference:.4f}%"
        )

        if difference > 0.1:
            print(
                "[RESULT] IMAGE CHANGED"
            )
        else:
            print(
                "[RESULT] IMAGE DID NOT "
                "SIGNIFICANTLY CHANGE"
            )

    # --------------------------------------------------------
    # Final state
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("[FINAL]")
    print_window_info(hwnd)

    mouse_position = (
        win32api.GetCursorPos()
    )

    print(
        f"[FINAL] Physical mouse = "
        f"{mouse_position}"
    )

    print("=" * 70)

    print()
    print("[TEST COMPLETE]")


if __name__ == "__main__":
    main()