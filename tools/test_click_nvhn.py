import time

from vision.capture import ScreenCapture
from vision.detector import GameDetector
from bot.controller import Controller


def main():
    capture = ScreenCapture()
    detector = GameDetector(threshold=0.80)
    controller = Controller()

    print("================================")
    print("       Test NVHN Click")
    print("================================")
    print()
    print("Looking for NVHN...")

    frame = capture.grab()
    result = detector.detect_nvhn(frame)

    if result is None:
        print("NVHN not found.")
        return

    x, y = result["center"]

    print(f"NVHN found")
    print(f"Position   : ({result['x']}, {result['y']})")
    print(f"Center     : ({x}, {y})")
    print(f"Confidence : {result['confidence']:.3f}")
    print()
    print("Clicking in 2 seconds...")
    print("Move the mouse away if necessary.")
    
    time.sleep(2)

    controller.click(x, y)

    print()
    print(f"Clicked NVHN at ({x}, {y})")


if __name__ == "__main__":
    main()