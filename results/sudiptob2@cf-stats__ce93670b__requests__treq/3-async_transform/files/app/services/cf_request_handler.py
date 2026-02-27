import treq
import asyncio

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    @classmethod
    async def _get_user_info(cls):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        try:
            response = await treq.get(url)
            response_json = await response.json()
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_info = response_json.get('result')[0]

    @classmethod
    async def _get_user_sub(cls):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        try:
            response = await treq.get(url)
            response_json = await response.json()
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_submission = response_json.get('result')

    @classmethod
    async def _get_rating_changes(cls):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        try:
            response = await treq.get(url)
            response_json = await response.json()
        except Exception:
            raise SystemExit('Could not connect to the codeforces API')
        cls.rating_changes = response_json.get('result')

    @staticmethod
    async def make_request():
        """Makes all the necessary requests to cf API."""
        await CFRequestHandler._get_user_info()
        await CFRequestHandler._get_user_sub()
        await CFRequestHandler._get_rating_changes()
