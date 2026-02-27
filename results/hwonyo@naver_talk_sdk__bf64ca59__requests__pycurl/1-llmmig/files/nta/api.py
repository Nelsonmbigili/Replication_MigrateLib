"""
    nta
    ~~~

    :copyright: (c) 2017 by Wonyo Hwang. hollal0726@gmail.com
    :license: MIT, see LICENSE for more details.

"""
import re
import pycurl
import json
from io import BytesIO

from .exceptions import NaverTalkApiError, NaverTalkApiConnectionError
from .models.responses import NaverTalkResponse, NaverTalkImageResponse
from .models.payload import (
    ProfilePayload, GenericPayload, ImageUploadPayload, ThreadPayload, ActionPayload,
    PersistentMenuPayload, ProductMessage
)
from .models.events import *

from .utils import LOGGER, PY3, _byteify


class WebhookParser(object):
    """Webhook Parser.
    WebhookParser for parsing json request from navertalk.
    It returns parsed data in an Event instance
    with snake case attributes.
    """

    def parse(self, req):
        """
        Parse webhook request
        and change into the Event instance

        Args:
            - req: request body from navertalk

        Returns:
            - event: Event instance in mdoels.events
        """
        if not PY3:
            req_json = json.loads(req, object_hook=_byteify)
        else:
            req_json = json.loads(req)

        event_type = req_json['event']
        if event_type == 'open':
            event = OpenEvent.new_from_json_dict(req_json)
        elif event_type == 'send':
            event = SendEvent.new_from_json_dict(req_json)
        elif event_type == 'leave':
            event = LeaveEvent.new_from_json_dict(req_json)
        elif event_type == 'friend':
            event = FriendEvent.new_from_json_dict(req_json)
        elif event_type == 'echo':
            event = EchoEvent.new_from_json_dict(req_json)
        elif event_type == 'pay_complete':
            event = PayCompleteEvent.new_from_json_dict(req_json)
        elif event_type == 'pay_confirm':
            event = PayConfirmEvent.new_from_json_dict(req_json)
        elif event_type == 'profile':
            event = ProfileEvent.new_from_json_dict(req_json)
        elif event_type == 'handover':
            event = HandOverEvent.new_from_json_dict(req_json)
        else:
            LOGGER.warn('Unknown event type: %s' % event_type)
            event = None

        return event


class NaverTalkApi(object):
    """NaverTalk Webhook Agent"""

    DEFAULT_API_ENDPOINT = 'https://gw.talk.naver.com/chatbot/v1/event'

    def __init__(self, naver_talk_access_token, endpoint=DEFAULT_API_ENDPOINT, **options):
        """ __init__ method.

        Args:
            - naver_talk_access_token: issued access_token
            - endpoint: endpoint to post request
        """

        self._endpoint = endpoint
        self._headers = {
            'Content-type': 'application/json;charset=UTF-8',
            'Authorization': naver_talk_access_token
        }
        self.parser = WebhookParser()

    # Other methods remain unchanged...

    def _send(self, payload, callback=None, response_form=NaverTalkResponse):
        """
        Request Post to Navertalktalk.
        """
        data = payload.as_json_string()
        response_buffer = BytesIO()

        # Initialize pycurl
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, self._endpoint)
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.POSTFIELDS, data)
        curl.setopt(pycurl.HTTPHEADER, [f"{key}: {value}" for key, value in self._headers.items()])
        curl.setopt(pycurl.WRITEDATA, response_buffer)

        try:
            curl.perform()
            status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        except pycurl.error as e:
            raise NaverTalkApiConnectionError(f"Connection error: {e}")
        finally:
            curl.close()

        # Check HTTP status code
        if status_code != 200:
            raise NaverTalkApiConnectionError(f"HTTP error: {status_code}")

        # Parse the response
        response_body = response_buffer.getvalue().decode('utf-8')
        try:
            response_json = json.loads(response_body)
        except json.JSONDecodeError as e:
            raise NaverTalkApiConnectionError(f"Failed to parse JSON response: {e}")

        res = response_form.new_from_json_dict(response_json)
        self.__error_check(res)

        if callback is not None:
            callback(res, payload)

        if self._after_send:
            self._after_send(res, payload)

    # Other methods remain unchanged...
