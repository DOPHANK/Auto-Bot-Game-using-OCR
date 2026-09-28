from vision.capture import ScreenCapture
from vision.template import TemplateMatcher


def main():
    capture = ScreenCapture()
    matcher = TemplateMatcher(threshold=0.80)

    frame = capture.grab()

    result = matcher.find(
        frame,
        "assets/templates/quest.png"
    )

    if result is None:
        print("Quest template: NOT FOUND")
        return

    print("Quest template found:")
    print(f"  Position : {result['x']}, {result['y']}")
    print(f"  Center   : {result['center']}")
    print(f"  Size     : {result['width']} x {result['height']}")
    print(f"  Confidence: {result['confidence']:.3f}")


if __name__ == "__main__":
    main()