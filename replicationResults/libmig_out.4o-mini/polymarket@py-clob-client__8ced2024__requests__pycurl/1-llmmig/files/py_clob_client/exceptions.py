import pycurl
from io import BytesIO


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp=None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.getinfo(pycurl.RESPONSE_CODE)
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp):
        buffer = BytesIO()
        resp.setopt(pycurl.WRITEFUNCTION, buffer.write)
        try:
            resp.perform()
            return buffer.getvalue().decode('utf-8')
        except Exception as e:
            return str(e)

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
