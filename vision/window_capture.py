import ctypes

import cv2
import numpy as np
import win32gui
import win32ui


user32 = ctypes.windll.user32

PrintWindow = user32.PrintWindow
PrintWindow.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_uint,
]
PrintWindow.restype = ctypes.c_bool


class WindowCapture:
    def __init__(self, hwnd):
        self.hwnd = hwnd

    def get_client_rect(self):
        left, top, right, bottom = win32gui.GetClientRect(
            self.hwnd
        )

        width = right - left
        height = bottom - top

        return width, height

    def grab(self):
        width, height = self.get_client_rect()

        if width <= 0 or height <= 0:
            raise RuntimeError(
                "Game window has invalid client size. "
                "It may be minimized."
            )

        hwnd_dc = win32gui.GetWindowDC(self.hwnd)

        if not hwnd_dc:
            raise RuntimeError(
                "GetWindowDC failed."
            )

        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        bitmap = win32ui.CreateBitmap()

        bitmap.CreateCompatibleBitmap(
            mfc_dc,
            width,
            height
        )

        save_dc.SelectObject(bitmap)

        try:
            # PW_CLIENTONLY = 0x00000001
            result = PrintWindow(
                self.hwnd,
                save_dc.GetSafeHdc(),
                1
            )

            if not result:
                raise RuntimeError(
                    "Windows PrintWindow failed."
                )

            bitmap_bits = bitmap.GetBitmapBits(True)

            frame = np.frombuffer(
                bitmap_bits,
                dtype=np.uint8
            )

            frame = frame.reshape(
                height,
                width,
                4
            )

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGRA2BGR
            )

            return frame.copy()

        finally:
            win32gui.DeleteObject(
                bitmap.GetHandle()
            )

            save_dc.DeleteDC()
            mfc_dc.DeleteDC()

            win32gui.ReleaseDC(
                self.hwnd,
                hwnd_dc
            )

    def save(self, filename):
        frame = self.grab()

        if not cv2.imwrite(filename, frame):
            raise RuntimeError(
                f"Unable to save screenshot: {filename}"
            )

        return frame