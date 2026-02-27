import unittest

from tests.mock_data import user_agent
from tests.mock_data import wikipedia_api_request
import wikipediaapi
import pytest


class TestCategoryMembers(unittest.TestCase):
    def setUp(self):
        self.wiki = wikipediaapi.Wikipedia(user_agent, "en")
        self.wiki._query = wikipedia_api_request

    @pytest.mark.asyncio
    async def test_links_single_page_count(self):
        page = await self.wiki.page("Category:C1")
        self.assertEqual(len(page.categorymembers), 3)

    @pytest.mark.asyncio
    async def test_links_single_page_titles(self):
        page = await self.wiki.page("Category:C1")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.categorymembers.values()))),
            ["Title - " + str(i + 1) for i in range(3)],
        )

    @pytest.mark.asyncio
    async def test_links_multi_page_count(self):
        page = await self.wiki.page("Category:C2")
        self.assertEqual(len(page.categorymembers), 5)

    @pytest.mark.asyncio
    async def test_links_multi_page_titles(self):
        page = await self.wiki.page("Category:C2")
        self.assertEqual(
            list(sorted(map(lambda s: s.title, page.categorymembers.values()))),
            ["Title - " + str(i + 1) for i in range(5)],
        )
