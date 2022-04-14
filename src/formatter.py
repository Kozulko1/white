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


class TabsFormatter(Formatter):
    def format(self, file: PythonFile) -> PythonFile:
        file.update_lines(self.__replace_tabs_with_spaces(line, -1) for line in file.get_lines())
        return file

    def __replace_tabs_with_spaces(self, string: str, break_point: int) -> str:
        idx = 0
        for char in string:
            if char == "\t" and idx > break_point:
                if not self.__check_if_part_of_string(string, idx):
                    new_break_point = idx
                    string = string[:new_break_point] + string[new_break_point:].replace("\t", "    ", 1)
                    return self.__replace_tabs_with_spaces(string, new_break_point)
                else:
                    new_break_point = idx + string[idx:].index('"')
                    return self.__replace_tabs_with_spaces(string, new_break_point)
            idx += 1
        return string

    def __check_if_part_of_string(self, string: str, idx: int) -> bool:
        quote_count = 0
        for char in string[:idx]:
            if char == '"' or char == "'":
                quote_count += 1
        if quote_count % 2 == 1:
            if '"' in string[idx:] or "'" in string[idx:]:
                return True
        return False
