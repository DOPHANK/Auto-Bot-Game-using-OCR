import time
from pathlib import Path

import cv2
import win32api
import win32con
import win32gui
import yaml

from vision.window_capture import WindowCapture
from vision.detector import GameDetector
from vision.template import TemplateMatcher


# ============================================================
# CONFIG
# ============================================================

GAME_TITLE = "Vua Hải Tặc"

BUTTON_CONFIG_PATH = Path(
    "config/buttons.yaml"
)

REFRESH_CONFIG_PATH = Path(
    "config/refresh.yaml"
)

REFRESH_TEMPLATE = Path(
    "assets/templates/refresh.png"
)

NVHN_TEMPLATE = Path(
    "assets/templates/buttons/NVHN/001.png"
)

DEBUG_DIR = Path(
    "debug/multi_mission_flow"
)

THRESHOLD = 0.80

# ------------------------------------------------------------
# IMPORTANT:
# Maximum refresh PER GAME WINDOW
# ------------------------------------------------------------

MAX_REFRESH = 1

# ------------------------------------------------------------
# Click waits
# ------------------------------------------------------------

CLICK_WAIT = 3.0

WAIT_AFTER_NVHN = 5.0


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

REFRESH_CONFIG = load_yaml(
    REFRESH_CONFIG_PATH
)


# ============================================================
# WINDOW MANAGER
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
    """
    Background click.

    IMPORTANT:
    - No physical mouse movement.
    - No SetForegroundWindow.
    - No BringWindowToTop.
    """

    x = int(x)
    y = int(y)

    lparam = win32api.MAKELONG(
        x,
        y
    )

    print()
    print(
        f"[BOT {bot_index}] [CLICK] "
        f"{description}"
    )

    print(
        f"[BOT {bot_index}] [CLICK] "
        f"HWND   = {hwnd}"
    )

    print(
        f"[BOT {bot_index}] [CLICK] "
        f"client = ({x},{y})"
    )

    foreground = (
        win32gui.GetForegroundWindow()
    )

    print(
        f"[BOT {bot_index}] [CLICK] "
        f"foreground = {foreground}"
    )

    if foreground == hwnd:
        print(
            f"[BOT {bot_index}] "
            "[WARNING] Game is foreground."
        )

    # --------------------------------------------------------
    # DOWN
    # --------------------------------------------------------

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        lparam
    )

    time.sleep(0.05)

    # --------------------------------------------------------
    # UP
    # --------------------------------------------------------

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONUP,
        0,
        lparam
    )

    print(
        f"[BOT {bot_index}] [CLICK] "
        f"message sent."
    )

    print(
        f"[BOT {bot_index}] [CLICK] "
        f"waiting {CLICK_WAIT:.1f}s..."
    )

    time.sleep(CLICK_WAIT)


# ============================================================
# CAPTURE
# ============================================================

def capture_game(
    bot_index,
    hwnd,
    label=""
):
    capture = WindowCapture(hwnd)

    frame = capture.grab()

    print(
        f"[BOT {bot_index}] "
        f"[CAPTURE] {label} "
        f"{frame.shape[1]}x{frame.shape[0]}"
    )

    DEBUG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"bot_{bot_index}_{label}.png"
    )

    path = DEBUG_DIR / filename

    cv2.imwrite(
        str(path),
        frame
    )

    return frame


# ============================================================
# NVHN
# ============================================================

def detect_nvhn(
    bot_index,
    frame
):
    matcher = TemplateMatcher(
        threshold=THRESHOLD
    )

    detection = matcher.find(
        frame,
        NVHN_TEMPLATE
    )

    if detection is None:

        print(
            f"[BOT {bot_index}] "
            "[NVHN] NOT FOUND"
        )

        return None

    print(
        f"[BOT {bot_index}] "
        f"[NVHN] confidence="
        f"{detection['confidence']:.4f} "
        f"center={detection['center']}"
    )

    return detection


# ============================================================
# REFRESH
# ============================================================

