from typing import List
from dataclasses import dataclass

from client.service import Prompt, AiClient


prompt: Prompt = {
    "role": "assistant",
    "content": """
    Generate documentation for functions and classes using Google Style Python. 
    Follow these formatting standards:
    - Only use single quotation marks if needed.
    - Do not respond with the triple quotation marks for the start and end of the docstring.
    - Limit each line to the required number of characters requested below.
    - Avoid any escaping characters such as slashes, or backslashes.
    - Ensure no trailing spaces at the end of each line.
    - If the object type is a module, describe its contents and its purpose
    """,
}

client = AiClient(prompt=prompt)


@dataclass
class Position:
    indent_level: int
    body_start: int
    body_end: int


@dataclass
class CodePosition(Position):
    declaration_start: int
    # @offset will help with getting lambda functions, offset from line start
    offset = int | None
    # @line_offset will capture preceding decorators
    line_offset = int | None


class DocString:

    def __init__(
        self,
        doc_str: List[str] | str,
        position: Position,
    ) -> None:
        self.position = position
        self.raw_doc_string = doc_str

    @property
    def doc_string(self) -> str:
        return "".join(self.raw_doc_string)

    @property
    def raw_doc_string(self) -> List[str]:
        return self._raw_doc_string

    @raw_doc_string.setter
    def raw_doc_string(self, val: List[str] | str) -> None:
        if isinstance(val, str):
            self.raw_doc_string = val.splitlines(keepends=True)
        else:
            self._raw_doc_string = val

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, pos: Position) -> None:
        self._position = pos

    def __len__(self) -> int:
        if self.position.body_end < 0:
            return 0
        return self.position.body_end - self.position.body_start

    @classmethod
    def generate_docstring(
        cls,
        name: str,
        object_type: str,
        code_sample: str,
        file_type: str,
        max_line_length: int,
    ) -> str:

        doc_str_prompt = f"""
        Write a docstring for a {file_type} {object_type} named '{name}'.
        Each line should not exceed {max_line_length} characters for the following
        {object_type}:

        {code_sample}
        """
        response = client.single_response(doc_str_prompt)

        return response

    # def _format_str(self, input_str: str, indent_count: int) -> str:
    #     words = input_str.split(" ")
    #     max_line_length = 79 - indent_count
    #     indent = " " * indent_count

    #     lines = []
    #     current_line = indent

    #     for word in words:
    #         if len(current_line) + len(word) + 1 > max_line_length:
    #             lines.append(current_line.rstrip())
    #             current_line = indent + word
    #         else:
    #             if len(current_line) > len(indent):
    #                 current_line += " " + word
    #             else:
    #                 current_line += word

    #     lines.append(current_line.rstrip())
    #     return "\n".join(lines)

    @classmethod
    def format_to_docstring(
        cls,
        doc_string: str,
        allowed_doc_str_fmt: str,
        rep_doc_str_fmt: List[str],
        indent_level: int = 0,
        chars_skip: int = 3,
    ) -> str:
        str_starts = [doc_string.startswith(str_fmt) for str_fmt in rep_doc_str_fmt]
        str_ends = [doc_string.endswith(str_fmt) for str_fmt in rep_doc_str_fmt]

        if any(str_starts):
            doc_string = doc_string[chars_skip:]
        if any(str_ends):
            doc_string = doc_string[:-chars_skip]

        indentation = " " * indent_level
        doc_string = doc_string.replace(allowed_doc_str_fmt[0], "")
        docstring_text = "\n".join(
            [indentation + line for line in doc_string.splitlines()]
        )
        quotations = indentation + f"{allowed_doc_str_fmt}\n"

        return f"{quotations}{docstring_text}\n{quotations}"

    def reset(self) -> None:
        self.raw_doc_string = []
        self.position.body_start = -1
        self.position.body_end = -1

    def updated_position(self, start, end) -> None:
        self.position.body_start = start
        self.position.body_end = end


class CodeBlock:

    def __init__(
        self,
        name: str,
        obj_type: str,
        position: CodePosition,
        doc_string: DocString | None = None,
    ):
        self.name = name
        self.obj_type = obj_type
        self.position = position
        self.doc_string = doc_string

    def __str__(self) -> str:
        return (
            f"{self.obj_type}: {self.name} (doc:{self.doc_string is not None})\n"
            + f"Start: {self.position.declaration_start} End: {self.position.body_end}\n"
        )

    @property
    def doc_string(self) -> DocString | None:
        return self._doc_string

    @doc_string.setter
    def doc_string(self, doc_str: DocString) -> None:
        self._doc_string = doc_str

    def generate_docstring(
        self,
        code_sample: str,
        file_type: str,
        allowed_doc_str_fmt: str,
        rep_doc_str_fmt: List[str],
    ) -> str:
        doc_str = DocString.generate_docstring(
            name=self.name,
            object_type=self.obj_type,
            code_sample=code_sample,
            file_type=file_type,
            max_line_length=(
                self.position.indent_level + 4 if self.obj_type != "module" else 0
            ),
        )

        indent_level = (
            self.position.indent_level + 4 if self.obj_type != "module" else 0
        )

        generated_doc_str = DocString.format_to_docstring(
            doc_str,
            allowed_doc_str_fmt,
            rep_doc_str_fmt,
            indent_level,
            len(allowed_doc_str_fmt),
        )

        return generated_doc_str

    def add_docstring(self) -> None:
        pass

    def reset_doc_str(self) -> None:
        self.doc_string = None

    def __repr__(self) -> str:
        return self.__class__.__name__ + " : " + self.name


class Module:
    def __init__(
        self,
        name: str,
        code_blocks: List[CodeBlock],
        docstring: DocString,
        start_line: int = 0,
    ) -> None:
        self.name = name
        self.docstring: DocString | None = docstring
        self.code_blocks = code_blocks
        self.start_line = start_line
        self.imports: List[str] = []
        self._index = 0

    def __iter__(self):
        return self.code_blocks

    def __next__(self):
        if self._index < len(self.code_blocks):
            code_block = self.code_blocks[self._index]
            self._index += 1
            return code_block
        raise StopIteration
