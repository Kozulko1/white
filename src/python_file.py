from __future__ import annotations
import logging

from io import TextIOWrapper
from pathlib import Path
from typing import List


class PythonFile:
    def __init__(self, file_path: Path) -> None:
        self.__file: TextIOWrapper = None
        self.__file_path: Path = file_path

    def get_file_path(self) -> Path:
        return self.__file_path

    def get_lines(self) -> List[str]:
        try:
            return self.__lines
        except:
            logging.error("No file has been loaded")

    def save(self):
        with open(self.__file_path, "w") as file:
            [file.write(line) for line in self.__lines]

    def update_lines(self, new_lines: List[str]) -> None:
        self.__lines = new_lines

    def set_new_file_path(self, file_path: Path) -> None:
        self.__file_path = file_path

    def __eq__(self, __o: PythonFile) -> bool:
        return self.__lines == __o.__lines

    def __enter__(self) -> PythonFile:
        self.__file = open(self.__file_path, "r")
        self.__lines: list = self.__file.readlines()
        return self

    def __exit__(self, type, value, traceback):
        self.__file.close()

    def __str__(self):
        output = ""
        for line in self.__lines:
            output += line
        return output
