import unittest

from sleeper.api import (
    get_draft,
    get_drafts_in_league,
    get_player_draft_picks,
    get_traded_draft_picks,
    get_user_drafts_for_year,
)
from test.integration.test_api.constants import (
    LEAGUE_A_DRAFT_1,
    LEAGUE_A_DRAFT_ID_1,
    LEAGUE_A_DRAFT_ID_2,
    LEAGUE_A_DRAFT_ID_2_TRADED_PICKS,
    LEAGUE_A_DRAFTS,
    LEAGUE_A_LEAGUE_ID,
    USER_A_DRAFT_PICKS_DRAFT_ID_1_2023,
    USER_A_DRAFTS_2023,
    USER_A_USER_ID,
)
import pytest


class TestDraft(unittest.TestCase):
    @pytest.mark.asyncio
    async def test_get_user_drafts_for_year_happy_path(self):
        response = await get_user_drafts_for_year(
            user_id=USER_A_USER_ID, sport="nfl", year=2023
        )
        self.assertEqual(USER_A_DRAFTS_2023, response)

    @pytest.mark.asyncio
    async def test_get_drafts_in_league(self):
        response = await get_drafts_in_league(league_id=LEAGUE_A_LEAGUE_ID)
        self.assertEqual(LEAGUE_A_DRAFTS, response)

    @pytest.mark.asyncio
    async def test_get_draft(self):
        response = await get_draft(draft_id=LEAGUE_A_DRAFT_ID_1)
        self.assertEqual(LEAGUE_A_DRAFT_1, response)

    @pytest.mark.asyncio
    async def test_get_player_draft_picks(self):
        response = await get_player_draft_picks(
            draft_id=LEAGUE_A_DRAFT_ID_1,
        )
        self.assertEqual(USER_A_DRAFT_PICKS_DRAFT_ID_1_2023, response)

    @pytest.mark.asyncio
    async def test_get_traded_draft_picks(self):
        response = await get_traded_draft_picks(draft_id=LEAGUE_A_DRAFT_ID_2)
        self.assertEqual(LEAGUE_A_DRAFT_ID_2_TRADED_PICKS, response)
