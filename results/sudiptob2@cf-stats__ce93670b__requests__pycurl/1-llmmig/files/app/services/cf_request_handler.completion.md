### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` with `pycurl`**:
   - `pycurl` requires setting up a `pycurl.Curl` object, configuring it with the URL, and capturing the response using a `BytesIO` buffer.
   - The response data is then decoded from bytes to a string and parsed as JSON.
2. **Error Handling**:
   - `pycurl` raises exceptions for connection issues, so the `try-except` block was updated to handle `pycurl.error`.
3. **Response Parsing**:
   - Since `pycurl` does not directly return a JSON object like `requests`, the response is manually decoded and parsed using the `json` module.
4. **Imports**:
   - Added imports for `pycurl` and `io.BytesIO` (to capture the response).
   - Added `json` for parsing the response.

Below is the modified code.

---

### Modified Code
```python
import pycurl
import json
from io import BytesIO

from config.config import settings
from app.constant import Constant


class CFRequestHandler:
    """Provides services for requesting codeforces API."""

    user_info: dict = None
    user_submission: list = None
    rating_changes: list = None

    @classmethod
    def _get_user_info(cls):
        """Gets data from codeforces user.info api."""
        url = Constant.USER_INFO.format(settings.cf_handle)
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        try:
            curl.perform()
        except pycurl.error:
            raise SystemExit('Could not connect to the codeforces API')
        finally:
            curl.close()
        response_data = buffer.getvalue().decode('utf-8')
        cls.user_info = json.loads(response_data).get('result')[0]

    @classmethod
    def _get_user_sub(cls):
        """Gets data from codeforces user.status api."""
        url = Constant.USER_STATUS.format(settings.cf_handle)
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        try:
            curl.perform()
        except pycurl.error:
            raise SystemExit('Could not connect to the codeforces API')
        finally:
            curl.close()
        response_data = buffer.getvalue().decode('utf-8')
        cls.user_submission = json.loads(response_data).get('result')

    @classmethod
    def _get_rating_changes(cls):
        """Gets all rating changes from codeforces api."""
        url = Constant.USER_RATING.format(settings.cf_handle)
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        try:
            curl.perform()
        except pycurl.error:
            raise SystemExit('Could not connect to the codeforces API')
        finally:
            curl.close()
        response_data = buffer.getvalue().decode('utf-8')
        cls.rating_changes = json.loads(response_data).get('result')

    @staticmethod
    def make_request():
        """Makes all the necessary requests to cf API."""
        CFRequestHandler._get_user_info()
        CFRequestHandler._get_user_sub()
        CFRequestHandler._get_rating_changes()
```

---

### Key Points
1. **Buffer for Response**:
   - `pycurl` writes the response to a buffer (in this case, `BytesIO`), which is then decoded and parsed.
2. **Error Handling**:
   - `pycurl.error` is caught to handle connection issues.
3. **JSON Parsing**:
   - Since `pycurl` does not provide built-in JSON parsing, the `json` module is used to parse the response.

This code maintains the original structure and functionality while replacing `requests` with `pycurl`.