from typing import Tuple
import argparse


def cli_parser() -> Tuple[argparse.Namespace, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser(description="Ai Documentation Helper.")
    parser.add_argument(
        "-D",
        dest="target_dir_name",
        type=str,
        required=False,
        help="Specify a directory",
    )
    parser.add_argument(
        "-T",
        dest="num_workers",
        type=int,
        required=False,
        default=4,
        help="Specify max number of workers",
    )
    parser.add_argument(
        "--r",
        dest="replace_docs",
        action="store_true",
        help="Replace or updated docs",
    )
    parser.add_argument(
        "-F",
        dest="target_file_name",
        type=str,
        required=False,
        help="Specify a filename",
    )
    parser.add_argument(
        "-R",
        dest="remove_docs",
        action="store_true",
        help="Remove all documentation in file",
    )
    parser.add_argument(
        "--cmd",
        dest="command",
        type=str,
        required=False,
        help="Specify a command to run and capture errors from",
    )

    args = parser.parse_args()

    return (args, parser)