def detect_refresh(
    bot_index,
    frame
):
    config = REFRESH_CONFIG["refresh"]

    x1 = config["x1"]
    y1 = config["y1"]
    x2 = config["x2"]
    y2 = config["y2"]

    crop = frame[
        y1:y2,
        x1:x2
    ]

    matcher = TemplateMatcher(
        threshold=THRESHOLD
    )

    detection = matcher.find(
        crop,
        REFRESH_TEMPLATE
    )

    if detection is None:

        print(
            f"[BOT {bot_index}] "
            "[REFRESH] NOT FOUND"
        )

        return None

    detection["x"] += x1
    detection["y"] += y1

    cx, cy = detection["center"]

    detection["center"] = (
        cx + x1,
        cy + y1
    )

    print(
        f"[BOT {bot_index}] "
        f"[REFRESH] confidence="
        f"{detection['confidence']:.4f} "
        f"center={detection['center']}"
    )

    return detection


# ============================================================
# PRINT DETECTIONS
# ============================================================

def print_detections(
    bot_index,
    detection
):

    active_quests = detection.get(
        "active_quests",
        []
    )

    missions = detection.get(
        "missions",
        []
    )

    print()
    print(
        f"[BOT {bot_index}] "
        "--------------------------------------------"
    )

    print(
        f"[BOT {bot_index}] "
        f"[ACTIVE QUESTS] {len(active_quests)}"
    )

    for quest in active_quests:

        print(
            f"  {quest['slot']}: "
            f"{quest['type']} "
            f"confidence="
            f"{quest['confidence']:.3f} "
            f"center={quest['center']}"
        )

    print()

    print(
        f"[BOT {bot_index}] "
        f"[MISSIONS] {len(missions)}"
    )

    for mission in missions:

        print(
            f"  {mission['slot']}: "
            f"{mission['type']} "
            f"confidence="
            f"{mission['confidence']:.3f} "
            f"center={mission['center']}"
        )

    print(
        f"[BOT {bot_index}] "
        "--------------------------------------------"
    )


# ============================================================
# MATCH
# ============================================================

def match_quest_to_mission(
    quest,
    missions
):
    quest_type = quest["type"]

    for mission in missions:

        if mission["type"] == quest_type:

            return mission

    return None


def find_matching_mission(
    bot_index,
    detection
):
    """
    Try ALL active quests.

    Example:

        quest_1 = Arena
        quest_2 = Sail

        missions:
            Enhance
            Forge
            Sail

    Result:
        quest_2 + Sail
    """

    quests = detection.get(
        "active_quests",
        []
    )

    missions = detection.get(
        "missions",
        []
    )

    if not quests:

        print(
            f"[BOT {bot_index}] "
            "[MATCH] No active quest detected."
        )

        return None, None

    # --------------------------------------------------------
    # IMPORTANT:
    # Do NOT use quests[0] only.
    # --------------------------------------------------------

    for quest in quests:

        quest_type = quest["type"]

        print(
            f"[BOT {bot_index}] "
            f"[MATCH] Quest type: "
            f"{quest_type}"
        )

        mission = match_quest_to_mission(
            quest,
            missions
        )

        if mission is None:

            print(
                f"[BOT {bot_index}] "
                f"[MATCH] No mission for "
                f"{quest_type}"
            )

            continue

        print(
            f"[BOT {bot_index}] "
            f"[MATCH] FOUND "
            f"{quest_type} -> "
            f"{mission['slot']}"
        )

        return quest, mission

    print(
        f"[BOT {bot_index}] "
        "[MATCH] No mission for "
        "any active quest."
    )

    return None, None


# ============================================================
# BUTTON
# ============================================================

def click_button(
    bot_index,
    hwnd,
    button_name
):
    buttons = BUTTON_CONFIG["buttons"]

    if button_name not in buttons:

        raise KeyError(
            f"Button '{button_name}' "
            f"not found in "
            f"{BUTTON_CONFIG_PATH}"
        )

    button = buttons[button_name]

    x = button.get("center", {}).get(
        "x"
    )

    y = button.get("center", {}).get(
        "y"
    )

    # --------------------------------------------------------
    # Current buttons.yaml stores x1/y1/x2/y2.
    # Calculate center when center isn't stored.
    # --------------------------------------------------------

    if x is None or y is None:

        x = (
            button["x1"] +
            button["x2"]
        ) // 2

        y = (
            button["y1"] +
            button["y2"]
        ) // 2

    post_mouse_click(
        bot_index,
        hwnd,
        x,
        y,
        description=button_name
    )


