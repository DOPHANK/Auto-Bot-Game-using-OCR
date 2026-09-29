import time
from pathlib import Path

import cv2
import win32api
import win32con
import win32gui
import yaml

from vision.detector import GameDetector
from vision.window_capture import WindowCapture


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

NVHN_TEMPLATE_DIR = Path(
    "assets/templates/buttons/NVHN"
)

DEBUG_CAPTURE_DIR = Path(
    "debug/captures"
)

MAX_REFRESH = 1

# Chờ sau mỗi lần gửi click
CLICK_WAIT = 5.0

# Chờ sau khi mở NVHN
WAIT_AFTER_NVHN = 3.0

# Chờ sau khi refresh
WAIT_AFTER_REFRESH = 3.0

# Chờ sau Select
WAIT_AFTER_SELECT = 3.0

# Chờ sau khi đi tới destination
WAIT_AFTER_DESTINATION = 8.0


# ============================================================
# GAME WINDOW
# ============================================================

def find_game_window():

    windows = []

    def callback(hwnd, extra):

        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd)

        if title == GAME_TITLE:
            windows.append(hwnd)

    win32gui.EnumWindows(
        callback,
        None
    )

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

        config = yaml.safe_load(f)

    if not config:
        return {}

    return config


def load_button_config():

    config = load_yaml(
        BUTTON_CONFIG_PATH
    )

    if "buttons" not in config:

        raise ValueError(
            f"Missing 'buttons' section "
            f"in {BUTTON_CONFIG_PATH}"
        )

    return config["buttons"]


def load_refresh_config():

    config = load_yaml(
        REFRESH_CONFIG_PATH
    )

    if "refresh" not in config:

        raise ValueError(
            f"Missing 'refresh' section "
            f"in {REFRESH_CONFIG_PATH}"
        )

    return config["refresh"]


# ============================================================
# CONFIG VALIDATION
# ============================================================

def validate_button_config(buttons):

    required_buttons = [
        "NVHN",
        "Select",
        "Explorer",
        "Training",
        "Arena",
        "Sail",
        "Cook",
        "Forge",
        "Gold",
        "Enhance",
        "Fight",
    ]

    print()
    print(
        "[CONFIG] Checking buttons.yaml"
    )

    for button_name in required_buttons:

        if button_name not in buttons:

            raise ValueError(
                f"Missing button "
                f"'{button_name}' "
                f"in {BUTTON_CONFIG_PATH}"
            )

        config = buttons[button_name]

        for key in [
            "x1",
            "y1",
            "x2",
            "y2",
        ]:

            if key not in config:

                raise ValueError(
                    f"Button '{button_name}' "
                    f"missing '{key}'"
                )

        print(
            f"  [OK] {button_name}"
        )


def validate_refresh_config(refresh):

    print()
    print(
        "[CONFIG] Checking refresh.yaml"
    )

    for key in [
        "x1",
        "y1",
        "x2",
        "y2",
    ]:

        if key not in refresh:

            raise ValueError(
                f"Refresh config missing "
                f"'{key}'"
            )

    if not REFRESH_TEMPLATE.exists():

        raise FileNotFoundError(
            f"Refresh template not found: "
            f"{REFRESH_TEMPLATE}"
        )

    print(
        f"  [OK] template: "
        f"{REFRESH_TEMPLATE}"
    )

    print(
        f"  [OK] ROI: "
        f"({refresh['x1']}, {refresh['y1']}) -> "
        f"({refresh['x2']}, {refresh['y2']})"
    )


# ============================================================
# ACTIVATE GAME WINDOW
# ============================================================

def activate_game_window(hwnd):

    print(
        f"[WINDOW] Activating HWND={hwnd}"
    )

    try:

        win32gui.ShowWindow(
            hwnd,
            win32con.SW_RESTORE
        )

        win32gui.BringWindowToTop(
            hwnd
        )

        win32gui.SetForegroundWindow(
            hwnd
        )

        time.sleep(
            0.2
        )

    except Exception as e:

        print(
            f"[WINDOW] Activation warning: "
            f"{e}"
        )

    foreground = (
        win32gui.GetForegroundWindow()
    )

    print(
        f"[WINDOW] Foreground HWND="
        f"{foreground}"
    )

    return foreground == hwnd


# ============================================================
# CLIENT COORDINATE -> LPARAM
# ============================================================

def make_lparam(x, y):

    return win32api.MAKELONG(
        int(x),
        int(y)
    )


# ============================================================
# NON-INTRUSIVE WINDOW CLICK
# ============================================================

