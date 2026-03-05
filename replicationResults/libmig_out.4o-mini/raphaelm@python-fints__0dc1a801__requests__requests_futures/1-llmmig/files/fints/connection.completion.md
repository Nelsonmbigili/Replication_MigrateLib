### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Change**: The `requests` library was replaced with `requests_futures.sessions`. This allows us to use the `FuturesSession` class, which supports asynchronous requests.
2. **Session Initialization**: Instead of creating a standard `requests.session()`, we now create a `FuturesSession()` instance. This enables the use of asynchronous requests.
3. **Asynchronous Request Handling**: The `post` method of `FuturesSession` returns a `Future` object. We need to call the `result()` method on this object to get the actual response.

The rest of the code remains unchanged to adhere to the guidelines provided.

### Modified Code
```python
import base64
import io
import logging

from requests_futures.sessions import FuturesSession
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
        self.session = FuturesSession()

    def send(self, msg: FinTSMessage):
        log_out = io.StringIO()
        with Password.protect():
            log_msg = reduce_message_for_log(msg)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Sending {}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{}\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
            log_out.truncate(0)

        future = self.session.post(
            self.url, data=base64.b64encode(msg.render_bytes()),
            headers={
                'Content-Type': 'text/plain',
            },
        )

        r = future.result()  # Get the actual response from the Future

        if r.status_code < 200 or r.status_code > 299:
            raise FinTSConnectionError('Bad status code {}'.format(r.status_code))

        response = base64.b64decode(r.content.decode('iso-8859-1'))
        retval = FinTSInstituteMessage(segments=response)

        with Password.protect():
            log_msg = reduce_message_for_log(retval)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Received {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n{}\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
        return retval
```