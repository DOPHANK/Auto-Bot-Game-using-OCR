import time
from pathlib import Path

import cv2
import win32con
import win32gui

from vision.window_capture import WindowCapture
from vision.template import TemplateMatcher


GAME_TITLE = "Vua Hải Tặc"
NVHN_TEMPLATE = "assets/templates/buttons/NVHN/001.png"

OUTPUT_DIR = Path("debug/mission_screens")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def find_game_windows():
    windows = []

    def callback(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd):
            return

        if win32gui.GetWindowText(hwnd) == GAME_TITLE:
            windows.append(hwnd)

    win32gui.EnumWindows(callback, None)

    return windows


def post_mouse_click(hwnd, x, y):
    lparam = (y << 16) | (x & 0xFFFF)

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        lparam,
    )

    time.sleep(0.05)

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONUP,
        0,
        lparam,
    )


def main():
    print("=" * 70)
    print("BOTVHT - DEBUG MISSION SCREEN")
    print("=" * 70)

    windows = find_game_windows()

    print(f"[MANAGER] Found {len(windows)} game window(s)")

    matcher = TemplateMatcher(threshold=0.80)

    for index, hwnd in enumerate(windows, start=1):

        print()
        print("=" * 70)
        print(f"[BOT {index}] HWND = {hwnd}")
        print("=" * 70)

        capture = WindowCapture(hwnd)

        # Initial
        frame = capture.grab()

        print(
            f"[CAPTURE] initial "
            f"{frame.shape[1]}x{frame.shape[0]}"
        )

        cv2.imwrite(
            str(OUTPUT_DIR / f"bot_{index}_initial.png"),
            frame,
        )

        # NVHN
        nvhn = matcher.find(
            frame,
            NVHN_TEMPLATE,
        )

        if nvhn is None:
            print("[NVHN] NOT FOUND")
            continue

        print(
            f"[NVHN] confidence={nvhn['confidence']:.4f} "
            f"center={nvhn['center']}"
        )

        x, y = nvhn["center"]

        # Background click
        print("[CLICK] NVHN")

        post_mouse_click(
            hwnd,
            x,
            y,
        )

        print("[WAIT] 8 seconds after NVHN...")
        time.sleep(8)

        # Capture resulting UI
        after = capture.grab()

        output = (
            OUTPUT_DIR / f"bot_{index}_after_nvhn.png"
        )

        cv2.imwrite(
            str(output),
            after,
        )

        print(
            f"[CAPTURE] after NVHN "
            f"{after.shape[1]}x{after.shape[0]}"
        )

        print(f"[SAVED] {output}")

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()