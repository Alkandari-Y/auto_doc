import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Type

from core import settings
from parsers.base_parser import Parser
from parsers.py_parser import PythonParser

shared_resource_lock = Lock()


class App:
    def __init__(self, **kwargs) -> None:
        self.target_dir_name = kwargs.get("target_dir_name")
        self.num_workers = kwargs.get("num_workers", settings.WORKER_COUNT)
        self.target_file_name = kwargs.get("target_file_name")
        self.replace_docs = kwargs.get("replace_docs")
        self.remove_docs = kwargs.get("remove_docs")

    def _get_language_type(self, file_name: str) -> str | None:
        _, extension = os.path.splitext(file_name)
        language = None
        if extension in [".py"]:
            language = "python"
        else:
            print("Unsupported file type")
        return language

    def _get_parser_for_language(self, language: str) -> Type[Parser]:
        parsers: dict[str, type[Parser]] = {"python": PythonParser}
        if language not in parsers:
            raise ValueError("Unsupported language")
        return parsers[language]

    def process_file(self, file_path: str) -> None:
        try:
            print(f"Processing file: {file_path}")
            language = self._get_language_type(file_path)

            if language is None:
                raise ValueError("Unsupported Language")

            f_parser = self._get_parser_for_language(language)(file_path)  # type: ignore

            with shared_resource_lock:
                f_parser.parse_file()
                if self.replace_docs or self.remove_docs:
                    f_parser.remove_doc_strings()
                if not self.remove_docs:
                    f_parser.embed_documentation()
                f_parser.write_to_file()

        except ValueError as e:
            print(f"Error processing file {file_path}: {e}")
            traceback.print_exc()

    def process_directory(self) -> None:
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            for root, dirs, files in os.walk(self.target_dir_name, topdown=True):
                dirs[:] = [d for d in dirs if d not in settings.IGNORED_DIRS_SET]
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        executor.submit(self.process_file, file_path)

    def run(self):
        if self.target_dir_name is not None:
            self.process_directory()
        elif self.target_file_name is not None:
            self.process_file(self.target_file_name)
        else:
            raise ValueError("invalid targets")
