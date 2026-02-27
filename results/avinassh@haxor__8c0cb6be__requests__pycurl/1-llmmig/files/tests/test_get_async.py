#!/usr/bin/env python

"""
Tests supported Hacker News API versions

@author john keck
@email robertjkeck
"""

import unittest
import pycurl
from io import BytesIO
import json


class HackerNews:
    def __init__(self):
        pass

    def _run_async(self, urls):
        responses = []
        for url in urls:
            buffer = BytesIO()
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.WRITEDATA, buffer)
            try:
                curl.perform()
                status_code = curl.getinfo(pycurl.RESPONSE_CODE)
                if status_code == 200:
                    body = buffer.getvalue().decode('utf-8')
                    responses.append(json.loads(body))
                else:
                    responses.append(None)
            except pycurl.error:
                responses.append(None)
            finally:
                curl.close()
                buffer.close()
        return responses


class TestGetAsync(unittest.TestCase):

    def setUp(self):
        self.hn = HackerNews()
        self.url = 'https://hacker-news.firebaseio.com/v0/item/8863.json'
        self.err_url = 'https://hacker-news.firebaseio.com/v0/items/8863.json'

    def test_get_async(self):
        response = self.hn._run_async([self.url])
        self.assertEqual(response[0]['id'], 8863)
        self.assertEqual(response[0]['by'], 'dhouston')

    def test_get_async_error(self):
        response = self.hn._run_async([self.err_url])
        self.assertEqual(response, [None])

    def tearDown(self):
        pass  # No session to close in pycurl


if __name__ == '__main__':
    unittest.main()
