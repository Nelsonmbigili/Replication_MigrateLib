### Explanation of Changes
To migrate the code from using `urllib3` to `httpx`, the following changes were made:
1. The `driver.command_executor._request` method, which is specific to `urllib3`, was replaced with `httpx`'s `httpx.get` method to perform the GET request.
2. The response handling was adjusted to accommodate the structure returned by `httpx`, which is different from `urllib3`. Specifically, the response is accessed using `response.json()` to retrieve the JSON data.

### Modified Code
```python
import httpx

class Waits:
    def __init__(self, driver):
        response = httpx.get(f"{driver.command_executor._url}/session/{driver.session_id}/timeouts")
        response_data = response.json()
        self.implicit = int(response_data["value"]["implicit"] / 1000)
        self.page_load = int(response_data["value"]["pageLoad"] / 1000)
        self.script = int(response_data["value"]["script"] / 1000)


def get_implicit_wait(driver):
    response = httpx.get(f"{driver.command_executor._url}/session/{driver.session_id}/timeouts")
    response_data = response.json()
    return int(response_data["value"]["implicit"] / 1000)
```