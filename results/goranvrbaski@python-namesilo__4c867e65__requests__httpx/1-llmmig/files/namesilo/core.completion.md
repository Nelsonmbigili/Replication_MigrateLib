### Explanation of Changes:
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Import Change**: Replaced `import requests` with `import httpx`.
2. **HTTP GET Requests**: Replaced `requests.get` with `httpx.get`. The usage of `httpx.get` is similar to `requests.get`, so the transition is straightforward.
3. **Response Handling**: The `httpx` response object is similar to the `requests` response object, so no changes were needed for accessing `status_code`, `content`, or `decode()`.

The rest of the code remains unchanged as the migration only affects the HTTP request handling.

---

### Modified Code:
```python
import os
import httpx  # Changed from requests to httpx
import xmltodict

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
        api_request = httpx.get(os.path.join(self._base_url, url))  # Changed from requests.get to httpx.get
        if api_request.status_code != 200:
            raise Exception(
                f"API responded with status code: {api_request.status_code}"
            )

        content = xmltodict.parse(api_request.content.decode())
        return content

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

    def get_domain_info(self, domain_name: str) -> DomainInfo:
        """
        Returns information about specified domain

        :param str domain_name: name of domain
        :return: domain information
        :rtype: DomainInfo
        """
        url_extend = f"getDomainInfo?version=1&type=xml&key={self._token}&" \
                     f"domain={domain_name}"
        parsed_content = self._process_data(url_extend)
        return DomainInfo(parsed_content)

    def change_domain_nameservers(self, domain: str, primary_ns: str, secondary_ns: str) -> bool:
        """
        Change name server for specified domain

        :param str domain: Domain name
        :param str primary_ns: Primary name Server
        :param str secondary_ns: Secondary name server
        :return: Status of action
        :rtype: bool
        """
        url_extend = f"changeNameServers?version=1&" \
                     f"type=xml&key={self._token}&domain={domain}&" \
                     f"ns1={primary_ns}&ns2={secondary_ns}"
        self._process_data(url_extend)
        return True

    def list_domains(self) -> List:
        """
        List all domains registered with current account

        :return: list of registered domains
        :rtype: list
        """
        url_extend = f"listDomains?version=1&type=xml&key={self._token}"
        parsed_content = self._process_data(url_extend)
        return parsed_content['namesilo']['reply']['domains']['domain']

    # The rest of the methods remain unchanged as they rely on `_process_data` and `_get_content_xml`.
```

---

### Summary:
The migration from `requests` to `httpx` was achieved by replacing `requests.get` with `httpx.get`. The rest of the code remains unchanged as the response handling and other logic are compatible with both libraries.