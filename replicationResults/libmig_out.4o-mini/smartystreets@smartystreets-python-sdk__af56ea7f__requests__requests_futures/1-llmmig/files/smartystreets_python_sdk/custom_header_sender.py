from requests_futures.sessions import FuturesSession


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner
        self.session = FuturesSession()  # Create a FuturesSession instance

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        return self.session.send(request)  # Use FuturesSession to send the request

    def build_request(self, smarty_request):
        request = Request(url=smarty_request.url_prefix, params=smarty_request.parameters)
        request.headers = self.headers
        if smarty_request.payload:
            request.data = smarty_request.payload
            request.method = 'POST'
        else:
            request.method = 'GET'
        return request
