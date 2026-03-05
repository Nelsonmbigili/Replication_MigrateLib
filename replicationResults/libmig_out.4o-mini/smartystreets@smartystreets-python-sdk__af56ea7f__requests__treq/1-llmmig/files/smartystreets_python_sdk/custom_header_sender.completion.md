### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement was changed from `from requests import Request` to `import treq`. The `Request` class is not needed in `treq` as it handles requests differently.
2. **Building and Sending Requests**: The `build_request` method was modified to directly use `treq` functions for sending requests. Instead of creating a `Request` object, we will use `treq.get` or `treq.post` to send the request based on the method.
3. **Parameters and Headers**: The parameters and headers are passed directly to the `treq` functions instead of being set on a `Request` object.

### Modified Code
```python
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
```