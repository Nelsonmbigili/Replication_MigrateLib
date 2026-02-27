import unittest

import segment.analytics as analytics
import pytest


class TestModule(unittest.TestCase):

    # def failed(self):
    #     self.failed = True

    def setUp(self):
        self.failed = False
        analytics.write_key = 'testsecret'
        analytics.on_error = self.failed

    def test_no_write_key(self):
        analytics.write_key = None
        self.assertRaises(Exception, analytics.track)

    def test_no_host(self):
        analytics.host = None
        self.assertRaises(Exception, analytics.track)

    @pytest.mark.asyncio
    async def test_track(self):
        await analytics.track('userId', 'python module event')
        await analytics.flush()

    @pytest.mark.asyncio
    async def test_identify(self):
        await analytics.identify('userId', {'email': 'user@email.com'})
        await analytics.flush()

    @pytest.mark.asyncio
    async def test_group(self):
        await analytics.group('userId', 'groupId')
        await analytics.flush()

    @pytest.mark.asyncio
    async def test_alias(self):
        await analytics.alias('previousId', 'userId')
        await analytics.flush()

    @pytest.mark.asyncio
    async def test_page(self):
        await analytics.page('userId')
        await analytics.flush()

    @pytest.mark.asyncio
    async def test_screen(self):
        await analytics.screen('userId')
        await analytics.flush()

    @pytest.mark.asyncio
    async def test_flush(self):
        await analytics.flush()
