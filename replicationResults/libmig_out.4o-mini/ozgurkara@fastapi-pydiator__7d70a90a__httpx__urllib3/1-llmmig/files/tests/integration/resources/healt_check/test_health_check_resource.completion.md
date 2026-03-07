### Explanation of Changes
To migrate the code from using the `httpx` library to `urllib3`, the following changes were made:
1. The `test_app.get` method, which is specific to `httpx`, was replaced with `urllib3`'s way of making HTTP requests.
2. An instance of `urllib3.PoolManager` was created to handle the connection pool and make requests.
3. The response handling was adjusted to match `urllib3`'s response structure, specifically accessing the status code and data.

### Modified Code
```python
from starlette.status import HTTP_200_OK
import urllib3

class TestTodo:

    def test_get(self, test_app):
        http = urllib3.PoolManager()
        response = http.request('GET', 'http://localhost:8000/health-check')

        assert response.status == HTTP_200_OK
        assert response.data == b"OK"
```