def post_mouse_click(hwnd, x, y):
    x = int(x)
    y = int(y)

    lparam = win32api.MAKELONG(x, y)

    print()
    print("=" * 70)
    print("[CLICK]")
    print(f"[CLICK] HWND   = {hwnd}")
    print(f"[CLICK] client = ({x},{y})")
    print("[CLICK] Method = Windows PostMessage")
    print("[CLICK] Physical mouse will NOT move.")
    print("[CLICK] Game does NOT need foreground.")

    if not win32gui.IsWindow(hwnd):
        raise RuntimeError(
            f"Invalid HWND: {hwnd}"
        )

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONDOWN,
        win32con.MK_LBUTTON,
        lparam
    )

    print(
        "[CLICK] WM_LBUTTONDOWN posted."
    )

    time.sleep(0.05)

    win32gui.PostMessage(
        hwnd,
        win32con.WM_LBUTTONUP,
        0,
        lparam
    )

    print(
        "[CLICK] WM_LBUTTONUP posted."
    )

    print("[CLICK] Click message sent.")
    print(
        f"[CLICK] Waiting {CLICK_WAIT:.1f}s..."
    )

    time.sleep(CLICK_WAIT)

    print("=" * 70)

    return True



# ============================================================
# CLICK DETECTION
# ============================================================

def click_detection(
    hwnd,
    detection
):

    if detection is None:

        print(
            "[CLICK] Detection is None."
        )

        return False

    x, y = detection["center"]

    print(
        f"[CLICK] Detection center="
        f"({x},{y})"
    )

    return post_mouse_click(
        hwnd,
        x,
        y
    )


# ============================================================
# CLICK BUTTON FROM YAML
# ============================================================

def click_button(
    hwnd,
    buttons,
    button_name
):

    if button_name not in buttons:

        print(
            f"[BUTTON] '{button_name}' "
            f"not found in buttons.yaml"
        )

        return False

    config = buttons[
        button_name
    ]

    x1 = config["x1"]
    y1 = config["y1"]
    x2 = config["x2"]
    y2 = config["y2"]

    center_x = (
        x1 + x2
    ) // 2

    center_y = (
        y1 + y2
    ) // 2

    print()
    print(
        f"[BUTTON] {button_name}"
    )

    print(
        f"         ROI="
        f"({x1},{y1}) -> "
        f"({x2},{y2})"
    )

    print(
        f"         center="
        f"({center_x},{center_y})"
    )

    return post_mouse_click(
        hwnd,
        center_x,
        center_y
    )


# ============================================================
# NVHN TEMPLATE
# ============================================================

def get_nvhn_template():

    templates = sorted(
        NVHN_TEMPLATE_DIR.glob("*.png")
    )

    if not templates:

        raise FileNotFoundError(
            f"No NVHN template found in "
            f"{NVHN_TEMPLATE_DIR}"
        )

    template = templates[0]

    print(
        f"[NVHN] Template: "
        f"{template}"
    )

    return template


# ============================================================
# NVHN DEBUG
# ============================================================

