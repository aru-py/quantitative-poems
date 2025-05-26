"""
utils.py
"""


class Writer:
    """
    Base class for writers.
    """

    def __init__(self, model=None):
        self.model = model

    def write(self, args: str) -> str:
        raise NotImplementedError
