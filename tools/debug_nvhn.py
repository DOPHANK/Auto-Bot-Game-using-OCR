import cv2
from vision.capture import ScreenCapture


def main():
    capture = ScreenCapture()
    frame = capture.grab()

    template = cv2.imread(
        "assets/templates/buttons/NVHN/001.png",
        cv2.IMREAD_COLOR
    )

    if template is None:
        print("Cannot load NVHN.png")
        return

    result = cv2.matchTemplate(
        frame,
        template,
        cv2.TM_CCOEFF_NORMED
    )

    _, max_value, _, max_location = cv2.minMaxLoc(result)

    print("================================")
    print("NVHN DEBUG")
    print("================================")
    print(f"Template size : {template.shape[1]} x {template.shape[0]}")
    print(f"Best score    : {max_value:.4f}")
    print(f"Best position : {max_location}")

    if max_value >= 0.50:
        x, y = max_location
        h, w = template.shape[:2]

        debug = frame.copy()

        cv2.rectangle(
            debug,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.imwrite(
            "screenshots/nvhn_debug.png",
            debug
        )

        print("Debug image saved:")
        print("screenshots/nvhn_debug.png")
    else:
        print("No reasonable match found.")


if __name__ == "__main__":
    main()