from pathlib import Path

from .python_file import PythonFile


class PythonRepairShop:
    def __init__(self, formatters: list) -> None:
        self.__formatters: list = formatters

    def repair_file(self, file: PythonFile) -> PythonFile:
        for formatter in self.__formatters:
            file = formatter.format(file)
        file.set_new_file_path(Path(f"{str(file.get_file_path())[:-3]}_formatted.py"))
        return file
