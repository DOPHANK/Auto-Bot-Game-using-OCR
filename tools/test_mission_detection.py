from pathlib import Path
import time

import cv2
import yaml
import win32con
import win32gui

from vision.detector import GameDetector
from vision.window_capture import WindowCapture


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

MISSIONS_CONFIG_PATH = Path(
    "config/missions.yaml"
)

DEBUG_DIR = Path(
    "debug/mission_detection_timing"
)

# ------------------------------------------------------------
# Detection
# ------------------------------------------------------------

DETECTOR_THRESHOLD = 0.80

# ------------------------------------------------------------
# Timing test
# ------------------------------------------------------------

# Wait after clicking NVHN before first capture
WAIT_BEFORE_FIRST_CAPTURE = 1.0

# Capture interval
CAPTURE_INTERVAL = 1.0

# Number of frames
NUM_FRAMES = 8

# ------------------------------------------------------------
# Multi-window
# ------------------------------------------------------------

MAX_BOTS = 5

# ------------------------------------------------------------
# Safety
# ------------------------------------------------------------

# This test ONLY clicks NVHN.
# It NEVER clicks mission / Select / Refresh.
DRY_RUN = True


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


BUTTON_CONFIG = load_yaml(
    BUTTON_CONFIG_PATH
)

MISSIONS_CONFIG = load_yaml(
    MISSIONS_CONFIG_PATH
)


# ============================================================
# WINDOW
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
# BACKGROUND CLICK
# ============================================================

def post_mouse_click(
    bot_index,
    hwnd,
    x,
    y,
    description=""
):
    x = int(x)
    y = int(y)

    lparam = (
        (y << 16) |
        (x & 0xFFFF)
    )

    print()
    print(
        f"[BOT {bot_index}] "
        f"[CLICK] {description}"
    )

    print(
        f"[BOT {bot_index}] "
        f"client=({x},{y})"
    )

    foreground = (
        win32gui.GetForegroundWindow()
    )

    print(
        f"[BOT {bot_index}] "
        f"foreground={foreground}"
    )

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

    print(
        f"[BOT {bot_index}] "
        "[CLICK] message sent"
    )


# ============================================================
# CAPTURE
# ============================================================

def capture_game(
    bot_index,
    hwnd,
    label
):
    capture = WindowCapture(hwnd)

    frame = capture.grab()

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    path = (
        DEBUG_DIR /
        f"bot_{bot_index}_{label}.png"
    )

    cv2.imwrite(
        str(path),
        frame
    )

    print(
        f"[BOT {bot_index}] "
        f"[CAPTURE] {label} "
        f"{frame.shape[1]}x{frame.shape[0]}"
    )

    print(
        f"[BOT {bot_index}] "
        f"[DEBUG] {path}"
    )

    return frame


# ============================================================
# DRAW DETECTIONS
# ============================================================

