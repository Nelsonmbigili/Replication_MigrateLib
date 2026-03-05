### Explanation of Changes

To migrate the code from using the `click` library to the `typer` library, the following changes were made:

1. **Import Statement**: The import statement for `click` was replaced with `typer`.
2. **Command and Option Definitions**: The `@click.group()` and `@click.command()` decorators were replaced with `@typer.Typer()` and `@typer.app()` respectively. The `@click.option()` decorator was replaced with `typer.Option()`, and `@click.argument()` was replaced with `typer.Argument()`.
3. **Parameter Types**: The parameter types for options and arguments were adjusted to use `typer`'s built-in types, which are more straightforward.
4. **Context Management**: The context management for commands remains the same, but the way to handle command-line arguments and options is now more integrated with `typer`.
5. **Help Text**: The help text remains unchanged, but the way it is displayed is now handled by `typer`.

The overall structure of the code remains the same, but the decorators and types are now aligned with `typer`'s API.

### Modified Code

```python
# Copyright (c) 2013-2024, Andrea Zoppi
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -m hexrec` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``hexrec.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``hexrec.__main__`` in ``sys.modules``.

  Also see (1) from https://click.palletsprojects.com/en/5.x/setuptools/#setuptools-integration
"""

from typing import Callable
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Type
from typing import cast as _cast

import typer

from .__init__ import __version__
from .__init__ import file_types
from .base import BaseFile
from .base import guess_format_name
from .formats.srec import SrecFile
from .formats.srec import SrecRecord
from .hexdump import hexdump_core
from .utils import hexlify
from .utils import parse_int
from .utils import unhexlify
from .xxd import xxd_core


class BasedIntParamType(typer.ParamType):
    name = 'integer'

    def convert(self, value, param, ctx):
        try:
            return parse_int(value)
        except ValueError:
            self.fail(f'invalid integer: {value!r}', param, ctx)


class ByteIntParamType(typer.ParamType):
    name = 'byte'

    def convert(self, value, param, ctx):
        try:
            b = parse_int(value)
            if not 0 <= b <= 255:
                raise ValueError()
            return b
        except ValueError:
            self.fail(f'invalid byte: {value!r}', param, ctx)


class OrderedOptionsCommand(typer.main.Command):

    def parse_args(self, ctx, args):

        parser = self.make_parser(ctx)
        opts, _, order = parser.parse_args(args=list(args))
        ordered_options = [(param, opts[param.name]) for param in order]
        setattr(self, 'ordered_options', ordered_options)
        return super().parse_args(ctx, args)


BASED_INT = BasedIntParamType()
BYTE_INT = ByteIntParamType()

FILE_PATH_IN = typer.Path(dir_okay=False, allow_dash=True, readable=True, exists=True)
FILE_PATH_OUT = typer.Path(dir_okay=False, allow_dash=True, writable=True)

FORMAT_CHOICE = typer.Choice(list(sorted(file_types.keys())))

DATA_FMT_FORMATTERS: Mapping[str, Callable[[bytes], bytes]] = {
    'ascii': lambda b: b,
    'hex': lambda b: hexlify(b, upper=False),
    'HEX': lambda b: hexlify(b, upper=True),
    'hex.': lambda b: hexlify(b, sep=b'.', upper=False),
    'HEX.': lambda b: hexlify(b, sep=b'.', upper=True),
    'hex-': lambda b: hexlify(b, sep=b'-', upper=False),
    'HEX-': lambda b: hexlify(b, sep=b'-', upper=True),
    'hex:': lambda b: hexlify(b, sep=b':', upper=False),
    'HEX:': lambda b: hexlify(b, sep=b':', upper=True),
    'hex_': lambda b: hexlify(b, sep=b'_', upper=False),
    'HEX_': lambda b: hexlify(b, sep=b'_', upper=True),
    'hex ': lambda b: hexlify(b, sep=b' ', upper=False),
    'HEX ': lambda b: hexlify(b, sep=b' ', upper=True),
}

DATA_FMT_PARSERS: Mapping[str, Callable[[bytes], bytes]] = {
    'ascii': lambda b: b,
    'hex': lambda b: unhexlify(b),
    'HEX': lambda b: unhexlify(b),
    'hex.': lambda b: unhexlify(b, delete=b'.'),
    'HEX.': lambda b: unhexlify(b, delete=b'.'),
    'hex-': lambda b: unhexlify(b, delete=b'-'),
    'HEX-': lambda b: unhexlify(b, delete=b'-'),
    'hex:': lambda b: unhexlify(b, delete=b':'),
    'HEX:': lambda b: unhexlify(b, delete=b':'),
    'hex_': lambda b: unhexlify(b, delete=b'_'),
    'HEX_': lambda b: unhexlify(b, delete=b'_'),
    'hexs': lambda b: unhexlify(b, delete=b' \t'),
    'HEXs': lambda b: unhexlify(b, delete=b' \t'),
}

DATA_FMT_CHOICE = typer.Choice(list(DATA_FMT_FORMATTERS.keys()))


# ----------------------------------------------------------------------------

def guess_input_type(
    input_path: Optional[str],
    input_format: Optional[str] = None,
) -> Type[BaseFile]:

    if input_format:
        input_type = file_types[input_format]
    elif input_path is None or input_path == '-':
        raise ValueError('standard input requires input format')
    else:
        name = guess_format_name(input_path)
        input_type = file_types[name]
    return input_type


def guess_output_type(
    output_path: Optional[str],
    output_format: Optional[str],
    input_type: Optional[Type[BaseFile]] = None,
) -> Type[BaseFile]:

    if output_format:
        output_type = file_types[output_format]
    elif output_path is None or output_path == '-':
        output_type = input_type
    else:
        name = guess_format_name(output_path)
        output_type = file_types[name]
    return output_type


def print_version(ctx: typer.Context, value: bool):
    if not value or ctx.resilient_parsing:
        return

    typer.echo(str(__version__))
    raise typer.Exit()


def print_hexdump_version(ctx: typer.Context, value: bool):
    if not value or ctx.resilient_parsing:
        return

    typer.echo(f'hexdump from Python hexrec {__version__!s}')
    raise typer.Exit()


# ----------------------------------------------------------------------------

class SingleFileInOutCtxMgr:

    def __init__(
        self,
        input_path: str,
        input_format: Optional[str],
        output_path: str,
        output_format: Optional[str],
        output_width: Optional[int],
    ):

        if input_path == '-':
            input_path = None

        if not output_path:
            output_path = input_path
        if output_path == '-':
            output_path = None

        self.input_path: Optional[str] = input_path
        self.input_format: Optional[str] = input_format
        self.input_type: Optional[Type[BaseFile]] = None
        self.input_file: Optional[BaseFile] = None

        self.output_path: Optional[str] = output_path
        self.output_format: Optional[str] = output_format
        self.output_type: Optional[Type[BaseFile]] = None
        self.output_file: Optional[BaseFile] = None
        self.output_width: Optional[int] = output_width

    def __enter__(self) -> 'SingleFileInOutCtxMgr':

        self.input_type = guess_input_type(self.input_path, self.input_format)
        self.input_file = self.input_type.load(self.input_path)

        self.output_type = guess_output_type(self.output_path, self.output_format, self.input_type)

        if self.output_type is self.input_type:
            self.output_file = self.input_file
            self.output_file.apply_records()
        else:
            self.output_file = self.output_type.convert(self.input_file)

        if self.output_width is not None:
            self.output_file.maxdatalen = self.output_width

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:

        self.output_file.save(self.output_path)


class MultiFileInOutCtxMgr:

    def __init__(
        self,
        input_paths: Sequence[str],
        input_formats: Sequence[Optional[str]],
        output_path: str,
        output_format: Optional[str],
        output_width: Optional[int],
    ):

        input_paths = list(input_paths)
        for i, input_path in enumerate(input_paths):
            if input_path == '-':
                input_paths[i] = None

        if not output_path:
            output_path = input_paths[0]
        if output_path == '-':
            output_path = None

        self.input_paths: Sequence[Optional[str]] = input_paths
        self.input_formats: Sequence[Optional[str]] = input_formats
        self.input_types: List[Optional[Type[BaseFile]]] = [None] * len(self.input_paths)
        self.input_files: List[Optional[BaseFile]] = [None] * len(self.input_paths)

        self.output_path: Optional[str] = output_path
        self.output_format: Optional[str] = output_format
        self.output_type: Optional[Type[BaseFile]] = None
        self.output_file: Optional[BaseFile] = None
        self.output_width: Optional[int] = output_width

    def __enter__(self) -> 'MultiFileInOutCtxMgr':

        for i in range(len(self.input_paths)):
            self.input_types[i] = guess_input_type(self.input_paths[i], self.input_formats[i])
            self.input_files[i] = self.input_types[i].load(self.input_paths[i])

        self.output_type = guess_output_type(self.output_path, self.output_format, self.input_types[0])
        self.output_file = self.output_type()

        if self.output_width is not None:
            self.output_file.maxdatalen = self.output_width

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:

        self.output_file.save(self.output_path)


# ============================================================================

app = typer.Typer()


@app.command()
def main() -> None:
    """
    A set of command line utilities for common operations with record files.

    Being built with `Typer <https://typer.tiangolo.com/>`_, all the
    commands follow POSIX-like syntax rules, as well as reserving the virtual
    file path ``-`` for command chaining via standard output/input buffering.
    """


# ----------------------------------------------------------------------------

@app.command()
def align(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    modulo: int = typer.Option(4, '-m', '--modulo', show_default=True, help="""
        Alignment modulo.
    """),
    start: Optional[int] = typer.Option(None, '-s', '--start', help="""
        Inclusive start address. Negative values are referred to the end of the data.
        By default it applies from the start of the data contents.
    """),
    endex: Optional[int] = typer.Option(None, '-e', '--endex', help="""
        Exclusive end address. Negative values are referred to the end of the data.
        By default it applies till the end of the data contents.
    """),
    value: Optional[int] = typer.Option(0, '-v', '--value', show_default=True, help="""
        Byte value used to flood alignment padding.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Pads blocks to align their boundaries.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width) as ctx:
        ctx.output_file.align(modulo, start=start, endex=endex, pattern=value)


