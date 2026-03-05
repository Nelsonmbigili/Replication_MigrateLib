### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement for `Response` from `requests` was removed, as `urllib3` does not have a direct equivalent for `Response`. Instead, we will handle the HTTP response directly using `urllib3`'s response object.
  
2. **Response Handling**: The `Response` object from `requests` is replaced with the response object returned by `urllib3`. The status code can be accessed directly from the response object, and the JSON content can be accessed using the `data` attribute and then decoded.

3. **Error Handling**: The method for extracting the message from the response was modified to accommodate the way `urllib3` handles response data.

Here is the modified code:

```python
import urllib3
import json


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp=None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.status
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp):
        try:
            return json.loads(resp.data.decode('utf-8'))
        except Exception:
            return resp.data.decode('utf-8')

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
``` 

This code now uses `urllib3` for HTTP requests and response handling, while maintaining the original structure and functionality of the code.