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

import plac

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


class BasedIntParamType:
    name = 'integer'

    def convert(self, value):
        try:
            return parse_int(value)
        except ValueError:
            raise ValueError(f'invalid integer: {value!r}')


class ByteIntParamType:
    name = 'byte'

    def convert(self, value):
        try:
            b = parse_int(value)
            if not 0 <= b <= 255:
                raise ValueError()
            return b
        except ValueError:
            raise ValueError(f'invalid byte: {value!r}')


class OrderedOptionsCommand:

    def parse_args(self, args):
        opts, order = {}, []
        for arg in args:
            if '=' in arg:
                key, value = arg.split('=', 1)
                opts[key] = value
            else:
                order.append(arg)
        setattr(self, 'ordered_options', [(key, opts[key]) for key in order])
        return opts


BASED_INT = BasedIntParamType()
BYTE_INT = ByteIntParamType()

FILE_PATH_IN = str
FILE_PATH_OUT = str

FORMAT_CHOICE = list(sorted(file_types.keys()))

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

DATA_FMT_CHOICE = list(DATA_FMT_FORMATTERS.keys())


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
    output_format: Optional[str] = None,
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


def print_version(value):
    if not value:
        return
    print(str(__version__))


def print_hexdump_version(value):
    if not value:
        return
    print(f'hexdump from Python hexrec {__version__!s}')


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

def main() -> None:
    """
    A set of command line utilities for common operations with record files.

    Being built with `Plac <https://plac.readthedocs.io/>`_, all the
    commands follow POSIX-like syntax rules, as well as reserving the virtual
    file path ``-`` for command chaining via standard output/input buffering.
    """


