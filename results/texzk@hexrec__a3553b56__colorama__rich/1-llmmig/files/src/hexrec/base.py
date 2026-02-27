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

r""" Base types and classes."""

import abc
import io
import os
import sys
from typing import IO
from typing import Any
from typing import List
from typing import Mapping
from typing import MutableMapping
from typing import MutableSequence
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import cast as _cast

from rich.console import Console
from bytesparse import Memory
from bytesparse.base import BlockSequence
from bytesparse.base import ImmutableMemory
from bytesparse.base import MutableMemory

try:
    from typing import TypeAlias
except ImportError:  # pragma: no cover
    TypeAlias = Any  # Python < 3.10

try:
    from typing import Literal
    ByteOrder: TypeAlias = Literal['big', 'little']
except ImportError:  # pragma: no cover
    Literal: TypeAlias = str  # Python < 3.8
    ByteOrder: TypeAlias = Literal

try:
    from typing import Self
except ImportError:  # pragma: no cover
    Self: TypeAlias = Any  # Python < 3.11
__TYPING_HAS_SELF = Self is not Any

AnyBytes: TypeAlias = Union[bytes, bytearray, memoryview]
AnyPath: TypeAlias = Union[bytes, bytearray, str, os.PathLike]
EllipsisType: TypeAlias = Type['Ellipsis']

file_types: MutableMapping[str, Type['BaseFile']] = {}
r"""Registered record file types.

This is an ordered mapping, where the first item has top priority."""

TOKEN_COLOR_CODES: Mapping[str, str] = {
    '':         "[/]",
    '<':        "[/]",
    '>':        "[/]",
    'address':  "[red]",
    'addrlen':  "[yellow]",
    'after':    "[/]",
    'before':   "[/]",
    'begin':    "[yellow]",
    'checksum': "[magenta]",
    'count':    "[blue]",
    'data':     "[cyan]",
    'dataalt':  "[bright_cyan]",
    'end':      "[/]",
    'tag':      "[green]",
}
r"""Rich color codes for each possible token type."""


def colorize_tokens(
    tokens: Mapping[str, bytes],
    altdata: bool = True,
) -> Mapping[str, bytes]:
    r"""Prepends Rich color codes to record field tokens.

    For each token within `tokens`, its key is used to look up the Rich color
    code from :data:`TOKEN_COLOR_CODES`.
    The retrieved code (string) is prepended to the token, and a reset tag
    (`[/]`) is appended.
    All the modified tokens are then collected and returned.

    Args:
        tokens (dict):
            A mapping of each token key name to token byte string.

        altdata (bool):
            If true, it alternates each byte (two hex digits) between the Rich
            color codes mapped with keys ``data`` (even byte index) and
            ``dataalt`` (odd byte index).
            If false, only the ``data`` code is prepended.

    Returns:
        dict: `tokens` with prepended Rich color codes.

    Examples:
        >>> from hexrec.base import colorize_tokens
        >>> from hexrec import IhexFile
        >>> from pprint import pprint

        >>> record = IhexFile.Record.create_end_of_file()
        >>> tokens = record.to_tokens()
        >>> pprint(tokens)  # doctest: +NORMALIZE_WHITESPACE
        {'address': b'0000',
         'after': b'',
         'before': b'',
         'begin': b':',
         'checksum': b'FF',
         'count': b'00',
         'data': b'',
         'end': b'\r\n',
         'tag': b'01'}
        >>> colorized = colorize_tokens(tokens)
        >>> pprint(colorized)  # doctest: +NORMALIZE_WHITESPACE
        {'<': b'[/]',
         '>': b'[/]',
         'address': b'[red]0000[/]',
         'begin': b'[yellow]:[/]',
         'checksum': b'[magenta]FF[/]',
         'count': b'[blue]00[/]',
         'end': b'[/]\r\n[/]',
         'tag': b'[green]01[/]'}
    """

    codes = TOKEN_COLOR_CODES
    colorized = {}
    colorized.setdefault('<', codes['<'].encode())

    for key, value in tokens.items():
        if key not in codes:
            key = ''
        if value:
            code = codes[key]

            if key == 'data' and altdata:
                altcode = codes['dataalt']
                buffer = bytearray()
                length = len(value)
                i = 0

                for i in range(0, length - 1, 2):
                    buffer.extend((altcode if i & 2 else code).encode())
                    buffer.append(value[i])
                    buffer.append(value[i + 1])
                    buffer.extend(b"[/]")

                if length & 1:
                    buffer.extend((code if i & 2 else altcode).encode())
                    buffer.append(value[length - 1])
                    buffer.extend(b"[/]")

                colorized[key] = bytes(buffer)
            else:
                colorized[key] = f"{code}{value.decode()}[/]".encode()

    colorized.setdefault('>', codes['>'].encode())
    return colorized

# The rest of the code remains unchanged.
