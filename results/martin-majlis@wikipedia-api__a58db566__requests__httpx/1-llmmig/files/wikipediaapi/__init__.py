"""
Wikipedia-API is easy to use wrapper for extracting information from Wikipedia.

It supports extracting texts, sections, links, categories, translations, etc.
from Wikipedia. Documentation provides code snippets for the most common use
cases.
"""

__version__ = (0, 7, 1)

from collections import defaultdict
from enum import IntEnum
import logging
import re
from typing import Any, Optional, Union
from urllib import parse

import httpx

USER_AGENT = (
    "Wikipedia-API/"
    + ".".join(str(s) for s in __version__)
    + "; https://github.com/martin-majlis/Wikipedia-API/"
)

log = logging.getLogger(__name__)


# https://www.mediawiki.org/wiki/API:Main_page
PagesDict = dict[str, "WikipediaPage"]


class ExtractFormat(IntEnum):
    """Represents extraction format."""

    WIKI = 1
    """
    Allows recognizing subsections

    Example: https://goo.gl/PScNVV
    """

    HTML = 2
    """
    Alows retrieval of HTML tags

    Example: https://goo.gl/1Jwwpr
    """

    # Plain: https://goo.gl/MAv2qz
    # Doesn't allow to recognize subsections
    # PLAIN = 3


class Namespace(IntEnum):
    """
    Represents namespace in Wikipedia

    You can gen list of possible namespaces here:

    * https://en.wikipedia.org/wiki/Wikipedia:Namespace
    * https://en.wikipedia.org/wiki/Wikipedia:Namespace#Programming

    Currently following namespaces are supported:
    """

    MAIN = 0
    TALK = 1
    USER = 2
    USER_TALK = 3
    WIKIPEDIA = 4
    WIKIPEDIA_TALK = 5
    FILE = 6
    FILE_TALK = 7
    MEDIAWIKI = 8
    MEDIAWIKI_TALK = 9
    TEMPLATE = 10
    TEMPLATE_TALK = 11
    HELP = 12
    HELP_TALK = 13
    CATEGORY = 14
    CATEGORY_TALK = 15
    PORTAL = 100
    PORTAL_TALK = 101
    PROJECT = 102
    PROJECT_TALK = 103
    REFERENCE = 104
    REFERENCE_TALK = 105
    BOOK = 108
    BOOK_TALK = 109
    DRAFT = 118
    DRAFT_TALK = 119
    EDUCATION_PROGRAM = 446
    EDUCATION_PROGRAM_TALK = 447
    TIMED_TEXT = 710
    TIMED_TEXT_TALK = 711
    MODULE = 828
    MODULE_TALK = 829
    GADGET = 2300
    GADGET_TALK = 2301
    GADGET_DEFINITION = 2302
    GADGET_DEFINITION_TALK = 2303


WikiNamespace = Union[Namespace, int]


def namespace2int(namespace: WikiNamespace) -> int:
    """Converts namespace into integer"""
    if isinstance(namespace, Namespace):
        return namespace.value

    return namespace


RE_SECTION = {
    ExtractFormat.WIKI: re.compile(r"\n\n *(==+) (.*?) (==+) *\n"),
    ExtractFormat.HTML: re.compile(
        r"\n? *<h([1-9])[^>]*?>(<span[^>]*></span>)? *"
        + "(<span[^>]*>)? *(<span[^>]*></span>)? *(.*?) *"
        + "(</span>)?(<span>Edit</span>)?</h[1-9]>\n?"
        #                  ^^^^
        # Example page with 'Edit' erroneous links: https://bit.ly/2ui4FWs
    ),
    # ExtractFormat.PLAIN.value: re.compile(r'\n\n *(===*) (.*?) (===*) *\n'),
}


class Wikipedia:
    """Wikipedia is wrapper for Wikipedia API."""

    def __init__(
        self,
        user_agent: str,
        language: str = "en",
        extract_format: ExtractFormat = ExtractFormat.WIKI,
        headers: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """
        Constructs Wikipedia object for extracting information Wikipedia.

        :param user_agent: HTTP User-Agent used in requests
                https://meta.wikimedia.org/wiki/User-Agent_policy
        :param language: Language mutation of Wikipedia -
                http://meta.wikimedia.org/wiki/List_of_Wikipedias
        :param extract_format: Format used for extractions
                :class:`ExtractFormat` object.
        :param headers:  Headers sent as part of HTTP request
        :param kwargs: Optional parameters used in -
                http://docs.python-requests.org/en/master/api/#requests.request

        Examples:

        * Proxy: ``Wikipedia('foo (merlin@example.com)', proxies={'http': 'http://proxy:1234'})``
        """
        kwargs.setdefault("timeout", 10.0)

        default_headers = {} if headers is None else headers
        if user_agent:
            default_headers.setdefault(
                "User-Agent",
                user_agent,
            )
        used_user_agent = default_headers.get("User-Agent")
        if not (used_user_agent and len(used_user_agent) > 5):
            raise AssertionError(
                "Please, be nice to Wikipedia and specify user agent - "
                + "https://meta.wikimedia.org/wiki/User-Agent_policy. Current user_agent: '"
                + str(used_user_agent)
                + "' is not sufficient."
            )
        default_headers["User-Agent"] += " (" + USER_AGENT + ")"

        self.language = language.strip().lower()
        if not self.language:
            raise AssertionError(
                "Specify language. Current language: '"
                + str(self.language)
                + "' is not sufficient."
            )
        self.extract_format = extract_format

        log.info(
            "Wikipedia: language=%s, user_agent: %s, extract_format=%s",
            self.language,
            default_headers["User-Agent"],
            self.extract_format,
        )

        self._session = httpx.Client(headers=default_headers, timeout=kwargs["timeout"])
        self._request_kwargs = kwargs

    def __del__(self) -> None:
        """Closes session."""
        if hasattr(self, "_session") and self._session:
            self._session.close()

    def _query(self, page: "WikipediaPage", params: dict[str, Any]):
        """Queries Wikimedia API to fetch content."""
        base_url = "https://" + page.language + ".wikipedia.org/w/api.php"
        log.info(
            "Request URL: %s",
            base_url + "?" + "&".join([k + "=" + str(v) for k, v in params.items()]),
        )
        params["format"] = "json"
        params["redirects"] = 1
        r = self._session.get(base_url, params=params, **self._request_kwargs)
        return r.json()

    # The rest of the code remains unchanged.
