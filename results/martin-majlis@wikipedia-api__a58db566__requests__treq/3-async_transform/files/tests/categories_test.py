import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi
import pytest


class TestCategories(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request

    @pytest.mark.asyncio
    async def test_categories_count(self):
        page = await self.wiki.page("Test_1")
        self.assertEqual(len(page.categories), 3)

    @pytest.mark.asyncio
    async def test_categories_titles(self):
        page = await self.wiki.page("Test_1")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.categories.values()))),
            ["Category:C" + str(i + 1) for i in range(3)],
        )

    @pytest.mark.asyncio
    async def test_categories_nss(self):
        page = await self.wiki.page("Test_1")
        self.assertEqual(
            list(sorted(map(lambda s: s.ns, page.categories.values()))), [14] * 3
        )

    @pytest.mark.asyncio
    async def test_no_categories_count(self):
        page = await self.wiki.page("No_Categories")
        self.assertEqual(len(page.categories), 0)
