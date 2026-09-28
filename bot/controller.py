import time
import pyautogui


class Controller:
    def __init__(self):
        pyautogui.PAUSE = 0.05

    def move(self, x, y, duration=0.1):
        pyautogui.moveTo(x, y, duration=duration)

    def click(self, x=None, y=None):
        if x is not None and y is not None:
            pyautogui.click(x, y)
        else:
            pyautogui.click()

    def press(self, key):
        pyautogui.press(key)

    def key_down(self, key):
        pyautogui.keyDown(key)

    def key_up(self, key):
        pyautogui.keyUp(key)

    def wait(self, seconds):
        time.sleep(seconds)