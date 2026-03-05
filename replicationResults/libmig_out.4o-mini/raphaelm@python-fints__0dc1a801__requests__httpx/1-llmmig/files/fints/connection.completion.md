### Explanation of Changes

To migrate the code from using the `requests` library to the `httpx` library, the following changes were made:

1. **Import Statement**: Changed the import from `requests` to `httpx`.
2. **Session Creation**: The `requests.session()` method was replaced with `httpx.Client()`, which is the equivalent way to create a session in `httpx`.
3. **Sending Requests**: The `post` method of the session was updated to use `httpx`'s `post` method. The parameters remain the same, but the method is now called on the `httpx.Client` instance.
4. **Response Handling**: The response object from `httpx` does not have a `content` attribute like `requests`. Instead, we use `response.text` to get the response body as a string, and then decode it as needed.

Here is the modified code:

```python
import base64
import io
import logging

import httpx
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
        self.session = httpx.Client()

    def send(self, msg: FinTSMessage):
        log_out = io.StringIO()
        with Password.protect():
            log_msg = reduce_message_for_log(msg)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Sending {}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{}\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
            log_out.truncate(0)

        r = self.session.post(
            self.url, data=base64.b64encode(msg.render_bytes()),
            headers={
                'Content-Type': 'text/plain',
            },
        )

        if r.status_code < 200 or r.status_code > 299:
            raise FinTSConnectionError('Bad status code {}'.format(r.status_code))

        response = base64.b64decode(r.text.encode('iso-8859-1'))
        retval = FinTSInstituteMessage(segments=response)

        with Password.protect():
            log_msg = reduce_message_for_log(retval)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Received {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n{}\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
        return retval
``` 

This code now uses `httpx` for HTTP requests while maintaining the original structure and functionality of the code.