import win32gui


def enum_windows(hwnd, results):
    if not win32gui.IsWindowVisible(hwnd):
        return

    title = win32gui.GetWindowText(hwnd)

    if title.strip():
        rect = win32gui.GetWindowRect(hwnd)

        left, top, right, bottom = rect
        width = right - left
        height = bottom - top

        results.append({
            "hwnd": hwnd,
            "title": title,
            "left": left,
            "top": top,
            "right": right,
            "bottom": bottom,
            "width": width,
            "height": height,
        })


windows = []

win32gui.EnumWindows(
    lambda hwnd, extra: enum_windows(hwnd, windows),
    None
)

print()
print("=" * 90)
print("OPEN WINDOWS")
print("=" * 90)

for window in windows:
    print(
        f"HWND={window['hwnd']} | "
        f"{window['title']} | "
        f"position=({window['left']},{window['top']}) | "
        f"size={window['width']}x{window['height']}"
    )