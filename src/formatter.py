import re

from abc import ABC, abstractmethod

from .python_file import PythonFile


WHITESPACE_PATTERN = r"[ \t]+(\r?$)"
FUNCTION_PROTOTYPE_PATTERN = r"\s*def\s+.*"


class Formatter(ABC):
    @abstractmethod
    def format(self, file: PythonFile) -> PythonFile:
        pass


class TrailingWhitespaceFormatter(Formatter):
    def format(self, file: PythonFile) -> PythonFile:
        file.update_lines(
            [re.sub(WHITESPACE_PATTERN, "", line) for line in file.get_lines()]
        )
        return file


class TabsFormatter(Formatter):
    def format(self, file: PythonFile) -> PythonFile:
        file.update_lines(
            [self.__replace_tabs_with_spaces(line, -1)
            for line in file.get_lines()]
        )
        return file

    def __replace_tabs_with_spaces(self, string: str, break_point: int) -> str:
        idx = 0
        for char in string:
            if char == "\t" and idx > break_point:
                if not self.__check_if_part_of_string(string, idx):
                    new_break_point = idx
                    string = string[:new_break_point] + string[
                        new_break_point:
                    ].replace("\t", "    ", 1)
                    return self.__replace_tabs_with_spaces(
                        string, new_break_point
                    )
                else:
                    new_break_point = idx + string[idx:].index('"')
                    return self.__replace_tabs_with_spaces(
                        string, new_break_point
                    )
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


class LineLengthFormatter(Formatter):
    def __init__(self, length_limit: int) -> None:
        self.length_limit = length_limit

    def format(self, file: PythonFile) -> PythonFile:
        formatted_lines = []
        file_lines = file.get_lines()
        counter = 0
        while counter < len(file_lines):
            line: str = file_lines[counter]
            if len(line) < self.length_limit:
                formatted_lines.append(file_lines[counter])
                counter += 1
                continue
            if self.__check_if_function_prototype(line):
                num_of_spaces = line.index("d")
                if self.__check_if_params_exceed_limit(
                    self.__single_out_function_params(line), num_of_spaces + 4
                ):
                    self.__append_exceeding_function(
                        formatted_lines, line, num_of_spaces
                    )
                else:
                    self.__append_unexceeding_function(
                        formatted_lines, line, num_of_spaces
                    )
                counter += 1
                continue
            self.__append_non_function_prototype_exceeding_line(
                formatted_lines, line
            )
            counter += 1
        file.update_lines(formatted_lines)
        return file

    def __check_if_function_prototype(self, line: str) -> bool:
        if re.search(FUNCTION_PROTOTYPE_PATTERN, line):
            return True
        return False

    def __single_out_function_params(self, line: str) -> str:
        return line[line.index("(") + 1 : line.index(")")]

    def __check_if_params_exceed_limit(
        self, params: str, num_of_spaces: int
    ) -> bool:
        if (len(params) + num_of_spaces) < self.length_limit:
            return False
        return True

    def __get_spaces(self, num_of_spaces: int) -> str:
        output = ""
        while num_of_spaces > 0:
            output += " "
            num_of_spaces -= 1
        return output

    def __append_unexceeding_function(
        self, formatted_lines: list, line: str, num_of_spaces: int
    ) -> None:
        formatted_lines.append(line[: line.index("(") + 1])
        formatted_lines.append(
            f"{self.__get_spaces(num_of_spaces + 4)}{self.__single_out_function_params(line)}"
        )
        formatted_lines.append(f"{self.__get_spaces(num_of_spaces)})")

    def __append_exceeding_function(
        self, formatted_lines: list, line: str, num_of_spaces: int
    ) -> None:
        formatted_lines.append(line[: line.index("(") + 1])
        for param in self.__single_out_function_params(line).split(","):
            param = param[len(param) - len(param.lstrip()) :]
            formatted_lines.append(
                f"{self.__get_spaces(num_of_spaces + 4)}{param},"
            )
        formatted_lines.append(f"{self.__get_spaces(num_of_spaces)})")

    def __append_non_function_prototype_exceeding_line(
        self, formatted_lines: list, line: str
    ) -> None:
        num_of_spaces = len(line) - len(line.lstrip())
        if "(" in line[: self.length_limit]:
            idx = line[: self.length_limit].rindex("(")
            formatted_lines.append(line[: idx + 1])
            self.__append_exceeded_parenthesis_line(
                formatted_lines, line[idx + 1 :, num_of_spaces]
            )
        else:
            pass  # TODO

    def __append_exceeded_parenthesis_line(
        self, formatted_lines: list, line: str, num_of_spaces: int
    ) -> None:
        if (
            len(line + num_of_spaces + 4) < self.length_limit
            and line[len(line) - 1] == ")"
        ):
            formatted_lines.append(
                f"{self.__get_spaces(num_of_spaces + 4)}{line[:len(line)-1]}"
            )
            formatted_lines.append(f"{self.__get_spaces(num_of_spaces)})")
        else:
            pass  # TODO
