### Explanation of Changes
To migrate the code from using the `httpx` library to the `requests` library, the following changes were made:
1. The `test_app.get` method, which is specific to `httpx`, was replaced with a call to `requests.get`. This change assumes that `test_app` is a wrapper around the `requests` library.
2. The response handling remains the same, as both libraries provide similar attributes for accessing the status code and content of the response.

### Modified Code
```python
from starlette.status import HTTP_200_OK
import requests


class TestTodo:

    def test_get(self, test_app):
        response = requests.get(test_app.url + "/health-check")

        assert response.status_code == HTTP_200_OK
        assert response.content == b"OK"
```