### Explanation of the Changes:
The original code uses `httpx` for making HTTP requests. To migrate to `requests`, the following changes were made:
1. The `test_app.get` method (specific to `httpx`) was replaced with `requests.get` since `requests` provides a similar method for making GET requests.
2. The `response.content` in `httpx` returns the raw response body as bytes, which is the same behavior in `requests`. No changes were needed for this part.
3. The `test_app` object was removed since it is specific to `httpx`. Instead, the `requests.get` method is used directly with the URL.

### Modified Code:
```python
from starlette.status import HTTP_200_OK
import requests


class TestTodo:

    def test_get(self):
        response = requests.get("http://localhost:8000/health-check")

        assert response.status_code == HTTP_200_OK
        assert response.content == b"OK"
```