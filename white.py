import sys

from argparse import ArgumentParser, Namespace
from copy import copy
from pathlib import Path

from src.formatter import (
    ImportsFormatter,
    LineLengthFormatter,
    TabsFormatter,
    TrailingWhitespaceFormatter,
)
from src.python_file import PythonFile
from src.repair_shop import PythonRepairShop


def parse_arguments() -> Namespace:
    parser = ArgumentParser(
        description="Select criteria for formatting python files"
    )
    parser.add_argument(
        "--directory_path",
        help="Directory where python files are kept",
        required=True,
    )
    parser.add_argument(
        "--line_length", help="Line length limit", required=True
    )
    return parser.parse_args()


def check_line_length(line_length: int) -> bool:
    if line_length == 80 or line_length == 120:
        return False
    return True


def load_python_filepaths(directory: Path) -> list:
    return [path for path in directory.rglob("*.py")]


def save_files(files: list) -> None:
    for file in files:
        file.save()


def main(args: Namespace) -> int:
    try:
        if check_line_length(int(args.line_length)):
            sys.exit("Line length must be 80 or 120")
    except ValueError as exc:
        raise ValueError(
            f"--line_length must be integer (80 or 120). Received: {exc}"
        )
    python_files = []
    for file_path in load_python_filepaths(Path(args.directory_path)):
        with PythonFile(file_path) as file:
            python_files.append(file)

    formatters = [
        TrailingWhitespaceFormatter(),
        TabsFormatter(),
        ImportsFormatter(),
        LineLengthFormatter(int(args.line_length)),
    ]
    repair_shop = PythonRepairShop(formatters)
    repaired_files = [
        repair_shop.repair_file(copy(file)) for file in python_files
    ]
    changed_files = [
        repaired_files[idx]
        for idx in range(len(repaired_files))
        if repaired_files[idx] != python_files[idx]
    ]
    save_files(changed_files)
    return 0


if __name__ == "__main__":
    sys.exit(main(parse_arguments()))