# ----------------------------------------------------------------------------

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    modulo=('Alignment modulo.', 'option', 'm', int),
    start=('Inclusive start address. Negative values are referred to the end of the data. By default it applies from the start of the data contents.', 'option', 's', int),
    endex=('Exclusive end address. Negative values are referred to the end of the data. By default it applies till the end of the data contents.', 'option', 'e', int),
    value=('Byte value used to flood alignment padding.', 'option', 'v', int),
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    infile=('INFILE is the path of the input file. Set to - to read from standard input; input format required.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def align(input_format: Optional[str], output_format: Optional[str], modulo: int, start: Optional[int], endex: Optional[int], value: Optional[int], width: Optional[int], infile: str, outfile: str) -> None:
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

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    start=('Inclusive start address. Negative values are referred to the end of the data. By default it applies from the start of the data contents.', 'option', 's', int),
    endex=('Exclusive end address. Negative values are referred to the end of the data. By default it applies till the end of the data contents.', 'option', 'e', int),
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    infile=('INFILE is the path of the input file. Set to - to read from standard input; input format required.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def clear(input_format: Optional[str], output_format: Optional[str], start: Optional[int], endex: Optional[int], width: Optional[int], infile: str, outfile: str) -> None:
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

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    infile=('INFILE is the list of paths of the input files. Set to - to read from standard input; input format required.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def convert(input_format: Optional[str], output_format: Optional[str], width: Optional[int], infile: str, outfile: str) -> None:

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

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    start=('Inclusive start address. Negative values are referred to the end of the data. By default it applies from the start of the data contents.', 'option', 's', int),
    endex=('Exclusive end address. Negative values are referred to the end of the data. By default it applies till the end of the data contents.', 'option', 'e', int),
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    infile=('INFILE is the path of the input file. Set to - to read from standard input; input format required.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def crop(input_format: Optional[str], output_format: Optional[str], start: Optional[int], endex: Optional[int], value: Optional[int], width: Optional[int], infile: str, outfile: str) -> None:
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

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    start=('Inclusive start address. Negative values are referred to the end of the data. By default it applies from the start of the data contents.', 'option', 's', int),
    endex=('Exclusive end address. Negative values are referred to the end of the data. By default it applies till the end of the data contents.', 'option', 'e', int),
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    infile=('INFILE is the path of the input file. Set to - to read from standard input; input format required.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def delete(input_format: Optional[str], output_format: Optional[str], start: Optional[int], endex: Optional[int], width: Optional[int], infile: str, outfile: str) -> None:
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

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    value=('Byte value used to fill the address range.', 'option', 'v', int),
    start=('Inclusive start address. Negative values are referred to the end of the data. By default it applies from the start of the data contents.', 'option', 's', int),
    endex=('Exclusive end address. Negative values are referred to the end of the data. By default it applies till the end of the data contents.', 'option', 'e', int),
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    infile=('INFILE is the path of the input file. Set to - to read from standard input; input format required.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def fill(input_format: Optional[str], output_format: Optional[str], value: int, start: Optional[int], endex: Optional[int], width: Optional[int], infile: str, outfile: str) -> None:
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

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    value=('Byte value used to flood the address range.', 'option', 'v', int),
    start=('Inclusive start address. Negative values are referred to the end of the data. By default it applies from the start of the data contents.', 'option', 's', int),
    endex=('Exclusive end address. Negative values are referred to the end of the data. By default it applies till the end of the data contents.', 'option', 'e', int),
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    infile=('INFILE is the path of the input file. Set to - to read from standard input; input format required.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def flood(input_format: Optional[str], output_format: Optional[str], value: int, start: Optional[int], endex: Optional[int], width: Optional[int], infile: str, outfile: str) -> None:
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

@plac.annotations(
    one_byte_octal=('One-byte octal display. Display the input offset in hexadecimal, followed by sixteen space-separated, three-column, zero-filled bytes of input data, in octal, per line.', 'flag', 'b'),
    one_byte_hex=('One-byte hexadecimal display. Display the input offset in hexadecimal, followed by sixteen space-separated, two-column, zero-filled bytes of input data, in hexadecimal, per line.', 'flag', 'X'),
    one_byte_char=('One-byte character display. Display the input offset in hexadecimal, followed by sixteen space-separated, three-column, space-filled characters of input data per line.', 'flag', 'c'),
    canonical=('Canonical hex+ASCII display. Display the input offset in hexadecimal, followed by sixteen space-separated, two-column, hexadecimal bytes, followed by the same sixteen bytes in %_p format enclosed in | characters. Invoking the program as hd implies this option.', 'flag', 'C'),
    two_bytes_decimal=('Two-byte decimal display. Display the input offset in hexadecimal, followed by eight space-separated, five-column, zero-filled, two-byte units of input data, in unsigned decimal, per line.', 'flag', 'd'),
    two_bytes_octal=('Two-byte octal display. Display the input offset in hexadecimal, followed by eight space-separated, six-column, zero-filled, two-byte quantities of input data, in octal, per line.', 'flag', 'o'),
    two_bytes_hex=('Two-byte hexadecimal display. Display the input offset in hexadecimal, followed by eight space-separated, four-column, zero-filled, two-byte quantities of input data, in hexadecimal, per line.', 'flag', 'x'),
    length=('Interpret only length bytes of input.', 'option', 'n', int),
    skip=('Skip offset bytes from the beginning of the input.', 'option', 's', int),
    no_squeezing=('The -v option causes hexdump to display all input data. Without the -v option, any number of groups of output lines which would be identical to the immediately preceding group of output lines (except for the input offsets), are replaced with a line comprised of a single asterisk.', 'flag', 'v'),
    upper=('Uses upper case hex letters on address and data.', 'flag', 'U'),
    input_format='Forces the input file format.',
    version=('Print version and exit.', 'flag', 'V'),
    infile=('INFILE is the path of the input file. Set to - to read from standard input.', 'argument', str),
)
def hexdump(infile: str, one_byte_octal: Sequence[bool], one_byte_hex: Sequence[bool], one_byte_char: Sequence[bool], canonical: Sequence[bool], two_bytes_decimal: Sequence[bool], two_bytes_octal: Sequence[bool], two_bytes_hex: Sequence[bool], length: Optional[int], skip: Optional[int], no_squeezing: bool, upper: bool, input_format: Optional[str], version: bool) -> None:
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

@plac.annotations(
    one_byte_octal=('One-byte octal display. Display the input offset in hexadecimal, followed by sixteen space-separated, three-column, zero-filled bytes of input data, in octal, per line.', 'flag', 'b'),
    one_byte_hex=('One-byte hexadecimal display. Display the input offset in hexadecimal, followed by sixteen space-separated, two-column, zero-filled bytes of input data, in hexadecimal, per line.', 'flag', 'X'),
    one_byte_char=('One-byte character display. Display the input offset in hexadecimal, followed by sixteen space-separated, three-column, space-filled characters of input data per line.', 'flag', 'c'),
    two_bytes_decimal=('Two-byte decimal display. Display the input offset in hexadecimal, followed by eight space-separated, five-column, zero-filled, two-byte units of input data, in unsigned decimal, per line.', 'flag', 'd'),
    two_bytes_octal=('Two-byte octal display. Display the input offset in hexadecimal, followed by eight space-separated, six-column, zero-filled, two-byte quantities of input data, in octal, per line.', 'flag', 'o'),
    two_bytes_hex=('Two-byte hexadecimal display. Display the input offset in hexadecimal, followed by eight space-separated, four-column, zero-filled, two-byte quantities of input data, in hexadecimal, per line.', 'flag', 'x'),
    length=('Interpret only length bytes of input.', 'option', 'n', int),
    skip=('Skip offset bytes from the beginning of the input.', 'option', 's', int),
    no_squeezing=('The -v option causes hexdump to display all input data. Without the -v option, any number of groups of output lines which would be identical to the immediately preceding group of output lines (except for the input offsets), are replaced with a line comprised of a single asterisk.', 'flag', 'v'),
    upper=('Uses upper case hex letters on address and data.', 'flag', 'U'),
    input_format='Forces the input file format.',
    version=('Print version and exit.', 'flag', 'V'),
    infile=('INFILE is the path of the input file. Set to - to read from standard input.', 'argument', str),
)
def hd(infile: str, one_byte_octal: Sequence[bool], one_byte_hex: Sequence[bool], one_byte_char: Sequence[bool], two_bytes_decimal: Sequence[bool], two_bytes_octal: Sequence[bool], two_bytes_hex: Sequence[bool], length: Optional[int], skip: Optional[int], no_squeezing: bool, upper: bool, input_format: Optional[str], version: bool) -> None:
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

@plac.annotations(
    input_format='Forces the input file format for all input files. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    clear_holes=('Merges memory holes, clearing data at their place.', 'flag', 'c'),
    infiles=('INFILES is the list of paths of the input files. Set any to - or none to read from standard input; input format required.', 'argument', str, '...'),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output.', 'argument', str),
)
def merge(input_format: Optional[str], output_format: Optional[str], width: Optional[int], clear_holes: bool, infiles: Sequence[str], outfile: str) -> None:
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

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    output_format='Forces the output file format. By default it is that of the input file.',
    amount=('Address shift to apply.', 'option', 'n', int),
    width=('Sets the length of the record data field, in bytes. By default it is that of the input file.', 'option', 'w', int),
    infile=('INFILE is the path of the input file. Set to - to read from standard input; input format required.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def shift(input_format: Optional[str], output_format: Optional[str], amount: int, width: Optional[int], infile: str, outfile: str) -> None:
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

@plac.annotations(
    input_format='Forces the input file format. Required for the standard input.',
    infile=('INFILE is the path of the input file. Set to - to read from standard input; input format required.', 'argument', str),
)
def validate(input_format: Optional[str], infile: str) -> None:
    r"""Validates a record file.

    ``INFILE`` is the path of the input file.
    Set to ``-`` to read from standard input; input format required.
    """

    input_type = guess_input_type(infile, input_format)
    input_file = input_type.load(infile)
    input_file.validate_records()


# ----------------------------------------------------------------------------

@plac.annotations()
def srec() -> None:
    """Motorola SREC specific"""


# ----------------------------------------------------------------------------

@plac.annotations(
    format=('Header data format.', 'option', 'f', str),
    infile=('INFILE is the path of the input file; \'srec\' record type. Set to - to read from standard input.', 'argument', str),
)
def get_header(format: str, infile: str) -> None:
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

@plac.annotations(
    format=('Header data format.', 'option', 'f', str),
    header=('Header data to set.', 'argument', str),
    infile=('INFILE is the path of the input file; \'srec\' record type. Set to - to read from standard input.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def set_header(format: str, header: str, infile: str, outfile: str) -> None:
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

@plac.annotations(
    infile=('INFILE is the path of the input file; \'srec\' record type. Set to - to read from standard input.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output. Leave empty to overwrite INFILE.', 'argument', str),
)
def del_header(infile: str, outfile: str) -> None:
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

@plac.annotations(
    autoskip=('Toggles autoskip. A single * replaces null lines.', 'flag', 'a'),
    bits=('Binary digits. Switches to bits (binary digits) dump, rather than hexdump.', 'flag', 'b'),
    cols=('Formats <cols> octets per line. Max 256. Defaults: normal 16, -i 12, -p 30, -b 6.', 'option', 'c', int),
    ebcdic=('Uses EBCDIC charset. Changes the character encoding in the right-hand column from ASCII to EBCDIC.', 'flag', 'E'),
    endian=('Switches to little-endian hexdump.', 'flag', 'e'),
    groupsize=('Byte group size. Suppresses grouping if set to 0.', 'option', 'g', int),
    include=('Output in C include file style.', 'flag', 'i'),
    length=('Stops after writing <length> octets.', 'option', 'l', int),
    offset=('Adds <offset> to the displayed file position.', 'option', 'o', int),
    postscript=('Outputs in postscript continuous hexdump style.', 'flag', 'p'),
    quadword=('Uses 64-bit addressing.', 'flag', 'q'),
    revert=('Reverse operation. Convert (or patch) hexdump into binary.', 'flag', 'r'),
    seek=('Input seeking. Starts at <s> bytes absolute (or relative) input offset.', 'option', 's', str),
    upper_all=('Uses upper case hex letters on address and data.', 'flag', 'U'),
    upper=('Uses upper case hex letters on data only.', 'flag', 'u'),
    input_format='Forces the input file format.',
    output_format='Forces the output file format.',
    seek_zeroes=('Output seeking writes zeroes while seeking.', 'flag', 'z'),
    version=('Prints the package version number.', 'flag', 'v'),
    infile=('INFILE is the path of the input file. Set to - to read from standard input.', 'argument', str),
    outfile=('OUTFILE is the path of the output file. Set to - to write to standard output.', 'argument', str),
)
def xxd(autoskip: bool, bits: bool, cols: int, ebcdic: bool, endian: bool, groupsize: int, include: bool, length: int, offset: int, postscript: bool, quadword: bool, revert: bool, seek: str, upper_all: bool, upper: bool, input_format: str, output_format: str, seek_zeroes: bool, version: bool, infile: str, outfile: str) -> None:
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
        seek=seek,
        upper_all=upper_all,
        upper=upper,
        seek_zeroes=seek_zeroes,
    )

    if output_format:
        output_file.save(output_path)