def save_nvhn_candidate_debug(
    frame,
    candidate,
    template_path
):

    DEBUG_CAPTURE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    x = candidate["x"]
    y = candidate["y"]
    w = candidate["width"]
    h = candidate["height"]

    # --------------------------------------------------------
    # Candidate crop
    # --------------------------------------------------------

    candidate_crop = frame[
        y:y + h,
        x:x + w
    ]

    candidate_file = (
        DEBUG_CAPTURE_DIR /
        "nvhn_candidate.png"
    )

    cv2.imwrite(
        str(candidate_file),
        candidate_crop
    )

    # --------------------------------------------------------
    # Template
    # --------------------------------------------------------

    template = cv2.imread(
        str(template_path),
        cv2.IMREAD_COLOR
    )

    template_file = (
        DEBUG_CAPTURE_DIR /
        "nvhn_template.png"
    )

    cv2.imwrite(
        str(template_file),
        template
    )

    # --------------------------------------------------------
    # Full debug frame
    # --------------------------------------------------------

    debug = frame.copy()

    cv2.rectangle(
        debug,
        (x, y),
        (x + w, y + h),
        (0, 255, 0),
        2
    )

    cx, cy = candidate["center"]

    cv2.circle(
        debug,
        (cx, cy),
        5,
        (0, 0, 255),
        -1
    )

    cv2.putText(
        debug,
        f"NVHN {candidate['confidence']:.4f}",
        (x, max(20, y - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    full_file = (
        DEBUG_CAPTURE_DIR /
        "nvhn_match_debug.png"
    )

    cv2.imwrite(
        str(full_file),
        debug
    )

    print(
        f"[NVHN DEBUG] Candidate image: "
        f"{candidate_file}"
    )

    print(
        f"[NVHN DEBUG] Template image: "
        f"{template_file}"
    )

    print(
        f"[NVHN DEBUG] Full image: "
        f"{full_file}"
    )

    print(
        f"[NVHN DEBUG] Candidate bbox: "
        f"x={x}, y={y}, "
        f"w={w}, h={h}"
    )


# ============================================================
# DETECT NVHN
# ============================================================

def detect_nvhn(
    frame,
    detector
):

    template_path = get_nvhn_template()

    print(
        f"[NVHN] Template: "
        f"{template_path}"
    )

    print(
        "[NVHN] Searching entire game window"
    )

    candidates = detector.matcher.find_all(
        frame,
        template_path,
        threshold=0.90
    )

    print(
        f"[NVHN] Found "
        f"{len(candidates)} candidate(s)"
    )

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        print(
            f"[NVHN] Candidate {index}: "
            f"confidence="
            f"{candidate['confidence']:.4f}, "
            f"center="
            f"{candidate['center']}"
        )

    if not candidates:

        print(
            "[NVHN] No candidate found"
        )

        return None

    # Candidates are already sorted by confidence
    nvhn = candidates[0]

    nvhn["type"] = "NVHN"
    nvhn["template"] = (
        template_path.stem
    )

    save_nvhn_candidate_debug(
        frame,
        nvhn,
        template_path
    )

    print(
        f"[NVHN] Selected candidate: "
        f"confidence="
        f"{nvhn['confidence']:.4f}, "
        f"center="
        f"{nvhn['center']}"
    )

    return nvhn


# ============================================================
# DETECT REFRESH
# ============================================================

def detect_refresh(
    frame,
    detector,
    refresh_config
):

    x1 = refresh_config["x1"]
    y1 = refresh_config["y1"]
    x2 = refresh_config["x2"]
    y2 = refresh_config["y2"]

    crop = frame[
        y1:y2,
        x1:x2
    ]

    detection = detector.matcher.find(
        crop,
        REFRESH_TEMPLATE
    )

    if detection is None:

        return None

    detection["x"] += x1
    detection["y"] += y1

    cx, cy = detection["center"]

    detection["center"] = (
        cx + x1,
        cy + y1
    )

    detection["type"] = "Refresh"

    return detection


# ============================================================
# CLICK REFRESH
# ============================================================

def click_refresh(
    hwnd,
    frame,
    detector,
    refresh_config
):

    print()
    print(
        "[REFRESH] Detecting refresh..."
    )

    detection = detect_refresh(
        frame,
        detector,
        refresh_config
    )

    if detection is None:

        print(
            "[REFRESH] Button not detected."
        )

        return False

    print(
        f"[REFRESH] Found "
        f"confidence="
        f"{detection['confidence']:.3f} "
        f"center="
        f"{detection['center']}"
    )

    return click_detection(
        hwnd,
        detection
    )


# ============================================================
# MATCH QUEST -> MISSION
# ============================================================

def match_quest_to_mission(
    quest,
    missions
):

    quest_type = quest["type"]

    print(
        f"[MATCH] Quest type: "
        f"{quest_type}"
    )

    candidates = [
        mission
        for mission in missions
        if mission["type"] == quest_type
    ]

    if not candidates:

        print(
            f"[MATCH] No mission for "
            f"{quest_type}"
        )

        return None

    candidates.sort(
        key=lambda item:
        item["confidence"],
        reverse=True
    )

    mission = candidates[0]

    print(
        "[MATCH] Found mission:"
    )

    print(
        f"        type="
        f"{mission['type']}"
    )

    print(
        f"        slot="
        f"{mission['slot']}"
    )

    print(
        f"        confidence="
        f"{mission['confidence']:.3f}"
    )

    print(
        f"        center="
        f"{mission['center']}"
    )

    return mission


# ============================================================
# PRINT DETECTIONS
# ============================================================

def print_detections(
    detection
):

    print()
    print(
        "---------------- DETECTION ----------------"
    )

    # --------------------------------------------------------
    # NVHN
    # --------------------------------------------------------

    nvhn = detection.get(
        "nvhn"
    )

    if nvhn:

        print(
            "[NVHN]"
            f" confidence="
            f"{nvhn['confidence']:.3f}"
            f" center="
            f"{nvhn['center']}"
        )

    else:

        print(
            "[NVHN] NOT FOUND"
        )

    # --------------------------------------------------------
    # Active quests
    # --------------------------------------------------------

    print()

    quests = detection.get(
        "active_quests",
        []
    )

    print(
        f"[ACTIVE QUESTS] "
        f"{len(quests)}"
    )

    for quest in quests:

        print(
            f"  {quest['slot']}: "
            f"{quest['type']} "
            f"confidence="
            f"{quest['confidence']:.3f} "
            f"center="
            f"{quest['center']}"
        )

    # --------------------------------------------------------
    # Missions
    # --------------------------------------------------------

    print()

    missions = detection.get(
        "missions",
        []
    )

    print(
        f"[MISSIONS] "
        f"{len(missions)}"
    )

    for mission in missions:

        print(
            f"  {mission['slot']}: "
            f"{mission['type']} "
            f"confidence="
            f"{mission['confidence']:.3f} "
            f"center="
            f"{mission['center']}"
        )

    print(
        "--------------------------------------------"
    )

    print()


# ============================================================
# CAPTURE
# ============================================================

def capture_game(
    capture,
    label
):

    DEBUG_CAPTURE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print(
        "[CAPTURE] Capturing game..."
    )

    frame = capture.grab()

    print(
        f"[CAPTURE] "
        f"{frame.shape[1]}x"
        f"{frame.shape[0]}"
    )

    output_path = (
        DEBUG_CAPTURE_DIR /
        f"{label}.png"
    )

    if not cv2.imwrite(
        str(output_path),
        frame
    ):

        raise RuntimeError(
            f"Unable to save capture: "
            f"{output_path}"
        )

    print(
        f"[CAPTURE] Saved: "
        f"{output_path}"
    )

    return frame


# ============================================================
# SELECT MISSION
# ============================================================

def select_mission(
    hwnd,
    buttons,
    mission
):

    print()
    print(
        "[STEP] Selecting mission"
    )

    print(
        f"[MISSION] "
        f"{mission['type']} "
        f"{mission['slot']}"
    )

    # --------------------------------------------------------
    # Click mission slot
    # --------------------------------------------------------

    if not click_detection(
        hwnd,
        mission
    ):

        raise RuntimeError(
            "Unable to click mission."
        )

    # --------------------------------------------------------
    # Click Select
    # --------------------------------------------------------

    if not click_button(
        hwnd,
        buttons,
        "Select"
    ):

        raise RuntimeError(
            "Button 'Select' is missing "
            "from buttons.yaml"
        )

    print(
        f"[SELECT] Waiting "
        f"{WAIT_AFTER_SELECT:.1f}s..."
    )

    time.sleep(
        WAIT_AFTER_SELECT
    )

    return True


# ============================================================
# GO TO DESTINATION
# ============================================================

def go_to_destination(
    hwnd,
    buttons,
    mission_type
):

    print()
    print(
        "[STEP] Going to destination:"
    )

    print(
        f"       {mission_type}"
    )

    if mission_type not in buttons:

        raise RuntimeError(
            f"No destination button "
            f"'{mission_type}' "
            f"in buttons.yaml"
        )

    if not click_button(
        hwnd,
        buttons,
        mission_type
    ):

        raise RuntimeError(
            f"Unable to click destination "
            f"'{mission_type}'"
        )

    print(
        f"[DESTINATION] Waiting "
        f"{WAIT_AFTER_DESTINATION:.1f}s..."
    )

    time.sleep(
        WAIT_AFTER_DESTINATION
    )

    print(
        f"[DESTINATION] "
        f"{mission_type}"
    )

    return True


# ============================================================
# FIND QUEST + MATCH
# ============================================================

def find_matching_mission(
    detection
):

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
            "[MATCH] No active quest detected."
        )

        return None, None

    # --------------------------------------------------------
    # Try all active quests.
    # If quest_1 has no matching mission,
    # continue with quest_2, quest_3, ...
    # --------------------------------------------------------

    for quest in quests:
        print(
            f"[MATCH] Quest type: {quest['type']}"
        )

        mission = match_quest_to_mission(
            quest,
            missions
        )

        if mission is not None:
            print(
                f"[MATCH] Found mission "
                f"for {quest['type']}"
            )

            return quest, mission

    print(
        "[MATCH] No mission for any active quest."
    )

    return None, None


# ============================================================
# MAIN FLOW
# ============================================================

def main():

    print("=" * 70)
    print(
        "BotVHT - TEST MISSION FLOW"
    )
    print("=" * 70)

    print()
    print(
        "[INPUT] Using non-intrusive "
        "Windows PostMessage clicks."
    )

    print(
        "[INPUT] Physical mouse will NOT move."
    )

    # ========================================================
    # 1. WINDOW
    # ========================================================

    hwnd = find_game_window()

    # ========================================================
    # 2. CAPTURE
    # ========================================================

    capture = WindowCapture(
        hwnd
    )

    # ========================================================
    # 3. DETECTOR
    # ========================================================

    detector = GameDetector(
        threshold=0.80
    )

    # ========================================================
    # 4. CONFIG
    # ========================================================

    buttons = load_button_config()

    refresh_config = load_refresh_config()

    validate_button_config(
        buttons
    )

    validate_refresh_config(
        refresh_config
    )

    print()
    print(
        "[CONFIG] Buttons loaded:"
    )

    for name in buttons:

        print(
            f"  - {name}"
        )

    # ========================================================
    # 5. INITIAL CAPTURE
    # ========================================================

    frame = capture_game(
        capture,
        "01_initial"
    )

    # ========================================================
    # 6. DETECT NVHN
    # ========================================================

    print()
    print(
        "[STEP] Detecting NVHN"
    )

    nvhn = detect_nvhn(
        frame,
        detector
    )

    if nvhn is None:

        print(
            "[NVHN] Not found."
        )

        return

    print(
        f"[NVHN] Found "
        f"confidence="
        f"{nvhn['confidence']:.3f} "
        f"center="
        f"{nvhn['center']}"
    )

    # ========================================================
    # 7. CLICK NVHN
    # ========================================================

    print()
    print(
        "[STEP] Opening NVHN"
    )

    if not click_detection(
        hwnd,
        nvhn
    ):

        raise RuntimeError(
            "Failed to send NVHN click."
        )

    print(
        f"[NVHN] Waiting "
        f"{WAIT_AFTER_NVHN:.1f}s..."
    )

    time.sleep(
        WAIT_AFTER_NVHN
    )

    # ========================================================
    # 8. CAPTURE AFTER NVHN
    # ========================================================

    frame = capture_game(
        capture,
        "02_after_nvhn_click"
    )

    # ========================================================
    # 9. MISSION SEARCH LOOP
    # ========================================================

    refresh_count = 0

    while True:

        print()
        print("=" * 70)

        print(
            f"[LOOP] Mission search "
            f"(refresh={refresh_count}/"
            f"{MAX_REFRESH})"
        )

        print("=" * 70)

        # ----------------------------------------------------
        # Fresh capture
        # ----------------------------------------------------

        frame = capture_game(
            capture,
            f"mission_{refresh_count:02d}"
        )

        # ----------------------------------------------------
        # Detect
        # ----------------------------------------------------

        detection = detector.detect(
            frame
        )

        print_detections(
            detection
        )

        # ----------------------------------------------------
        # Match
        # ----------------------------------------------------

        quest, mission = (
            find_matching_mission(
                detection
            )
        )

        if quest is None:

            print(
                "[STOP] No active quest."
            )

            return

        # ----------------------------------------------------
        # MATCH FOUND
        # ----------------------------------------------------

        if mission is not None:

            print()
            print(
                "[SUCCESS] Matching mission found."
            )

            # ------------------------------------------------
            # Select mission
            # ------------------------------------------------

            select_mission(
                hwnd,
                buttons,
                mission
            )

            # ------------------------------------------------
            # Destination
            # ------------------------------------------------

            go_to_destination(
                hwnd,
                buttons,
                mission["type"]
            )

            print()
            print("=" * 70)

            print(
                "[DONE] Mission flow completed."
            )

            print(
                f"Quest       : "
                f"{quest['type']}"
            )

            print(
                f"Mission     : "
                f"{mission['type']}"
            )

            print(
                f"Mission slot: "
                f"{mission['slot']}"
            )

            print("=" * 70)

            return

        # ====================================================
        # NO MATCH -> REFRESH
        # ====================================================

        if refresh_count >= MAX_REFRESH:

            print()
            print(
                f"[STOP] Reached maximum "
                f"refresh count: "
                f"{MAX_REFRESH}"
            )

            return

        refresh_count += 1

        print()
        print(
            "[NO MATCH] "
            f"Refreshing missions "
            f"({refresh_count}/"
            f"{MAX_REFRESH})..."
        )

        # ----------------------------------------------------
        # Detect + click Refresh
        # ----------------------------------------------------

        if not click_refresh(
            hwnd,
            frame,
            detector,
            refresh_config
        ):

            raise RuntimeError(
                "Refresh button could not be "
                "detected using refresh.yaml "
                "and refresh.png"
            )

        print(
            f"[REFRESH] Waiting "
            f"{WAIT_AFTER_REFRESH:.1f}s..."
        )

        time.sleep(
            WAIT_AFTER_REFRESH
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()