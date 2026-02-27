### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Session Management**: `pycurl` does not have a session object like `requests`. Instead, we use a `pycurl.Curl` object to handle HTTP requests.
2. **POST Request**: The `requests.session().post()` method was replaced with `pycurl.Curl`'s configuration for a POST request. This includes setting the URL, HTTP headers, and POST data.
3. **Response Handling**: `pycurl` writes the response to a buffer (e.g., `io.BytesIO`) instead of returning it directly. The response content is then extracted from the buffer.
4. **Error Handling**: `pycurl` does not raise exceptions for HTTP status codes. Instead, we manually check the HTTP response code using `curl.getinfo(pycurl.RESPONSE_CODE)`.

Below is the modified code:

---

### Modified Code
```python
import base64
import io
import logging
import pycurl

from fints.utils import Password, log_configuration

from .exceptions import *
from .message import FinTSInstituteMessage, FinTSMessage
from .types import SegmentSequence

logger = logging.getLogger(__name__)


def reduce_message_for_log(msg):
    log_msg = msg
    if log_configuration.reduced:
        # Try to find a single inner message
        if len(log_msg.segments) == 4 and log_msg.segments[2].header.type == 'HNVSD':
            log_msg = log_msg.segments[2]
            if len(log_msg.data.segments) > 2 and log_msg.data.segments[0].header.type == "HNSHK" and \
                    log_msg.data.segments[-1].header.type == "HNSHA":
                log_msg = SegmentSequence(segments=log_msg.data.segments[1:-1])
    return log_msg


class FinTSHTTPSConnection:
    def __init__(self, url):
        self.url = url
        self.curl = pycurl.Curl()

    def send(self, msg: FinTSMessage):
        log_out = io.StringIO()
        with Password.protect():
            log_msg = reduce_message_for_log(msg)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Sending {}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{}\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
            log_out.truncate(0)

        # Prepare the POST data
        post_data = base64.b64encode(msg.render_bytes())

        # Buffer to capture the response
        response_buffer = io.BytesIO()

        # Configure the pycurl request
        self.curl.setopt(pycurl.URL, self.url)
        self.curl.setopt(pycurl.POST, 1)
        self.curl.setopt(pycurl.POSTFIELDS, post_data)
        self.curl.setopt(pycurl.HTTPHEADER, ['Content-Type: text/plain'])
        self.curl.setopt(pycurl.WRITEDATA, response_buffer)

        # Perform the request
        try:
            self.curl.perform()
        except pycurl.error as e:
            raise FinTSConnectionError(f"Connection error: {e}")

        # Check the HTTP response code
        http_code = self.curl.getinfo(pycurl.RESPONSE_CODE)
        if http_code < 200 or http_code > 299:
            raise FinTSConnectionError(f"Bad status code {http_code}")

        # Decode the response
        response = base64.b64decode(response_buffer.getvalue().decode('iso-8859-1'))
        retval = FinTSInstituteMessage(segments=response)

        with Password.protect():
            log_msg = reduce_message_for_log(retval)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Received {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n{}\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
        return retval
```

---

### Key Changes in the Code
1. **Initialization**:
   - Replaced `requests.session()` with `pycurl.Curl()` in the `__init__` method.

2. **POST Request**:
   - Configured `pycurl` for a POST request using `setopt`:
     - `pycurl.URL`: Set the target URL.
     - `pycurl.POST`: Enabled POST method.
     - `pycurl.POSTFIELDS`: Set the POST data (base64-encoded message).
     - `pycurl.HTTPHEADER`: Set the `Content-Type` header.
     - `pycurl.WRITEDATA`: Redirected the response to a buffer (`io.BytesIO`).

3. **Response Handling**:
   - Used `io.BytesIO` to capture the response body.
   - Decoded the response from the buffer and processed it as before.

4. **Error Handling**:
   - Checked the HTTP response code using `curl.getinfo(pycurl.RESPONSE_CODE)`.
   - Raised a `FinTSConnectionError` if the response code was not in the 2xx range.

5. **Cleanup**:
   - The `pycurl.Curl` object is reused for multiple requests, as it is initialized in the `__init__` method. This avoids creating a new `Curl` object for every request.

---

This migration ensures that the functionality remains consistent while replacing `requests` with `pycurl`.