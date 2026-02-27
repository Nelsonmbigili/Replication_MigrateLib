### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.head` with `pycurl` for HTTP HEAD requests**:
   - Used `pycurl.Curl` to perform the HEAD request.
   - Configured the `pycurl` object to set the HTTP method to `HEAD` and handle headers.
   - Parsed the response headers manually to extract the `Link` header for LDP inbox discovery.

2. **Replaced `requests.get` with `pycurl` for HTTP GET requests**:
   - Used `pycurl.Curl` to perform the GET request.
   - Configured the `pycurl` object to set the HTTP method to `GET` and handle headers and response data.
   - Parsed the response body and headers manually to extract the content type and process the RDF data.

3. **Added helper functions**:
   - Added a helper function `_perform_request` to encapsulate the common logic for making `pycurl` requests and capturing the response.
   - Added logic to parse headers and response data from `pycurl`.

4. **Preserved the original logic**:
   - The structure and flow of the original code were maintained, with only the HTTP request logic replaced.

---

### Modified Code
```python
from rdflib import Graph, URIRef
import pycurl
from io import BytesIO


class BaseLDN(object):

    ACCEPT_HEADERS = ("application/ld+json; q=1.0,"
                      "text/turtle; q=0.9,"
                      "application/xml+rdf; q=0.5")
    JSON_LD = "application/ld+json"
    LDP_INBOX = "http://www.w3.org/ns/ldp#inbox"
    LDP_CONTAINS = "http://www.w3.org/ns/ldp#contains"

    def __init__(self, **kwargs):
        self.accept_headers = kwargs.get('accept_headers', self.ACCEPT_HEADERS)

    def _perform_request(self, url, method="GET", headers=None):
        """
        Helper function to perform an HTTP request using pycurl.
        """
        buffer = BytesIO()
        header_buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.HEADERFUNCTION, header_buffer.write)

        # Set HTTP method
        if method == "HEAD":
            c.setopt(c.NOBODY, True)
        elif method == "GET":
            c.setopt(c.HTTPGET, True)

        # Set headers
        if headers:
            c.setopt(c.HTTPHEADER, [f"{key}: {value}" for key, value in headers.items()])

        # Perform the request
        c.perform()

        # Capture response details
        status_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        # Parse headers and body
        response_headers = header_buffer.getvalue().decode('utf-8')
        response_body = buffer.getvalue().decode('utf-8')
        return status_code, response_headers, response_body

    def __discover_head(self, target, **kwargs):
        headers = kwargs.get('headers', {})
        status_code, response_headers, _ = self._perform_request(target, method="HEAD", headers=headers)

        if status_code >= 400:
            raise Exception(f"HTTP HEAD request failed with status code {status_code}")

        # Parse Link headers
        links = {}
        for line in response_headers.splitlines():
            if line.lower().startswith("link:"):
                link_header = line[5:].strip()
                parts = link_header.split(";")
                url = parts[0].strip("<>")
                rel = None
                for part in parts[1:]:
                    if part.strip().startswith("rel="):
                        rel = part.split("=")[1].strip('"')
                if rel:
                    links[rel] = {"url": url}

        if self.LDP_INBOX in links:
            return links[self.LDP_INBOX].get('url')

    def __discover_get(self, target, **kwargs):
        headers = kwargs.get('headers', {})
        status_code, response_headers, response_body = self._perform_request(target, method="GET", headers=headers)

        if status_code >= 400:
            raise Exception(f"HTTP GET request failed with status code {status_code}")

        # Parse content type
        content_type = None
        for line in response_headers.splitlines():
            if line.lower().startswith("content-type:"):
                content_type = line.split(":", 1)[1].strip()
                break

        if not content_type:
            raise Exception("Content-Type header is missing in the response")

        # Parse RDF data
        g = Graph().parse(data=response_body, format=self.content_type_to_mime_type(content_type))

        for (subject, inbox) in g[:URIRef(self.LDP_INBOX)]:
            return str(inbox)

    def content_type_to_mime_type(self, content_type):
        """
        A utility method to convert a content-type header into a
        mime-type string.
        """
        return content_type.split(";")[0].strip()

    def discover(self, target, **kwargs):
        """Discover the inbox for a resource."""
        headers = kwargs.pop("headers", dict())
        if 'accept' not in headers:
            headers['accept'] = kwargs.pop("accept", self.accept_headers)
        allow_redirects = kwargs.pop('allow_redirects', True)

        inbox = self.__discover_head(target, headers=headers,
                                     allow_redirects=allow_redirects,
                                     **kwargs)
        if inbox is None:
            return self.__discover_get(target, headers=headers,
                                       allow_redirects=allow_redirects,
                                       **kwargs)
        else:
            return inbox
```

---

### Key Notes
- The `pycurl` library requires manual handling of headers and response data, which is why additional parsing logic was added.
- The `requests` library's `raise_for_status` method was replaced with manual status code checks.
- The `Link` header parsing logic was implemented to extract the LDP inbox URL.