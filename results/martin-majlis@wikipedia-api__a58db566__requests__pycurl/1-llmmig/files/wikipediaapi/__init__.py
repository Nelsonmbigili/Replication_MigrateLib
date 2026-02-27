import pycurl
from io import BytesIO
import json

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
        :param kwargs: Optional parameters used in HTTP requests
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

        # Initialize pycurl.Curl object
        self._curl = pycurl.Curl()
        self._curl.setopt(pycurl.USERAGENT, default_headers["User-Agent"])
        self._curl.setopt(pycurl.TIMEOUT, int(kwargs["timeout"]))
        self._headers = default_headers
        self._request_kwargs = kwargs

    def __del__(self) -> None:
        """Closes the Curl object."""
        if hasattr(self, "_curl") and self._curl:
            self._curl.close()

    def _query(self, page: "WikipediaPage", params: dict[str, Any]):
        """Queries Wikimedia API to fetch content using pycurl."""
        base_url = "https://" + page.language + ".wikipedia.org/w/api.php"
        log.info(
            "Request URL: %s",
            base_url + "?" + "&".join([k + "=" + str(v) for k, v in params.items()]),
        )
        params["format"] = "json"
        params["redirects"] = 1

        # Build the full URL with query parameters
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{base_url}?{query_string}"

        # Prepare a buffer to capture the response
        response_buffer = BytesIO()

        # Set pycurl options
        self._curl.setopt(pycurl.URL, full_url)
        self._curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)

        # Perform the request
        try:
            self._curl.perform()
        except pycurl.error as e:
            log.error("PycURL error: %s", e)
            raise RuntimeError(f"PycURL error: {e}")

        # Get the response data
        response_data = response_buffer.getvalue().decode("utf-8")
        response_buffer.close()

        # Parse the JSON response
        try:
            return json.loads(response_data)
        except json.JSONDecodeError as e:
            log.error("Failed to parse JSON response: %s", e)
            raise RuntimeError(f"Failed to parse JSON response: {e}")
