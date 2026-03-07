### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `requests` library was replaced with `urllib3`. The `requests` library is a higher-level abstraction over HTTP requests, while `urllib3` is a lower-level library that requires more manual handling of connections and responses.

2. **Creating a PoolManager**: A `PoolManager` instance from `urllib3` was created to manage connections. This is necessary because `urllib3` does not automatically handle connection pooling like `requests`.

3. **Making Requests**: The `requests.get` and `requests.post` methods were replaced with `http.request` method calls. The parameters for these methods were adjusted to fit the `urllib3` API.

4. **Handling Responses**: The response handling was modified to access the response data and status code directly from the `urllib3` response object.

5. **Error Handling**: The error handling for HTTP status codes was adjusted to use `urllib3`'s response attributes.

Here is the modified code:

```python
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urljoin
import urllib3
import json

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
        self.http = urllib3.PoolManager()

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

    def request(self, url, method, params=None):
        """Send an API request to open Engage."""

        if method.casefold() == "get":
            response = self.http.request("GET", url, fields=params, timeout=10)
        elif method.casefold() == "post":
            response = self.http.request("POST", url, body=json.dumps(params), headers={'Content-Type': 'application/json'}, timeout=10)
        else:
            raise ConnectionError(f"Unknown method for query: {method}")

        return response

    def query(self, query, method="get", params=None):
        """Perform a direct query."""

        r = self.request(urljoin(self.base, query), method, params=params)
        if r.status != 200:
            raise ConnectionError(f"Request failed with status {r.status}")
        return json.loads(r.data)

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
            r = self.request(urljoin(self.base, query), method, params=params)
            if r.status == 400:
                raise ValueError(json.loads(r.data)["message"])
            if r.status != 200:
                raise ConnectionError(f"Request failed with status {r.status}")
            r = json.loads(r.data)
            r = r["itemHits"]

            # If we have no more results, bail out
            if len(r) == 0:
                return

            yield from r
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