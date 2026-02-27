### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` and `requests.post`**:
   - `pycurl` does not have high-level methods like `get` or `post`. Instead, it uses a lower-level interface where you configure the HTTP method, URL, headers, and other options manually.
   - For `GET` requests, the URL is set directly, and query parameters are appended to the URL.
   - For `POST` requests, the payload is sent as JSON using the `CURLOPT_POSTFIELDS` option.
2. **Replaced `requests` timeout**:
   - The `CURLOPT_TIMEOUT` option in `pycurl` is used to set the timeout.
3. **Replaced `requests` response handling**:
   - `pycurl` writes the response to a buffer, which is then read and parsed as JSON.
4. **Error handling**:
   - `pycurl` does not raise exceptions for HTTP status codes. Instead, the HTTP status code is manually checked after the request.
5. **Added a helper function**:
   - A helper function `perform_request` was added to encapsulate the common logic for making `pycurl` requests and handling responses.

### Modified Code
```python
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urljoin, urlencode
import pycurl
import json
from io import BytesIO

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

now_datetime = datetime.now()
launch_dates = {"chemrxiv": "2017-01-01"}


class ChemrxivAPI:
    """Handle OpenEngage API requests, using access.
    Adapted from https://github.com/fxcoudert/tools/blob/master/chemRxiv/chemRxiv.py.
    """

    base = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/"

    def __init__(
        self,
        begin_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page_size: Optional[int] = None,
    ):
        """
        Initialize API class.

        Args:
            begin_date (Optional[str], optional): begin date expressed as YYYY-MM-DD.
                Defaults to None.
            end_date (Optional[str], optional): end date expressed as YYYY-MM-DD.
                Defaults to None.
            page_size (int, optional): The batch size used to fetch the records from chemrxiv.
        """

        self.page_size = page_size or 50

        # Begin Date and End Date of the search
        launch_date = launch_dates["chemrxiv"]
        launch_datetime = datetime.fromisoformat(launch_date)

        if begin_date:
            begin_datetime = datetime.fromisoformat(begin_date)
            if begin_datetime < launch_datetime:
                self.begin_date = launch_date
                logger.warning(
                    f"Begin date {begin_date} is before chemrxiv launch date. Will use {launch_date} instead."
                )
            else:
                self.begin_date = begin_date
        else:
            self.begin_date = launch_date
        if end_date:
            end_datetime = datetime.fromisoformat(end_date)
            if end_datetime > now_datetime:
                logger.warning(
                    f"End date {end_date} is in the future. Will use {now_datetime} instead."
                )
                self.end_date = now_datetime.strftime("%Y-%m-%d")
            else:
                self.end_date = end_date
        else:
            self.end_date = now_datetime.strftime("%Y-%m-%d")

    def perform_request(self, url, method, params=None):
        """Helper function to perform a pycurl request."""
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
        curl.setopt(pycurl.TIMEOUT, 10)

        if method.casefold() == "post":
            curl.setopt(pycurl.POST, 1)
            if params:
                curl.setopt(pycurl.POSTFIELDS, json.dumps(params))
            curl.setopt(pycurl.HTTPHEADER, ["Content-Type: application/json"])
        elif method.casefold() == "get" and params:
            query_string = urlencode(params)
            curl.setopt(pycurl.URL, f"{url}?{query_string}")

        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()

        if status_code >= 400:
            raise ConnectionError(f"HTTP Error {status_code} for URL: {url}")

        response_data = buffer.getvalue().decode("utf-8")
        return json.loads(response_data)

    def request(self, url, method, params=None):
        """Send an API request to open Engage."""
        return self.perform_request(url, method, params)

    def query(self, query, method="get", params=None):
        """Perform a direct query."""
        response = self.request(urljoin(self.base, query), method, params=params)
        return response

    def query_generator(self, query, method: str = "get", params: Dict = {}):
        """Query for a list of items, with paging. Returns a generator."""

        page = 0
        while True:
            params.update(
                {
                    "limit": self.page_size,
                    "skip": page * self.page_size,
                    "searchDateFrom": self.begin_date,
                    "searchDateTo": self.end_date,
                }
            )
            response = self.request(urljoin(self.base, query), method, params=params)
            if "itemHits" not in response or len(response["itemHits"]) == 0:
                return

            yield from response["itemHits"]
            page += 1

    def all_preprints(self):
        """Return a generator to all the chemRxiv articles."""
        return self.query_generator("items")

    def preprint(self, article_id):
        """Information on a given preprint.
        .. seealso:: https://docs.figshare.com/#public_article
        """
        return self.query(os.path.join("items", article_id))

    def number_of_preprints(self):
        return self.query("items")["totalCount"]
```

### Key Notes
- The `perform_request` function encapsulates the logic for making `pycurl` requests, handling both `GET` and `POST` methods.
- The `pycurl` library requires more manual configuration compared to `requests`, but the functionality remains equivalent.
- The error handling for HTTP status codes is implemented manually since `pycurl` does not raise exceptions for non-2xx responses.