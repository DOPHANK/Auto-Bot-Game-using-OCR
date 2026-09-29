import time


class MissionSelector:

    def __init__(self, controller):
        self.controller = controller

    def select(self, mission):
        center = mission.get("center")

        if center is None:
            print("[MissionSelector] Mission has no center")
            return False

        x, y = center

        print(f"[MissionSelector] Clicking mission at ({x}, {y})")

        self.controller.click(x, y)

        time.sleep(0.3)

        return True