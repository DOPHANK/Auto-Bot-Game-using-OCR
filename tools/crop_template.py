import cv2
import mss
import numpy as np
from pathlib import Path


OUTPUT_DIR = Path("assets/templates")


def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]

        screenshot = sct.grab(monitor)

        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        return frame


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("================================")
    print("     BotVHT Template Tool")
    print("================================")
    print()
    print("Capturing current screen...")

    image = capture_screen()

    print(f"Screen size: {image.shape[1]} x {image.shape[0]}")
    print()
    print("Select the game UI element.")
    print("ENTER = save")
    print("ESC   = cancel")
    print()

    cv2.namedWindow(
        "BotVHT - Select Template",
        cv2.WINDOW_NORMAL
    )

    cv2.imshow(
        "BotVHT - Select Template",
        image
    )

    roi = cv2.selectROI(
        "BotVHT - Select Template",
        image,
        showCrosshair=True,
        fromCenter=False
    )

    x, y, w, h = roi

    if w == 0 or h == 0:
        print("No region selected.")
        cv2.destroyAllWindows()
        return

    crop = image[y:y + h, x:x + w]

    print()
    print(f"x      = {x}")
    print(f"y      = {y}")
    print(f"width  = {w}")
    print(f"height = {h}")

    name = input("Template name: ").strip()

    if not name:
        print("Invalid template name.")
        cv2.destroyAllWindows()
        return

    output = OUTPUT_DIR / f"{name}.png"

    cv2.imwrite(str(output), crop)

    print()
    print(f"Template saved:")
    print(output)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()