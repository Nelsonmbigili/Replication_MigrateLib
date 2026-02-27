### Explanation of Changes:
The original code uses `httpx` for making HTTP requests, but since the migration is to `urllib3`, the `httpx`-specific `test_app.get` method needs to be replaced with an equivalent `urllib3` implementation. `urllib3` does not have a direct `test_app` equivalent, so we use `urllib3.PoolManager` to make HTTP requests. The `PoolManager` is used to send a `GET` request to the specified URL, and the response is processed accordingly.

### Modified Code:
```python
from starlette.status import HTTP_200_OK
import urllib3


class TestTodo:

    def test_get(self, test_app):
        http = urllib3.PoolManager()
        response = http.request("GET", "http://testserver/health-check")

        assert response.status == HTTP_200_OK
        assert response.data == b"OK"
```

### Key Changes:
1. **Replaced `test_app.get`**: Since `urllib3` does not have a `test_app` equivalent, I used `urllib3.PoolManager` to make the HTTP request.
2. **Changed `response.status_code` to `response.status`**: In `urllib3`, the status code of the response is accessed using the `status` attribute instead of `status_code`.
3. **Changed `response.content` to `response.data`**: In `urllib3`, the response body is accessed using the `data` attribute instead of `content`.
4. **Added `http://testserver` to the URL**: `urllib3` requires a fully qualified URL, so I added `http://testserver` to the path `/health-check`. This assumes the test server is running locally. Adjust the base URL as needed for your application.