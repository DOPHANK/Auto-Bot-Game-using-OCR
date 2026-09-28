import time
import cv2

from vision.capture import ScreenCapture
from vision.detector import GameDetector
from bot.state_machine import StateMachine


def main():
    print("================================")
    print("       BotVHT started!")
    print("================================")

    capture = ScreenCapture()

    detector = GameDetector()
    state_machine = StateMachine()

    print("Screen capture initialized.")
    print("Vision initialized.")
    print("State machine initialized.")
    print("Press ESC to stop.")


    while True:
        frame = capture.grab()

        detection = detector.detect(frame)
        state = state_machine.update(detection)

        cv2.imshow("BotVHT Vision", frame)

        key = cv2.waitKey(30) & 0xFF

        if key == 27:
            print("Stopping BotVHT...")
            break

        time.sleep(0.01)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()