### Explanation of Changes:
To migrate the code from the `requests` library to the `pycurl` library, the following changes were made:
1. **Replaced `requests.get` with `pycurl` for HTTP GET requests**:
   - `pycurl` requires setting up a `pycurl.Curl` object, configuring it with the URL, and capturing the response using a buffer.
   - The `requests.get` call in the `_get_content_xml` method was replaced with equivalent `pycurl` logic.
2. **Added a `BytesIO` buffer**:
   - `pycurl` writes the response to a buffer, so a `BytesIO` object from the `io` module was used to capture the response.
3. **Handled response decoding**:
   - The response content captured in the buffer was decoded from bytes to a string before parsing it with `xmltodict`.
4. **Error handling**:
   - Checked the HTTP response code using `pycurl`'s `getinfo` method to ensure the response was successful (status code 200).

Below is the modified code:

---

### Modified Code:
```python
import os
import pycurl
import xmltodict
from io import BytesIO

from typing import List, Tuple

from namesilo.common import DomainInfo
from namesilo.exceptions import exception_codes

__author__ = 'goran.vrbaski'


class ContactModel:
    def __init__(self, **kwargs):
        """
        Model for manipulating NameSilo contacts

        :param str contact_id: Contact ID
        :param str first_name: First Name
        :param str last_name: Last Name
        :param str address: Address
        :param str city: City
        :param str state: State
        :param str country: Country
        :param str email: Email address
        :param str phone: Telephone number
        :param str zip: ZIP Code
        """
        self.contact_id = self._correct_formating(kwargs.get('contact_id'))
        self.first_name = self._correct_formating(kwargs.get('first_name'))
        self.last_name = self._correct_formating(kwargs.get('last_name'))
        self.address = self._correct_formating(kwargs.get('address'))
        self.city = self._correct_formating(kwargs.get('city'))
        self.state = self._correct_formating(kwargs.get('state'))
        self.country = self._correct_formating(kwargs.get('country'))
        self.email = self._correct_formating(kwargs.get('email'))
        self.phone = self._correct_formating(kwargs.get('phone'))
        self.zip = self._correct_formating(kwargs.get('zip'))

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.contact_id}"

    @staticmethod
    def convert_contact_model(reply):
        """
        Convert standard Namesilo reply to ContactModel

        :param reply: Namesilo Contact response
        :return: Populated ContactModel from Namesilo
        :rtype: ContactModel
        """
        return ContactModel(
            contact_id=reply['contact_id'],
            first_name=reply['first_name'],
            last_name=reply['last_name'],
            address=reply['address'],
            city=reply['city'],
            state=reply['state'],
            country=reply['country'],
            zip=reply['zip'],
            email=reply['email'],
            phone=reply['phone']
        )

    @staticmethod
    def _correct_formating(data: str):
        """
        Replacing all whitespaces with %20 (NameSilo requirement)
        :param data:

        :return: string
        """
        return data.replace(" ", "%20")


class NameSilo:
    def __init__(self, token, sandbox: bool=True):
        """
        Creating Namesilo object with given token

        :param token: access token from namesilo.com
        :param sandbox: true or false
        """
        self._token = token
        if sandbox:
            self._base_url = "http://sandbox.namesilo.com/api/"
        else:
            self._base_url = "https://www.namesilo.com/api/"

    def _process_data(self, url_extend):
        parsed_context = self._get_content_xml(url_extend)
        self.check_error_code(self._get_error_code(parsed_context))
        return parsed_context

    @staticmethod
    def _get_error_code(data):
        return int(data['namesilo']['reply']['code']), \
               data['namesilo']['reply']['detail']

    @staticmethod
    def check_error_code(error_code: tuple):
        if error_code[0] in [300, 301, 302]:
            return exception_codes[error_code[0]]
        else:
            raise exception_codes[error_code[0]](error_code[1])

    def _get_content_xml(self, url: str) -> dict:
        """
        Fetches XML content from the API using pycurl.

        :param url: The URL to fetch data from.
        :return: Parsed XML content as a dictionary.
        """
        full_url = os.path.join(self._base_url, url)
        buffer = BytesIO()
        curl = pycurl.Curl()

        try:
            # Set up the curl request
            curl.setopt(pycurl.URL, full_url)
            curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
            curl.setopt(pycurl.FOLLOWLOCATION, True)
            curl.setopt(pycurl.CONNECTTIMEOUT, 10)
            curl.setopt(pycurl.TIMEOUT, 30)

            # Perform the request
            curl.perform()

            # Check the HTTP response code
            http_code = curl.getinfo(pycurl.RESPONSE_CODE)
            if http_code != 200:
                raise Exception(f"API responded with status code: {http_code}")

            # Decode and parse the response
            content = buffer.getvalue().decode('utf-8')
            return xmltodict.parse(content)

        finally:
            # Clean up
            curl.close()
            buffer.close()

    def check_domain(self, domain_name: str) -> bool:
        """
        Check if domain name is available

        :param str domain_name: Domain name for checking
        :return: Availability of domain
        :rtype: bool
        """
        url_extend = f"checkRegisterAvailability?version=1&type=xml&" \
                     f"key={self._token}&domains={domain_name}"
        parsed_content = self._process_data(url_extend)
        if 'available' in parsed_content['namesilo']['reply'].keys():
            return True

        return False

    # Other methods remain unchanged...
```

---

### Key Notes:
1. Only the `_get_content_xml` method was modified to replace `requests.get` with `pycurl`.
2. The rest of the code remains unchanged, as per the instructions.
3. The `pycurl` library requires explicit setup and cleanup, which is handled using a `try-finally` block to ensure resources are released properly.