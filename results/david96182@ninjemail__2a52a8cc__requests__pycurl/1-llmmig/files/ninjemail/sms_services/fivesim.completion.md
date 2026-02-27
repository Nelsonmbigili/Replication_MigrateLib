### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` with `pycurl`**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with options such as the URL, headers, and HTTP method.
   - The response is captured using a `BytesIO` object to store the output of the request.
2. **Error Handling**:
   - `pycurl` does not raise exceptions like `requests` for HTTP errors. Instead, the HTTP status code must be checked manually.
   - Added logic to raise `APIError` if the HTTP status code is not 200.
3. **Response Parsing**:
   - The response from `pycurl` is stored as bytes in a `BytesIO` object, which is then decoded to a string and parsed as JSON.
4. **Removed `requests` imports**:
   - The `requests` library was removed from the imports since it is no longer used.

### Modified Code:
```python
import logging
import re
import time
import pycurl
import json
from io import BytesIO

PREFIXES = {
        "usa": "1",
        }

class APIError(Exception):
    pass

class FiveSim:
    """
    This class provides functionalities to interact with the 5Sim API to obtain phone numbers and SMS verification codes.

    Attributes:
        token (str): Your 5Sim api key.
        service (str): 5Sim service name.
        country (str, optional): The country name for the phone number. Defaults to 'usa'.

    Methods:
        request(kwargs): Sends a GET request to the 5Sim API with the provided arguments.
        get_phone(send_prefix=False): Purchases a phone number from the 5Sim API.
            - send_prefix (bool, optional): Specifies whether to return the phone number with or without the prefix. Defaults to False.
        get_code(phone): Retrieves the SMS verification code sent to the provided phone number.

    Exceptions:
        APIError: Raised when an error occurs while interacting with the 5Sim API.
    """

    _last_phone = None
    code_patt = re.compile(r"([0-9]{5,6})")

    def __init__(
            self,
            service,
            token,
            country='usa',
            ):
        self.token = token
        self.service = service
        self.country = country
        self.prefix = PREFIXES.get(self.country) or ''
        self.API_URL = "https://5sim.net/v1/user/"

    def request(self, cmd):
        """
        Sends a GET request to the 5Sim API with the provided arguments.

        Args:
            cmd (str): The API command to execute.

        Returns:
            dict: The API response parsed as JSON.

        Raises:
            APIError: If the API returns an error message or a non-200 status code.
        """
        headers = [
            'Authorization: Bearer ' + self.token,
        ]

        url = self.API_URL + cmd
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.WRITEFUNCTION, buffer.write)

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            curl.close()
            raise APIError(f"Request failed: {str(e)}")

        curl.close()

        if status_code != 200:
            raise APIError(f"HTTP error: {status_code}")

        response_data = buffer.getvalue().decode('utf-8')
        buffer.close()

        try:
            response_json = json.loads(response_data)
        except json.JSONDecodeError as e:
            raise APIError(f"Failed to parse JSON response: {str(e)}")

        if response_json == "no free phones":
            raise APIError('5Sim has no free phones')
        if response_json == "not enough user balance":
            raise APIError("Not enough balance")

        return response_json

    def get_phone(self, send_prefix=False):
        """
        Purchases a phone number from the 5Sim API.

        Args:
            send_prefix (bool, optional): Specifies whether to return the phone number with or without the prefix. Defaults to False.

        Returns:
            str: The retrieved phone number, optionally with the prefix removed and the order id of the purchased phone number.

        Raises:
            APIError: If an error occurs while retrieving the phone number.
        """
        logging.info("Getting a phone number")

        cmd = 'buy/activation/' + self.country + '/any/' + self.service
        data = self.request(cmd=cmd)

        self._last_phone = data
        phone_number = data['phone'] 
        phone_number = phone_number.removeprefix('+')
        order_id = data['id']

        logging.info("Got phone: %s", phone_number)

        if not send_prefix:
            phone_number = phone_number.removeprefix('1')
        return phone_number, order_id

    def get_code(self, order_id):
        """
        Retrieves the SMS verification code sent to the provided phone number.

        Args:
            order_id (str): The order_id to retrieve the code for the sms.

        Returns:
            str: The extracted SMS verification code.

        Raises:
            APIError: If an error occurs while retrieving the code.
            AssertionError: If no code is found in the API response.
        """
        logging.info("Getting the verification code")

        cmd = '/check/' + str(order_id)
        received = False
        while not received:
            res = self.request(cmd=cmd)
            if res['sms']:
                received = True
            elif res['status'] in ['CANCELED', 'TIMEOUT', 'BANNED']:
                raise APIError('Error getting verification code, order status: %s' % res['status'])
            else:
                logging.info("Retrying...")
                time.sleep(10)

        sms = res['sms']
        code = sms[0]['code']

        logging.info("Got code %s", code)
        return code
```

### Key Points:
- The `request` method now uses `pycurl` to perform HTTP GET requests.
- The response is captured in a `BytesIO` object and decoded to a string before being parsed as JSON.
- HTTP errors are manually checked using the status code returned by `pycurl`.
- The rest of the code remains unchanged to ensure compatibility with the larger application.