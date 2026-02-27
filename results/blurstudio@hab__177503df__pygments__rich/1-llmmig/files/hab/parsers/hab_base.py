import logging
import os
import subprocess
from pathlib import Path

import anytree
from colorama import Fore, Style
from jinja2 import Environment, FileSystemLoader
from packaging.version import Version
from rich.console import Console
from rich.syntax import Syntax

from .. import NotSet, utils
from ..errors import (
    DuplicateJsonError,
    HabError,
    InvalidAliasError,
    ReservedVariableNameError,
)
from ..formatter import Formatter
from ..site import MergeDict
from ..solvers import Solver
from .meta import HabMeta, hab_property

logger = logging.getLogger(__name__)

TEMPLATES = Path(__file__).parent.parent / "templates"


class HabBase(anytree.NodeMixin, metaclass=HabMeta):
    # ... (rest of the class remains unchanged)

    def print_script(self, filename, content):
        """Prints a header including the filename and content.

        Args:
            filename (pathlib.Path): The name of the file contents is to be
                written to.
            content (str): Shell script that is to be written to filename.
                If colorize is enabled, then syntax highlighting is applied
                based on filenames extension.
        """
        colorize = self.resolver.site.get("colorize", True)
        console = Console()

        # Print the name of the script being printed
        if colorize:
            header = f"{Fore.GREEN}-- Script: {filename} --{Fore.RESET}"
        else:
            header = f"-- Script: {filename} --"
        print(header)

        # Highlight and print the script contents using rich
        if colorize:
            syntax = Syntax(content, lexer=filename.suffix.lstrip("."), theme="monokai", word_wrap=True)
            console.print(syntax)
        else:
            print(content)
