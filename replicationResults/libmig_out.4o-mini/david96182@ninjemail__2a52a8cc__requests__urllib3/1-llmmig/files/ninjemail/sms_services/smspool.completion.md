### Explanation of Changes

To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `urllib3`.
2. **Creating a Pool Manager**: A `PoolManager` instance from `urllib3` was created to handle the HTTP connections.
3. **Making Requests**: The `requests.post` method was replaced with `http.request('POST', ...)` from `urllib3`, which requires specifying the method and the URL.
4. **Handling Parameters**: The parameters for the request were passed as a dictionary to the `fields` argument in `http.request`.
5. **Response Handling**: The response from `urllib3` is different from `requests`. The response body is accessed using `response.data`, and JSON parsing is done using `json.loads()` instead of `res.json()`.
6. **Error Handling**: The error handling was adjusted to check the status code directly from the response object.

Here is the modified code:

```python
import logging
import random
import re
import time
import urllib3
import json

class APIError(Exception):
    pass

class SMSPool:
    """
    This class provides functionalities to interact with the SMSPool API to obtain phone numbers and SMS verification codes.

    Attributes:
        token (str): Your SMSPool api key.
        service (str): SMSPool service ID.
        country (str, optional): The country code for the phone number. Defaults to 'hk'.

    Methods:
        request(kwargs): Sends a POST request to the SMSPool API with the provided arguments.
        get_phone(send_prefix=False): Purchases a phone number from the SMSPool API.
            - send_prefix (bool, optional): Specifies whether to return the phone number with or without the prefix. Defaults to False.
        get_code(phone): Retrieves the SMS verification code sent to the provided phone number.

    Exceptions:
        APIError: Raised when an error occurs while interacting with the SMSPool API.
    """

    _last_phone = None
    code_patt = re.compile(r"([0-9]{5,6})")

    def __init__(
            self,
            service,
            token,
            country=1,
            ):
        self.token = token
        self.service = service
        self.country = country
        self.API_URL = "http://api.smspool.net/"
        self.http = urllib3.PoolManager()

    def request(self, cmd, **kwargs):
        """
        Sends a POST request to the SMSPool API with the provided arguments.

        Args:
            kwargs (dict): Additional arguments to be included in the request body.

        Returns:
            str: The API response text.

        Raises:
            APIError: If the API returns an error message.
        """
        payload = dict(
                key=self.token,
                **kwargs
                )

        response = self.http.request(
                'POST',
                self.API_URL + cmd,
                fields=payload
                )

        if response.status != 200:
            raise APIError('HTTP Error: {}'.format(response.status))

        res = json.loads(response.data.decode('utf-8'))
        if 'success' in res:
            if not res['success']:
                raise APIError(res.get('message', 'Unknown error'))
        elif 'status' in res:
            if res['status'] != 3:
                raise APIError(res.get('message', 'Unknown error'))

        return res

    def get_phone(self, send_prefix=False):
        """
        Purchases a phone number from the SMSPool API.

        Args:
            send_prefix (bool, optional): Specifies whether to return the phone number with or without the prefix. Defaults to False.

        Returns:
            str: The retrieved phone number, optionally with the prefix removed and the order id of the purchased phone number.

        Raises:
            APIError: If an error occurs while retrieving the phone number.
        """
        logging.info("Getting a phone number")

        data = {
                "country": self.country,
                "service": self.service,
                "pricing_option": 0,
                }

        data = self.request(cmd="purchase/sms", **data)

        self._last_phone = data
        phone_number = data['number'] 
        order_id = data['order_id']

        logging.info("Got phone: %s", phone_number)

        if not send_prefix:
            phone_number = data['phonenumber']
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

        data = {
                "orderid": order_id,
                }
        while True:
            try:
                res = self.request(cmd="sms/check", **data)
            except APIError as exc:
                logging.info("Retrying...")
                time.sleep(10)
            else:
                break
        code = res['sms']

        logging.info("Got code %s", code)
        return code
```