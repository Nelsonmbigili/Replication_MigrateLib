# -*- coding: utf-8 -*-

"""
excel parser cli module
"""

import sys
from collections.abc import Iterable
from pathlib import Path
from pprint import PrettyPrinter

import plac
import pandas as pd

from .core import (
    df_find_tables,
    df_normalize_data,
    df_serialize_table,
    get_df_from_file,
)
from .interfaces import ExcelParse, i_factory


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


def main(
    input: ("Input source", str) = "null:///",
    output: ("Output destination", str) = "null:///",
    file: ("File(s) or dir(s) to target", str) = None,
    debug: ("Use debug mode", bool) = False,
    loose: ("Find tables loosely", bool) = True,
    recursive: ("Find files recursively", bool) = False,
    truncate: ("Truncate dataframe output", bool) = True,
    verbose: ("Increase output verbosity", int) = 0,
):
    """
    excel parser
    """
    ctx = {
        "input": input,
        "output": output,
        "file": file,
        "debug": debug,
        "loose": loose,
        "recursive": recursive,
        "truncate": truncate,
        "verbose": verbose,
    }

    files = []

    # get target file(s)
    if file:
        for i in file.split(","):
            if Path(i).is_dir():
                g = "**/*" if recursive else "*"
                files += Path(i).glob(g)
            elif Path(i).is_file():
                files.append(Path(i))

    ctx["files"] = files

    if verbose:
        print(f"found {len(files)} files")

    # get input and output objects
    for t in ("input", "output"):
        try:
            ctx[f"{t}_obj"] = i_factory(ctx[t], ExcelParse)
        except ValueError as e:
            handle(e, msg=f"{t} error - {e}", debug=debug)

    # set truncate option
    if not truncate:
        pd.set_option("display.max_rows", None)

    return ctx


@plac.annotations(
    number=("Stop after n excel files", int, "n", None),
    sheet=("Name of sheet to scan for", str, "s", None),
    tables=("Count tables in scanned sheets", bool, "t", None),
)
def scan(ctx, number=None, sheet=None, tables=False):
    """
    scan for excel files in target
    """

    ctx["number"] = number
    ctx["sheet"] = sheet
    ctx["tables"] = tables

    if ctx["debug"]:
        PrettyPrinter().pprint(ctx)

    # process each Excel file in files
    for i, f in enumerate(ctx["files"]):
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
                handle(e, msg=msg, debug=ctx["debug"], exit=False)
                continue

            # get basic info about Excel file
            f_size_mb = f.stat().st_size / 1_024_000
            sheets = []

            if type(e_file) is dict:
                sheets = e_file.keys()

            # build output result based on options selected
            result = f"{f.name}"

            if ctx["verbose"]:
                result += f" {f_size_mb:.2f}MB"

            if sheet is not None:
                result += f" with {sheet} {e_file.shape}"

                if tables:
                    t = df_find_tables(e_file, ctx["loose"])
                    result += f" containing {len(t)} tables"

                    if ctx["verbose"] > 1:
                        result += f" ({t})"

            else:
                if ctx["verbose"]:
                    result += f" with {len(sheets)} sheets"

                if ctx["verbose"] > 1 and len(sheets):
                    result += f' {",".join(sheets)}'

            # print result
            print(result)

            if ctx["debug"]:
                PrettyPrinter().pprint(e_file)

            # continue if number has not been reached
            if number is not None and i >= number:
                break


@plac.annotations(
    sheet=("Name of sheet(s) to parse", str, "s", None),
    serialize=("Serialize table output", bool, "z", None),
    table=("Name of table to parse", str, "t", None),
    nacount=("Allow for this many NA values when spanning rows and columns", int, None),
)
def parse(ctx, sheet=None, serialize=False, table=None, nacount=0):
    """
    parse table(s) found in sheet for target(s)
    """

    ctx["sheet"] = sheet
    ctx["serialize"] = serialize
    ctx["table"] = table
    ctx["na_tolerance_r"] = nacount + 1
    ctx["na_tolerance_c"] = nacount + 1

    if ctx["debug"]:
        PrettyPrinter().pprint(ctx)

    for f in ctx["files"]:
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
                    ctx["loose"],
                    sheet,
                    table,
                    ctx["na_tolerance_r"],
                    ctx["na_tolerance_c"],
                ):
                    if ctx["verbose"]:
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

                    if ctx["debug"]:
                        PrettyPrinter().pprint(output)

                    try:
                        ctx["output_obj"].output(output, ctx)
                    except Exception as e:
                        msg = f'output to {ctx["output"]} failed - {e}'
                        handle(e, msg=msg, debug=ctx["debug"], exit=False)
                        break

            except Exception as e:
                msg = f"skipping {f} - {e}"
                handle(e, msg=msg, debug=ctx["debug"], exit=False)
                continue


def entry_point():
    """
    required to make plac work as the entry point
    """
    plac.call(main)


if __name__ == "__main__":
    entry_point()
