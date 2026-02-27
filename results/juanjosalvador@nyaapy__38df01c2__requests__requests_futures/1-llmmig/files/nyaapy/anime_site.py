from requests_futures.sessions import FuturesSession
from nyaapy import torrent
from nyaapy.parser import parse_nyaa, parse_single, parse_nyaa_rss


class AnimeTorrentSite:
    SITE = torrent.TorrentSite.NYAASI
    URL = "https://nyaa.si"
    session = FuturesSession()  # Initialize a FuturesSession for asynchronous requests

    @classmethod
    def last_uploads(self, number_of_results: int):
        future = self.session.get(self.URL)  # Use session.get instead of requests.get
        r = future.result()  # Retrieve the actual response object

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

        future = self.session.get(search_uri)  # Use session.get instead of requests.get
        http_response = future.result()  # Retrieve the actual response object
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
        future = self.session.get(f"{self.URL}/view/{view_id}")  # Use session.get
        r = future.result()  # Retrieve the actual response object
        r.raise_for_status()

        json_data = parse_single(request_text=r.content, site=self.SITE)

        return torrent.json_to_class(json_data)

    @classmethod
    def get_from_user(self, username):
        future = self.session.get(f"{self.URL}/user/{username}")  # Use session.get
        r = future.result()  # Retrieve the actual response object
        r.raise_for_status()

        json_data = parse_nyaa(request_text=r.content, limit=None, site=self.SITE)
        return torrent.json_to_class(json_data)
