import re

from abc import ABC, abstractmethod

from .python_file import PythonFile


WHITESPACE_PATTERN = r"[ \t]+(\r?$)"

class Formatter(ABC):
    @abstractmethod
    def format(file: PythonFile) -> PythonFile:
        pass


class TrailingWhitespaceFormatter(Formatter):
    def format(self, file: PythonFile) -> PythonFile:
        file.update_lines([re.sub(WHITESPACE_PATTERN, "", line) for line in file.get_lines()])
        return file
