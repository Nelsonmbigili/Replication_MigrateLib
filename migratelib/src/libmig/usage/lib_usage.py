from dataclasses import dataclass


@dataclass
class LibUsage:
    """
    Represents a usage of a library in a Python file.
    :arg file: The path to the file where the usage is found, relative to the project root.
    :arg line: The line number where the usage is found. 1-indexed.
    :arg char: The character number where the usage is found. 0-indexed.
    :arg api: The API of the library that is used.
    :arg code: The code statement that uses the library.

    Note that the line is 1-indexed, while the char is 0-indexed.
    This is how the ast module represents them, so we keep it consistent.
    """
    file: str
    line: int
    char: int
    api: str
    code: str
