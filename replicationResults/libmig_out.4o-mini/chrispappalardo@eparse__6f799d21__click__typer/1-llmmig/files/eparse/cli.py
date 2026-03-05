# -*- coding: utf-8 -*-

"""
excel parser cli module
"""

import sys
from collections.abc import Iterable
from pathlib import Path
from pprint import PrettyPrinter

import typer
import pandas as pd

from .core import (
    df_find_tables,
    df_normalize_data,
    df_serialize_table,
    get_df_from_file,
)
from .interfaces import ExcelParse, i_factory

app = typer.Typer()

def handle(e, exceptions=None, msg=None, debug=False, exit=True):
    """
    handle exceptions based on settings
    """

    if msg is None:
        msg = f"an error occurred - {e}"

    if exceptions and not isinstance(exceptions, Iterable):
        exceptions = [exceptions]

    if exceptions is None or type(e) in exceptions:
        print(msg)

        if debug:
            raise e
        elif exit:
            sys.exit(1)

@app.command()
def main(
    input: str = typer.Option("null:///", "--input", "-i", help="input source"),
    output: str = typer.Option("null:///", "--output", "-o", help="output destination"),
    file: list[str] = typer.Option(..., "--file", "-f", help="file(s) or dir(s) to target"),
    debug: bool = typer.Option(False, "--debug", "-d", help="use debug mode"),
    loose: bool = typer.Option(True, "--loose", "-l", help="find tables loosely"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="find files recursively"),
    truncate: bool = typer.Option(True, "--truncate", "-t", help="truncate dataframe output"),
    verbose: int = typer.Option(0, "--verbose", "-v", help="increase output verbosity"),
):
    """
    excel parser
    """

    files = []

    # get target file(s)
    for i in file:
        if Path(i).is_dir():
            g = "**/*" if recursive else "*"
            files += Path(i).glob(g)
        elif Path(i).is_file():
            files.append(Path(i))

    if verbose:
        print(f"found {len(files)} files")

    # get input and output objects
    for t in ("input", "output"):
        try:
            obj = i_factory(locals()[t], ExcelParse)
            locals()[f"{t}_obj"] = obj
        except ValueError as e:
            handle(e, msg=f"{t} error - {e}", debug=debug)

    # set truncate option
    if not truncate:
        pd.set_option("display.max_rows", None)

@app.command()
def scan(
    number: int = typer.Option(None, "--number", "-n", help="stop after n excel files"),
    sheet: str = typer.Option(None, "--sheet", "-s", help="name of sheet to scan for"),
    tables: bool = typer.Option(False, "--tables", "-t", help="count tables in scanned sheets"),
):
    """
    scan for excel files in target
    """

    if debug:
        PrettyPrinter().pprint(locals())

    # process each Excel file in files
    for i, f in enumerate(files):
        if f.is_file() and "xls" in f.name:
            try:
                e_file = pd.read_excel(
                    f,
                    sheet_name=sheet,
                    header=None,
                    index_col=None,
                )
            except Exception as e:
                msg = f"skipping {f} - {e}"
                handle(e, msg=msg, debug=debug, exit=False)
                continue

            # get basic info about Excel file
            f_size_mb = f.stat().st_size / 1_024_000
            sheets = []

            if type(e_file) is dict:
                sheets = e_file.keys()

            # build output result based on options selected
            result = f"{f.name}"

            if verbose:
                result += f" {f_size_mb:.2f}MB"

            if sheet is not None:
                result += f" with {sheet} {e_file.shape}"

                if tables:
                    t = df_find_tables(e_file, locals()["loose"])
                    result += f" containing {len(t)} tables"

                    if verbose > 1:
                        result += f" ({t})"

            else:
                if verbose:
                    result += f" with {len(sheets)} sheets"

                if verbose > 1 and len(sheets):
                    result += f' {",".join(sheets)}'

            # print result
            print(result)

            if debug:
                PrettyPrinter().pprint(e_file)

            # continue if number has not been reached
            if number is not None and i >= number:
                break

@app.command()
def parse(
    sheet: list[str] = typer.Option(..., "--sheet", "-s", help="name of sheet(s) to parse"),
    serialize: bool = typer.Option(False, "--serialize", "-z", help="serialize table output"),
    table: str = typer.Option(None, "--table", "-t", help="name of table to parse"),
    nacount: int = typer.Option(0, help="allow for this many NA values when spanning rows and columns"),
):
    """
    parse table(s) found in sheet for target(s)
    """

    if debug:
        PrettyPrinter().pprint(locals())

    for f in files:
        if f.is_file() and "xls" in f.name:
            print(f"{f.name}")

            try:
                for (
                    output,
                    excel_RC,
                    name,
                    s,
                ) in get_df_from_file(
                    f,
                    locals()["loose"],
                    sheet,
                    table,
                    nacount + 1,
                    nacount + 1,
                ):
                    if verbose:
                        m = "{} table {} {} found at {} in {}"
                        v = (f.name, name, output.shape, excel_RC, s)
                        print(m.format(*v))

                    if serialize:
                        output = df_serialize_table(
                            output,
                            name=name,
                            sheet=s,
                            f_name=f.name,
                        )

                    if debug:
                        PrettyPrinter().pprint(output)

                    try:
                        locals()["output_obj"].output(output, locals())
                    except Exception as e:
                        msg = f'output to {locals()["output"]} failed - {e}'
                        handle(e, msg=msg, debug=debug, exit=False)
                        break

            except Exception as e:
                msg = f"skipping {f} - {e}"
                handle(e, msg=msg, debug=debug, exit=False)
                continue

@app.command()
def query(
    filter: list[tuple[str, str]] = typer.Option(..., "--filter", "-f", nargs=2, help="django-style filter(s) to apply to base queryset"),
    method: str = typer.Option("get_queryset", "--method", "-m", help="method to call on eparse model"),
    serialize: bool = typer.Option(False, "--serialize", "-z", help="serialize query output"),
):
    """
    query eparse output
    """

    if debug:
        PrettyPrinter().pprint(locals())

    # input data
    try:
        data = locals()["input_obj"].input(method, **{k: v for k, v in filter})
    except Exception as e:
        msg = f'input from {locals()["input"]} failed with {e}'
        handle(e, msg=msg, debug=debug)

    if serialize:
        try:
            data = [df_normalize_data(d) for d in data.to_dict("records")]
        except Exception as e:
            msg = "serialization error (some methods can't be serialized)"
            handle(e, msg=f"{msg} - {e}", debug=debug)

    # output data
    try:
        locals()["output_obj"].output(data, locals())
    except Exception as e:
        msg = f'output to {locals()["output"]} failed with {e}'
        handle(e, msg=msg, debug=debug)

@app.command()
def migrate(
    migration: list[str] = typer.Option(..., "--migration", "-m", required=True, help="database migration(s) to apply"),
):
    """
    migrate eparse table
    """

    if debug:
        PrettyPrinter().pprint(locals())

    # apply migrations
    for _migration in migration:
        try:
            locals()["input_obj"].migrate(_migration)
            print(f"applied {_migration}")
        except Exception as e:
            handle(e, msg=f"migration error - {e}", debug=debug)

def entry_point():
    """
    required to make setuptools and click play nicely (context object)
    """

    app()

if __name__ == "__main__":
    entry_point()
