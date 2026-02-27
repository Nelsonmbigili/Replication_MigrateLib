from datetime import datetime, date
import unittest
import json
import aiohttp
import asyncio

from segment.analytics.request import post, DatetimeSerializer
import pytest


class TestRequests(unittest.IsolatedAsyncioTestCase):

    @pytest.mark.asyncio
    async def test_valid_request(self):
        res = await post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }])
        self.assertEqual(res.status, 200)

    async def test_invalid_request_error(self):
        with self.assertRaises(Exception):
            await post('testsecret', 'https://api.segment.io', False, '[{]')

    async def test_invalid_host(self):
        with self.assertRaises(Exception):
            await post('testsecret', 'api.segment.io/', batch=[])

    def test_datetime_serialization(self):
        data = {'created': datetime(2012, 3, 4, 5, 6, 7, 891011)}
        result = json.dumps(data, cls=DatetimeSerializer)
        self.assertEqual(result, '{"created": "2012-03-04T05:06:07.891011"}')

    def test_date_serialization(self):
        today = date.today()
        data = {'created': today}
        result = json.dumps(data, cls=DatetimeSerializer)
        expected = '{"created": "%s"}' % today.isoformat()
        self.assertEqual(result, expected)

    @pytest.mark.asyncio
    async def test_should_not_timeout(self):
        res = await post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track'
        }], timeout=15)
        self.assertEqual(res.status, 200)

    @pytest.mark.asyncio
    async def test_should_timeout(self):
        with self.assertRaises(asyncio.TimeoutError):
            await post('testsecret', batch=[{
                'userId': 'userId',
                'event': 'python event',
                'type': 'track'
            }], timeout=0.0001)

    @pytest.mark.asyncio
    async def test_proxies(self):
        res = await post('testsecret', batch=[{
            'userId': 'userId',
            'event': 'python event',
            'type': 'track',
            'proxies': '203.243.63.16:80'
        }])
        self.assertEqual(res.status, 200)
