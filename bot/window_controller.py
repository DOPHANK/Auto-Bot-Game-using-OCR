import time

import win32api
import win32con
import win32gui


class WindowController:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def client_to_screen(self, x, y):
        return win32gui.ClientToScreen(
            self.hwnd,
            (int(x), int(y))
        )

    def click(self, x, y):
        """
        Click inside the game window without moving
        the user's physical mouse.
        """

        x = int(x)
        y = int(y)

        lparam = win32api.MAKELONG(x, y)

        win32gui.PostMessage(
            self.hwnd,
            win32con.WM_MOUSEMOVE,
            0,
            lparam
        )

        win32gui.PostMessage(
            self.hwnd,
            win32con.WM_LBUTTONDOWN,
            win32con.MK_LBUTTON,
            lparam
        )

        time.sleep(0.03)

        win32gui.PostMessage(
            self.hwnd,
            win32con.WM_LBUTTONUP,
            0,
            lparam
        )

    def press(self, key):
        vk = win32api.VkKeyScan(key)

        win32gui.PostMessage(
            self.hwnd,
            win32con.WM_KEYDOWN,
            vk,
            0
        )

        win32gui.PostMessage(
            self.hwnd,
            win32con.WM_KEYUP,
            vk,
            0
        )