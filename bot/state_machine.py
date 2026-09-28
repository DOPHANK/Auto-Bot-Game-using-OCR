from enum import Enum


class BotState(Enum):
    UNKNOWN = "unknown"
    IDLE = "idle"
    PLAYING = "playing"
    MENU = "menu"
    LOADING = "loading"
    ERROR = "error"


class StateMachine:
    def __init__(self):
        self.state = BotState.UNKNOWN

    def update(self, detection):
        """
        Tạm thời chưa có game-specific detection.
        """
        self.state = BotState.UNKNOWN
        return self.state