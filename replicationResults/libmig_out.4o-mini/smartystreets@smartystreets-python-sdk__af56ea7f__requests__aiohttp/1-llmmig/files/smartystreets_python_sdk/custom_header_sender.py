from aiohttp import ClientSession


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    async def send(self, smarty_request):
        async with ClientSession() as session:
            request = self.build_request(smarty_request)
            return await self.inner.send(request, session)

    def build_request(self, smarty_request):
        request = {
            'url': smarty_request.url_prefix,
            'params': smarty_request.parameters,
            'headers': self.headers,
            'data': smarty_request.payload if smarty_request.payload else None,
            'method': 'POST' if smarty_request.payload else 'GET'
        }
        return request
