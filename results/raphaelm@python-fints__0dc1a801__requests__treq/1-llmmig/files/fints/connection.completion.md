### Explanation of Changes
To migrate the code from the `requests` library to the `treq` library, the following changes were made:
1. **Session Management**: `treq` does not use sessions like `requests`. Instead, it uses an asynchronous approach with `twisted`. The `requests.session()` was removed, and `treq` functions are used directly.
2. **Asynchronous Requests**: `treq` is asynchronous, so the `send` method was modified to be asynchronous (`async def`) and uses `await` for the `treq.post` call.
3. **Response Handling**: `treq` returns a `Deferred` object, so the response content is accessed using `await response.text()` or `await response.content()`.
4. **Error Handling**: The status code is checked using `response.code` instead of `response.status_code`.
5. **Dependencies**: The `treq` library requires `twisted`, so the code assumes the application is already set up to work with `twisted`.

### Modified Code
```python
import base64
import io
import logging

import treq
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

    async def send(self, msg: FinTSMessage):
        log_out = io.StringIO()
        with Password.protect():
            log_msg = reduce_message_for_log(msg)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Sending {}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{}\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
            log_out.truncate(0)

        response = await treq.post(
            self.url,
            data=base64.b64encode(msg.render_bytes()),
            headers={
                'Content-Type': 'text/plain',
            },
        )

        if response.code < 200 or response.code > 299:
            raise FinTSConnectionError('Bad status code {}'.format(response.code))

        response_content = await response.text(encoding='iso-8859-1')
        decoded_response = base64.b64decode(response_content)
        retval = FinTSInstituteMessage(segments=decoded_response)

        with Password.protect():
            log_msg = reduce_message_for_log(retval)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Received {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n{}\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
        return retval
```

### Key Points
1. The `send` method is now asynchronous (`async def`) to accommodate `treq`'s asynchronous nature.
2. The `treq.post` function is used instead of `requests.session().post`.
3. The response content is accessed using `await response.text()` with the appropriate encoding (`iso-8859-1`).
4. The status code is checked using `response.code`.
5. The rest of the code remains unchanged to ensure compatibility with the existing application.