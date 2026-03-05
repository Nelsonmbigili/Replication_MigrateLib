### Explanation of Changes
To migrate the code from using the `urllib3` library to the `requests` library, the following changes were made:
1. The method for making HTTP requests was changed from `driver.command_executor._request` to `requests.get`. This is because `requests` provides a simpler and more user-friendly interface for making HTTP requests.
2. The URL construction remains the same, but the response handling is adjusted to work with the `requests` library, which returns a `Response` object. The JSON content of the response is accessed using the `.json()` method.

### Modified Code
```python
import requests

class Waits:
    def __init__(self, driver):
        response = requests.get(
            f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
        ).json()
        self.implicit = int(response["value"]["implicit"] / 1000)
        self.page_load = int(response["value"]["pageLoad"] / 1000)
        self.script = int(response["value"]["script"] / 1000)


def get_implicit_wait(driver):
    response = requests.get(
        f"{driver.command_executor._url}/session/{driver.session_id}/timeouts"
    ).json()
    return int(response["value"]["implicit"] / 1000)
```