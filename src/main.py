"""
main.py
"""

import importlib
from subprocess import run

import fire
from rich import print

from book import Book
from config import writer_name, Paths

page = importlib.import_module(f"writers.{writer_name}").writer
book = Book(writer=page)


def format_tex():
    """
    Format LaTeX files using latexindent.
    """
    return run(f"latexindent -w {Paths.content_dir / '*.tex'}", shell=True)


def format_py():
    """
    Format Python files using black.
    """
    src = Paths.root_dir / "src"
    suffix = "*.py"
    return run(f"black {src / suffix} {src / 'writers' / suffix}", shell=True)


if __name__ == "__main__":
    fire.Fire(serialize=lambda s: print(s) if s else None)
