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
import urllib3

__version__ = "0.9.6"

http = urllib3.PoolManager()


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

    # Other methods remain unchanged...

    def _process(self) -> None:
        self._content_str = self._get_str(self._content)
        lines = self._content_str.split("\n")
        self._line_no = 1
        for line in lines:
            self._line_info.append(self._parse_line(line))
            self._line_no += 1
        self._line_no = None
        self.validate_contents()

    # Other methods remain unchanged...


CORRECT_PATH = ".well-known/security.txt"


class SecurityTXT(Parser):
    def __init__(self, url: str, recommend_unknown_fields: bool = True, is_local: bool = False):
        url_parts = urlsplit(url)
        if url_parts.scheme and not is_local:
            if not url_parts.netloc:
                raise ValueError("Invalid URL")
            loc = url_parts.netloc
        else:
            loc = url
        self._loc = loc
        self._path: Optional[str] = None
        self._url: Optional[str] = None
        super().__init__(b'', recommend_unknown_fields=recommend_unknown_fields, is_local=is_local)

    def _process(self) -> None:
        if self.is_local:
            security_txt_file = open(self._loc, mode="rb")
            self._content = security_txt_file.read()
            security_txt_file.close()
            super()._process()
        else:
            security_txt_found = False
            for scheme in ["https", "http"]:
                for path in [".well-known/security.txt", "security.txt"]:
                    url = urlunsplit((scheme, self._loc, path, None, None))
                    try:
                        resp = http.request(
                            "GET",
                            url,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) '
                                              'Gecko/20100101 Firefox/12.0'},
                            timeout=5
                        )
                    except urllib3.exceptions.SSLError:
                        if not any(d["code"] == "invalid_cert" for d in self._errors):
                            self._add_error(
                                "invalid_cert",
                                "security.txt must be served with a valid TLS certificate.",
                            )
                        try:
                            resp = http.request(
                                "GET",
                                url,
                                headers={
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) '
                                                  'Gecko/20100101 Firefox/12.0'},
                                timeout=5,
                                cert_reqs='CERT_NONE'
                            )
                        except:
                            continue
                    except:
                        continue
                    if resp.status == 200:
                        if resp.get_redirect_location():
                            if not resp.get_redirect_location().endswith(path):
                                continue
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
                                # According to RFC9116, charset default is utf-8
                                self._add_error(
                                    "invalid_charset",
                                    "Charset parameter in Content-Type header must be "
                                    "'utf-8' if present.",
                                )
                        self._content = resp.data
                        if resp.get_redirect_location():
                            self._urls = [resp.get_redirect_location(), url]
                        else:
                            self._urls = [url]
                        super()._process()
                        security_txt_found = True
                        break
                if security_txt_found:
                    break
            if not security_txt_found:
                self._add_error("no_security_txt", "security.txt could not be located.")
