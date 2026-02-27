### Explanation of Changes
To migrate the code from the `requests` library to the `httpx` library, the following changes were made:
1. **Session Initialization**: Replaced `requests.session()` with `httpx.Client()`, as `httpx.Client` is the equivalent of a session in `httpx`.
2. **POST Request**: Updated the `post` method call to use `httpx.Client.post`. The parameters (`url`, `data`, and `headers`) remain the same.
3. **Response Content**: In `httpx`, the response content is accessed using `response.content` (same as in `requests`), so no changes were needed here.
4. **Error Handling**: The status code check remains the same, as `httpx` also uses `response.status_code`.
5. **Session Cleanup**: Added a `close()` call for the `httpx.Client` session to ensure proper cleanup, as `httpx` requires explicit session closure. Alternatively, a context manager (`with`) could be used, but to avoid altering the structure of the code, the `close()` method was used.

### Modified Code
Here is the complete code after migrating to `httpx`:

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

        response = base64.b64decode(r.content.decode('iso-8859-1'))
        retval = FinTSInstituteMessage(segments=response)

        with Password.protect():
            log_msg = reduce_message_for_log(retval)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Received {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n{}\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
        
        return retval

    def close(self):
        self.session.close()
```

### Key Notes
- The `close()` method was added to ensure the `httpx.Client` session is properly closed when no longer needed. This is important for resource management.
- The rest of the code remains unchanged, as the migration only required replacing `requests` with `httpx` and ensuring compatibility with the new library.