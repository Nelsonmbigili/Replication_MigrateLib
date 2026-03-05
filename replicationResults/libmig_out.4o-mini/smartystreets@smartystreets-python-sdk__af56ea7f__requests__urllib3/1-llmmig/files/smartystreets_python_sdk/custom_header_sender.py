import urllib3
from urllib3.util import urlencode

class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner
        self.http = urllib3.PoolManager()

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        return self.inner.send(request)

    def build_request(self, smarty_request):
        url = smarty_request.url_prefix
        if smarty_request.parameters:
            url += '?' + urlencode(smarty_request.parameters)
        
        if smarty_request.payload:
            response = self.http.request('POST', url, headers=self.headers, body=smarty_request.payload)
        else:
            response = self.http.request('GET', url, headers=self.headers)
        
        return response
