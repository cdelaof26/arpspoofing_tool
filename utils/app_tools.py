# Various utilities

from pathlib import Path


def read_file(file: Path) -> str:
    if not file.exists() or not file.is_file():
        return ""

    try:
        with open(file, "r") as f:
            return f.read()
    except UnicodeDecodeError:
        return ""


def write_file(file: Path, data: str) -> bool:
    if not file.parent.exists():
        return False

    try:
        with open(file, "w") as f:
            f.write(data)
            return True
    except UnicodeDecodeError:
        return False


def select_file() -> Path:
    while True:
        print("Drag and drop your file")
        file_path = input("> ").replace("\\", "").strip()

        file = Path(file_path)
        if file.exists():
            return file.resolve()

        print(f"{file.name} doesn't exist")


def select_option(options: list, values=None) -> str:
    selection = ""

    while not selection:
        selection = input("> ")
        if selection not in options:
            print("Invalid option")
            selection = ""

    if values is not None:
        return values[options.index(selection)]
    return selection