# ============================================================
# MISSION CLICK
# ============================================================

def click_mission(
    bot_index,
    hwnd,
    mission
):
    x, y = mission["center"]

    post_mouse_click(
        bot_index,
        hwnd,
        x,
        y,
        description=(
            f"Mission "
            f"{mission['slot']} "
            f"({mission['type']})"
        )
    )


# ============================================================
# SELECT
# ============================================================

def select_mission(
    bot_index,
    hwnd
):
    print()
    print(
        f"[BOT {bot_index}] "
        "[SELECT] Clicking Select"
    )

    click_button(
        bot_index,
        hwnd,
        "Select"
    )


# ============================================================
# DESTINATION
# ============================================================

def go_to_destination(
    bot_index,
    hwnd,
    mission_type
):
    """
    Destination button is stored in buttons.yaml
    under the mission type.

    Example:

        Sail    -> buttons.Sail
        Arena   -> buttons.Arena
        Forge   -> buttons.Forge
    """

    print()
    print(
        f"[BOT {bot_index}] "
        f"[DESTINATION] "
        f"{mission_type}"
    )

    buttons = BUTTON_CONFIG["buttons"]

    if mission_type not in buttons:

        raise KeyError(
            f"No destination button "
            f"for mission type: "
            f"{mission_type}"
        )

    click_button(
        bot_index,
        hwnd,
        mission_type
    )


# ============================================================
# REFRESH
# ============================================================

def refresh_missions(
    bot_index,
    hwnd,
    frame,
    refresh_count
):
    if refresh_count >= MAX_REFRESH:

        print(
            f"[BOT {bot_index}] "
            f"[REFRESH] Maximum refresh "
            f"reached: {MAX_REFRESH}"
        )

        return (
            frame,
            refresh_count,
            False
        )

    detection = detect_refresh(
        bot_index,
        frame
    )

    if detection is None:

        print(
            f"[BOT {bot_index}] "
            "[REFRESH] Cannot find refresh."
        )

        return (
            frame,
            refresh_count,
            False
        )

    refresh_count += 1

    print()
    print(
        f"[BOT {bot_index}] "
        f"[REFRESH] "
        f"{refresh_count}/{MAX_REFRESH}"
    )

    x, y = detection["center"]

    post_mouse_click(
        bot_index,
        hwnd,
        x,
        y,
        description="Refresh"
    )

    print(
        f"[BOT {bot_index}] "
        "[REFRESH] Capturing new missions..."
    )

    new_frame = capture_game(
        bot_index,
        hwnd,
        f"after_refresh_{refresh_count}"
    )

    return (
        new_frame,
        refresh_count,
        True
    )


# ============================================================
# ONE BOT
# ============================================================

