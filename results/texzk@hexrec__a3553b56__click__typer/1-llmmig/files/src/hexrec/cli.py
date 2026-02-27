import typer
from typing import Callable, List, Mapping, Optional, Sequence, Type
from .__init__ import __version__, file_types
from .base import BaseFile, guess_format_name
from .formats.srec import SrecFile, SrecRecord
from .hexdump import hexdump_core
from .utils import hexlify, parse_int, unhexlify
from .xxd import xxd_core

app = typer.Typer()

class BasedIntParamType:
    def __call__(self, value: str) -> int:
        try:
            return parse_int(value)
        except ValueError:
            raise typer.BadParameter(f"Invalid integer: {value!r}")

class ByteIntParamType:
    def __call__(self, value: str) -> int:
        try:
            b = parse_int(value)
            if not 0 <= b <= 255:
                raise ValueError()
            return b
        except ValueError:
            raise typer.BadParameter(f"Invalid byte: {value!r}")

BASED_INT = BasedIntParamType()
BYTE_INT = ByteIntParamType()

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

def guess_input_type(input_path: Optional[str], input_format: Optional[str] = None) -> Type[BaseFile]:
    if input_format:
        input_type = file_types[input_format]
    elif input_path is None or input_path == '-':
        raise ValueError('Standard input requires input format')
    else:
        name = guess_format_name(input_path)
        input_type = file_types[name]
    return input_type

def guess_output_type(output_path: Optional[str], output_format: Optional[str] = None, input_type: Optional[Type[BaseFile]] = None) -> Type[BaseFile]:
    if output_format:
        output_type = file_types[output_format]
    elif output_path is None or output_path == '-':
        output_type = input_type
    else:
        name = guess_format_name(output_path)
        output_type = file_types[name]
    return output_type

def print_version(value: bool):
    if value:
        typer.echo(__version__)
        raise typer.Exit()

@app.command()
def align(
    input_format: Optional[str] = typer.Option(None, "-i", "--input-format", help="Forces the input file format."),
    output_format: Optional[str] = typer.Option(None, "-o", "--output-format", help="Forces the output file format."),
    modulo: int = typer.Option(4, "-m", "--modulo", help="Alignment modulo."),
    start: Optional[int] = typer.Option(None, "-s", "--start", help="Inclusive start address."),
    endex: Optional[int] = typer.Option(None, "-e", "--endex", help="Exclusive end address."),
    value: Optional[int] = typer.Option(0, "-v", "--value", help="Byte value used to flood alignment padding."),
    width: Optional[int] = typer.Option(None, "-w", "--width", help="Sets the length of the record data field."),
    infile: str = typer.Argument(..., help="Input file path."),
    outfile: str = typer.Argument(..., help="Output file path.")
):
    """Pads blocks to align their boundaries."""
    with SingleFileInOutCtxMgr(infile, input_format, outfile, output_format, width) as ctx:
        ctx.output_file.align(modulo, start=start, endex=endex, pattern=value)

# Additional commands (e.g., clear, convert, crop, etc.) would follow the same pattern.

if __name__ == "__main__":
    app()
