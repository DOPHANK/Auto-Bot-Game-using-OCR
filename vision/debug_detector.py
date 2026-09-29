from pathlib import Path
from datetime import datetime
import ctypes

import cv2
import numpy as np
import win32gui
import win32ui

from vision.detector import GameDetector


GAME_TITLE = "Vua Hải Tặc"
THRESHOLD = 0.80

OUTPUT_DIR = Path("debug")
OUTPUT_DIR.mkdir(exist_ok=True)

user32 = ctypes.windll.user32


# ============================================================
# FIND GAME WINDOW
# ============================================================

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

    print()
    print("Found game windows:")

    for i, hwnd in enumerate(windows):
        rect = win32gui.GetWindowRect(hwnd)

        left, top, right, bottom = rect

        print(
            f"  [{i}] "
            f"HWND={hwnd} "
            f"position=({left}, {top}) "
            f"size={right-left}x{bottom-top}"
        )

    # Luôn chọn cửa sổ game đầu tiên
    selected = windows[0]

    print()
    print(
        f"Using first game window: "
        f"HWND={selected}"
    )

    return selected


# ============================================================
# CAPTURE GAME WINDOW
# ============================================================

def capture_game_window(hwnd):
    # Client area của cửa sổ
    left, top, right, bottom = (
        win32gui.GetClientRect(hwnd)
    )

    width = right - left
    height = bottom - top

    if width <= 0 or height <= 0:
        raise RuntimeError(
            f"Invalid game window size: "
            f"{width}x{height}"
        )

    print()
    print("Game window:")
    print(f"  HWND     = {hwnd}")
    print(f"  client   = {width}x{height}")

    hwnd_dc = win32gui.GetWindowDC(hwnd)

    if not hwnd_dc:
        raise RuntimeError(
            "Không lấy được Window DC."
        )

    mfc_dc = win32ui.CreateDCFromHandle(
        hwnd_dc
    )

    save_dc = mfc_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()

    bitmap.CreateCompatibleBitmap(
        mfc_dc,
        width,
        height
    )

    save_dc.SelectObject(bitmap)

    # PW_CLIENTONLY + PW_RENDERFULLCONTENT
    flags = 0x00000001 | 0x00000002

    result = user32.PrintWindow(
        hwnd,
        save_dc.GetSafeHdc(),
        flags
    )

    print(
        f"  PrintWindow = {result}"
    )

    if result == 0:
        # Cleanup trước khi báo lỗi
        win32gui.DeleteObject(
            bitmap.GetHandle()
        )

        save_dc.DeleteDC()
        mfc_dc.DeleteDC()

        win32gui.ReleaseDC(
            hwnd,
            hwnd_dc
        )

        raise RuntimeError(
            "PrintWindow không render được "
            "nội dung game."
        )

    bmpstr = bitmap.GetBitmapBits(True)

    frame = np.frombuffer(
        bmpstr,
        dtype=np.uint8
    )

    frame = frame.reshape(
        height,
        width,
        4
    )

    frame = cv2.cvtColor(
        frame,
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

    return frame


# ============================================================
# DRAW DETECTION
# ============================================================

def draw_detection(
    frame,
    detection,
    label,
    color,
    thickness=2
):
    x = detection["x"]
    y = detection["y"]

    width = detection["width"]
    height = detection["height"]

    confidence = detection["confidence"]

    # Bounding box
    cv2.rectangle(
        frame,
        (x, y),
        (x + width, y + height),
        color,
        thickness
    )

    # Center
    cx, cy = detection["center"]

    cv2.circle(
        frame,
        (cx, cy),
        4,
        color,
        -1
    )

    # Label
    text = (
        f"{label} "
        f"{confidence:.3f}"
    )

    text_y = max(
        y - 8,
        20
    )

    cv2.putText(
        frame,
        text,
        (x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.50,
        color,
        2,
        cv2.LINE_AA
    )


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(
    quests,
    missions
):
    print()
    print("=" * 70)
    print("ACTIVE QUESTS")
    print("=" * 70)

    if not quests:
        print(
            "No active quests detected."
        )
    else:
        for i, detection in enumerate(
            quests,
            start=1
        ):
            print(
                f"[{i}] "
                f"{detection['type']:10s} "
                f"{detection['template']:12s} "
                f"confidence="
                f"{detection['confidence']:.3f} "
                f"center="
                f"{detection['center']}"
            )

    print()
    print("=" * 70)
    print("MISSIONS")
    print("=" * 70)

    if not missions:
        print(
            "No missions detected."
        )
    else:
        for i, detection in enumerate(
            missions,
            start=1
        ):
            print(
                f"[{i}] "
                f"{detection['type']:10s} "
                f"{detection['template']:12s} "
                f"confidence="
                f"{detection['confidence']:.3f} "
                f"center="
                f"{detection['center']}"
            )


# ============================================================
# MAIN
# ============================================================

def main():
    print()
    print("=" * 70)
    print("BotVHT Debug Detector")
    print("=" * 70)

    # --------------------------------------------------------
    # 1. Find game
    # --------------------------------------------------------

    print()
    print("Searching for game window...")

    hwnd = find_game_window()

    # --------------------------------------------------------
    # 2. Capture game
    # --------------------------------------------------------

    print()
    print("Capturing game window...")

    frame = capture_game_window(hwnd)

    print()
    print(
        f"Screenshot size: "
        f"{frame.shape[1]}x"
        f"{frame.shape[0]}"
    )

    # --------------------------------------------------------
    # 3. Detection
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("Running detection...")
    print("=" * 70)

    detector = GameDetector(
        threshold=THRESHOLD
    )

    detections = detector.detect(
        frame
    )

    quests = detections.get(
        "active_quests",
        []
    )

    missions = detections.get(
        "missions",
        []
    )

    # --------------------------------------------------------
    # 4. Print results
    # --------------------------------------------------------

    print_results(
        quests,
        missions
    )

    # --------------------------------------------------------
    # 5. Draw quests
    # --------------------------------------------------------

    for detection in quests:
        label = (
            f"QUEST "
            f"{detection['type']} "
            f"{detection['template']}"
        )

        # Yellow
        color = (0, 255, 255)

        draw_detection(
            frame,
            detection,
            label,
            color
        )

    # --------------------------------------------------------
    # 6. Draw missions
    # --------------------------------------------------------

    for detection in missions:
        label = (
            f"MISSION "
            f"{detection['type']} "
            f"{detection['template']}"
        )

        # Green
        color = (0, 255, 0)

        draw_detection(
            frame,
            detection,
            label,
            color
        )

    # --------------------------------------------------------
    # 7. Save debug image
    # --------------------------------------------------------

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    output_path = (
        OUTPUT_DIR /
        f"detector_{timestamp}.png"
    )

    cv2.imwrite(
        str(output_path),
        frame
    )

    # --------------------------------------------------------
    # 8. Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    print(
        f"Detected "
        f"{len(quests)} active quest(s), "
        f"{len(missions)} mission(s)."
    )

    print()
    print(
        f"Debug image saved to:\n"
        f"  {output_path}"
    )

    print()
    print("Done.")


if __name__ == "__main__":
    main()