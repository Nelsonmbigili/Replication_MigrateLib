from functools import partial

import plac
from ditk import logging
from ditk.config.meta import __VERSION__
from .generate import generate_annotated_doc, Lang


def print_version(module, value):
    """
    Print version information of cli
    :param module: current module using this cli.
    :param value: value of current parameter
    """
    if not value:
        return  # pragma: no cover

    print(f'CLI for {module}, version {__VERSION__}')


@plac.annotations(
    version=('Show version information.', 'flag', 'v'),
)
def cli(version=False):
    if version:
        print_version('ditk.doc.annotated', True)
    plac.call(main)


@plac.annotations(
    input_file=('Input source code.', 'option', 'i', str),
    output_file=('Output annotated documentation code.', 'option', 'o', str),
    assets_directory=('Directory for assets file of this documentation.', 'option', 'A', str),
    language=('Language for documentation.', 'option', 'L', str, Lang.English.value),
    title=('Title of the documentation.', 'option', 'T', str, '<Untitled Documentation>'),
)
def main(input_file, output_file, assets_directory=None, language=Lang.English.value, title='<Untitled Documentation>'):
    logging.try_init_root(logging.INFO)
    generate_annotated_doc(input_file, output_file, title, assets_directory, language)


if __name__ == '__main__':
    plac.call(cli)
