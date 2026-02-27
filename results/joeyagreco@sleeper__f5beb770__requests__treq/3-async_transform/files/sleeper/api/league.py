from sleeper.api._constants import (
    LEAGUE_ROUTE,
    LEAGUES_ROUTE,
    LOSERS_BRACKET_ROUTE,
    MATCHUPS_ROUTE,
    ROSTERS_ROUTE,
    SLEEPER_APP_BASE_URL,
    STATE_ROUTE,
    TRADED_PICKS_ROUTE,
    TRANSACTIONS_ROUTE,
    USER_ROUTE,
    USERS_ROUTE,
    VERSION,
    WINNERS_BRACKET_ROUTE,
)
from sleeper.api._types import Sport
from sleeper.api._utils import build_route, get


async def get_league(*, league_id: str) -> dict:
    return await get(build_route(SLEEPER_APP_BASE_URL, VERSION, LEAGUE_ROUTE, league_id))


async def get_user_leagues_for_year(*, user_id: str, sport: Sport, year: int) -> list[dict]:
    return await get(
        build_route(
            SLEEPER_APP_BASE_URL,
            VERSION,
            USER_ROUTE,
            user_id,
            LEAGUES_ROUTE,
            sport,
            year,
        )
    )


async def get_rosters(*, league_id: str) -> list[dict]:
    return await get(
        build_route(
            SLEEPER_APP_BASE_URL,
            VERSION,
            LEAGUE_ROUTE,
            league_id,
            ROSTERS_ROUTE,
        )
    )


async def get_users_in_league(*, league_id: str) -> list[dict]:
    return await get(
        build_route(
            SLEEPER_APP_BASE_URL,
            VERSION,
            LEAGUE_ROUTE,
            league_id,
            USERS_ROUTE,
        )
    )


async def get_matchups_for_week(*, league_id: str, week: int) -> list[dict]:
    return await get(
        build_route(
            SLEEPER_APP_BASE_URL,
            VERSION,
            LEAGUE_ROUTE,
            league_id,
            MATCHUPS_ROUTE,
            week,
        )
    )


async def get_winners_bracket(*, league_id: str) -> list[dict]:
    return await get(
        build_route(
            SLEEPER_APP_BASE_URL,
            VERSION,
            LEAGUE_ROUTE,
            league_id,
            WINNERS_BRACKET_ROUTE,
        )
    )


async def get_losers_bracket(*, league_id: str) -> list[dict]:
    return await get(
        build_route(
            SLEEPER_APP_BASE_URL,
            VERSION,
            LEAGUE_ROUTE,
            league_id,
            LOSERS_BRACKET_ROUTE,
        )
    )


async def get_transactions(*, league_id: str, week: int) -> list[dict]:
    return await get(
        build_route(
            SLEEPER_APP_BASE_URL,
            VERSION,
            LEAGUE_ROUTE,
            league_id,
            TRANSACTIONS_ROUTE,
            week,
        )
    )


async def get_traded_picks(*, league_id: str) -> list[dict]:
    return await get(
        build_route(
            SLEEPER_APP_BASE_URL,
            VERSION,
            LEAGUE_ROUTE,
            league_id,
            TRADED_PICKS_ROUTE,
        )
    )


async def get_sport_state(sport: Sport) -> dict:
    return await get(build_route(SLEEPER_APP_BASE_URL, VERSION, STATE_ROUTE, sport))
