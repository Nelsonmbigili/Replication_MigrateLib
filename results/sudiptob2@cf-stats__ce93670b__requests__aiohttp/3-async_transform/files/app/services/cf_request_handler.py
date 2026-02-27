import aiohttp
import asyncio

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    @classmethod
    async def _get_user_info(cls, session):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = await response.json()
                cls.user_info = data.get('result')[0]
        except aiohttp.ClientError:
            raise SystemExit('Could not connect to the codeforces API')

    @classmethod
    async def _get_user_sub(cls, session):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = await response.json()
                cls.user_submission = data.get('result')
        except aiohttp.ClientError:
            raise SystemExit('Could not connect to the codeforces API')

    @classmethod
    async def _get_rating_changes(cls, session):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        try:
            async with session.get(url) as response:
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = await response.json()
                cls.rating_changes = data.get('result')
        except aiohttp.ClientError:
            raise SystemExit('Could not connect to the codeforces API')

    @staticmethod
    async def make_request():
        """Makes all the necessary requests to cf API."""
        async with aiohttp.ClientSession() as session:
            await CFRequestHandler._get_user_info(session)
            await CFRequestHandler._get_user_sub(session)
            await CFRequestHandler._get_rating_changes(session)

