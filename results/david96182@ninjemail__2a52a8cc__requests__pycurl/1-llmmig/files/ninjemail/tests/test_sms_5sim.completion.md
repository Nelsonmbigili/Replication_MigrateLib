### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replace `requests.get` with `pycurl`**:
   - `pycurl` does not have a high-level API like `requests`. Instead, it uses a lower-level interface where you configure options for the HTTP request and handle the response manually.
   - A `BytesIO` object from the `io` module is used to capture the response body.
   - The `pycurl` options `CURLOPT_URL`, `CURLOPT_HTTPHEADER`, and `CURLOPT_WRITEFUNCTION` are used to set the URL, headers, and response handling, respectively.

2. **Mocking `pycurl`**:
   - Since `pycurl` does not have a direct equivalent to `requests.get`, the mocking strategy is adjusted to mock the behavior of `pycurl.Curl` and its options.

3. **Error Handling**:
   - `pycurl` raises exceptions for HTTP errors, so the code is updated to handle `pycurl.error` instead of `requests.exceptions.HTTPError`.

4. **Response Parsing**:
   - The response body captured in the `BytesIO` object is decoded and parsed as JSON using the `json` module.

5. **Fixtures and Tests**:
   - The `mock_requests_get` fixture is replaced with a `mock_pycurl_get` fixture that mocks the behavior of `pycurl`.

### Modified Code:
```python
import pytest
import pycurl
import json
from io import BytesIO

from ..sms_services.fivesim import FiveSim, APIError

# Mocking pycurl.Curl
@pytest.fixture
def mock_pycurl_get(mocker):
    mock_curl = mocker.patch("pycurl.Curl")
    mock_instance = mock_curl.return_value
    mock_instance.perform.side_effect = None  # No exception by default
    mock_instance.getinfo.return_value = 200  # HTTP status code
    return mock_instance

# Mocking time.sleep
@pytest.fixture
def mock_time_sleep(mocker):
    return mocker.patch("time.sleep")

# Fixture to create an instance of FiveSim
@pytest.fixture
def fivesim():
    return FiveSim(service="service_id", token="api_key", country="usa")

def test_request_success(mock_pycurl_get, fivesim):
    # Mock response body
    response_body = BytesIO()
    response_body.write(json.dumps({"success": True}).encode('utf-8'))
    response_body.seek(0)

    # Mock pycurl behavior
    mock_pycurl_get.setopt.side_effect = lambda opt, val: response_body if opt == pycurl.WRITEFUNCTION else None

    response = fivesim.request("some_command")
    assert response == {"success": True}
    mock_pycurl_get.setopt.assert_any_call(pycurl.URL, "https://5sim.net/v1/user/some_command")
    mock_pycurl_get.setopt.assert_any_call(
        pycurl.HTTPHEADER,
        ['Authorization: Bearer api_key']
    )

def test_request_failure(mock_pycurl_get, fivesim):
    mock_pycurl_get.perform.side_effect = pycurl.error
    with pytest.raises(APIError):
        fivesim.request("some_command")

def test_get_phone(mock_pycurl_get, fivesim):
    # Mock response body
    response_body = BytesIO()
    response_body.write(json.dumps({"phone": "+1234567890", "id": "order123"}).encode('utf-8'))
    response_body.seek(0)

    # Mock pycurl behavior
    mock_pycurl_get.setopt.side_effect = lambda opt, val: response_body if opt == pycurl.WRITEFUNCTION else None

    phone, order_id = fivesim.get_phone()
    assert phone == "234567890"
    assert order_id == "order123"

def test_get_code(mock_pycurl_get, fivesim):
    # Mock response body
    response_body = BytesIO()
    response_body.write(json.dumps({"sms": [{"code": "12345"}]}).encode('utf-8'))
    response_body.seek(0)

    # Mock pycurl behavior
    mock_pycurl_get.setopt.side_effect = lambda opt, val: response_body if opt == pycurl.WRITEFUNCTION else None

    code = fivesim.get_code("order123")
    assert code == "12345"

def test_get_phone_with_prefix(mock_pycurl_get, fivesim):
    # Mock response body
    response_body = BytesIO()
    response_body.write(json.dumps({"phone": "+1234567890", "id": "order123"}).encode('utf-8'))
    response_body.seek(0)

    # Mock pycurl behavior
    mock_pycurl_get.setopt.side_effect = lambda opt, val: response_body if opt == pycurl.WRITEFUNCTION else None

    phone, order_id = fivesim.get_phone(send_prefix=True)
    assert phone == "1234567890"
    assert order_id == "order123"

def test_request_error_response(mock_pycurl_get, fivesim):
    mock_pycurl_get.perform.side_effect = pycurl.error
    with pytest.raises(APIError):
        fivesim.request("some_command")

def test_get_phone_error_response(mock_pycurl_get, fivesim):
    mock_pycurl_get.perform.side_effect = pycurl.error

    with pytest.raises(APIError):
        fivesim.get_phone()

def test_request_error_no_free_phones(mock_pycurl_get, fivesim):
    # Mock response body
    response_body = BytesIO()
    response_body.write("no free phones".encode('utf-8'))
    response_body.seek(0)

    # Mock pycurl behavior
    mock_pycurl_get.setopt.side_effect = lambda opt, val: response_body if opt == pycurl.WRITEFUNCTION else None

    with pytest.raises(APIError) as exc_info:
        fivesim.request('no_phone')
    assert str(exc_info.value) == '5Sim has no free phones'

def test_request_error_not_enough_balance(mock_pycurl_get, fivesim):
    # Mock response body
    response_body = BytesIO()
    response_body.write("not enough user balance".encode('utf-8'))
    response_body.seek(0)

    # Mock pycurl behavior
    mock_pycurl_get.setopt.side_effect = lambda opt, val: response_body if opt == pycurl.WRITEFUNCTION else None

    with pytest.raises(APIError) as exc_info:
        fivesim.request('no_balance')
    assert str(exc_info.value) == 'Not enough balance'

def test_get_code_error_response(mock_pycurl_get, mock_time_sleep, fivesim):
    mock_time_sleep.side_effect = Exception("Test exception")
    # Mock response body
    response_body = BytesIO()
    response_body.write(json.dumps({"status": "CANCELLED", "sms": []}).encode('utf-8'))
    response_body.seek(0)

    # Mock pycurl behavior
    mock_pycurl_get.setopt.side_effect = lambda opt, val: response_body if opt == pycurl.WRITEFUNCTION else None

    with pytest.raises(Exception) as exc_info:
        fivesim.get_code("order123")
    assert str(exc_info.value) == "Test exception"
```

### Key Notes:
- The `pycurl` library requires more manual handling of HTTP requests and responses compared to `requests`.
- Mocking `pycurl` involves simulating the behavior of `pycurl.Curl` and its options, which is more complex than mocking `requests.get`.
- The `BytesIO` object is used to capture and simulate the response body for testing purposes.