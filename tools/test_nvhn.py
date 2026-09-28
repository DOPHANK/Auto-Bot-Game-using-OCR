from vision.capture import ScreenCapture
from vision.detector import GameDetector


def main():
    capture = ScreenCapture()
    detector = GameDetector(threshold=0.80)

    frame = capture.grab()

    print(f"Frame size: {frame.shape[1]} x {frame.shape[0]}")
    print("Looking for NVHN...")

    result = detector.detect_nvhn(frame)

    if result is None:
        print("NVHN: NOT FOUND")
        return

    print("NVHN: FOUND")
    print(f"Position   : ({result['x']}, {result['y']})")
    print(f"Center     : {result['center']}")
    print(f"Size       : {result['width']} x {result['height']}")
    print(f"Confidence : {result['confidence']:.3f}")


if __name__ == "__main__":
    main()