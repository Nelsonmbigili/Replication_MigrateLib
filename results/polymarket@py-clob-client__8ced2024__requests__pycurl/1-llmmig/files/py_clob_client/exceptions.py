import json
import pycurl
from io import BytesIO


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp=None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code, self.response_body = self._parse_pycurl_response(resp)
            self.error_msg = self._get_message(self.response_body)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _parse_pycurl_response(self, resp):
        """
        Parses the raw response from pycurl and extracts the status code and body.
        :param resp: A tuple containing (status_code, response_body) from pycurl.
        :return: A tuple (status_code, response_body).
        """
        status_code, response_body = resp
        return status_code, response_body

    def _get_message(self, response_body):
        """
        Extracts the error message from the response body.
        :param response_body: The raw response body (bytes).
        :return: Parsed JSON or plain text message.
        """
        try:
            return json.loads(response_body)
        except Exception:
            return response_body.decode('utf-8')

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
