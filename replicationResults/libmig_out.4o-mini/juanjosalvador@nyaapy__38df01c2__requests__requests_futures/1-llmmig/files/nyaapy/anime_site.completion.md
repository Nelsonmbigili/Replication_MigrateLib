### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The `requests` library was replaced with `requests_futures.sessions`. This allows us to use the `FuturesSession` class, which provides asynchronous capabilities.
  
2. **Session Creation**: Instead of directly calling `requests.get()`, we create an instance of `FuturesSession` and use it to make the HTTP requests. This allows the requests to be executed in the background.

3. **Handling Responses**: Since the requests are now asynchronous, we need to access the `result()` method of the future object returned by the `FuturesSession` to get the actual response.

4. **Error Handling**: The error handling remains the same, but it is applied to the response obtained from the future.

Here is the modified code:

```python
import requests_futures.sessions
from nyaapy import torrent
from nyaapy.parser import parse_nyaa, parse_single, parse_nyaa_rss


class AnimeTorrentSite:
    SITE = torrent.TorrentSite.NYAASI
    URL = "https://nyaa.si"
    session = requests_futures.sessions.FuturesSession()

    @classmethod
    def last_uploads(self, number_of_results: int):
        future = self.session.get(self.URL)
        r = future.result()

        # If anything up with nyaa servers let the user know.
        r.raise_for_status()

        json_data = parse_nyaa(
            request_text=r.text, limit=number_of_results, site=self.SITE
        )

        return torrent.json_to_class(json_data)

    @classmethod
    def search(self, keyword: str, **kwargs):
        base_url = self.URL

        user = kwargs.get("user", None)
        category = kwargs.get("category", 0)
        subcategory = kwargs.get("subcategory", 0)
        filters = kwargs.get("filters", 0)
        page = kwargs.get("page", 0)
        sorting = kwargs.get(
            "sort", "id"
        )  # Sorting by id = sorting by date, this is the default.
        order = kwargs.get("order", "desc")

        user_uri = f"user/{user}" if user else ""

        if page > 0:
            search_uri = "{}/{}?f={}&c={}_{}&q={}&p={}&s={}&o={}".format(
                base_url,
                user_uri,
                filters,
                category,
                subcategory,
                keyword,
                page,
                sorting,
                order,
            )
        else:
            search_uri = "{}/{}?f={}&c={}_{}&q={}&s={}&o={}".format(
                base_url,
                user_uri,
                filters,
                category,
                subcategory,
                keyword,
                sorting,
                order,
            )

        if not user:
            search_uri += "&page=rss"

        future = self.session.get(search_uri)
        http_response = future.result()
        http_response.raise_for_status()

        if user:
            json_data = parse_nyaa(
                request_text=http_response.content, limit=None, site=self.SITE
            )
        else:
            json_data = parse_nyaa_rss(
                request_text=http_response.content, limit=None, site=self.SITE
            )

        # Convert JSON data to a class object
        return torrent.json_to_class(json_data)

    @classmethod
    def get(self, view_id: int):
        future = self.session.get(f"{self.URL}/view/{view_id}")
        r = future.result()
        r.raise_for_status()

        json_data = parse_single(request_text=r.content, site=self.SITE)

        return torrent.json_to_class(json_data)

    @classmethod
    def get_from_user(self, username):
        future = self.session.get(f"{self.URL}/user/{username}")
        r = future.result()
        r.raise_for_status()

        json_data = parse_nyaa(request_text=r.content, limit=None, site=self.SITE)
        return torrent.json_to_class(json_data)
``` 

This code now uses `requests_futures` to handle HTTP requests asynchronously while maintaining the original structure and functionality.