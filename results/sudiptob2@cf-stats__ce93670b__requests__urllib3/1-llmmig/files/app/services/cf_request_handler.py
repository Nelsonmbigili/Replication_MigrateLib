import urllib3
import json

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    # Create a PoolManager instance for making HTTP requests
    http = urllib3.PoolManager()

    @classmethod
    def _get_user_info(cls):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        try:
            response = cls.http.request("GET", url)
        except urllib3.exceptions.HTTPError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_info = json.loads(response.data.decode('utf-8')).get('result')[0]

    @classmethod
    def _get_user_sub(cls):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        try:
            response = cls.http.request("GET", url)
        except urllib3.exceptions.HTTPError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.user_submission = json.loads(response.data.decode('utf-8')).get('result')

    @classmethod
    def _get_rating_changes(cls):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        try:
            response = cls.http.request("GET", url)
        except urllib3.exceptions.HTTPError:
            raise SystemExit('Could not connect to the codeforces API')
        cls.rating_changes = json.loads(response.data.decode('utf-8')).get('result')

    @staticmethod
    def make_request():
        """Makes all the necessary requests to cf API."""
        CFRequestHandler._get_user_info()
        CFRequestHandler._get_user_sub()
        CFRequestHandler._get_rating_changes()
