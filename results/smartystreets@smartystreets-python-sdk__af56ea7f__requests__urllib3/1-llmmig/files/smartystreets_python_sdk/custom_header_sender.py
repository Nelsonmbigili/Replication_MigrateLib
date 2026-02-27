import urllib3


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner
        self.http = urllib3.PoolManager()  # Initialize a PoolManager for making requests

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        return self.inner.send(request)

    def build_request(self, smarty_request):
        # Determine the HTTP method and payload
        method = 'POST' if smarty_request.payload else 'GET'
        body = smarty_request.payload if smarty_request.payload else None

        # Make the request using urllib3
        response = self.http.request(
            method=method,
            url=smarty_request.url_prefix,
            fields=smarty_request.parameters if method == 'GET' else None,
            body=body,
            headers=self.headers
        )
        return response
