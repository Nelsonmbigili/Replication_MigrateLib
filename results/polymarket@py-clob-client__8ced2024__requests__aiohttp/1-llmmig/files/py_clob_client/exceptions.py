from aiohttp import ClientResponse


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp: ClientResponse = None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.resp = resp  # Store the response for later use
            self.status_code = resp.status
        else:
            self.resp = None
            self.status_code = None

        self.error_msg = error_msg

    async def initialize(self):
        """Asynchronous initializer to fetch the error message if a response is provided."""
        if self.resp is not None:
            self.error_msg = await self._get_message(self.resp)

    async def _get_message(self, resp: ClientResponse):
        try:
            return await resp.json()
        except Exception:
            return await resp.text()

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
