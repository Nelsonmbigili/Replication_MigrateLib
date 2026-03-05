import pycurl
from io import BytesIO
from nyaapy import torrent
from nyaapy.parser import parse_nyaa, parse_single, parse_nyaa_rss


class AnimeTorrentSite:
    SITE = torrent.TorrentSite.NYAASI
    URL = "https://nyaa.si"

    @classmethod
    def last_uploads(self, number_of_results: int):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.URL)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        if c.getinfo(c.RESPONSE_CODE) != 200:
            raise Exception("Failed to fetch data from nyaa servers.")

        c.close()
        json_data = parse_nyaa(
            request_text=buffer.getvalue().decode('utf-8'), limit=number_of_results, site=self.SITE
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

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, search_uri)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        if c.getinfo(c.RESPONSE_CODE) != 200:
            raise Exception("Failed to fetch data from nyaa servers.")

        c.close()

        if user:
            json_data = parse_nyaa(
                request_text=buffer.getvalue(), limit=None, site=self.SITE
            )
        else:
            json_data = parse_nyaa_rss(
                request_text=buffer.getvalue(), limit=None, site=self.SITE
            )

        # Convert JSON data to a class object
        return torrent.json_to_class(json_data)

    @classmethod
    def get(self, view_id: int):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, f"{self.URL}/view/{view_id}")
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        if c.getinfo(c.RESPONSE_CODE) != 200:
            raise Exception("Failed to fetch data from nyaa servers.")

        c.close()
        json_data = parse_single(request_text=buffer.getvalue(), site=self.SITE)

        return torrent.json_to_class(json_data)

    @classmethod
    def get_from_user(self, username):
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, f"{self.URL}/user/{username}")
        c.setopt(c.WRITEDATA, buffer)
        c.perform()

        if c.getinfo(c.RESPONSE_CODE) != 200:
            raise Exception("Failed to fetch data from nyaa servers.")

        c.close()
        json_data = parse_nyaa(request_text=buffer.getvalue(), limit=None, site=self.SITE)
        return torrent.json_to_class(json_data)
