# -*- coding: utf-8 -*-
import aiohttp


def raise_requests_exception_mock(*args, **kwargs):
    raise aiohttp.ClientError


async def not_ok_response_mock(*args, **kwargs):
    class Response:
        ok = False
        text = 'text'
        content = 'content'

        def __bool__(self):
            return bool(self.ok)

        async def json(self):
            return {
                'message': 'an error message',
                'count': 1,
                'bpmn20Xml': '<my>test</xml>',
                'version': '7.12.0-alpha4',
                'cmmnXml': '<my>test</xml>',
                'dmnXml': '<my>test</xml>',
                'instructionReports': [],
                'enableTelemetry': None
            }

    return Response()


async def response_mock(*args, **kwargs):
    class Response:
        ok = True
        text = 'text'
        content = 'content'

        def __bool__(self):
            return bool(self.ok)

        async def json(self):
            return {
                'message': 'an error message',
                'count': 1,
                'bpmn20Xml': '<my>test</xml>',
                'cmmnXml': '<my>test</xml>',
                'dmnXml': '<my>test</xml>',
            }

    return Response()


async def count_response_mock(*args, **kwargs):
    class Response:
        ok = True

        def __bool__(self):
            return bool(self.ok)

        async def json(self):
            return {'count': 1}

    return Response()


async def version_response_mock(*args, **kwargs):
    class Response:
        ok = True

        def __bool__(self):
            return bool(self.ok)

        async def json(self):
            return {'version': '7.12.0-alpha4'}

    return Response()


async def fetch_response_mock(*args, **kwargs):
    class Response:

        async def json(self):
            return {'enableTelemetry': True}

    return Response()
