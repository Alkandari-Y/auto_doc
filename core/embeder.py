from typing import List
import fileinput
import sys

from models.blocks import CodeBlock
from client.service import AiClient


class DocstringManager:
    def __init__(
        self, client: AiClient,
        code_blocks: List[CodeBlock]
    ) -> None:
        self.client = client
        self.code_blocks = code_blocks


    def _is_line_in_ranges(self, line_number) -> bool:
        for node in self.code_blocks:
            if node.doc_string is None:
                return False
            position = node.doc_string.position
            if position.body_start + 1 <= line_number <= position.body_end:
                return True
        return False

    def remove_doc_strings(self) -> None:
        with fileinput.input(files=[self.file_name], inplace=True, mode='r') as file:
            for line in file:
                line_number = fileinput.filelineno()
                if not self._is_line_in_ranges(line_number):
                    sys.stdout.write(line)
