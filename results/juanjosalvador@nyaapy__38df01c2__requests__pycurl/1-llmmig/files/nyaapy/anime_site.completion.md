### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` with `pycurl`**:
   - `pycurl` requires setting up a `pycurl.Curl` object, configuring it with the URL, and capturing the response in a buffer.
   - The `pycurl` equivalent of `requests.get` involves setting the `CURLOPT_URL` option and using a `BytesIO` buffer to capture the response.
2. **Error Handling**:
   - `requests` provides `raise_for_status()` to handle HTTP errors. In `pycurl`, we manually check the HTTP status code using `curl.getinfo(pycurl.RESPONSE_CODE)`.
3. **Response Content**:
   - `requests` provides `r.text` and `r.content` for response data. In `pycurl`, the response is captured in a `BytesIO` buffer, and we decode it to get the text or use the raw bytes as needed.
4. **Replaced all instances of `requests.get`**:
   - Each `requests.get` call was replaced with the equivalent `pycurl` implementation.

Below is the modified code.

---

### Modified Code
```python
import pycurl
from io import BytesIO
from nyaapy import torrent
from nyaapy.parser import parse_nyaa, parse_single, parse_nyaa_rss


class AnimeTorrentSite:
    SITE = torrent.TorrentSite.NYAASI
    URL = "https://nyaa.si"

    @staticmethod
    def _pycurl_get(url):
        """Helper method to perform a GET request using pycurl."""
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.FOLLOWLOCATION, True)  # Follow redirects
        curl.perform()

        # Check HTTP status code
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        if status_code != 200:
            raise Exception(f"HTTP request failed with status code {status_code}")

        curl.close()
        return buffer.getvalue()

    @classmethod
    def last_uploads(self, number_of_results: int):
        response_content = self._pycurl_get(self.URL)

        # Parse the response content
        json_data = parse_nyaa(
            request_text=response_content.decode("utf-8"),
            limit=number_of_results,
            site=self.SITE,
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

        response_content = self._pycurl_get(search_uri)

        if user:
            json_data = parse_nyaa(
                request_text=response_content.decode("utf-8"),
                limit=None,
                site=self.SITE,
            )
        else:
            json_data = parse_nyaa_rss(
                request_text=response_content.decode("utf-8"),
                limit=None,
                site=self.SITE,
            )

        # Convert JSON data to a class object
        return torrent.json_to_class(json_data)

    @classmethod
    def get(self, view_id: int):
        response_content = self._pycurl_get(f"{self.URL}/view/{view_id}")

        json_data = parse_single(
            request_text=response_content.decode("utf-8"), site=self.SITE
        )

        return torrent.json_to_class(json_data)

    @classmethod
    def get_from_user(self, username):
        response_content = self._pycurl_get(f"{self.URL}/user/{username}")

        json_data = parse_nyaa(
            request_text=response_content.decode("utf-8"), limit=None, site=self.SITE
        )
        return torrent.json_to_class(json_data)
```

---

### Key Notes:
1. **Helper Method `_pycurl_get`**:
   - A helper method was added to encapsulate the `pycurl` GET request logic. This avoids duplicating the setup and teardown of `pycurl.Curl` objects.
2. **Error Handling**:
   - HTTP errors are manually checked using the `RESPONSE_CODE` from `pycurl`.
3. **Response Decoding**:
   - The response content is captured as bytes in a `BytesIO` buffer and decoded to a string (`utf-8`) where necessary.

This ensures the functionality remains consistent while using `pycurl` instead of `requests`.