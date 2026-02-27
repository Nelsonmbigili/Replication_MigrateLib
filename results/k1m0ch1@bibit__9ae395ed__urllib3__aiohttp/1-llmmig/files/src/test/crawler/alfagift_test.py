import unittest
import aiohttp

class TestAlfagiftCrawler(unittest.IsolatedAsyncioTestCase):

    HOST = "https://webcommerce-gw.alfagift.id/v2"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Origin": "https://alfagift.id",
        "Referer": "https://alfagift.id/",
        "Devicemodel": "Chrome",
        "Devicetype": "Web",
        "Fingerprint": "5xJ5r/SKUXZKqQOBwVL9TS9r9MTR6B34kkwc3Qaivyao4H6445IWBgP8TNRWiTjs"
    }

    async def getCatalog(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.HOST}/categories", headers=self.HEADERS) as response:
                response_data = await response.json()
                categories = []

                for category in response_data['categories']:
                    categories.append(category['categoryId'])
                    if category['subCategories'] is not None:
                        for cat in category['subCategories']:
                            categories.append(cat['categoryId'])
                            if cat['subCategories'] is not None:
                                for c in cat['subCategories']:
                                    categories.append(c['categoryId'])
                return categories

    async def test_host_alive(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.HOST}/categories", headers=self.HEADERS) as response:
                self.assertEqual(response.status, 200, "Should be HTTP Code 200")

    async def test_get_catalog(self):
        categories = await self.getCatalog()
        self.assertEqual(len(categories) > 1, True, "The return suppose to be more than 1")

if __name__ == '__main__':
    unittest.main()
