import treq
from collections import defaultdict
from enum import IntEnum
import logging
import re
from typing import Any, Optional, Union
from urllib import parse

USER_AGENT = (
    "Wikipedia-API/"
    + ".".join(str(s) for s in (0, 7, 1))
    + "; https://github.com/martin-majlis/Wikipedia-API/"
)

log = logging.getLogger(__name__)

PagesDict = dict[str, "WikipediaPage"]


class ExtractFormat(IntEnum):
    WIKI = 1
    HTML = 2


class Namespace(IntEnum):
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
    if isinstance(namespace, Namespace):
        return namespace.value
    return namespace


RE_SECTION = {
    ExtractFormat.WIKI: re.compile(r"\n\n *(==+) (.*?) (==+) *\n"),
    ExtractFormat.HTML: re.compile(
        r"\n? *<h([1-9])[^>]*?>(<span[^>]*></span>)? *"
        + "(<span[^>]*>)? *(<span[^>]*></span>)? *(.*?) *"
        + "(</span>)?(<span>Edit</span>)?</h[1-9]>\n?"
    ),
}


class Wikipedia:
    def __init__(
        self,
        user_agent: str,
        language: str = "en",
        extract_format: ExtractFormat = ExtractFormat.WIKI,
        headers: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> None:
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

        self._headers = default_headers
        self._request_kwargs = kwargs

    async def page(
        self,
        title: str,
        ns: WikiNamespace = Namespace.MAIN,
        unquote: bool = False,
    ) -> "WikipediaPage":
        if unquote:
            title = parse.unquote(title)

        return WikipediaPage(self, title=title, ns=ns, language=self.language)

    async def _query(self, page: "WikipediaPage", params: dict[str, Any]):
        base_url = "https://" + page.language + ".wikipedia.org/w/api.php"
        log.info(
            "Request URL: %s",
            base_url + "?" + "&".join([k + "=" + str(v) for k, v in params.items()]),
        )
        params["format"] = "json"
        params["redirects"] = 1
        response = await treq.get(base_url, params=params, headers=self._headers, **self._request_kwargs)
        return await response.json()

    # Other methods (e.g., extracts, info, langlinks, etc.) should also be updated to use `await self._query(...)`
    # and be defined as `async def` to support asynchronous behavior.
