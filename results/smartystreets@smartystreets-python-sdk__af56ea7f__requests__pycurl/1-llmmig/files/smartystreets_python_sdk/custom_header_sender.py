import pycurl
from io import BytesIO


class CustomHeaderSender:
    def __init__(self, headers, inner):
        self.headers = headers
        self.inner = inner

    def send(self, smarty_request):
        curl = self.build_request(smarty_request)
        return self.inner.send(curl)

    def build_request(self, smarty_request):
        c = pycurl.Curl()
        buffer = BytesIO()

        # Set the URL with query parameters if provided
        url = smarty_request.url_prefix
        if smarty_request.parameters:
            query_string = "&".join(f"{key}={value}" for key, value in smarty_request.parameters.items())
            url = f"{url}?{query_string}"
        c.setopt(pycurl.URL, url)

        # Set headers
        header_list = [f"{key}: {value}" for key, value in self.headers.items()]
        c.setopt(pycurl.HTTPHEADER, header_list)

        # Set payload and method
        if smarty_request.payload:
            c.setopt(pycurl.POST, True)
            c.setopt(pycurl.POSTFIELDS, smarty_request.payload)
        else:
            c.setopt(pycurl.HTTPGET, True)

        # Set the response buffer
        c.setopt(pycurl.WRITEFUNCTION, buffer.write)

        return c
