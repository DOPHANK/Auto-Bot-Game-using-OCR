import cv2
from pathlib import Path


QUEST_TEMPLATE_DIR = Path(
    "assets/templates/active_quests"
)

QUEST_SOURCE_DIR = Path(
    "screenshots/active_quests"
)


def get_next_number(directory):
    if not directory.exists():
        return 1

    numbers = []

    for file in directory.glob("*.png"):
        try:
            numbers.append(int(file.stem))
        except ValueError:
            pass

    if not numbers:
        return 1

    return max(numbers) + 1


def save_template(image, quest_name):
    quest_name = quest_name.strip()

    if not quest_name:
        return None

    QUEST_TEMPLATE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # ? = Active Quest chưa có nhiệm vụ
    if quest_name == "?":
        output = QUEST_TEMPLATE_DIR / "unknown.png"

        if output.exists():
            print(
                "unknown.png đã tồn tại."
            )
            return output

        if not cv2.imwrite(
            str(output),
            image
        ):
            raise RuntimeError(
                f"Unable to save {output}"
            )

        return output

    # Mission thực tế
    directory = (
        QUEST_TEMPLATE_DIR /
        quest_name
    )

    directory.mkdir(
        parents=True,
        exist_ok=True
    )

    number = get_next_number(directory)

    output = directory / f"{number:03d}.png"

    if not cv2.imwrite(
        str(output),
        image
    ):
        raise RuntimeError(
            f"Unable to save {output}"
        )

    return output


def show_quest(quest_number, image):
    window_name = (
        f"Active Quest {quest_number}"
    )

    display = image.copy()

    cv2.putText(
        display,
        f"Quest {quest_number}",
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

    height, width = display.shape[:2]

    scale = 4

    cv2.resizeWindow(
        window_name,
        max(width * scale, 200),
        max(height * scale, 150)
    )

    cv2.imshow(
        window_name,
        display
    )

    # Cho OpenCV render window
    cv2.waitKey(300)

    print()
    print("--------------------------------")
    print(f"Active Quest {quest_number}")
    print("--------------------------------")
    print()
    print("Nhập tên nhiệm vụ.")
    print("Ví dụ:")
    print("  brulee")
    print("  t_bone")
    print("  defeat_marine")
    print()
    print("Nhập ? nếu Quest đang trống.")
    print("Nhập SKIP để bỏ qua.")
    print()

    name = input(
        "Quest name: "
    ).strip()

    cv2.destroyWindow(
        window_name
    )

    cv2.waitKey(100)

    return name


def main():
    print("========================================")
    print("      ACTIVE QUEST TEMPLATE COLLECTOR")
    print("========================================")
    print()

    if not QUEST_SOURCE_DIR.exists():
        raise RuntimeError(
            "Không tìm thấy "
            "screenshots/active_quests"
        )

    quests = []

    for i in range(1, 4):
        path = (
            QUEST_SOURCE_DIR /
            f"quest_{i}.png"
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

        quests.append(image)

    print(
        "Đã load 3 Active Quest."
    )

    saved = []

    for i, image in enumerate(
        quests,
        start=1
    ):
        name = show_quest(
            i,
            image
        )

        if name.upper() == "SKIP":
            print(
                f"Quest {i}: SKIPPED"
            )
            continue

        if not name:
            print(
                f"Quest {i}: EMPTY"
            )
            continue

        output = save_template(
            image,
            name
        )

        if output is not None:
            saved.append(output)

        print()
        print(
            f"Quest {i} -> {output}"
        )

    print()
    print("========================================")
    print("              COMPLETED")
    print("========================================")
    print()

    print(
        "Active Quest templates:"
    )

    for path in saved:
        print(
            f"  {path}"
        )


if __name__ == "__main__":
    main()