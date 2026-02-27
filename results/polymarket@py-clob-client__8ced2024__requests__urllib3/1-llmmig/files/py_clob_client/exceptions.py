from urllib3.response import HTTPResponse
import json


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: HTTPResponse = None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.status
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp: HTTPResponse):
        try:
            # Read and decode the response body
            body = resp.data.decode('utf-8')
            # Attempt to parse the body as JSON
            return json.loads(body)
        except json.JSONDecodeError:
            # If parsing fails, return the raw text
            return body

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
