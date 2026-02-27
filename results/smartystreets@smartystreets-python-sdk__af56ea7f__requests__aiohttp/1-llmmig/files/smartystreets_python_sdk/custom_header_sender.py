import aiohttp


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    async def send(self, smarty_request):
        request = await self.build_request(smarty_request)
        return await self.inner.send(request)

    async def build_request(self, smarty_request):
        async with aiohttp.ClientSession() as session:
            if smarty_request.payload:
                # POST request
                async with session.post(
                    url=smarty_request.url_prefix,
                    params=smarty_request.parameters,
                    headers=self.headers,
                    data=smarty_request.payload
                ) as response:
                    return response
            else:
                # GET request
                async with session.get(
                    url=smarty_request.url_prefix,
                    params=smarty_request.parameters,
                    headers=self.headers
                ) as response:
                    return response
