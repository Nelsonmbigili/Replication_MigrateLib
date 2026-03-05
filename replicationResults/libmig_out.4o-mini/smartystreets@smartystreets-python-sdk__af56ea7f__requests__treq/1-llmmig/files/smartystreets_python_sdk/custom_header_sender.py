import treq


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        return self.inner.send(request)

    def build_request(self, smarty_request):
        if smarty_request.payload:
            request = treq.post(smarty_request.url_prefix, params=smarty_request.parameters, headers=self.headers, json=smarty_request.payload)
        else:
            request = treq.get(smarty_request.url_prefix, params=smarty_request.parameters, headers=self.headers)
        return request
