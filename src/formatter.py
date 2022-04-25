import re

from abc import ABC, abstractmethod
from typing import List

from .python_file import PythonFile


WHITESPACE_PATTERN = r"[ \t]+(\r?$)"
FUNCTION_PROTOTYPE_PATTERN = r"\s*def\s+.*"


class Formatter(ABC):
    @abstractmethod
    def format(self, file: PythonFile) -> PythonFile:
        pass

    def _remove_starting_whitespace_from_string(self, line: str) -> str:
        return line[len(line) - len(line.lstrip()) :]


class TrailingWhitespaceFormatter(Formatter):
    def format(self, file: PythonFile) -> PythonFile:
        file.update_lines(
            [re.sub(WHITESPACE_PATTERN, "", line) for line in file.get_lines()]
        )
        return file


class TabsFormatter(Formatter):
    def format(self, file: PythonFile) -> PythonFile:
        file.update_lines(
            [
                self.__replace_tabs_with_spaces(line, -1)
                for line in file.get_lines()
            ]
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


class ImportsFormatter(Formatter):
    def format(self, file: PythonFile) -> PythonFile:
        num_of_import_lines = 0
        file_lines = file.get_lines()
        contains_from_import = False
        for line in file_lines:
            if self._remove_starting_whitespace_from_string(line).startswith(
                "import"
            ):
                file_lines.insert(
                    num_of_import_lines,
                    self._remove_starting_whitespace_from_string(
                        file_lines.pop(file_lines.index(line))
                    ),
                )
                num_of_import_lines += 1
            elif (
                self._remove_starting_whitespace_from_string(line).startswith(
                    "from"
                )
                and "import" in line
            ):
                file_lines.insert(
                    num_of_import_lines,
                    self._remove_starting_whitespace_from_string(
                        file_lines.pop(file_lines.index(line))
                    ),
                )
                contains_from_import = True
        if contains_from_import:
            file_lines.insert(num_of_import_lines, "\n")
        if num_of_import_lines:
            file_lines = self.__handle_comma_imports(
                file_lines, num_of_import_lines
            )
        file.update_lines(file_lines)
        return file

    def __handle_comma_imports(
        self, lines: List[str], imports_num: int
    ) -> None:
        idx_increment = 0
        updated_lines = lines.copy()
        for idx in range(imports_num):
            if "," in lines[idx]:
                separated_imports = self.__get_separated_imports_from_line(
                    lines[idx][7:]
                )
                del updated_lines[idx + idx_increment]
                updated_lines[
                    idx + idx_increment : idx + idx_increment
                ] = separated_imports
                idx_increment = idx_increment + len(separated_imports) - 1
        return updated_lines

    def __get_separated_imports_from_line(self, line: str) -> List[str]:
        imports = line.split(",")
        for part in imports:
            if "\n" in part:
                imports.insert(
                    imports.index(part),
                    f"import {imports.pop(imports.index(part)).replace(' ', '')}",
                )
            else:
                imports.insert(
                    imports.index(part),
                    f"import {imports.pop(imports.index(part)).replace(' ', '')}\n",
                )
        return imports


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
            # imports TODO
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
        self, formatted_lines: List[str], line: str, num_of_spaces: int
    ) -> None:
        formatted_lines.append(f'{line[: line.index("(") + 1]}\n')
        formatted_lines.append(
            f"{self.__get_spaces(num_of_spaces + 4)}{self.__single_out_function_params(line)}\n"
        )
        formatted_lines.append(f"{self.__get_spaces(num_of_spaces)}):\n")

    def __append_exceeding_function(
        self, formatted_lines: List[str], line: str, num_of_spaces: int
    ) -> None:
        formatted_lines.append(f'{line[: line.index("(") + 1]}\n')
        for param in self.__single_out_function_params(line).split(","):
            param = self._remove_starting_whitespace_from_string(param)
            formatted_lines.append(
                f"{self.__get_spaces(num_of_spaces + 4)}{param},\n"
            )
        formatted_lines.append(f"{self.__get_spaces(num_of_spaces)}):\n")

    def __append_non_function_prototype_exceeding_line(
        self, formatted_lines: List[str], line: str
    ) -> None:
        num_of_spaces = len(line) - len(line.lstrip())
        if "(" in line[: self.length_limit]:
            idx = line[: self.length_limit].rindex("(")
            formatted_lines.append(f"{line[: idx + 1]}\n")
            self.__append_exceeded_parenthesis_line(
                formatted_lines, line[idx + 1 :, num_of_spaces]
            )
        else:
            pass  # TODO

    def __append_exceeded_parenthesis_line(
        self, formatted_lines: List[str], line: str, num_of_spaces: int
    ) -> None:
        if (
            len(line + num_of_spaces + 4) < self.length_limit
            and line[len(line) - 1] == ")"
        ):
            formatted_lines.append(
                f"{self.__get_spaces(num_of_spaces + 4)}{line[:len(line)-1]}\n"
            )
            formatted_lines.append(f"{self.__get_spaces(num_of_spaces)})")
        else:
            pass  # TODO
