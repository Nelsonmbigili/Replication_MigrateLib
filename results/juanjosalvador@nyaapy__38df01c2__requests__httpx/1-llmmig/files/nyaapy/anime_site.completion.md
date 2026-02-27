### Explanation of Changes
To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: The `requests` library was replaced with `httpx`.
2. **HTTP Methods**: The `httpx` library uses the same method names (`get`, `post`, etc.) as `requests`, so the method calls remain the same.
3. **Response Content**: The `httpx` response object uses `.text` and `.content` in the same way as `requests`, so no changes were needed for accessing response data.
4. **Error Handling**: The `raise_for_status()` method is also available in `httpx`, so no changes were needed for error handling.
5. **Session Management**: Since the code does not use sessions, no additional changes were required.

Below is the modified code using `httpx`.

---

### Modified Code
```python
import httpx
from nyaapy import torrent
from nyaapy.parser import parse_nyaa, parse_single, parse_nyaa_rss


class AnimeTorrentSite:
    SITE = torrent.TorrentSite.NYAASI
    URL = "https://nyaa.si"

    @classmethod
    def last_uploads(self, number_of_results: int):
        r = httpx.get(self.URL)

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

        http_response = httpx.get(search_uri)
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
        r = httpx.get(f"{self.URL}/view/{view_id}")
        r.raise_for_status()

        json_data = parse_single(request_text=r.content, site=self.SITE)

        return torrent.json_to_class(json_data)

    @classmethod
    def get_from_user(self, username):
        r = httpx.get(f"{self.URL}/user/{username}")
        r.raise_for_status()

        json_data = parse_nyaa(request_text=r.content, limit=None, site=self.SITE)
        return torrent.json_to_class(json_data)
```

---

### Summary
The migration from `requests` to `httpx` was straightforward because both libraries share similar APIs for basic HTTP operations. The changes were limited to replacing `requests` with `httpx` in the import statement and method calls. No additional modifications were necessary.