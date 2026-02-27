import pycurl
import json
from io import BytesIO

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    @classmethod
    def _get_user_info(cls):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        try:
            curl.perform()
        except pycurl.error:
            raise SystemExit('Could not connect to the codeforces API')
        finally:
            curl.close()
        response_data = buffer.getvalue().decode('utf-8')
        cls.user_info = json.loads(response_data).get('result')[0]

    @classmethod
    def _get_user_sub(cls):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        try:
            curl.perform()
        except pycurl.error:
            raise SystemExit('Could not connect to the codeforces API')
        finally:
            curl.close()
        response_data = buffer.getvalue().decode('utf-8')
        cls.user_submission = json.loads(response_data).get('result')

    @classmethod
    def _get_rating_changes(cls):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        try:
            curl.perform()
        except pycurl.error:
            raise SystemExit('Could not connect to the codeforces API')
        finally:
            curl.close()
        response_data = buffer.getvalue().decode('utf-8')
        cls.rating_changes = json.loads(response_data).get('result')

    @staticmethod
    def make_request():
        """Makes all the necessary requests to cf API."""
        CFRequestHandler._get_user_info()
        CFRequestHandler._get_user_sub()
        CFRequestHandler._get_rating_changes()
