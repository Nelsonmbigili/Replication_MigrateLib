from treq.response import Response
from twisted.internet.defer import inlineCallbacks, returnValue


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: Response = None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.code  # `treq` uses `code` instead of `status_code`
            self.error_msg = None  # Placeholder, will be set asynchronously
            self._set_message(resp)  # Asynchronous call to set the error message
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    @inlineCallbacks
    def _set_message(self, resp: Response):
        try:
            json_body = yield resp.json()
            self.error_msg = json_body
        except Exception:
            text_body = yield resp.text()
            self.error_msg = text_body

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
