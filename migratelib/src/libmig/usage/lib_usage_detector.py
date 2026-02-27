import ast
from _ast import Import, ImportFrom
from pathlib import Path
from typing import Generator

from libmig.usage.lib_usage import LibUsage


class GenericImport:
    """
    There are two main ways to import modules in python.
    Using 'import x' and using 'from x import y'.
    The ast library provides different representation of the two types of import statement.
    This class encapsulates them into one generic type to reduce duplicate in our code.
    """

    def __init__(self, import_name: str, api_name: str, alias: str, statement: Import | ImportFrom):
        self.import_name = import_name or "."
        self.api_name = api_name
        self.alias = alias or api_name
        self.statement = statement

    @classmethod
    def from_import(cls, statement: Import):
        return [cls(name.name, name.name, name.asname, statement) for name in statement.names]

    @classmethod
    def from_import_from(cls, statement: ImportFrom):
        return [cls(statement.module, name.name, name.asname, statement) for name in statement.names]

    def resolves(self, import_name):
        # the or is for imports like from a.b import c.
        return self.import_name == import_name or self.import_name.startswith(f"{import_name}.")

    def is_direct_lib_import(self):
        # example: import os, we store it as import_name=os, api_name=os, alias=os
        return self.import_name == self.api_name == self.alias

    def standardize(self, exclude_alias=False):
        if exclude_alias:
            return f"from {self.import_name} import {self.api_name}"
        return f"from {self.import_name} import {self.api_name} as {self.alias}"

    def __repr__(self):
        return self.standardize()

    def __str__(self):
        return self.standardize()

    def __eq__(self, other):
        return self.standardize() == other.standardize()

    def __hash__(self):
        return hash(self.standardize())


def _get_imports(root_node) -> list[GenericImport]:
    imports = []

    for node in ast.walk(root_node):
        if isinstance(node, ast.Import):
            imports += GenericImport.from_import(node)
        elif isinstance(node, ast.ImportFrom):
            imports += GenericImport.from_import_from(node)

    return imports


class LibUsageDetector:
    def __init__(self, code_path: Path, exclude_dirs: list[str], import_names: list[str]):
        assert code_path.exists(), f"Path {code_path.absolute().resolve()} does not exist."

        self.code_path = code_path
        self.exclude_dirs = set(exclude_dirs or [])
        self.import_names = import_names

    def detect(self) -> list[LibUsage]:
        py_files = list(self.code_path.rglob("*.py"))
        # keep the files which are not in any of the excluded directory
        py_files = [file for file in py_files if not any((part in self.exclude_dirs) for part in file.parts)]

        usages = []
        for file in py_files:
            usages += list(self._detect_for_file(file))

        return usages

    def _detect_for_file(self, file: Path) -> Generator[LibUsage, None, None]:
        code = file.read_text("utf-8")
        parsed = ast.parse(code, filename=file.as_posix())
        imports = _get_imports(parsed)
        for imp in imports:
            for import_name in self.import_names:
                if imp.resolves(import_name):
                    yield LibUsage(
                        file=file.relative_to(self.code_path).as_posix(),
                        line=imp.statement.lineno,
                        char=imp.statement.col_offset,
                        api=imp.api_name,
                        code=ast.unparse(imp.statement),
                    )
