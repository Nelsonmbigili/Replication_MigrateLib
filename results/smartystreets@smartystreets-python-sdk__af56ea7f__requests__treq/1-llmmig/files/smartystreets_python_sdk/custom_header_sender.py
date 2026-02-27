import treq


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    async def send(self, smarty_request):
        if smarty_request.payload:
            # POST request with payload
            response = await treq.post(
                url=smarty_request.url_prefix,
                headers=self.headers,
                params=smarty_request.parameters,
                json=smarty_request.payload
            )
        else:
            # GET request without payload
            response = await treq.get(
                url=smarty_request.url_prefix,
                headers=self.headers,
                params=smarty_request.parameters
            )
        return await self.inner.send(response)
