import pycurl
from io import BytesIO

class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    def send(self, smarty_request):
        request = self.build_request(smarty_request)
        return self.inner.send(request)

    def build_request(self, smarty_request):
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, smarty_request.url_prefix)
        curl.setopt(curl.WRITEDATA, buffer)
        curl.setopt(curl.HTTPHEADER, [f"{key}: {value}" for key, value in self.headers.items()])
        
        if smarty_request.payload:
            curl.setopt(curl.POSTFIELDS, smarty_request.payload)
            curl.setopt(curl.CUSTOMREQUEST, 'POST')
        else:
            curl.setopt(curl.CUSTOMREQUEST, 'GET')
        
        return curl
