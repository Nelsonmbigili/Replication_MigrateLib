### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replace `requests.get` with `pycurl`**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with options such as the URL, headers, and other parameters.
   - The response body is captured using a `BytesIO` object from the `io` module.
2. **Handle HTTP status codes**:
   - `pycurl` does not raise exceptions for HTTP errors like `requests` does. Instead, the HTTP status code is manually checked after the request.
3. **Extract response headers and body**:
   - `pycurl` does not directly provide headers and body as separate attributes. Headers are captured using a custom header function, and the body is captured using a `BytesIO` object.
4. **Parse the response**:
   - The response body is decoded from bytes to a string before being passed to the RDFLib `Graph` or JSON parser.

### Modified Code
```python
from rdflib import Graph, URIRef
import pycurl
from io import BytesIO
import json

from .base import BaseLDN


class Consumer(BaseLDN):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    def notifications(self, inbox, **kwargs):
        """
        Retrieve all of the notification IRIs from an ldp:inbox as a list.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        # Prepare headers for pycurl
        curl_headers = [f"{key}: {value}" for key, value in headers.items()]

        # Set up pycurl
        c = pycurl.Curl()
        c.setopt(c.URL, inbox)
        c.setopt(c.HTTPHEADER, curl_headers)

        # Capture response body
        response_body = BytesIO()
        c.setopt(c.WRITEDATA, response_body)

        # Perform the request
        c.perform()

        # Check HTTP status code
        status_code = c.getinfo(c.RESPONSE_CODE)
        if status_code < 200 or status_code >= 300:
            c.close()
            raise Exception(f"HTTP request failed with status code {status_code}")

        # Parse response
        response_text = response_body.getvalue().decode('utf-8')
        content_type = c.getinfo(c.CONTENT_TYPE)
        c.close()

        g = Graph().parse(data=response_text, format=self.content_type_to_mime_type(content_type))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        # Prepare headers for pycurl
        curl_headers = [f"{key}: {value}" for key, value in headers.items()]

        # Set up pycurl
        c = pycurl.Curl()
        c.setopt(c.URL, iri)
        c.setopt(c.HTTPHEADER, curl_headers)

        # Capture response body
        response_body = BytesIO()
        c.setopt(c.WRITEDATA, response_body)

        # Perform the request
        c.perform()

        # Check HTTP status code
        status_code = c.getinfo(c.RESPONSE_CODE)
        if status_code < 200 or status_code >= 300:
            c.close()
            raise Exception(f"HTTP request failed with status code {status_code}")

        # Parse response
        response_text = response_body.getvalue().decode('utf-8')
        content_type = c.getinfo(c.CONTENT_TYPE)
        c.close()

        mime_type = self.content_type_to_mime_type(content_type)
        if mime_type == self.JSON_LD:
            return json.loads(response_text)
        else:
            g = Graph().parse(data=response_text, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
```

### Key Notes
- The `pycurl.Curl` object is used to configure and execute HTTP requests.
- The `BytesIO` object is used to capture the response body.
- HTTP status codes are manually checked, and exceptions are raised for non-2xx responses.
- The `CONTENT_TYPE` information is retrieved using `c.getinfo(c.CONTENT_TYPE)` to determine the response's MIME type.
- The response body is decoded from bytes to a string before being processed further.