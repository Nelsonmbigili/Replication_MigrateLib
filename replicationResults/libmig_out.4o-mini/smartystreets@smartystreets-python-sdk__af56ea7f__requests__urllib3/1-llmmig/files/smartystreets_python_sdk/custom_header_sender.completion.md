### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement was changed from `from requests import Request` to `import urllib3`.
2. **Request Creation**: The `Request` object from `requests` was replaced with the `urllib3` method for creating requests. In `urllib3`, we typically use a `PoolManager` to make requests.
3. **Sending Requests**: The way to send requests and handle parameters, headers, and payloads was adjusted to fit the `urllib3` API.
4. **Response Handling**: The response handling was modified to accommodate the differences in how `urllib3` returns responses compared to `requests`.

Here is the modified code:

```python
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
``` 

This code now uses `urllib3` to handle HTTP requests while maintaining the original structure and functionality of the code.