### Explanation of Changes

To migrate the code from using the `requests` library to `pycurl`, the following changes were made:

1. **Replaced `requests.post` with `pycurl` for HTTP POST requests**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with the appropriate options (e.g., URL, POST data, headers).
   - The response body is captured using a `BytesIO` object from the `io` module.

2. **Modified Mocking**:
   - Since `pycurl` does not have a direct equivalent to `requests.post`, the mocking strategy was updated to mock the `pycurl.Curl` object and its behavior.

3. **Error Handling**:
   - `pycurl` raises exceptions of type `pycurl.error` for HTTP errors or connection issues. These were mapped to the existing error-handling logic.

4. **Response Parsing**:
   - The response body from `pycurl` is a byte string, so it was decoded to a string and parsed as JSON using the `json` module.

5. **Updated Tests**:
   - Mocking for `pycurl` was implemented by patching the `pycurl.Curl` object and its methods (e.g., `perform`, `setopt`).

Below is the modified code.

---

### Modified Code

```python
import pytest
import pycurl
import json
from io import BytesIO
from unittest.mock import MagicMock, patch

from ..sms_services.smspool import SMSPool, APIError

# Mocking pycurl.Curl
@pytest.fixture
def mock_pycurl(mocker):
    mock_curl = mocker.patch("pycurl.Curl")
    mock_instance = mock_curl.return_value
    mock_instance.perform.return_value = None
    mock_instance.getinfo.return_value = 200  # Simulate HTTP 200 status
    mock_instance.response_body = BytesIO()
    mock_instance.response_body.write(json.dumps({"success": True}).encode("utf-8"))
    mock_instance.response_body.seek(0)
    return mock_instance

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of SMSPool
@pytest.fixture
def sms_pool():
    return SMSPool(service="service_id", token="api_key", country="hk")

def test_request_success(mock_pycurl, sms_pool):
    response = sms_pool.request("some_command")
    assert response == {"success": True}
    mock_pycurl.setopt.assert_any_call(pycurl.URL, "http://api.smspool.net/some_command")
    mock_pycurl.setopt.assert_any_call(pycurl.POSTFIELDS, "key=api_key")

def test_request_failure(mock_pycurl, sms_pool):
    mock_pycurl.perform.side_effect = pycurl.error
    with pytest.raises(pycurl.error):
        sms_pool.request("some_command")

def test_get_phone(mock_pycurl, sms_pool):
    mock_pycurl.response_body = BytesIO()
    mock_pycurl.response_body.write(json.dumps({
        "success": True,
        "number": "1234567890",
        "phonenumber": "234567890",
        "order_id": "order123"
    }).encode("utf-8"))
    mock_pycurl.response_body.seek(0)
    phone, order_id = sms_pool.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

def test_get_code(mock_pycurl, sms_pool):
    mock_pycurl.response_body = BytesIO()
    mock_pycurl.response_body.write(json.dumps({
        "success": True,
        "sms": "12345"
    }).encode("utf-8"))
    mock_pycurl.response_body.seek(0)
    code = sms_pool.get_code("order123")
    assert code == "12345"

def test_get_phone_with_prefix(mock_pycurl, sms_pool):
    mock_pycurl.response_body = BytesIO()
    mock_pycurl.response_body.write(json.dumps({
        "success": True,
        "number": "1234567890",
        "phonenumber": "234567890",
        "order_id": "order123"
    }).encode("utf-8"))
    mock_pycurl.response_body.seek(0)
    phone, order_id = sms_pool.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

def test_request_error_response(mock_pycurl, sms_pool):
    mock_pycurl.response_body = BytesIO()
    mock_pycurl.response_body.write(json.dumps({
        "success": False,
        "message": "Error message"
    }).encode("utf-8"))
    mock_pycurl.response_body.seek(0)
    with pytest.raises(APIError) as exc_info:
        sms_pool.request("some_command")
    assert str(exc_info.value) == "Error message"

def test_get_phone_error_response(mock_pycurl, sms_pool):
    mock_pycurl.response_body = BytesIO()
    mock_pycurl.response_body.write(json.dumps({
        "success": False,
        "message": "Error message"
    }).encode("utf-8"))
    mock_pycurl.response_body.seek(0)
    with pytest.raises(APIError) as exc_info:
        sms_pool.get_phone()
    assert str(exc_info.value) == "Error message"

def test_get_code_error_response(mock_pycurl, mock_time_sleep, sms_pool):
    mock_time_sleep.side_effect = Exception("Test exception")
    mock_pycurl.response_body = BytesIO()
    mock_pycurl.response_body.write(json.dumps({
        "success": False,
        "message": "Error message"
    }).encode("utf-8"))
    mock_pycurl.response_body.seek(0)
    with pytest.raises(Exception) as exc_info:
        sms_pool.get_code("order123")
    assert str(exc_info.value) == "Test exception"
```

---

### Key Notes:
- The `pycurl.Curl` object is mocked to simulate HTTP requests and responses.
- The response body is written to a `BytesIO` object to mimic the behavior of `pycurl` capturing the response.
- Error handling and assertions remain consistent with the original `requests`-based implementation.