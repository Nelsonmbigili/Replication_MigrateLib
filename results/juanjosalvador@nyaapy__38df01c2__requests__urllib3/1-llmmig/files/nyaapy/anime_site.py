import urllib3
from nyaapy import torrent
from nyaapy.parser import parse_nyaa, parse_single, parse_nyaa_rss


class AnimeTorrentSite:
    SITE = torrent.TorrentSite.NYAASI
    URL = "https://nyaa.si"
    http = urllib3.PoolManager()  # Create a PoolManager instance for HTTP requests

    @classmethod
    def last_uploads(self, number_of_results: int):
        r = self.http.request("GET", self.URL)

        # If anything up with nyaa servers let the user know.
        if r.status != 200:
            raise urllib3.exceptions.HTTPError(f"HTTP request failed with status {r.status}")

        json_data = parse_nyaa(
            request_text=r.data.decode("utf-8"), limit=number_of_results, site=self.SITE
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

        http_response = self.http.request("GET", search_uri)
        if http_response.status != 200:
            raise urllib3.exceptions.HTTPError(f"HTTP request failed with status {http_response.status}")

        if user:
            json_data = parse_nyaa(
                request_text=http_response.data.decode("utf-8"), limit=None, site=self.SITE
            )
        else:
            json_data = parse_nyaa_rss(
                request_text=http_response.data.decode("utf-8"), limit=None, site=self.SITE
            )

        # Convert JSON data to a class object
        return torrent.json_to_class(json_data)

    @classmethod
    def get(self, view_id: int):
        r = self.http.request("GET", f"{self.URL}/view/{view_id}")
        if r.status != 200:
            raise urllib3.exceptions.HTTPError(f"HTTP request failed with status {r.status}")

        json_data = parse_single(request_text=r.data.decode("utf-8"), site=self.SITE)

        return torrent.json_to_class(json_data)

    @classmethod
    def get_from_user(self, username):
        r = self.http.request("GET", f"{self.URL}/user/{username}")
        if r.status != 200:
            raise urllib3.exceptions.HTTPError(f"HTTP request failed with status {r.status}")

        json_data = parse_nyaa(request_text=r.data.decode("utf-8"), limit=None, site=self.SITE)
        return torrent.json_to_class(json_data)
