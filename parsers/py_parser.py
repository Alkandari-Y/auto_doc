import ast
import re
from typing import List, Callable

from models.blocks import CodeBlock, DocString, Position, CodePosition
from parsers.base_parser import Parser


def dec_end_check(lines: List[str], line_num: int, check: str) -> bool:
    return lines[line_num].endswith(check)


def get_ast_doc_str(ast_code_block: ast.AST | ast.Module) -> str | None:
    return ast.get_docstring(ast_code_block)  # type: ignore


def check_ast_doc_str(ast_code_block: ast.AST) -> Callable[[], bool]:
    def has_docstring() -> bool:
        return get_ast_doc_str(ast_code_block) is not None

    return has_docstring


class PythonParser(Parser):
    AST_TYPES = {
        ast.FunctionDef: "function",
        ast.AsyncFunctionDef: "function",
        ast.ClassDef: "class",
        ast.Module: "module",
    }

    def __init__(self, file_name: str, module_doc: bool = False) -> None:
        super().__init__(file_name, "Python")
        self.allowed_doc_str_fmt = '"""'
        self.rep_doc_str_fmt = [
            '"""',
            "'''",
            "```",
        ]
        self.module_doc = module_doc

    @property
    def chars_skip(self) -> int:
        return len(self.allowed_doc_str_fmt)

    def parse_file(self) -> None:
        with open(self.file_name, "r+", encoding="utf8") as file:
            file_content = file.read()
            tree = ast.parse(file_content, filename=self.file_name)
            self.lines = file_content.splitlines(keepends=True)

        self._process_ast_tree(tree=tree, lines=self.lines)
        self.code_blocks.sort(
            key=lambda code_block: code_block.position.declaration_start
        )

    def embed_documentation(self) -> None:
        code_blocks = self.code_blocks[::-1]
        for code_block in code_blocks:
            if code_block.doc_string is not None:
                continue
            code_sample = "".join(
                self.lines[
                    code_block.position.declaration_start : code_block.position.body_end
                ]
            )
            doc_string = code_block.generate_docstring(
                code_sample,
                self.file_type,
                self.allowed_doc_str_fmt,
                self.rep_doc_str_fmt,
            )
            self.lines.insert(code_block.position.body_start, doc_string)
        # iterate over every code_block and check if they have a docstring or not
        # added/update relevant details for ensure positions of code blocks and
        # comments are accurate (could re-use existing logic, might need to code-split)
        super().embed_documentation()

    def remove_doc_strings(self) -> None:
        lines_removed = 0

        module_code_block_ref: None | CodeBlock = None
        for code_block in self.code_blocks:
            if code_block.obj_type == "module":
                module_code_block_ref = code_block

            code_block.position.declaration_start = (
                code_block.position.declaration_start - lines_removed
            )
            code_block.position.body_start = code_block.position.body_start - lines_removed  # type: ignore
            code_block.position.body_end = code_block.position.body_end - lines_removed

            if code_block.doc_string is None:
                continue

            doc_str_obj = code_block.doc_string
            if doc_str_obj.position is None:  # type: ignore
                print(
                    f"Error in removing docstring for {code_block.name} {self.file_name}"
                )
                break

            doc_start = doc_str_obj.position.body_start  # type: ignore
            doc_str_len = len(doc_str_obj)  # type: ignore
            code_block.position.body_end = code_block.position.body_end - doc_str_len

            cursor = doc_start - lines_removed
            if not self.lines[cursor].strip().startswith('"""'):
                print("Error removing", code_block.name)
                continue

            # refactor this to avoid loops
            for _ in range(doc_str_len, 0, -1):
                self.lines.pop(cursor)
                lines_removed += 1
            code_block.reset_doc_str()

        if module_code_block_ref is not None:
            module_code_block_ref.position.body_end = len(self.lines)

    def _process_ast_tree(self, tree: ast.AST, lines: List[str]) -> None:
        for ast_node in ast.walk(tree):
            if not isinstance(
                ast_node,
                tuple(PythonParser.AST_TYPES.keys()),
            ):
                continue

            if (ast_node_type := PythonParser.AST_TYPES[type(ast_node)]) == "module":
                setattr(ast_node, "name", self.file_name)
                ast_node.lineno = 0
                ast_node.end_lineno = len(lines)
            else:
                ast_node.end_lineno += 1  # type: ignore

            if ast_node.lineno is None or ast_node.end_lineno is None:
                print(f"Error Attempting to parse {self.file_name}")
                print(
                    f"""ast_node {ast_node.name} of type {
                        ast_node_type} does not contain start or endline"""
                )
                continue

            dec_start, body_start, end_line = self._get_code_block_pos(ast_node)
            indent_level = getattr(ast_node, "col_offset", 0)

            code_position = CodePosition(
                declaration_start=dec_start,
                indent_level=indent_level,
                body_start=body_start,
                body_end=end_line,
            )
            new_code_block = CodeBlock(
                ast_node.name, ast_node_type, code_position  # type: ignore
            )

            code_block_doc_string: str | None = (
                get_ast_doc_str(ast_node)
                if ast_node_type != "module"
                else get_ast_doc_str(tree)
            )
            if code_block_doc_string is not None:
                new_code_block.doc_string = DocString(
                    code_block_doc_string,
                    Position(
                        (
                            indent_level + 4
                            if ast_node_type != "module"
                            else indent_level
                        ),
                        *self._get_doc_str_index(new_code_block),
                    ),
                )

            self.code_blocks.append(new_code_block)

    def _get_code_block_pos(self, code_block: ast.AST) -> tuple[int, int, int]:
        if PythonParser.AST_TYPES[type(code_block)] == "module":
            pattern = re.compile(r"^#!.+")
            body_start: int | None = 1 if pattern.match(self.lines[0]) else 0
            return (code_block.lineno, body_start, code_block.end_lineno)  # type: ignore

        declaration_start = code_block.lineno - 1
        body_start = None
        end_line = code_block.end_lineno - 1  # type: ignore

        for index in range(declaration_start, end_line):
            if dec_end_check(self.lines, index, ":\n"):
                body_start = index + 1
                break
        if body_start is None:
            body_start = code_block.lineno

        return (declaration_start, body_start, end_line)

    def _get_doc_str_index(self, code_block: CodeBlock) -> tuple[int, int]:
        start_index, last_index = None, None
        for index in range(code_block.position.body_start, len(self.lines)):
            if start_index is None and self.lines[index].strip().startswith(
                self.allowed_doc_str_fmt
            ):
                start_index = index
            elif start_index is not None and self.lines[index].strip().startswith(
                self.allowed_doc_str_fmt
            ):
                last_index = index + 1
                break
        if start_index is None or last_index is None:
            raise ValueError(f'Unable to locate docstring for {code_block.name}')

        return (start_index, last_index)
