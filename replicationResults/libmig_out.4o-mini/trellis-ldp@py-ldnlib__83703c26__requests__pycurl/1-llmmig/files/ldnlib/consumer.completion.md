### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several key changes were made:

1. **Importing PycURL**: The `requests` library was replaced with `pycurl`. The `requests` library provides a higher-level interface for HTTP requests, while `pycurl` is a lower-level interface that requires more manual setup.

2. **Setting Up Curl Options**: Instead of using `requests.get()`, we set up a `pycurl.Curl` object and configure it with options such as the URL, headers, and other parameters. 

3. **Handling Response**: The response from `pycurl` is handled differently. We need to set up a callback to capture the response data since `pycurl` does not return the response directly like `requests`.

4. **Error Handling**: The error handling with `raise_for_status()` is replaced with a check on the HTTP response code after executing the request.

5. **Response Parsing**: The response data is captured in a buffer and then processed similarly to how it was done with `requests`.

Here is the modified code:

```python
from rdflib import Graph, URIRef
import pycurl
import json
from io import BytesIO

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

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, inbox)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
        
        try:
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code != 200:
                raise Exception(f"HTTP error: {response_code}")
        finally:
            c.close()

        body = buffer.getvalue().decode('utf-8')
        g = Graph().parse(data=body, format=self.content_type_to_mime_type(
            c.getinfo(c.CONTENT_TYPE)))
        return [str(o) for (s, o) in g[:URIRef(self.LDP_CONTAINS)]]

    def notification(self, iri, **kwargs):
        """
        Retrieve a single LDN notification and decode into a Python object.
        """
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, iri)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])
        
        try:
            c.perform()
            response_code = c.getinfo(c.RESPONSE_CODE)
            if response_code != 200:
                raise Exception(f"HTTP error: {response_code}")
        finally:
            c.close()

        body = buffer.getvalue().decode('utf-8')
        mime_type = self.content_type_to_mime_type(c.getinfo(c.CONTENT_TYPE))
        if mime_type == self.JSON_LD:
            return json.loads(body)
        else:
            g = Graph().parse(data=body, format=mime_type)
            return json.loads(g.serialize(format="json-ld"))
``` 

This code now uses `pycurl` for HTTP requests while maintaining the original structure and functionality of the application.