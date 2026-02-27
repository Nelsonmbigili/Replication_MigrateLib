from functools import partial

import typer
from typer import Context, Option

from ditk import logging
from ditk.config.meta import __VERSION__
from .generate import generate_annotated_doc, Lang

app = typer.Typer(
    help="Utils for creating annotation documentation."
)


def print_version(module: str, ctx: Context, value: bool) -> None:
    """
    Print version information of cli
    :param module: current module using this cli.
    :param ctx: typer context
    :param value: value of current parameter
    """
    if not value:
        return  # pragma: no cover

    typer.echo(f"CLI for {module}, version {__VERSION__}")
    raise typer.Exit()


@app.callback()
def main(
    version: bool = Option(
        None,
        "--version",
        "-v",
        is_flag=True,
        callback=partial(print_version, "ditk.doc.annotated"),
        is_eager=True,
        help="Show version information.",
    )
):
    pass


@app.command(
    "create",
    help="Utils for creating annotation documentation from local code.",
)
def create(
    input_file: typer.FileText = typer.Option(
        ..., "--input_file", "-i", help="Input source code."
    ),
    output_file: str = typer.Option(
        ..., "--output_file", "-o", help="Output annotated documentation code."
    ),
    assets_directory: str = typer.Option(
        None,
        "--assets_dir",
        "-A",
        help="Directory for assets file of this documentation.",
    ),
    language: Lang = typer.Option(
        Lang.English.value,
        "--language",
        "-L",
        case_sensitive=False,
        help="Language for documentation.",
        show_default=True,
    ),
    title: str = typer.Option(
        "<Untitled Documentation>",
        "--title",
        "-T",
        help="Title of the documentation.",
        show_default=True,
    ),
):
    logging.try_init_root(logging.INFO)
    generate_annotated_doc(input_file.name, output_file, title, assets_directory, language)


if __name__ == "__main__":
    app()
