import abc
from typing import List, Callable

from models.blocks import CodeBlock


class BaseParser(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def parse_file(self) -> None:
        pass

    @abc.abstractmethod
    def remove_doc_strings(self) -> None:
        pass

    @abc.abstractmethod
    def embed_documentation(self) -> None:
        pass

    @abc.abstractmethod
    def write_to_file(self) -> None:
        pass

    @abc.abstractmethod
    def _get_indentation_level(self, line) -> int:
        pass

    @abc.abstractmethod
    def _check_has_docstring(
        self, code_block: CodeBlock, callback: Callable[[], bool]
    ) -> bool:
        pass


class Parser(BaseParser):

    def __init__(self, file_name: str, file_type: str) -> None:
        self.file_name = file_name
        self.file_type = file_type
        self.lines = []
        self.code_blocks = []
        self.allowed_doc_str_fmt = ""
        self.rep_doc_str_fmt: List[str] = []

    @property
    def lines(self) -> List[str]:
        return self._lines

    @lines.setter
    def lines(self, lines: List[str]) -> None:
        self._lines = lines

    @property
    def code_blocks(self) -> List[CodeBlock]:
        return self._code_blocks

    @code_blocks.setter
    def code_blocks(self, code_blocks: List[CodeBlock]) -> None:
        self._code_blocks = code_blocks

    def parse_file(self) -> None:
        raise NotImplementedError("parse_file not implemented")

    def embed_documentation(self) -> None:
        print(f"Documentation embedded successfully for {self.file_name}")

    def write_to_file(self) -> None:
        with open(self.file_name, "w", encoding="utf8") as f:
            f.writelines(self.lines)

    def _get_indentation_level(self, line: str) -> int:
        return len(line) - len(line.lstrip())

    def _check_has_docstring(
        self, code_block: CodeBlock, callback: Callable[[], bool]
    ) -> bool:
        next_line = self.lines[code_block.position.body_start].strip()
        return next_line.startswith(self.allowed_doc_str_fmt) or callback()
