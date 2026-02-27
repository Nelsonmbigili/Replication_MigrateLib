from httpx import Request, Client


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        return self.inner.send(request)

    def build_request(self, smarty_request):
        method = 'POST' if smarty_request.payload else 'GET'
        request = Request(
            method=method,
            url=smarty_request.url_prefix,
            params=smarty_request.parameters,
            headers=self.headers,
            data=smarty_request.payload if smarty_request.payload else None
        )
        return request
