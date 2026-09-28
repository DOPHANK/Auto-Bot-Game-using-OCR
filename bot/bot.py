from bot.controller import Controller
from bot.state_machine import StateMachine


class BotVHT:
    def __init__(self, detector):
        self.controller = Controller()
        self.detector = detector
        self.state_machine = StateMachine()

        self.running = True

    def update(self, frame):
        detection = self.detector.detect(frame)
        state = self.state_machine.update(detection)

        return state, detection

    def stop(self):
        self.running = False