# ----------------------------------------------------------------------------

@app.command()
def clear(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    start: Optional[int] = typer.Option(None, '-s', '--start', help="""
        Inclusive start address. Negative values are referred to the end of the data.
        By default it applies from the start of the data contents.
    """),
    endex: Optional[int] = typer.Option(None, '-e', '--endex', help="""
        Exclusive end address. Negative values are referred to the end of the data.
        By default it applies till the end of the data contents.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Clears an address range.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width) as ctx:
        ctx.output_file.clear(start=start, endex=endex)


# ----------------------------------------------------------------------------

@app.command()
def convert(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:

    r"""Converts a file to another format.

    ``INFILE`` is the list of paths of the input files.
    Set to ``-`` to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width):
        pass


# ----------------------------------------------------------------------------

@app.command()
def crop(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    start: Optional[int] = typer.Option(None, '-s', '--start', help="""
        Inclusive start address. Negative values are referred to the end of the data.
        By default it applies from the start of the data contents.
    """),
    endex: Optional[int] = typer.Option(None, '-e', '--endex', help="""
        Exclusive end address. Negative values are referred to the end of the data.
        By default it applies till the end of the data contents.
    """),
    value: Optional[int] = typer.Option(None, '-v', '--value', help="""
        Byte value used to flood the address range.
        By default, no flood is performed.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Selects data from an address range.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width) as ctx:
        ctx.output_file.crop(start=start, endex=endex)

        if value is not None:
            ctx.output_file.flood(start=start, endex=endex, pattern=value)


# ----------------------------------------------------------------------------

@app.command()
def delete(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    start: Optional[int] = typer.Option(None, '-s', '--start', help="""
        Inclusive start address. Negative values are referred to the end of the data.
        By default it applies from the start of the data contents.
    """),
    endex: Optional[int] = typer.Option(None, '-e', '--endex', help="""
        Exclusive end address. Negative values are referred to the end of the data.
        By default it applies till the end of the data contents.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Deletes an address range.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width) as ctx:
        ctx.output_file.delete(start=start, endex=endex)


# ----------------------------------------------------------------------------

@app.command()
def fill(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    value: int = typer.Option(0, '-v', '--value', show_default=True, help="""
        Byte value used to fill the address range.
    """),
    start: Optional[int] = typer.Option(None, '-s', '--start', help="""
        Inclusive start address. Negative values are referred to the end of the data.
        By default it applies from the start of the data contents.
    """),
    endex: Optional[int] = typer.Option(None, '-e', '--endex', help="""
        Exclusive end address. Negative values are referred to the end of the data.
        By default it applies till the end of the data contents.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Fills an address range with a byte value.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width) as ctx:
        ctx.output_file.fill(start=start, endex=endex, pattern=value)


# ----------------------------------------------------------------------------

@app.command()
def flood(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    value: int = typer.Option(0, '-v', '--value', show_default=True, help="""
        Byte value used to flood the address range.
    """),
    start: Optional[int] = typer.Option(None, '-s', '--start', help="""
        Inclusive start address. Negative values are referred to the end of the data.
        By default it applies from the start of the data contents.
    """),
    endex: Optional[int] = typer.Option(None, '-e', '--endex', help="""
        Exclusive end address. Negative values are referred to the end of the data.
        By default it applies till the end of the data contents.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Fills emptiness of an address range with a byte value.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width) as ctx:
        ctx.output_file.flood(start=start, endex=endex, pattern=value)


# ----------------------------------------------------------------------------

@app.command(cls=OrderedOptionsCommand)
def hexdump(
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    one_byte_octal: Sequence[bool] = typer.Option(False, '-b', '--one-byte-octal', is_flag=True,
              help="""
    One-byte octal display. Display the input offset in
    hexadecimal, followed by sixteen space-separated,
    three-column, zero-filled bytes of input data, in octal, per
    line.
"""),
    one_byte_hex: Sequence[bool] = typer.Option(False, '-X', '--one-byte-hex', is_flag=True,
              help="""
    One-byte hexadecimal display. Display the input offset in
    hexadecimal, followed by sixteen space-separated, two-column,
    zero-filled bytes of input data, in hexadecimal, per line.
"""),
    one_byte_char: Sequence[bool] = typer.Option(False, '-c', '--one-byte-char', is_flag=True,
              help="""
    One-byte character display. Display the input offset in
    hexadecimal, followed by sixteen space-separated,
    three-column, space-filled characters of input data per line.
"""),
    canonical: Sequence[bool] = typer.Option(False, '-C', '--canonical', is_flag=True,
              help="""
    Canonical hex+ASCII display. Display the input offset in
    hexadecimal, followed by sixteen space-separated, two-column,
    hexadecimal bytes, followed by the same sixteen bytes in %_p
    format enclosed in | characters. Invoking the program as hd
    implies this option.
"""),
    two_bytes_decimal: Sequence[bool] = typer.Option(False, '-d', '--two-bytes-decimal', is_flag=True,
              help="""
    Two-byte decimal display. Display the input offset in
    hexadecimal, followed by eight space-separated, five-column,
    zero-filled, two-byte units of input data, in unsigned
    decimal, per line.
"""),
    two_bytes_octal: Sequence[bool] = typer.Option(False, '-o', '--two-bytes-octal', is_flag=True,
              help="""
    Two-byte octal display. Display the input offset in
    hexadecimal, followed by eight space-separated, six-column,
    zero-filled, two-byte quantities of input data, in octal, per
    line.
"""),
    two_bytes_hex: Sequence[bool] = typer.Option(False, '-x', '--two-bytes-hex', is_flag=True,
              help="""
    Two-byte hexadecimal display. Display the input offset in
    hexadecimal, followed by eight space-separated, four-column,
    zero-filled, two-byte quantities of input data, in
    hexadecimal, per line.
"""),
    length: Optional[int] = typer.Option(None, '-n', '--length', help="""
    Interpret only length bytes of input.
"""),
    skip: Optional[int] = typer.Option(None, '-s', '--skip', help="""
    Skip offset bytes from the beginning of the input.
"""),
    no_squeezing: bool = typer.Option(False, '-v', '--no_squeezing', is_flag=True, help="""
    The -v option causes hexdump to display all input data.
    Without the -v option, any number of groups of output lines
    which would be identical to the immediately preceding group
    of output lines (except for the input offsets), are replaced
    with a line comprised of a single asterisk.
"""),
    upper: bool = typer.Option(False, '-U', '--upper', is_flag=True, help="""
    Uses upper case hex letters on address and data.
"""),
    input_format: Optional[str] = typer.Option(None, '-I', '--input-format', help="""
    Forces the input file format.
"""),
    version: bool = typer.Option(False, '-V', '--version', is_flag=True, is_eager=True,
              help="""
    Print version and exit.
"""),
) -> None:
    r"""Display file contents in hexadecimal, decimal, octal, or ascii.

    The hexdump utility is a filter which displays the specified
    files, or standard input if no files are specified, in a
    user-specified format.

    Below, the length and offset arguments may be followed by the
    multiplicative suffixes KiB (=1024), MiB (=1024*1024), and so on
    for GiB, TiB, PiB, EiB, ZiB and YiB (the "iB" is optional, e.g.,
    "K" has the same meaning as "KiB"), or the suffixes KB (=1000),
    MB (=1000*1000), and so on for GB, TB, PB, EB, ZB and YB.

    For each input file, hexdump sequentially copies the input to
    standard output, transforming the data according to the format
    strings specified by the -e and -f options, in the order that
    they were specified.
    """

    kwargs = {
        'one_byte_octal': any(one_byte_octal),
        'one_byte_hex': any(one_byte_hex),
        'one_byte_char': any(one_byte_char),
        'canonical': any(canonical),
        'two_bytes_decimal': any(two_bytes_decimal),
        'two_bytes_octal': any(two_bytes_octal),
        'two_bytes_hex': any(two_bytes_hex),
    }
    format_order = [param.name
                    for param, value in hexdump.ordered_options
                    if (param.name in kwargs) and value]

    if input_format:
        input_type = guess_input_type(infile, input_format)
        input_file = input_type.load(infile)
        infile = input_file.memory

    hexdump_core(
        infile=infile,
        length=length,
        skip=skip,
        no_squeezing=no_squeezing,
        upper=upper,
        format_order=format_order,
        **kwargs,
    )


# ----------------------------------------------------------------------------

@app.command(cls=OrderedOptionsCommand)
def hd(
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    one_byte_octal: Sequence[bool] = typer.Option(False, '-b', '--one-byte-octal', is_flag=True,
              help="""
    One-byte octal display. Display the input offset in
    hexadecimal, followed by sixteen space-separated,
    three-column, zero-filled bytes of input data, in octal, per
    line.
"""),
    one_byte_hex: Sequence[bool] = typer.Option(False, '-X', '--one-byte-hex', is_flag=True,
              help="""
    One-byte hexadecimal display. Display the input offset in
    hexadecimal, followed by sixteen space-separated, two-column,
    zero-filled bytes of input data, in hexadecimal, per line.
"""),
    one_byte_char: Sequence[bool] = typer.Option(False, '-c', '--one-byte-char', is_flag=True,
              help="""
    One-byte character display. Display the input offset in
    hexadecimal, followed by sixteen space-separated,
    three-column, space-filled characters of input data per line.
"""),
    two_bytes_decimal: Sequence[bool] = typer.Option(False, '-d', '--two-bytes-decimal', is_flag=True,
              help="""
    Two-byte decimal display. Display the input offset in
    hexadecimal, followed by eight space-separated, five-column,
    zero-filled, two-byte units of input data, in unsigned
    decimal, per line.
"""),
    two_bytes_octal: Sequence[bool] = typer.Option(False, '-o', '--two-bytes-octal', is_flag=True,
              help="""
    Two-byte octal display. Display the input offset in
    hexadecimal, followed by eight space-separated, six-column,
    zero-filled, two-byte quantities of input data, in octal, per
    line.
"""),
    two_bytes_hex: Sequence[bool] = typer.Option(False, '-x', '--two-bytes-hex', is_flag=True,
              help="""
    Two-byte hexadecimal display. Display the input offset in
    hexadecimal, followed by eight space-separated, four-column,
    zero-filled, two-byte quantities of input data, in
    hexadecimal, per line.
"""),
    length: Optional[int] = typer.Option(None, '-n', '--length', help="""
    Interpret only length bytes of input.
"""),
    skip: Optional[int] = typer.Option(None, '-s', '--skip', help="""
    Skip offset bytes from the beginning of the input.
"""),
    no_squeezing: bool = typer.Option(False, '-v', '--no_squeezing', is_flag=True, help="""
    The -v option causes hexdump to display all input data.
    Without the -v option, any number of groups of output lines
    which would be identical to the immediately preceding group
    of output lines (except for the input offsets), are replaced
    with a line comprised of a single asterisk.
"""),
    upper: bool = typer.Option(False, '-U', '--upper', is_flag=True, help="""
    Uses upper case hex letters on address and data.
"""),
    input_format: Optional[str] = typer.Option(None, '-I', '--input-format', help="""
    Forces the input file format.
"""),
) -> None:
    r"""Display file contents in hexadecimal, decimal, octal, or ascii.

    The hexdump utility is a filter which displays the specified
    files, or standard input if no files are specified, in a
    user-specified format.

    Below, the length and offset arguments may be followed by the
    multiplicative suffixes KiB (=1024), MiB (=1024*1024), and so on
    for GiB, TiB, PiB, EiB, ZiB and YiB (the "iB" is optional, e.g.,
    "K" has the same meaning as "KiB"), or the suffixes KB (=1000),
    MB (=1000*1000), and so on for GB, TB, PB, EB, ZB and YB.

    For each input file, hexdump sequentially copies the input to
    standard output, transforming the data according to the format
    strings specified by the -e and -f options, in the order that
    they were specified.
    """

    kwargs = {
        'one_byte_octal': any(one_byte_octal),
        'one_byte_hex': any(one_byte_hex),
        'one_byte_char': any(one_byte_char),
        'two_bytes_decimal': any(two_bytes_decimal),
        'two_bytes_octal': any(two_bytes_octal),
        'two_bytes_hex': any(two_bytes_hex),
    }
    format_order = [param.name
                    for param, value in hd.ordered_options
                    if (param.name in kwargs) and value]
    format_order.insert(0, 'canonical')
    kwargs['canonical'] = True

    if input_format:
        input_type = guess_input_type(infile, input_format)
        input_file = input_type.load(infile)
        infile = input_file.memory

    hexdump_core(
        infile=infile,
        length=length,
        skip=skip,
        no_squeezing=no_squeezing,
        upper=upper,
        format_order=format_order,
        **kwargs,
    )


# ----------------------------------------------------------------------------

@app.command()
def merge(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format for all input files.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    clear_holes: bool = typer.Option(False, '--clear-holes', is_flag=True, help="""
        Merges memory holes, clearing data at their place.
    """),
    infiles: Sequence[str] = typer.Argument(..., type=FILE_PATH_IN, nargs=-1),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT),
) -> None:
    r"""Merges multiple files.

    ``INFILES`` is the list of paths of the input files.
    Set any to ``-`` or none to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.

    Every file of ``INFILES`` will overwrite data of previous files of the
    list where addresses overlap.
    """

    if not infiles:
        infiles = [None]
    input_formats = [input_format] * len(infiles)

    with MultiFileInOutCtxMgr(infiles, input_formats, outfile, output_format, width) as ctx:
        ctx.output_file.merge(*ctx.input_files, clear=clear_holes)


# ----------------------------------------------------------------------------

@app.command()
def shift(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    output_format: Optional[str] = typer.Option(None, '-o', '--output-format', help="""
        Forces the output file format.
        By default it is that of the input file.
    """),
    amount: int = typer.Option(0, '-n', '--amount', default=0, help="""
        Address shift to apply.
    """),
    width: Optional[int] = typer.Option(None, '-w', '--width', help="""
        Sets the length of the record data field, in bytes.
        By default it is that of the input file.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Shifts data addresses.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width) as ctx:
        ctx.output_file.shift(amount)


# ----------------------------------------------------------------------------

@app.command()
def validate(
    input_format: Optional[str] = typer.Option(None, '-i', '--input-format', help="""
        Forces the input file format.
        Required for the standard input.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
) -> None:
    r"""Validates a record file.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.
    """

    input_type = guess_input_type(infile, input_format)
    input_file = input_type.load(infile)
    input_file.validate_records()


# ----------------------------------------------------------------------------

@app.group()
def srec() -> None:
    """Motorola SREC specific"""


# ----------------------------------------------------------------------------

@srec.command()
def get_header(
    format: str = typer.Option('ascii', '-f', '--format', type=DATA_FMT_CHOICE,
              show_default=True, help="""
    Header data format.
"""),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
) -> None:
    r"""Gets the header data.

    ``INFILE`` is the path of the input file; 'srec' record type.
    Set to ``-`` to read from standard input.
    """

    input_file = SrecFile.load(infile)
    records = input_file.records

    if records and records[0].tag == 0:
        formatter = DATA_FMT_FORMATTERS[format]
        text = formatter(records[0].data).decode()
        print(text)


# ----------------------------------------------------------------------------

@srec.command()
def set_header(
    format: str = typer.Option('ascii', '-f', '--format', type=DATA_FMT_CHOICE,
              show_default=True, help="""
    Header data format.
"""),
    header: str = typer.Argument(...),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Sets the header data record.

    The header record is expected to be the first.
    All other records are kept as-is.
    No file-wise validation occurs.

    ``INFILE`` is the path of the input file; 'srec' record type.
    Set to ``-`` to read from standard input.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    parser = DATA_FMT_PARSERS[format]
    header_data = parser(header.encode())
    file = SrecFile.load(infile)
    records = _cast(List[SrecRecord], file.records)

    if records and records[0].tag == 0:
        record = records[0]
        record.data = header_data
        record.update_count()
        record.update_checksum()
    else:
        record = SrecRecord.create_header(header_data)
        records.insert(0, record)

    file.save(outfile)


# ----------------------------------------------------------------------------

@srec.command()
def del_header(
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Deletes the header data record.

    The header record is expected to be the first.
    All other records are kept as-is.
    No file-wise validation occurs.

    ``INFILE`` is the path of the input file; 'srec' record type.
    Set to ``-`` to read from standard input.

    ``OUTFILE`` is the path of the output file.
    Set to ``-`` to write to standard output.
    Leave empty to overwrite ``INFILE``.
    """

    file = SrecFile.load(infile)
    records = file.records

    if records and records[0].tag == 0:
        del records[0]

    file.save(outfile)


# ----------------------------------------------------------------------------

@app.command()
def xxd(
    autoskip: bool = typer.Option(False, '--autoskip', is_flag=True, help="""
        Toggles autoskip.

        A single '*' replaces null lines.
    """),
    bits: bool = typer.Option(False, '-b', '--bits', is_flag=True, help="""
        Binary digits.

        Switches to bits (binary digits) dump, rather than
        hexdump. This option writes octets as eight digits of '1' and '0'
        instead of a normal hexadecimal dump. Each line is preceded by a
        line number in hexadecimal and followed by an ASCII (or EBCDIC)
        representation.
        The argument switches -r, -p, -i do not work with this mode.
    """),
    cols: int = typer.Option(16, '-c', '--cols', type=int, help="""
        Formats <cols> octets per line. Max 256.

        Defaults: normal 16, -i 12, -p 30, -b 6.
    """),
    ebcdic: bool = typer.Option(False, '-E', '--ebcdic', '--EBCDIC', is_flag=True, help="""
        Uses EBCDIC charset.

        Changes the character encoding in the right-hand
        column from ASCII to EBCDIC.
        This does not change the hexadecimal representation.
        The option is meaningless in combinations with -r, -p or -i.
    """),
    endian: bool = typer.Option(False, '-e', '--endian', is_flag=True, help="""
        Switches to little-endian hexdump.

        This option treats  byte groups as words in little-endian byte order.
        The default grouping of 4 bytes may be changed using -g.
        This option only applies to hexdump, leaving the ASCII (or EBCDIC)
        representation unchanged.
        The switches -r, -p, -i do not work with this mode.
    """),
    groupsize: int = typer.Option(2, '-g', '--groupsize', type=int, help="""
        Byte group size.

        Separates the output of every <groupsize> bytes (two hex
        characters or eight bit-digits each) by a whitespace.
        Specify <groupsize> 0 to suppress grouping.
        <groupsize> defaults to 2 in normal mode, 4 in little-endian mode and 1
        in bits mode. Grouping does not apply to -p or -i.
    """),
    include: bool = typer.Option(False, '-i', '--include', is_flag=True, help="""
        Output in C include file style.

        A complete static array definition is written (named after the
        input file), unless reading from standard input.
    """),
    length: int = typer.Option(0, '-l', '--length', type=int, help="""
        Stops after writing <length> octets.
    """),
    offset: int = typer.Option(0, '-o', '--offset', type=int, help="""
        Adds <offset> to the displayed file position.
    """),
    postscript: bool = typer.Option(False, '-p', '--postscript', '--plain', '--ps', is_flag=True, help="""
        Outputs in postscript continuous hexdump style.

        Also known as plain hexdump style.
    """),
    quadword: bool = typer.Option(False, '-q', '--quadword', is_flag=True, help="""
        Uses 64-bit addressing.
    """),
    revert: bool = typer.Option(False, '-r', '--revert', is_flag=True, help="""
        Reverse operation.

        Convert (or patch) hexdump into binary.
        If not writing to standard output, it writes into its
        output file without truncating it.
        Use the combination -r and -p to read plain hexadecimal dumps
        without line number information and without a particular column
        layout. Additional Whitespace and line breaks are allowed anywhere.
    """),
    seek: int = typer.Option(0, '-k', '--seek', type=int, help="""
        Output seeking.

        When used after -r reverts with -o added to
        file positions found in hexdump.
    """),
    iseek: int = typer.Option(0, '-s', 'iseek', type=int, help="""
        Input seeking.

        Starts at <s> bytes absolute (or relative) input offset.
        Without -s option, it starts at the current file position.
        The prefix is used to compute the offset.
        '+' indicates that the seek is relative to the current input
        position.
        '-' indicates that the seek should be that many characters from
        the end of the input.
        '+-' indicates that the seek should be that many characters
        before the current stdin file position.
    """),
    upper_all: bool = typer.Option(False, '-U', '--upper-all', is_flag=True, help="""
        Uses upper case hex letters on address and data.
    """),
    upper: bool = typer.Option(False, '-u', '--upper', is_flag=True, help="""
        Uses upper case hex letters on data only.
    """),
    input_format: Optional[str] = typer.Option(None, '-I', '--input-format', help="""
        Forces the input file format.
    """),
    output_format: Optional[str] = typer.Option(None, '-O', '--output-format', help="""
        Forces the output file format.
    """),
    oseek_zeroes: bool = typer.Option(True, '--seek-zeroes/--no-seek-zeroes', is_flag=True,
              default=True, show_default=True, help="""
        Output seeking writes zeroes while seeking.
    """),
    version: bool = typer.Option(False, '-v', '--version', is_flag=True, is_eager=True,
              help="""
        Prints the package version number.
    """),
    infile: str = typer.Argument(..., type=FILE_PATH_IN, required=False),
    outfile: str = typer.Argument(..., type=FILE_PATH_OUT, required=False),
) -> None:
    r"""Emulates the xxd command.

    Please refer to the xxd manual page to know its features and caveats.

    Some parameters were changed to satisfy the POSIX-like command line parser.
    """

    infile = None if infile == '-' else infile
    outfile = None if outfile == '-' else outfile
    output_path = outfile
    output_file = None
    input_type = None

    if input_format:
        input_type = guess_input_type(infile, input_format)
        input_file = input_type.load(infile)
        infile = input_file.memory

    if output_format:
        output_type = guess_output_type(outfile, input_format, input_type)
        output_file = output_type()
        outfile = output_file.memory

    xxd_core(
        infile=infile,
        outfile=outfile,
        autoskip=autoskip,
        bits=bits,
        cols=cols,
        ebcdic=ebcdic,
        endian=endian,
        groupsize=groupsize,
        include=include,
        length=length,
        offset=offset,
        postscript=postscript,
        quadword=quadword,
        revert=revert,
        oseek=seek,
        iseek=iseek,
        upper_all=upper_all,
        upper=upper,
        oseek_zeroes=oseek_zeroes,
    )

    if output_format:
        output_file.save(output_path)

```