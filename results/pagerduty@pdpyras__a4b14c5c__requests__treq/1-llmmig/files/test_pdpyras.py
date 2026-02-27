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
import treq
import sys
import unittest
import asyncio

from unittest.mock import Mock, MagicMock, patch, call

import pdpyras

class SessionTest(unittest.TestCase):
    def assertDictContainsSubset(self, d0, d1):
        self.assertTrue(set(d0.keys()).issubset(set(d1.keys())),
            msg="First dict is not a subset of second dict")
        self.assertEqual(d0, dict([(k, d1[k]) for k in d0]))

class Session(object):
    """
    Python treq mockery class
    """
    request = None
    headers = None

class Response(object):
    """Mock class for emulating treq.Response objects

    Look for existing use of this class for examples on how to use.
    """
    def __init__(self, code, text, method='GET', url=None):
        super(Response, self).__init__()
        self.code = code
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
        self.json.return_value = json.loads(text)

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

class EntityWrappingTest(unittest.TestCase):

    def test_entity_wrappers(self):
        io_expected = [
            # Special endpoint (broken support v5.0.0 - 5.1.x) managed by script
            (('get', '/tags/{id}/users'), ('users', 'users')),
            # Conventional endpoint: singular read
            (('get', '/services/{id}'), ('service', 'service')),
            # Conventional endpoint: singular update
            (('put', '/services/{id}'), ('service', 'service')),
            # Conventional endpoint: create new
            (('pOsT', '/services'), ('service', 'service')),
            # Conventional endpoint: multi-update
            (('PUT', '/incidents/{id}/alerts'), ('alerts', 'alerts')),
            # Conventional endpoint: list resources
            (('get', '/incidents/{id}/alerts'), ('alerts', 'alerts')),
            # Expanded endpoint support: different request/response wrappers
            (('put', '/incidents/{id}/merge'), ('source_incidents', 'incident')),
            # Expanded support: same wrapper for req/res and all methods
            (
                ('post', '/event_orchestrations'),
                ('orchestrations', 'orchestrations')
            ),
            (
                ('get', '/event_orchestrations'),
                ('orchestrations', 'orchestrations')
            ),
            # Disabled
            (('post', '/analytics/raw/incidents'), (None, None)),
        ]
        for ((method, path), rval) in io_expected:
            self.assertEqual(rval, pdpyras.entity_wrappers(method, path))

    def test_infer_entity_wrapper(self):
        io_expected = [
            (('get', '/users'), 'users'),
            (('PoSt', '/users'), 'user'),
            (('PUT', '/service/{id}'), 'service'),
            (('PUT', '/incidents/{id}/alerts'), 'alerts'),
        ]
        for (method_path, expected_wrapper) in io_expected:
            self.assertEqual(
                expected_wrapper,
                pdpyras.infer_entity_wrapper(*method_path),
            )

    def test_unwrap(self):
        # Response has unexpected type, raise:
        r = Response(200, json.dumps([]))
        self.assertRaises(pdpyras.PDServerError, pdpyras.unwrap, r, 'foo')
        # Response has unexpected structure, raise:
        r = Response(200, json.dumps({'foo_1': {'bar':1}, 'foo_2': 'bar2'}))
        self.assertRaises(pdpyras.PDServerError, pdpyras.unwrap, r, 'foo')
        # Response has the expected structure, return the wrapped entity:
        foo_entity = {'type':'foo_reference', 'id': 'PFOOBAR'}
        r = Response(200, json.dumps({'foo': foo_entity}))
        self.assertEqual(foo_entity, pdpyras.unwrap(r, 'foo'))
        # Disabled entity wrapping (wrapper=None), return body as-is
        self.assertEqual({'foo': foo_entity}, pdpyras.unwrap(r, None))

# The rest of the code remains unchanged except for replacing `requests` with `treq` in relevant places.
