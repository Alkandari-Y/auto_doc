#!/usr/bin/env python3
import os
import sys
import subprocess

from core.app import App
from parsers.cli_parser import cli_parser


def main() -> None:
    args, parser = cli_parser()

    if args.command:
        raise NotImplemented('Not fully developed')
        process = subprocess.Popen(
            args.command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, stderr = process.communicate()


        if stderr and process.returncode != 0:
            print("Command error output:")
            print(stderr.decode())
            print("Command failed with exit code", process.returncode)
        else:
            sys.exit(1)

    elif not args.target_file_name and not args.target_dir_name:
        print("Invalid arguments")
        parser.print_help()
        sys.exit(1)

    if args.target_dir_name and not os.path.isdir(args.target_dir_name):
        print("Invalid directory path")
        sys.exit(1)
    elif args.target_file_name and not os.path.isfile(args.target_file_name):
        print("Invalid file path")
        sys.exit(1)

    app = App(**vars(args))
    app.run()


if __name__ == "__main__":
    main()

# TODO:
# - Use the dataclasses to record metadata
# - Add method within code blocks to include docstring class
#  (or variants, like a python specific one)
# - Refactor CodeBlock methods for generating docstring
# - Refactor DocString methods
# - Improve properties for Docstring like naming
# - Improve properties for CodeBlock like naming and more meta
# - Add Create A class module for code blocks (optional)
# - Add dependencies for Codeblock (graph nodes)
# - Improve prompt
# - Code split PyParser methods
# - Utilize Poetry as package manager
# - Add Logger
# - Create environment list per script file (add classes and functions)
