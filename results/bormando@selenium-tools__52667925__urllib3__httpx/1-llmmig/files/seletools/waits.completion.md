### Explanation of Changes:
To migrate the code from `urllib3` to `httpx`, the following changes were made:
1. **HTTP Client**: `urllib3` uses its own `PoolManager` or `HTTPConnectionPool` for making HTTP requests, but in this code, the `driver.command_executor._request` method abstracts the HTTP request. To migrate to `httpx`, we directly use `httpx` to perform the HTTP GET request.
2. **Request Handling**: Replaced the `driver.command_executor._request` calls with `httpx.get` to perform the HTTP GET requests.
3. **Response Parsing**: The `httpx` library returns a `Response` object, so the response body is accessed using `.json()` instead of directly indexing into the response object as with `urllib3`.

### Modified Code:
```python
import httpx

class Waits:
    def __init__(self, driver):
        url = f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
        response = httpx.get(url)
        response_data = response.json()
        self.implicit = int(response_data["value"]["implicit"] / 1000)
        self.page_load = int(response_data["value"]["pageLoad"] / 1000)
        self.script = int(response_data["value"]["script"] / 1000)


def get_implicit_wait(driver):
    url = f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
    response = httpx.get(url)
    response_data = response.json()
    return int(response_data["value"]["implicit"] / 1000)
```

### Key Points:
- The `httpx.get` method is used to perform the GET request.
- The `.json()` method of the `httpx.Response` object is used to parse the JSON response.
- The rest of the code remains unchanged to ensure compatibility with the larger application.