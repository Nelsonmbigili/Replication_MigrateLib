import aiohttp
from nyaapy import torrent
from nyaapy.parser import parse_nyaa, parse_single, parse_nyaa_rss


class AnimeTorrentSite:
    SITE = torrent.TorrentSite.NYAASI
    URL = "https://nyaa.si"

    @classmethod
    async def last_uploads(self, number_of_results: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.URL) as r:
                r.raise_for_status()
                json_data = parse_nyaa(
                    request_text=await r.text(), limit=number_of_results, site=self.SITE
                )

        return torrent.json_to_class(json_data)

    @classmethod
    async def search(self, keyword: str, **kwargs):
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

        async with aiohttp.ClientSession() as session:
            async with session.get(search_uri) as http_response:
                http_response.raise_for_status()

                if user:
                    json_data = parse_nyaa(
                        request_text=await http_response.read(), limit=None, site=self.SITE
                    )
                else:
                    json_data = parse_nyaa_rss(
                        request_text=await http_response.read(), limit=None, site=self.SITE
                    )

        # Convert JSON data to a class object
        return torrent.json_to_class(json_data)

    @classmethod
    async def get(self, view_id: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.URL}/view/{view_id}") as r:
                r.raise_for_status()
                json_data = parse_single(request_text=await r.read(), site=self.SITE)

        return torrent.json_to_class(json_data)

    @classmethod
    async def get_from_user(self, username):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.URL}/user/{username}") as r:
                r.raise_for_status()
                json_data = parse_nyaa(request_text=await r.read(), limit=None, site=self.SITE)
        
        return torrent.json_to_class(json_data)
