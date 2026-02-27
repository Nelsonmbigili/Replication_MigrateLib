### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Session Management**: `requests.Session` was replaced with `pycurl`'s direct usage for HTTP requests. `pycurl` does not have a session concept like `requests`, so each request is handled independently.
2. **GET Requests**: The `_get_sync` method was rewritten to use `pycurl` for making HTTP GET requests. The response is captured using a `BytesIO` buffer.
3. **Error Handling**: `pycurl` does not raise exceptions for HTTP status codes (e.g., 404, 500). Instead, the HTTP status code is manually checked after the request.
4. **Response Parsing**: The response data is read from the `BytesIO` buffer and decoded into a string before being parsed as JSON.

### Modified Code:
Below is the updated code with the necessary changes to replace `requests` with `pycurl`.

```python
import pycurl
from io import BytesIO
from urllib.parse import urljoin
import json
import asyncio
import datetime
import aiohttp

from .settings import supported_api_versions

class HackerNewsError(Exception):
    pass


class InvalidItemID(HackerNewsError):
    pass


class InvalidUserID(HackerNewsError):
    pass


class InvalidAPIVersion(HackerNewsError):
    pass


class HTTPError(HackerNewsError):
    pass


class HackerNews(object):

    def __init__(self, version='v0'):
        """
        Args:
            version (string): specifies Hacker News API version.
            Default is `v0`.

        Raises:
          InvalidAPIVersion: If Hacker News version is not supported.
        """
        try:
            self.base_url = supported_api_versions[version]
        except KeyError:
            raise InvalidAPIVersion
        self.item_url = urljoin(self.base_url, 'item/')
        self.user_url = urljoin(self.base_url, 'user/')

    def _get_sync(self, url):
        """Internal method used for GET requests

        Args:
            url (str): URL to fetch

        Returns:
            Individual URL request's response

        Raises:
          HTTPError: If HTTP request failed.
        """
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.TIMEOUT, 10)

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
            curl.close()

            if status_code == 200:
                response_data = buffer.getvalue().decode('utf-8')
                return json.loads(response_data)
            else:
                raise HTTPError(f"HTTP request failed with status code {status_code}")
        except pycurl.error as e:
            curl.close()
            raise HTTPError(f"HTTP request failed: {e}")

    async def _get_async(self, url, session):
        """Asynchronous internal method used for GET requests

        Args:
            url (str): URL to fetch
            session (obj): aiohttp client session for async loop

        Returns:
            data (obj): Individual URL request's response coroutine
        """
        data = None
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
        return data

    async def _async_loop(self, urls):
        """Asynchronous internal method used to request multiple URLs

        Args:
            urls (list): URLs to fetch

        Returns:
            responses (obj): All URL requests' response coroutines
        """
        results = []
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        ) as session:
            for url in urls:
                result = asyncio.ensure_future(self._get_async(url, session))
                results.append(result)
            responses = await asyncio.gather(*results)
        return responses

    def _run_async(self, urls):
        """Asynchronous event loop execution

        Args:
            urls (list): URLs to fetch

        Returns:
            results (obj): All URL requests' responses
        """
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self._async_loop(urls))
        return results

    def _get_stories(self, page, limit):
        """
        Hacker News has different categories (i.e. stories) like
        'topstories', 'newstories', 'askstories', 'showstories', 'jobstories'.
        This method, first fetches the relevant story ids of that category

        The URL is: https://hacker-news.firebaseio.com/v0/<story_name>.json

        e.g. https://hacker-news.firebaseio.com/v0/topstories.json

        Then, asynchronously it fetches each story and returns the Item objects

        The URL for individual story is:
            https://hacker-news.firebaseio.com/v0/item/<item_id>.json

        e.g. https://hacker-news.firebaseio.com/v0/item/69696969.json
        """
        url = urljoin(self.base_url, F"{page}.json")
        story_ids = self._get_sync(url)[:limit]
        return self.get_items_by_ids(item_ids=story_ids)

    def get_item(self, item_id, expand=False):
        """Returns Hacker News `Item` object.

        Fetches the data from url:
            https://hacker-news.firebaseio.com/v0/item/<item_id>.json

        e.g. https://hacker-news.firebaseio.com/v0/item/69696969.json

        Args:
            item_id (int or string): Unique item id of Hacker News story,
            comment etc.
            expand (bool): expand (bool): Flag to indicate whether to
                transform all IDs into objects.

        Returns:
            `Item` object representing Hacker News item.

        Raises:
          InvalidItemID: If corresponding Hacker News story does not exist.
        """
        url = urljoin(self.item_url, F"{item_id}.json")
        response = self._get_sync(url)

        if not response:
            raise InvalidItemID

        item = Item(response)
        if expand:
            item.by = self.get_user(item.by)
            item.kids = self.get_items_by_ids(item.kids) if item.kids else None
            item.parent = self.get_item(item.parent) if item.parent else None
            item.poll = self.get_item(item.poll) if item.poll else None
            item.parts = (
                self.get_items_by_ids(item.parts) if item.parts else None
            )

        return item

    def get_items_by_ids(self, item_ids, item_type=None):
        """Given a list of item ids, return all the Item objects

        Args:
            item_ids (obj): List of item IDs to query
            item_type (str): (optional) Item type to filter results with

        Returns:
            List of `Item` objects for given item IDs and given item type
        """
        urls = [urljoin(self.item_url, F"{i}.json") for i in item_ids]
        result = self._run_async(urls=urls)
        items = [Item(r) for r in result if r]
        if item_type:
            return [item for item in items if item.item_type == item_type]
        else:
            return items

    def get_user(self, user_id, expand=False):
        """Returns Hacker News `User` object.

        Fetches data from the url:
            https://hacker-news.firebaseio.com/v0/user/<user_id>.json

        e.g. https://hacker-news.firebaseio.com/v0/user/pg.json

        Args:
            user_id (string): unique user id of a Hacker News user.
            expand (bool): Flag to indicate whether to
                transform all IDs into objects.

        Returns:
            `User` object representing a user on Hacker News.

        Raises:
          InvalidUserID: If no such user exists on Hacker News.
        """
        url = urljoin(self.user_url, F"{user_id}.json")
        response = self._get_sync(url)

        if not response:
            raise InvalidUserID

        user = User(response)
        if expand and user.submitted:
            items = self.get_items_by_ids(user.submitted)
            user_opt = {
                'stories': 'story',
                'comments': 'comment',
                'jobs': 'job',
                'polls': 'poll',
                'pollopts': 'pollopt'
            }
            for key, value in user_opt.items():
                setattr(
                    user,
                    key,
                    [i for i in items if i.item_type == value]
                )

        return user
```

### Key Notes:
- The `_get_sync` method now uses `pycurl` to perform synchronous HTTP GET requests.
- The asynchronous methods (`_get_async`, `_async_loop`) remain unchanged as they rely on `aiohttp`, which is still compatible with the rest of the code.
- The `pycurl` library requires explicit management of HTTP requests, which is why a `BytesIO` buffer is used to capture the response.