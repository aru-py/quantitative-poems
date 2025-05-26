import json
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor
from functools import cached_property
from pathlib import Path

from config import paths, tex_engine
from utils import Writer


class Book:

    def __init__(self, writer: Writer):
        self.writer = writer

    @cached_property
    def outline(self):
        """
        Returns the outline of all book pages.
        """
        with open(paths.outline_json, "r") as f:
            outline = json.load(f)
            return outline

    @staticmethod
    def _path_for_topic(idx, topic: str) -> Path:
        """
        Returns the path for the topic.
        """
        return paths.content_dir / "poems" / f"{idx:03d}_{topic}.tex"

    def build(self, **kwargs) -> None:
        """
        Builds the book by creating the outline and pages.
        """
        self.build_outline(**kwargs)
        self.build_pages(**kwargs)

    def build_outline(self, overwrite=False) -> None:
        """
        Builds `outline.tex` from the outline.json file.
        """

        outline_tex_path = paths.outline_tex

        # check if path exists
        if not overwrite and outline_tex_path.exists():
            logging.info(f"[yellow]Outline file {outline_tex_path} already exists. Skipping...[/yellow]")
            return

        output = []

        # create the outline.tex file
        topic_idx = 0
        for chapter, topics in self.outline.items():
            output.append(r"\part{%s}" % chapter)
            for topic in topics:
                topic_idx += 1
                page_path = self._path_for_topic(topic_idx, topic)
                relative_path = page_path.relative_to(paths.book_dir).with_suffix('')
                output.append(r"\input{%s}" % relative_path)

        # write the outline to the file
        with open(outline_tex_path, "w") as f:
            f.write("\n".join(output))

        logging.info(f"[green]Outline file {outline_tex_path} created.[/green]")

    def build_pages(self, overwrite=False, parallel=False):
        """
        Builds all pages from outline.
        """
        outline = self.outline
        topics = enumerate([topic for chapter in outline.values() for topic in chapter], 1)

        if parallel:
            with ThreadPoolExecutor(max_workers=5) as executor:
                executor.map(lambda args: self.build_page(*args, overwrite=overwrite),
                             topics)
                return None

        for idx, topic in topics:
            self.build_page(idx, topic, overwrite=overwrite)

        return None

    def build_page(self, idx, topic, overwrite=False) -> None:
        """
        Builds page for a given topic.
        """

        output_path = self._path_for_topic(idx, topic)

        if not overwrite and output_path.exists():
            logging.info(
                f"[{idx}] [gray]Page for [blue italic]{topic}[/blue italic] already exists. Skipping...[/gray]")
            return

        logging.info(f"[{idx}] [yellow]Writing page for [blue italic]{topic}[/blue italic]...[/yellow]")
        content = self.writer.write(topic)
        logging.info(f"[{idx}] [green]Finished page for [blue italic]{topic}[/blue italic].[/green]")
        with open(output_path, "w") as f:
            f.write(content)

    @staticmethod
    def compile(draft_mode=False, halt_on_error=True, quiet=False) -> subprocess.CompletedProcess:
        """
        Compiles the book using the specified TeX engine.
        """

        flags = []

        if draft_mode:
            flags.append("-draftmode")
        if halt_on_error:
            flags.append("-halt-on-error")
        if quiet:
            flags.append("-interaction=batchmode")

        out_dir = paths.out_dir
        book_dir = paths.book_dir
        index_tex = paths.index_tex
        cmd_args = [tex_engine, *flags, "-output-directory", str(out_dir), str(index_tex)]
        return subprocess.run(cmd_args, check=True, cwd=book_dir)

    @staticmethod
    def makeindex() -> subprocess.CompletedProcess:
        """
        Creates the index for the book.
        See https://www.overleaf.com/learn/latex/Indices.
        """
        index_idx = paths.index_idx.relative_to(paths.root_dir)
        cmd_args = ["makeindex", str(index_idx)]
        return subprocess.run(cmd_args, check=True)
