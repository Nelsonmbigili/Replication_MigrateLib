### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several key changes were made:

1. **Session Management**: The `requests` library uses a session object to manage connections, while `pycurl` does not have a session concept. Instead, we create a new `pycurl.Curl` object for each request.

2. **Request Execution**: The `requests.post` method is replaced with `pycurl` methods to set options and perform the request. This includes setting the URL, request method, headers, and data.

3. **Response Handling**: The response from `pycurl` is handled differently. We need to set up a callback to capture the response data since `pycurl` does not return the response directly like `requests`.

4. **Error Handling**: The status code check is done using `pycurl`'s `getinfo` method to retrieve the HTTP response code.

5. **Data Encoding**: The data sent in the request is encoded using `base64` before being passed to `pycurl`.

Here is the modified code:

```python
import base64
import io
import logging
import pycurl
from io import BytesIO

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

    def send(self, msg: FinTSMessage):
        log_out = io.StringIO()
        with Password.protect():
            log_msg = reduce_message_for_log(msg)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Sending {}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{}\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
            log_out.truncate(0)

        # Prepare to send the request using pycurl
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.url)
        c.setopt(c.POSTFIELDS, base64.b64encode(msg.render_bytes()).decode('utf-8'))
        c.setopt(c.HTTPHEADER, ['Content-Type: text/plain'])
        c.setopt(c.WRITEDATA, buffer)

        # Perform the request
        c.perform()

        # Check the response code
        response_code = c.getinfo(c.RESPONSE_CODE)
        c.close()

        if response_code < 200 or response_code > 299:
            raise FinTSConnectionError('Bad status code {}'.format(response_code))

        response = base64.b64decode(buffer.getvalue().decode('iso-8859-1'))
        retval = FinTSInstituteMessage(segments=response)

        with Password.protect():
            log_msg = reduce_message_for_log(retval)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Received {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n{}\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
        return retval
``` 

This code now uses `pycurl` to handle HTTP requests instead of `requests`, while maintaining the original structure and functionality of the code.