def draw_detections(
    frame,
    active_quests,
    missions
):
    debug = frame.copy()

    # --------------------------------------------------------
    # Active quests
    # --------------------------------------------------------

    for quest in active_quests:

        x, y = quest["center"]

        cv2.circle(
            debug,
            (int(x), int(y)),
            8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            debug,
            (
                f"Q:{quest['slot']} "
                f"{quest['type']} "
                f"{quest['confidence']:.2f}"
            ),
            (
                int(x) + 10,
                int(y)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1,
            cv2.LINE_AA
        )

    # --------------------------------------------------------
    # Missions
    # --------------------------------------------------------

    for mission in missions:

        x, y = mission["center"]

        cv2.circle(
            debug,
            (int(x), int(y)),
            8,
            (255, 0, 0),
            2
        )

        cv2.putText(
            debug,
            (
                f"M:{mission['slot']} "
                f"{mission['type']} "
                f"{mission['confidence']:.2f}"
            ),
            (
                int(x) + 10,
                int(y)
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            1,
            cv2.LINE_AA
        )

    return debug


# ============================================================
# SLOT STATUS
# ============================================================

def get_slot_status(missions):
    """
    Convert detector output into:

        slot_1 -> detection
        slot_2 -> detection
        slot_3 -> detection
        slot_4 -> detection
        slot_5 -> detection
    """

    result = {}

    for slot_name in (
        "slot_1",
        "slot_2",
        "slot_3",
        "slot_4",
        "slot_5",
    ):
        result[slot_name] = None

    for mission in missions:

        slot = mission["slot"]

        result[slot] = mission

    return result


# ============================================================
# PRINT SLOT STATUS
# ============================================================

def print_slot_status(
    bot_index,
    missions
):
    slots = get_slot_status(
        missions
    )

    print()
    print(
        f"[BOT {bot_index}] "
        "MISSION SLOT STATUS"
    )

    for slot_name in (
        "slot_1",
        "slot_2",
        "slot_3",
        "slot_4",
        "slot_5",
    ):

        mission = slots[slot_name]

        if mission is None:

            print(
                f"  {slot_name}: "
                "MISSING"
            )

        else:

            print(
                f"  {slot_name}: "
                f"{mission['type']} "
                f"confidence="
                f"{mission['confidence']:.4f}"
            )


# ============================================================
# PRINT DETECTIONS
# ============================================================

def print_detections(
    bot_index,
    active_quests,
    missions,
    elapsed
):
    print()
    print(
        "=" * 70
    )

    print(
        f"[BOT {bot_index}] "
        f"TIME = {elapsed:.1f}s"
    )

    print(
        f"[BOT {bot_index}] "
        f"ACTIVE QUESTS = "
        f"{len(active_quests)}"
    )

    for quest in active_quests:

        print(
            f"  {quest['slot']}: "
            f"{quest['type']} "
            f"confidence="
            f"{quest['confidence']:.4f}"
        )

    print()

    print(
        f"[BOT {bot_index}] "
        f"MISSIONS = "
        f"{len(missions)}"
    )

    for mission in missions:

        print(
            f"  {mission['slot']}: "
            f"{mission['type']} "
            f"confidence="
            f"{mission['confidence']:.4f}"
        )

    print_slot_status(
        bot_index,
        missions
    )

    print(
        "=" * 70
    )


# ============================================================
# ONE BOT
# ============================================================

def run_bot(
    bot_index,
    hwnd,
    detector
):
    print()
    print(
        "#" * 70
    )

    print(
        f"[BOT {bot_index}] START"
    )

    print(
        f"[BOT {bot_index}] "
        f"HWND = {hwnd}"
    )

    print(
        "#" * 70
    )

    # --------------------------------------------------------
    # Initial capture
    # --------------------------------------------------------

    initial_frame = capture_game(
        bot_index,
        hwnd,
        "initial"
    )

    # --------------------------------------------------------
    # Detect NVHN
    # --------------------------------------------------------

    nvhn = detector.detect_nvhn(
        initial_frame
    )

    if nvhn is None:

        print(
            f"[BOT {bot_index}] "
            "[NVHN] NOT FOUND"
        )

        return None

    print(
        f"[BOT {bot_index}] "
        f"[NVHN] FOUND "
        f"confidence="
        f"{nvhn['confidence']:.4f} "
        f"center={nvhn['center']}"
    )

    # --------------------------------------------------------
    # Click NVHN
    # --------------------------------------------------------

    x, y = nvhn["center"]

    if DRY_RUN:

        print(
            f"[BOT {bot_index}] "
            "[TEST] Clicking NVHN only."
        )

    post_mouse_click(
        bot_index,
        hwnd,
        x,
        y,
        description="NVHN"
    )

    # --------------------------------------------------------
    # Timing experiment
    # --------------------------------------------------------

    print()
    print(
        f"[BOT {bot_index}] "
        "Starting multi-frame timing test..."
    )

    print(
        f"[BOT {bot_index}] "
        f"Frames = {NUM_FRAMES}"
    )

    print(
        f"[BOT {bot_index}] "
        f"Interval = {CAPTURE_INTERVAL:.1f}s"
    )

    print()

    time.sleep(
        WAIT_BEFORE_FIRST_CAPTURE
    )

    results = []

    start_time = time.time()

    for frame_index in range(
        1,
        NUM_FRAMES + 1
    ):

        # ----------------------------------------------------
        # Capture
        # ----------------------------------------------------

        frame = capture_game(
            bot_index,
            hwnd,
            f"t{frame_index:02d}"
        )

        elapsed = (
            time.time() -
            start_time
        )

        # ----------------------------------------------------
        # Detect active quests
        # ----------------------------------------------------

        active_quests = (
            detector.detect_active_quests(
                frame
            )
        )

        # ----------------------------------------------------
        # Detect missions
        # ----------------------------------------------------

        missions = (
            detector.detect_missions(
                frame
            )
        )

        # ----------------------------------------------------
        # Print
        # ----------------------------------------------------

        print_detections(
            bot_index,
            active_quests,
            missions,
            elapsed
        )

        # ----------------------------------------------------
        # Draw debug image
        # ----------------------------------------------------

        debug = draw_detections(
            frame,
            active_quests,
            missions
        )

        debug_path = (
            DEBUG_DIR /
            f"bot_{bot_index}_"
            f"t{frame_index:02d}_detected.png"
        )

        cv2.imwrite(
            str(debug_path),
            debug
        )

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        slot_status = get_slot_status(
            missions
        )

        results.append(
            {
                "time": elapsed,
                "missions": missions,
                "slots": slot_status,
            }
        )

        # ----------------------------------------------------
        # Wait before next frame
        # ----------------------------------------------------

        if frame_index < NUM_FRAMES:

            time.sleep(
                CAPTURE_INTERVAL
            )

    # ========================================================
    # BOT SUMMARY
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        f"[BOT {bot_index}] "
        "TIMING TEST SUMMARY"
    )

    print(
        "=" * 70
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        slots = result["slots"]

        found = [
            slot
            for slot, detection
            in slots.items()
            if detection is not None
        ]

        missing = [
            slot
            for slot, detection
            in slots.items()
            if detection is None
        ]

        print(
            f"t{index:02d} "
            f"({result['time']:.1f}s): "
            f"{len(found)}/5"
        )

        print(
            f"    FOUND  : "
            f"{', '.join(found) if found else '-'}"
        )

        print(
            f"    MISSING: "
            f"{', '.join(missing) if missing else '-'}"
        )

    # ========================================================
    # SLOT EVOLUTION
    # ========================================================

    print()
    print(
        f"[BOT {bot_index}] "
        "SLOT EVOLUTION"
    )

    for slot_name in (
        "slot_1",
        "slot_2",
        "slot_3",
        "slot_4",
        "slot_5",
    ):

        print()
        print(
            f"  {slot_name}:"
        )

        for index, result in enumerate(
            results,
            start=1
        ):

            detection = (
                result["slots"][slot_name]
            )

            if detection is None:

                print(
                    f"    t{index}: "
                    "MISSING"
                )

            else:

                print(
                    f"    t{index}: "
                    f"{detection['type']} "
                    f"("
                    f"{detection['confidence']:.4f}"
                    f")"
                )

    print()
    print(
        f"[BOT {bot_index}] "
        "TIMING TEST COMPLETE"
    )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=" * 70
    )

    print(
        "BOTVHT - MISSION DETECTION "
        "TIMING DIAGNOSTIC"
    )

    print(
        "=" * 70
    )

    print()
    print(
        "[CONFIG] "
        f"THRESHOLD = {DETECTOR_THRESHOLD}"
    )

    print(
        "[CONFIG] "
        f"FIRST CAPTURE = "
        f"{WAIT_BEFORE_FIRST_CAPTURE}s"
    )

    print(
        "[CONFIG] "
        f"INTERVAL = "
        f"{CAPTURE_INTERVAL}s"
    )

    print(
        "[CONFIG] "
        f"FRAMES = {NUM_FRAMES}"
    )

    print(
        "[CONFIG] "
        f"MAX BOTS = {MAX_BOTS}"
    )

    print()
    print(
        "[CONFIG] "
        "Mission click = DISABLED"
    )

    print(
        "[CONFIG] "
        "Select click = DISABLED"
    )

    print(
        "[CONFIG] "
        "Refresh click = DISABLED"
    )

    # --------------------------------------------------------
    # Check YAML slots
    # --------------------------------------------------------

    configured_slots = (
        MISSIONS_CONFIG["missions"]["slots"]
    )

    print()
    print(
        "[CONFIG] Mission slots:"
    )

    for slot_name, slot in (
        configured_slots.items()
    ):

        print(
            f"  {slot_name}: "
            f"x1={slot['x1']} "
            f"x2={slot['x2']}"
        )

    # --------------------------------------------------------
    # Find windows
    # --------------------------------------------------------

    windows = find_all_game_windows()

    print()
    print(
        f"[MANAGER] Found "
        f"{len(windows)} game window(s)"
    )

    if not windows:

        print(
            "[STOP] "
            "No game windows found."
        )

        return

    if len(windows) > MAX_BOTS:

        windows = windows[:MAX_BOTS]

        print(
            f"[MANAGER] Limiting to "
            f"{MAX_BOTS} bots"
        )

    # --------------------------------------------------------
    # Shared detector
    # --------------------------------------------------------

    detector = GameDetector(
        threshold=DETECTOR_THRESHOLD
    )

    # --------------------------------------------------------
    # Run bots
    # --------------------------------------------------------

    all_results = []

    for index, hwnd in enumerate(
        windows,
        start=1
    ):

        try:

            results = run_bot(
                index,
                hwnd,
                detector
            )

            all_results.append(
                (
                    index,
                    hwnd,
                    results
                )
            )

        except Exception as e:

            print()
            print(
                f"[BOT {index}] "
                f"[ERROR] {e}"
            )

            all_results.append(
                (
                    index,
                    hwnd,
                    None
                )
            )

    # ========================================================
    # GLOBAL SUMMARY
    # ========================================================

    print()
    print(
        "=" * 70
    )

    print(
        "GLOBAL TIMING DIAGNOSTIC"
    )

    print(
        "=" * 70
    )

    for bot_index, hwnd, results in (
        all_results
    ):

        print()
        print(
            f"BOT {bot_index} "
            f"(HWND={hwnd})"
        )

        if results is None:

            print(
                "  ERROR / NO RESULTS"
            )

            continue

        max_found = 0
        best_frame = None

        for index, result in enumerate(
            results,
            start=1
        ):

            found_count = sum(
                1
                for detection
                in result["slots"].values()
                if detection is not None
            )

            if found_count > max_found:

                max_found = found_count
                best_frame = index

        print(
            f"  Best detection: "
            f"{max_found}/5"
        )

        if best_frame is not None:

            print(
                f"  Best frame: "
                f"t{best_frame:02d}"
            )

        if max_found == 5:

            print(
                "  RESULT: "
                "ALL 5 MISSIONS DETECTED"
            )

        else:

            print(
                "  RESULT: "
                "5 missions were NOT "
                "detected in this timing window"
            )

    print()
    print(
        "=" * 70
    )

    print(
        "[DONE] "
        f"Debug images saved to: "
        f"{DEBUG_DIR}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()