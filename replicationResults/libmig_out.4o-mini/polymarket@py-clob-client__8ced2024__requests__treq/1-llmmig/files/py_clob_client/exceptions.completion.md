### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `Response` from `requests` was removed, as `treq` does not require a separate `Response` class import. Instead, `treq` directly returns the response object when making requests.
  
2. **Response Handling**: The way to handle the response object was modified. The `resp` object in `PolyApiException` is now treated as a `treq` response, which behaves similarly to `requests` but does not require the `Response` type hint.

3. **JSON Handling**: The method `_get_message` remains largely unchanged, but it is now assumed that the response object from `treq` can be used directly without needing to specify the type.

Here is the modified code:

```python
import treq


class PolyException(Exception):
    def __init__(self, msg):
        self.msg = msg


class PolyApiException(PolyException):
    def __init__(self, resp=None, error_msg=None):
        assert resp is not None or error_msg is not None
        if resp is not None:
            self.status_code = resp.status_code
            self.error_msg = self._get_message(resp)
        if error_msg is not None:
            self.error_msg = error_msg
            self.status_code = None

    def _get_message(self, resp):
        try:
            return resp.json()
        except Exception:
            return resp.text

    def __repr__(self):
        return "PolyApiException[status_code={}, error_message={}]".format(
            self.status_code, self.error_msg
        )

    def __str__(self):
        return self.__repr__()
```