def run_bot(
    bot_index,
    hwnd,
    detector
):
    """
    Complete mission flow for ONE game window.
    """

    print()
    print("=" * 70)
    print(
        f"[BOT {bot_index}] START"
    )
    print(
        f"[BOT {bot_index}] HWND = {hwnd}"
    )
    print("=" * 70)

    refresh_count = 0

    # --------------------------------------------------------
    # STEP 1
    # Capture
    # --------------------------------------------------------

    frame = capture_game(
        bot_index,
        hwnd,
        "initial"
    )

    # --------------------------------------------------------
    # STEP 2
    # NVHN
    # --------------------------------------------------------

    nvhn = detect_nvhn(
        bot_index,
        frame
    )

    if nvhn is None:

        print(
            f"[BOT {bot_index}] "
            "[STOP] NVHN not found."
        )

        return False

    # --------------------------------------------------------
    # STEP 3
    # Open NVHN
    # --------------------------------------------------------

    x, y = nvhn["center"]

    post_mouse_click(
        bot_index,
        hwnd,
        x,
        y,
        description="NVHN"
    )

    print(
        f"[BOT {bot_index}] "
        f"[WAIT] Waiting "
        f"{WAIT_AFTER_NVHN:.1f}s "
        "after NVHN..."
    )

    time.sleep(
        WAIT_AFTER_NVHN
    )

    # --------------------------------------------------------
    # STEP 4
    # Mission matching / refresh
    # --------------------------------------------------------

    while True:

        print()
        print(
            f"[BOT {bot_index}] "
            "[DETECT] Active quests "
            "and missions"
        )

        detection = {
            "active_quests":
                detector.detect_active_quests(
                    frame
                ),
            "missions":
                detector.detect_missions(
                    frame
                )
        }

        print_detections(
            bot_index,
            detection
        )

        # ----------------------------------------------------
        # Try ALL active quests
        # ----------------------------------------------------

        quest, mission = (
            find_matching_mission(
                bot_index,
                detection
            )
        )

        # ----------------------------------------------------
        # MATCH FOUND
        # ----------------------------------------------------

        if (
            quest is not None
            and mission is not None
        ):

            print()
            print(
                f"[BOT {bot_index}] "
                "[MATCH] Selected:"
            )

            print(
                f"  Quest   : "
                f"{quest['slot']} -> "
                f"{quest['type']}"
            )

            print(
                f"  Mission : "
                f"{mission['slot']} -> "
                f"{mission['type']}"
            )

            # ------------------------------------------------
            # Click mission
            # ------------------------------------------------

            click_mission(
                bot_index,
                hwnd,
                mission
            )

            # ------------------------------------------------
            # Click Select
            # ------------------------------------------------

            select_mission(
                bot_index,
                hwnd
            )

            # ------------------------------------------------
            # Go destination
            # ------------------------------------------------

            go_to_destination(
                bot_index,
                hwnd,
                mission["type"]
            )

            print()
            print(
                f"[BOT {bot_index}] "
                "[SUCCESS] Mission selected "
                "and destination clicked."
            )

            return True

        # ----------------------------------------------------
        # No match
        # ----------------------------------------------------

        print()
        print(
            f"[BOT {bot_index}] "
            "[MATCH] No matching mission."
        )

        # ----------------------------------------------------
        # Refresh limit
        # ----------------------------------------------------

        if refresh_count >= MAX_REFRESH:

            print(
                f"[BOT {bot_index}] "
                f"[STOP] Reached maximum "
                f"refresh count: "
                f"{MAX_REFRESH}"
            )

            return False

        # ----------------------------------------------------
        # Refresh
        # ----------------------------------------------------

        frame, refresh_count, refreshed = (
            refresh_missions(
                bot_index,
                hwnd,
                frame,
                refresh_count
            )
        )

        if not refreshed:

            print(
                f"[BOT {bot_index}] "
                "[STOP] Refresh failed."
            )

            return False

        # ----------------------------------------------------
        # Loop -> detect again
        # ----------------------------------------------------


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 70)
    print("BOTVHT - MULTI WINDOW MISSION FLOW")
    print("=" * 70)

    print()
    print(
        "[CONFIG] "
        f"MAX_REFRESH = {MAX_REFRESH}"
    )

    print(
        "[CONFIG] "
        f"CLICK_WAIT = {CLICK_WAIT}s"
    )

    print(
        "[CONFIG] "
        "Background input = PostMessage"
    )

    print(
        "[CONFIG] "
        "Physical mouse = NEVER MOVED"
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
            "[STOP] No game windows found."
        )

        return

    # --------------------------------------------------------
    # Shared detector
    # --------------------------------------------------------

    detector = GameDetector(
        threshold=THRESHOLD
    )

    # --------------------------------------------------------
    # Process each game
    # --------------------------------------------------------

    results = []

    for index, hwnd in enumerate(
        windows,
        start=1
    ):

        try:

            success = run_bot(
                index,
                hwnd,
                detector
            )

            results.append(
                (
                    index,
                    hwnd,
                    success
                )
            )

        except Exception as e:

            print()
            print(
                f"[BOT {index}] "
                f"[ERROR] {e}"
            )

            results.append(
                (
                    index,
                    hwnd,
                    False
                )
            )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("MULTI WINDOW MISSION SUMMARY")
    print("=" * 70)

    for index, hwnd, success in results:

        status = (
            "SUCCESS"
            if success
            else "FAILED"
        )

        print(
            f"BOT {index}: "
            f"HWND={hwnd} "
            f"-> {status}"
        )

    successful = sum(
        1
        for _, _, success in results
        if success
    )

    print()
    print(
        f"[MANAGER] "
        f"{successful}/{len(results)} "
        "bots completed."
    )

    print("=" * 70)


if __name__ == "__main__":
    main()