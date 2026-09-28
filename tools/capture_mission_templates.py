import cv2
from pathlib import Path


MISSIONS_DIR = Path(
    "screenshots/missions"
)

TEMPLATE_DIR = Path(
    "assets/templates/missions"
)


def get_next_number(directory):
    if not directory.exists():
        return 1

    numbers = []

    for file in directory.glob("*.png"):
        try:
            numbers.append(
                int(file.stem)
            )
        except ValueError:
            pass

    if not numbers:
        return 1

    return max(numbers) + 1


def save_template(image, mission_name):
    mission_name = mission_name.strip()

    if not mission_name:
        raise ValueError(
            "Mission name cannot be empty."
        )

    # Không cho phép ? trong available missions
    if mission_name == "?":
        raise ValueError(
            "Available mission không được dùng '?'. "
            "Dấu '?' chỉ thuộc Active Quest."
        )

    directory = TEMPLATE_DIR / mission_name

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    number = get_next_number(directory)

    output = directory / f"{number:03d}.png"

    if not cv2.imwrite(str(output), image):
        raise RuntimeError(
            f"Unable to save {output}"
        )

    return output


def show_slot(slot_number, image):
    window_name = f"Mission Slot {slot_number}"

    display = image.copy()

    cv2.putText(
        display,
        f"Slot {slot_number}",
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.namedWindow(
        window_name,
        cv2.WINDOW_NORMAL
    )

    # Phóng cửa sổ để dễ nhìn
    height, width = display.shape[:2]

    scale = 4

    cv2.resizeWindow(
        window_name,
        width * scale,
        height * scale
    )

    cv2.imshow(
        window_name,
        display
    )

    # Cho OpenCV thời gian render cửa sổ
    cv2.waitKey(300)

    print()
    print("--------------------------------")
    print(f"Slot {slot_number}")
    print("--------------------------------")
    print()
    print("Ảnh đang hiển thị trong cửa sổ OpenCV.")
    print()
    print("Nhập tên nhiệm vụ:")
    print("  brulee")
    print("  t_bone")
    print("  defeat_marine")
    print()
    print("Nhập ? nếu không có nhiệm vụ.")
    print("Nhập SKIP nếu muốn bỏ qua.")
    print()

    name = input("Mission name: ").strip()

    cv2.destroyWindow(window_name)

    # Xử lý GUI event trước khi chuyển slot
    cv2.waitKey(100)

    return name


def main():
    print("========================================")
    print("       MISSION TEMPLATE COLLECTOR")
    print("========================================")
    print()

    if not MISSIONS_DIR.exists():
        raise RuntimeError(
            "Không tìm thấy screenshots/missions"
        )

    slots = []

    for i in range(1, 6):
        path = (
            MISSIONS_DIR /
            f"slot_{i}.png"
        )

        if not path.exists():
            raise RuntimeError(
                f"Không tìm thấy {path}"
            )

        image = cv2.imread(
            str(path),
            cv2.IMREAD_COLOR
        )

        if image is None:
            raise RuntimeError(
                f"Không thể đọc {path}"
            )

        slots.append(image)

    print(
        "Đã load 5 mission slots."
    )

    print()
    print(
        "Tên nhiệm vụ nên dùng tên ngắn,"
        " không dấu, ví dụ:"
    )
    print()
    print("  brulee")
    print("  t_bone")
    print("  defeat_marine")
    print("  collect_wood")
    print()
    print(
        "Nếu không có nhiệm vụ: nhập ?"
    )

    saved = []

    for i, image in enumerate(
        slots,
        start=1
    ):

        name = show_slot(
            i,
            image
        )

        if name.upper() == "SKIP":
            print(
                f"Slot {i}: SKIPPED"
            )
            continue

        if not name:
            print(
                f"Slot {i}: EMPTY"
            )
            continue

        output = save_template(
            image,
            name
        )

        saved.append(
            output
        )

        print()
        print(
            f"Slot {i} -> {output}"
        )

    print()
    print("========================================")
    print("              COMPLETED")
    print("========================================")
    print()

    if not saved:
        print(
            "Không có template nào được lưu."
        )
        return

    print("Templates:")
    for path in saved:
        print(
            f"  {path}"
        )

    print()
    print(
        f"Template directory: "
        f"{TEMPLATE_DIR}"
    )


if __name__ == "__main__":
    main()