from functools import partial

import typer
from ditk import logging
from ditk.config.meta import __VERSION__
from .generate import generate_annotated_doc, Lang

app = typer.Typer(help='Utils for creating annotation documentation.')

def print_version(module: str, value: bool) -> None:
    """
    Print version information of cli
    :param module: current module using this cli.
    :param value: value of current parameter
    """
    if not value:
        return  # pragma: no cover

    typer.echo(f'CLI for {module}, version {__VERSION__}')
    raise typer.Exit()

@app.callback()
def main(version: bool = typer.Option(False, '-v', '--version', is_eager=True, help="Show version information.")):
    if version:
        print_version('ditk.doc.annotated', True)

@app.command('create', help='Utils for creating annotation documentation from local code.')
def create(
    input_file: str = typer.Option(..., '-i', '--input_file', help='Input source code.'),
    output_file: str = typer.Option(..., '-o', '--output_file', help='Output annotated documentation code.'),
    assets_directory: str = typer.Option(None, '-A', '--assets_dir', help='Directory for assets file of this documentation.'),
    language: str = typer.Option(Lang.English.value, '-L', '--language', help='Language for documentation.', show_default=True),
    title: str = typer.Option('<Untitled Documentation>', '-T', '--title', help='Title of the documentation.', show_default=True)
):
    logging.try_init_root(logging.INFO)
    generate_annotated_doc(input_file, output_file, title, assets_directory, language)

if __name__ == '__main__':
    app()
