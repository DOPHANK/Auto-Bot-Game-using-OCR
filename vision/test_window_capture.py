import ctypes
from pathlib import Path

import cv2
import numpy as np
import win32gui
import win32ui


GAME_TITLE = "Vua Hải Tặc"

OUTPUT_DIR = Path("debug")
OUTPUT_DIR.mkdir(exist_ok=True)


user32 = ctypes.windll.user32


def find_game_window():
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
            f"Không tìm thấy cửa sổ: {GAME_TITLE}"
        )

    return windows[0]


def capture_window(hwnd):
    # Client area
    left, top, right, bottom = win32gui.GetClientRect(hwnd)

    width = right - left
    height = bottom - top

    print(f"Client size: {width}x{height}")

    hwnd_dc = win32gui.GetWindowDC(hwnd)

    if not hwnd_dc:
        raise RuntimeError("Không lấy được window DC.")

    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()

    bitmap.CreateCompatibleBitmap(
        mfc_dc,
        width,
        height
    )

    save_dc.SelectObject(bitmap)

    # PW_CLIENTONLY = 0x00000001
    # PW_RENDERFULLCONTENT = 0x00000002
    flags = 0x00000001 | 0x00000002

    result = user32.PrintWindow(
        hwnd,
        save_dc.GetSafeHdc(),
        flags
    )

    print(f"PrintWindow result: {result}")

    if result == 0:
        print(
            "WARNING: PrintWindow không render được "
            "nội dung cửa sổ."
        )

    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)

    image = np.frombuffer(
        bmpstr,
        dtype=np.uint8
    )

    image = image.reshape(
        height,
        width,
        4
    )

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGRA2BGR
    )

    # Cleanup
    win32gui.DeleteObject(
        bitmap.GetHandle()
    )

    save_dc.DeleteDC()
    mfc_dc.DeleteDC()

    win32gui.ReleaseDC(
        hwnd,
        hwnd_dc
    )

    return image


def main():
    print()
    print("=" * 70)
    print("GAME WINDOW CAPTURE TEST")
    print("=" * 70)

    hwnd = find_game_window()

    print(f"HWND : {hwnd}")
    print(
        f"TITLE: "
        f"{win32gui.GetWindowText(hwnd)}"
    )

    frame = capture_window(hwnd)

    print(
        f"Image size: "
        f"{frame.shape[1]}x{frame.shape[0]}"
    )

    output = (
        OUTPUT_DIR /
        "game_direct_capture.png"
    )

    cv2.imwrite(
        str(output),
        frame
    )

    print()
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()