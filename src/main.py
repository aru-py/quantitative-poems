import fire
from rich import print

from book import Book
from page import PoemWriter as Page

page = Page()
book = Book(writer=page)

if __name__ == '__main__':
    fire.Fire({
        "book": book,
        "page": page,
    }, serialize=lambda s: print(s) if s else None)
