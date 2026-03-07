### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several changes were made:

1. **Importing PyCurl**: The `requests` library was replaced with `pycurl`. The `pycurl` library requires a different approach for making HTTP requests.
  
2. **Request Method**: The `request` method was modified to use `pycurl` for making GET and POST requests. This involves setting up a `pycurl.Curl` object, configuring it with the appropriate options, and handling the response differently than with `requests`.

3. **Response Handling**: The response from `pycurl` is captured in a buffer instead of being returned directly. The response data is then decoded from bytes to a string and parsed as JSON.

4. **Error Handling**: The error handling was adjusted to work with `pycurl`, which raises exceptions differently than `requests`.

Here is the modified code:

```python
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urljoin
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

    def request(self, url, method, params=None):
        """Send an API request to open Engage."""
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.TIMEOUT, 10)

        if method.casefold() == "get":
            if params:
                url += '?' + '&'.join([f"{key}={value}" for key, value in params.items()])
            c.setopt(c.CUSTOMREQUEST, 'GET')
        elif method.casefold() == "post":
            c.setopt(c.POSTFIELDS, json.dumps(params))
            c.setopt(c.HTTPHEADER, ['Content-Type: application/json'])
            c.setopt(c.CUSTOMREQUEST, 'POST')
        else:
            raise ConnectionError(f"Unknown method for query: {method}")

        try:
            c.perform()
        except pycurl.error as e:
            raise ConnectionError(f"Request failed: {e}")

        response_data = buffer.getvalue().decode('utf-8')
        c.close()
        return json.loads(response_data)

    def query(self, query, method="get", params=None):
        """Perform a direct query."""

        r = self.request(urljoin(self.base, query), method, params=params)
        return r

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
            if 'message' in r and r.get("status") == 400:
                raise ValueError(r["message"])
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