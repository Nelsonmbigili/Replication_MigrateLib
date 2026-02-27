from requests_futures.sessions import FuturesSession


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = FuturesSession()  # Use FuturesSession for asynchronous requests

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        # Send the request asynchronously using FuturesSession
        if request.method == 'POST':
            return self.inner.post(request.url, headers=request.headers, data=request.data, params=request.params)
        else:  # Default to GET
            return self.inner.get(request.url, headers=request.headers, params=request.params)

    def build_request(self, smarty_request):
        request = Request(url=smarty_request.url_prefix, params=smarty_request.parameters)
        request.headers = self.headers
        if smarty_request.payload:
            request.data = smarty_request.payload
            request.method = 'POST'
        else:
            request.method = 'GET'
        return request
