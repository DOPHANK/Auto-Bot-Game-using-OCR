import cv2


IMAGE = "screenshots/daily_mission_window.png"
OUTPUT = "assets/templates/mission_region.png"

selection = None
start = None
drawing = False

frame = cv2.imread(IMAGE)

if frame is None:
    raise RuntimeError(
        f"Cannot read {IMAGE}"
    )


def callback(event, x, y, flags, param):
    global selection
    global start
    global drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        start = (x, y)
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        display = frame.copy()

        cv2.rectangle(
            display,
            start,
            (x, y),
            (0, 255, 0),
            2
        )

        cv2.imshow(
            "Mission Region",
            display
        )

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

        x1, y1 = start
        x2, y2 = x, y

        x1, x2 = sorted((x1, x2))
        y1, y2 = sorted((y1, y2))

        selection = (
            x1,
            y1,
            x2,
            y2
        )


cv2.namedWindow(
    "Mission Region",
    cv2.WINDOW_NORMAL
)

cv2.imshow(
    "Mission Region",
    frame
)

cv2.setMouseCallback(
    "Mission Region",
    callback
)

print("Kéo chuột quanh vùng chứa danh sách nhiệm vụ.")
print("ENTER = lưu")
print("ESC = hủy")

while True:
    key = cv2.waitKey(30) & 0xFF

    if key == 13:
        break

    if key == 27:
        cv2.destroyAllWindows()
        raise SystemExit


cv2.destroyAllWindows()

if selection is None:
    raise RuntimeError(
        "No region selected."
    )

x1, y1, x2, y2 = selection

crop = frame[
    y1:y2,
    x1:x2
]

cv2.imwrite(
    OUTPUT,
    crop
)

print()
print(
    f"Saved: {OUTPUT}"
)

print(
    f"Size: {crop.shape[1]} x {crop.shape[0]}"
)