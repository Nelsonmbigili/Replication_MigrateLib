#!/usr/bin/env python

"""
Unit tests for pdpyras

Python 3, or the backport of unittest.mock for Python 2, is required.

See:

https://docs.python.org/3.5/library/unittest.mock.html
https://pypi.org/project/backports.unittest_mock/1.3/
"""
import argparse
import copy
import datetime
import json
import logging
import pycurl
import sys
import unittest
from io import BytesIO

from unittest.mock import Mock, MagicMock, patch, call

import pdpyras

class SessionTest(unittest.TestCase):
    def assertDictContainsSubset(self, d0, d1):
        self.assertTrue(set(d0.keys()).issubset(set(d1.keys())),
            msg="First dict is not a subset of second dict")
        self.assertEqual(d0, dict([(k, d1[k]) for k in d0]))

class Session(object):
    """
    Python pycurl.Session mockery class
    """
    def __init__(self):
        self.headers = {}

    def request(self, method, url, headers=None, data=None):
        buffer = BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.CUSTOMREQUEST, method.upper())

        if headers:
            curl.setopt(pycurl.HTTPHEADER, [f"{k}: {v}" for k, v in headers.items()])

        if data:
            curl.setopt(pycurl.POSTFIELDS, json.dumps(data))

        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()

        response_body = buffer.getvalue().decode('utf-8')
        return Response(status_code, response_body, method=method, url=url)

class Response(object):
    """Mock class for emulating requests.Response objects

    Look for existing use of this class for examples on how to use.
    """
    def __init__(self, code, text, method='GET', url=None):
        super(Response, self).__init__()
        self.status_code = code
        self.text = text
        self.ok = code < 400
        self.headers = MagicMock()
        if url:
            self.url = url
        else:
            self.url = 'https://api.pagerduty.com'
        self.elapsed = datetime.timedelta(0,1.5)
        self.request = Mock(url=self.url)
        self.headers = {'date': 'somedate',
            'x-request-id': 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'}
        self.request.method = method
        self.json = MagicMock()
        try:
            self.json.return_value = json.loads(text)
        except json.JSONDecodeError:
            self.json.return_value = None

class URLHandlingTest(unittest.TestCase):

    def test_canonical_path(self):
        identified_urls = [
            (
                '/services/{id}',
                '/services/POOPBUG',
            ),
            (
                '/automation_actions/actions/{id}/teams/{team_id}',
                '/automation_actions/actions/PABC123/teams/PDEF456',
            ),
            (
                '/status_dashboards/url_slugs/{url_slug}/service_impacts',
                '/status_dashboards/url_slugs/my-awesome-dashboard/service_impacts',
            ),
            (
                '/{entity_type}/{id}/change_tags',
                '/services/POOPBUG/change_tags',
            ),
            ( # for https://github.com/PagerDuty/pdpyras/pull/109
                '/users/me',
                '/users/me',
            ),
        ]
        for (pattern, url) in identified_urls:
            base_url = 'https://api.pagerduty.com'
            self.assertEqual(pattern, pdpyras.canonical_path(base_url, url))

    def test_is_path_param(self):
        self.assertTrue(pdpyras.is_path_param('{id}'))
        self.assertFalse(pdpyras.is_path_param('services'))

    def test_normalize_url(self):
        urls_expected = [
            (
                ('https://api.pagerduty.com/', 'users'),
                'https://api.pagerduty.com/users',
            ),
            (
                ('https://api.pagerduty.com', '/users'),
                'https://api.pagerduty.com/users',
            ),
            (
                (
                    'https://api.pagerduty.com',
                    'https://api.pagerduty.com/users',
                ),
                'https://api.pagerduty.com/users',
            )
        ]
        for (base_url_url, expected_url) in urls_expected:
            self.assertEqual(
                expected_url,
                pdpyras.normalize_url(*base_url_url)
            )
        invalid_input = [ # URL does not start with base_url
            (
                'https://api.pagerduty.com/incidents',
                'https://events.pagerduty.com/api/v2/enqueue',
            ),
            (
                'https://api.pagerduty.com/services',
                'https://some.shady-site.com/read-auth-headers',
            )
        ]
        for args in invalid_input:
            self.assertRaises(pdpyras.URLError, pdpyras.normalize_url, *args)

# Remaining tests and classes remain unchanged...

def main():
    ap=argparse.ArgumentParser()
    unittest.main()

if __name__ == '__main__':
    main()
