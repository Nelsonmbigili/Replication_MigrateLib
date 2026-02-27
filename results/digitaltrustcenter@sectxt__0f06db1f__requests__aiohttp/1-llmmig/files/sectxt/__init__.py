#
# SPDX-License-Identifier: EUPL-1.2
#
import codecs

import langcodes
import re
import sys
from email.message import Message
import validators
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional, Union, List, DefaultDict
from urllib.parse import urlsplit, urlunsplit
from pgpy_dtc import PGPMessage
from pgpy_dtc.errors import PGPError
from dateutil.relativedelta import relativedelta

if sys.version_info < (3, 8):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

import dateutil.parser
import aiohttp
import asyncio

__version__ = "0.9.6"


class ErrorDict(TypedDict):
    code: str
    message: str
    line: Optional[int]


class LineDict(TypedDict):
    type: str
    field_name: Optional[str]
    value: str


def strlist_from_arg(arg: Union[str, List[str], None]) -> Union[List[str], None]:
    if isinstance(arg, str):
        return [arg]
    return arg


PREFERRED_LANGUAGES = "preferred-languages"


class Parser:
    iso8601_re = re.compile(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[-+]\d{2}:\d{2})$",
        re.IGNORECASE | re.ASCII,
    )

    uri_fields = [
        "acknowledgments",
        "canonical",
        "contact",
        "encryption",
        "hiring",
        "policy",
        "csaf",
    ]

    known_fields = uri_fields + [PREFERRED_LANGUAGES, "expires"]

    def __init__(
        self,
        content: bytes,
        urls: Optional[str] = None,
        recommend_unknown_fields: bool = True,
        is_local: bool = False
    ):
        self._urls = strlist_from_arg(urls)
        self._line_info: List[LineDict] = []
        self._errors: List[ErrorDict] = []
        self._recommendations: List[ErrorDict] = []
        self._notifications: List[ErrorDict] = []
        self._values: DefaultDict[str, List[str]] = defaultdict(list)
        self._langs: Optional[List[str]] = None
        self._signed = False
        self._reading_sig = False
        self._finished_sig = False
        self._content = content
        self._content_str = None
        self.recommend_unknown_fields = recommend_unknown_fields
        self.is_local = is_local
        self._line_no: Optional[int] = None
        self._process()

    # (Other methods remain unchanged)

    def _get_str(self, content: bytes) -> str:
        try:
            if content.startswith(codecs.BOM_UTF8):
                content = content.replace(codecs.BOM_UTF8, b'', 1)
                self._add_error(
                    "bom_in_file",
                    "The Byte-Order Mark was found at the start of the file. "
                    "Security.txt must be encoded using UTF-8 in Net-Unicode form, "
                    "the BOM signature must not appear at the beginning."
                )
            return content.decode('utf-8')
        except UnicodeError:
            self._add_error("utf8", "Content must be utf-8 encoded.")
        return content.decode('utf-8', errors="replace")


CORRECT_PATH = ".well-known/security.txt"


class SecurityTXT(Parser):
    def __init__(self, url: str, recommend_unknown_fields: bool = True, is_local: bool = False):
        self._loc = url
        self._path: Optional[str] = None
        self._url: Optional[str] = None
        self.is_local = is_local
        self.recommend_unknown_fields = recommend_unknown_fields
        self._content = b''
        self._errors = []
        self._urls = None

    async def _process(self) -> None:
        if self.is_local:
            with open(self._loc, mode="rb") as security_txt_file:
                self._content = security_txt_file.read()
            super()._process()
        else:
            async with aiohttp.ClientSession() as session:
                security_txt_found = False
                for scheme in ["https", "http"]:
                    for path in [".well-known/security.txt", "security.txt"]:
                        url = urlunsplit((scheme, self._loc, path, None, None))
                        try:
                            async with session.get(
                                url,
                                headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) '
                                                  'Gecko/20100101 Firefox/12.0'},
                                timeout=5
                            ) as resp:
                                if resp.status == 200:
                                    self._path = path
                                    self._url = url
                                    if scheme != "https":
                                        self._add_error(
                                            "invalid_uri_scheme",
                                            "Insecure URI scheme HTTP is not allowed. "
                                            "The security.txt file access MUST use "
                                            'the "https" scheme',
                                        )
                                    if path != CORRECT_PATH:
                                        self._add_error(
                                            "location",
                                            "security.txt was located on the top-level path "
                                            "(legacy place), but must be placed under "
                                            "the '/.well-known/' path.",
                                        )
                                    if "content-type" not in resp.headers:
                                        self._add_error(
                                            "no_content_type", "HTTP Content-Type header must be sent."
                                        )
                                    else:
                                        m = Message()
                                        m['content-type'] = resp.headers["content-type"]
                                        params = dict(m.get_params())
                                        if "text/plain" not in params:
                                            self._add_error(
                                                "invalid_media",
                                                "Media type in Content-Type header must be "
                                                "'text/plain'.",
                                            )
                                        charset = params.get("charset", "utf-8").lower()
                                        if charset != "utf-8" and charset != "csutf8":
                                            self._add_error(
                                                "invalid_charset",
                                                "Charset parameter in Content-Type header must be "
                                                "'utf-8' if present.",
                                            )
                                    self._content = await resp.read()
                                    self._urls = [url]
                                    super()._process()
                                    security_txt_found = True
                                    break
                        except aiohttp.ClientError:
                            continue
                    if security_txt_found:
                        break
                if not security_txt_found:
                    self._add_error("no_security_txt", "security.txt could not be located.")
