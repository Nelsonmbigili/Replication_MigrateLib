import base64
import io
import logging
import aiohttp

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
        self.session = aiohttp.ClientSession()

    async def send(self, msg: FinTSMessage):
        log_out = io.StringIO()
        with Password.protect():
            log_msg = reduce_message_for_log(msg)
            log_msg.print_nested(stream=log_out, prefix="\t")
            logger.debug("Sending {}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n{}\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
            log_out.truncate(0)

        try:
            async with self.session.post(
                self.url,
                data=base64.b64encode(msg.render_bytes()),
                headers={
                    'Content-Type': 'text/plain',
                },
            ) as response:
                if response.status < 200 or response.status > 299:
                    raise FinTSConnectionError('Bad status code {}'.format(response.status))

                response_content = await response.read()
                decoded_response = base64.b64decode(response_content.decode('iso-8859-1'))
                retval = FinTSInstituteMessage(segments=decoded_response)

                with Password.protect():
                    log_msg = reduce_message_for_log(retval)
                    log_msg.print_nested(stream=log_out, prefix="\t")
                    logger.debug("Received {}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n{}\n<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n".format("(abbrv.)" if log_configuration.reduced else "", log_out.getvalue()))
                return retval
        except aiohttp.ClientError as e:
            raise FinTSConnectionError(f"HTTP request failed: {e}")

    async def close(self):
        await self.session.close()
