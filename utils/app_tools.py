# Various utilities

from pathlib import Path
import subprocess
import re


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


def select_file(is_unix_like_system: bool) -> Path:
    while True:
        print("Drag and drop your file")
        file_path = input("> ").strip()
        if not file_path:
            raise InterruptedError("No file path was given")

        if is_unix_like_system:
            file_path = file_path.replace("\\", "")

        file = Path(file_path)
        if file.exists():
            return file.resolve()

        print(f"{file.name} doesn't exist")


def select_option(options: list, values=None) -> str:
    selection = ""

    while not selection:
        selection = input("> ").upper()
        if selection not in options:
            print("Invalid option")
            selection = ""

    if values is not None:
        return values[options.index(selection)]
    return selection


def get_int_in(lower_bound: int, upper_bound: int) -> int:
    number_str = ""
    while not number_str:
        number_str = input("> ")
        if re.sub(r"\d+", "", number_str):  # There still any characters
            print(f"Invalid input, integer must be in range [{lower_bound}, {upper_bound}]")
            number_str = ""

    return int(number_str)


def enumerate_list(data: list) -> tuple:
    data_str = ""
    options = list()
    for i, dat in enumerate(data):
        data_str += f"{i + 1}.\t{dat}\n"
        options.append(f"{i + 1}")

    return data_str[:-1], options


def merge_lists(list1: list, list2: list) -> list:
    new_list = list()
    for item1, item2 in zip(list1, list2):
        new_list.append(f"{item1}\t[{item2}]")

    return new_list


def clear_screen(is_unix_like_system: bool):
    if is_unix_like_system:
        subprocess.call("clear")
    else:
        subprocess.call("cls")


def run_command(cmd: str, include_error_output: bool, cwd="") -> str:
    if cwd:
        process = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True)
    else:
        process = subprocess.run(cmd, shell=True, capture_output=True)

    output = process.stdout.decode("utf-8")
    if include_error_output:
        output += process.stderr.decode("utf-8")

    return output


def get_command_process(cmd: str, cwd=""):
    if cwd:
        process = subprocess.Popen("exec " + cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        process = subprocess.Popen("exec " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return process
