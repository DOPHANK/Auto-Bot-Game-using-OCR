import win32gui


def callback(hwnd, extra):
    if not win32gui.IsWindowVisible(hwnd):
        return

    title = win32gui.GetWindowText(hwnd).strip()

    if not title:
        return

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    print(
        f"HWND={hwnd:<8} "
        f"SIZE={right-left}x{bottom-top:<6} "
        f"TITLE={title}"
    )


def main():
    print("================================")
    print("       Windows")
    print("================================")
    print()

    win32gui.EnumWindows(callback, None)


if __name__ == "__main__":
    main()