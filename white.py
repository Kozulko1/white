import sys

from argparse import ArgumentParser, Namespace
from pathlib import Path

from src.formatter import TabsFormatter,TrailingWhitespaceFormatter
from src.python_file import PythonFile
from src.repair_shop import PythonRepairShop


def parse_arguments() -> Namespace:
    parser = ArgumentParser(description="Select criteria for formatting python files")
    parser.add_argument("--directory_path", help="Directory where python files are kept", required=True)
    return parser.parse_args()


def load_python_filepaths(directory: Path) -> list:
    return [path for path in directory.rglob("*.py")]


def save_files(files: list) -> None:
    for file in files:
        file.save()


def main(args: Namespace) -> int:
    python_files = []
    for file_path in load_python_filepaths(Path(args.directory_path)):
        with PythonFile(file_path) as file:
            python_files.append(file)

    formatters = [TrailingWhitespaceFormatter(), TabsFormatter()]
    repair_shop = PythonRepairShop(formatters)

    save_files([repair_shop.repair_file(file) for file in python_files])
    return 0


if __name__ == "__main__":
    sys.exit(main(parse_arguments()))
