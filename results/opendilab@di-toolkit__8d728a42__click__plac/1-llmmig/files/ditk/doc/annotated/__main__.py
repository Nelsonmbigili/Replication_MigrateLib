from functools import partial
import plac
from pathlib import Path

from ditk import logging
from ditk.config.meta import __VERSION__
from .generate import generate_annotated_doc, Lang


def print_version(module: str):
    """
    Print version information of cli
    :param module: current module using this cli.
    """
    print(f'CLI for {module}, version {__VERSION__}')


def main(
    command: ("Command to execute", str),
    input_file: ("Input source code (required for 'create' command)", Path) = None,
    output_file: ("Output annotated documentation code (required for 'create' command)", Path) = None,
    assets_directory: ("Directory for assets file of this documentation", Path) = None,
    language: ("Language for documentation", str) = Lang.English.value,
    title: ("Title of the documentation", str) = '<Untitled Documentation>',
    version: ("Show version information", bool) = False,
):
    """
    Utils for creating annotation documentation.
    """
    if version:
        print_version('ditk.doc.annotated')
        return

    if command == 'create':
        if not input_file or not output_file:
            print("Error: 'create' command requires --input_file and --output_file.")
            return

        # Validate input_file exists
        if not input_file.exists():
            print(f"Error: Input file '{input_file}' does not exist.")
            return

        # Validate language
        if language not in Lang.__members__.values():
            print(f"Error: Invalid language '{language}'. Valid options are: {list(Lang.__members__.values())}")
            return

        logging.try_init_root(logging.INFO)
        generate_annotated_doc(str(input_file), str(output_file), title, str(assets_directory), language)
    else:
        print(f"Error: Unknown command '{command}'. Supported commands: create")


if __name__ == '__main__':
    plac.call(main)
