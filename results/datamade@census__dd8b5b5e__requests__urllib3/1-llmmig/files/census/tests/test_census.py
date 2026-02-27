#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import unittest
import json
import urllib3

from census.core import (
    Census, UnsupportedYearException)

KEY = os.environ.get('CENSUS_KEY', '')

CLIENTS = (
    ('acs5', (
        'us', 'state', 'state_county', 'state_county_subdivision',
        'state_county_tract', 'state_county_blockgroup',
        'state_place', 'state_district',
        'state_congressional_district',
        'state_legislative_district_upper',
        'state_legislative_district_lower', 'zipcode',
    )),
    ('acs1dp', (
        'us', 'state', 'state_congressional_district',
    )),
    ('sf1', (
        'state', 'state_county', 'state_county_subdivision',
        'state_county_tract', 'state_county_blockgroup',
        'state_place', 'state_congressional_district',
        'state_msa', 'state_csa', 'state_district_place',
        'state_zipcode',
    )),
    ('sf3', (
        'state', 'state_county', 'state_county_tract',
        'state_county_blockgroup', 'state_place',
    )),
    ('pl', (
        'us', 'state', 'state_county', 'state_county_subdivision',
        'state_county_tract', 'state_county_blockgroup',
        'state_place', 'state_congressional_district',
        'state_legislative_district_upper',
        'state_legislative_district_lower',
    ))
)

TEST_DATA = {
    'state_fips': '24',
    'county_fips': '031',
    'subdiv_fips': '90796',
    'tract': '700706',
    'blockgroup': '1',
    'place': '31175',
    'district': '06',       # for old `state_district` calling.
    'congressional_district': '06',
    'legislative_district': '06',
    'zcta': '20877',
    'msa': '47900',
    'csa': '548',
}


class CensusTestCase(unittest.TestCase):

    def setUp(self):
        self._client = Census(KEY)
        self.http = urllib3.PoolManager()  # Replace requests.Session with urllib3.PoolManager

    def client(self, name):
        return getattr(self._client, name)

    def tearDown(self):
        self.http.clear()  # Close the PoolManager


class TestUnsupportedYears(CensusTestCase):

    def setUp(self):
        self._client = Census(KEY, year=2008)

    def test_acs5(self):
        client = self.client('acs5')
        self.assertRaises(UnsupportedYearException,
                          client.state, ('NAME', '06'))

    def test_acs5st(self):
        client = self.client('acs5st')
        self.assertRaises(UnsupportedYearException,
                          client.state, ('NAME', '06'))

    def test_acs1dp(self):
        client = self.client('acs1dp')
        self.assertRaises(UnsupportedYearException,
                          client.state, ('NAME', '06'))

    def test_sf1(self):
        client = self.client('sf1')
        self.assertRaises(UnsupportedYearException,
                          client.state, ('NAME', '06'))

    def test_pl(self):
        client = self.client('sf1')
        self.assertRaises(UnsupportedYearException,
                          client.state, ('NAME', '06'))


class TestEncoding(CensusTestCase):
    """
    Test character encodings of results are properly handled.
    """

    def test_la_canada_2015(self):
        """
        The 'La Cañada Flintridge city, California' place can be a problem.
        """
        geo = {
            'for': 'place:39003',
            'in': u'state:06'
        }
        response = self.http.request(
            'GET',
            f'https://api.census.gov/data/2015/acs5?get=NAME&for=place:39003&in=state:06&key={KEY}'
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(
            data[0]['NAME'],
            u'La Cañada Flintridge city, California'
        )


class TestEndpoints(CensusTestCase):

    def check_endpoints(self, client_name, tests, **kwargs):

        client = self.client(client_name)
        fields = ('NAME',)

        for method_name, expected in tests:

            msg = '{}.{}'.format(client_name, method_name)

            method = getattr(client, method_name)
            data = method(fields, **TEST_DATA, **kwargs)
            self.assertTrue(data, msg)
            self.assertEqual(data[0]['NAME'], expected, msg)
            time.sleep(0.2)

    def test_tables(self):
        self.client('acs5').tables()
        self.client('acs5').tables(2010)
        self.client('sf1').tables()
        self.client('pl').tables()

    def test_acs5(self):

        tests = (
            ('us', 'United States'),
            ('state', 'Maryland'),
            ('state_county', 'Montgomery County, Maryland'),
            ('state_county_subdivision',
                'District 9, Montgomery County, Maryland'),
            ('state_county_tract',
                'Census Tract 7007.06; Montgomery County; Maryland'),
            ('state_county_blockgroup',
                ('Block Group 1; Census Tract 7007.06; '
                    'Montgomery County; Maryland')),
            ('state_place', 'Gaithersburg city, Maryland'),
            ('state_district',
                'Congressional District 6 (118th Congress), Maryland'),
            ('state_congressional_district',
                'Congressional District 6 (118th Congress), Maryland'),
            ('state_legislative_district_upper',
                'State Senate District 6 (2022), Maryland'),
            ('state_legislative_district_lower',
                'State Legislative District 6 (2022), Maryland'),
            ('state_zipcode', 'ZCTA5 20877'),
        )

        self.check_endpoints('acs5', tests)

    def test_acs5_previous_years(self):

        tests = (
            ('us', 'United States'),
            ('state', 'Maryland'),
            ('state_county', 'Montgomery County, Maryland'),
            ('state_county_subdivision',
                'District 9, Montgomery County, Maryland'),
            ('state_county_tract',
                'Census Tract 7007.06, Montgomery County, Maryland'),
            ('state_county_blockgroup',
                ('Block Group 1, Census Tract 7007.06, '
                    'Montgomery County, Maryland')),
            ('state_place', 'Gaithersburg city, Maryland'),
            ('state_district',
                'Congressional District 6 (116th Congress), Maryland'),
            ('state_congressional_district',
                'Congressional District 6 (116th Congress), Maryland'),
            ('state_legislative_district_upper',
                'State Senate District 6 (2018), Maryland'),
            ('state_legislative_district_lower',
                'State Legislative District 6 (2018), Maryland'),
            ('state_zipcode', 'ZCTA5 20877'),
        )

        self.check_endpoints('acs5', tests, year=2019)
