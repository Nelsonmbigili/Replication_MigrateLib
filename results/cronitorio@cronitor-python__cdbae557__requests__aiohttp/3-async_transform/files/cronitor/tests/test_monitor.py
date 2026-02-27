import copy
import cronitor
import unittest
from unittest.mock import call, patch, ANY

import cronitor

FAKE_API_KEY = 'cb54ac4fd16142469f2d84fc1bbebd84XXXDEADXXX'

MONITOR = {
    'type': 'job',
    'key': 'a-test_key',
    'schedule': '* * * * *',
    'assertions': [
        'metric.duration < 10 seconds'
    ],
    # 'notify': ['devops-alerts']
}
MONITOR_2 = copy.deepcopy(MONITOR)
MONITOR_2['key'] = 'another-test-key'

YAML_FORMAT_MONITORS = {
    'jobs': {
        MONITOR['key']: MONITOR,
        MONITOR_2['key']: MONITOR_2
    }
}

cronitor.api_key = FAKE_API_KEY
import pytest

class MonitorTests(unittest.TestCase):

    @pytest.mark.asyncio
    @patch('cronitor.Monitor._put', return_value=[MONITOR])
    async def test_create_monitor(self, mocked_create):
        monitor = await cronitor.Monitor.put(**MONITOR)
        self.assertEqual(monitor.data.key, MONITOR['key'])
        self.assertEqual(monitor.data.assertions, MONITOR['assertions'])
        self.assertEqual(monitor.data.schedule, MONITOR['schedule'])

    @pytest.mark.asyncio
    @patch('cronitor.Monitor._put', return_value=[MONITOR, MONITOR_2])
    async def test_create_monitors(self, mocked_create):
        monitors = await cronitor.Monitor.put([MONITOR, MONITOR_2])
        self.assertEqual(len(monitors), 2)
        self.assertCountEqual([MONITOR['key'], MONITOR_2['key']], list(map(lambda m: m.data.key, monitors)))

    @pytest.mark.asyncio
    @patch('cronitor.Monitor._req.put')
    async def test_create_monitor_fails(self, mocked_put):
        mocked_put.return_value.status_code = 400
        with self.assertRaises(cronitor.APIValidationError):
             await cronitor.Monitor.put(**MONITOR)

    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_get_monitor_invalid_code(self, mocked_get):
        mocked_get.return_value.status_code = 404
        with self.assertRaises(cronitor.MonitorNotFound):
             monitor = cronitor.Monitor("I don't exist")
             monitor.data

    @pytest.mark.asyncio
    @patch('cronitor.Monitor._put')
    async def test_update_monitor_data(self, mocked_update):
        monitor_data = MONITOR.copy()
        monitor_data.update({'name': 'Updated Name'})
        mocked_update.return_value = [monitor_data]

        monitor = await cronitor.Monitor.put(key=MONITOR['key'], name='Updated Name')
        self.assertEqual(monitor.data.name, 'Updated Name')

    @pytest.mark.asyncio
    @patch('cronitor.Monitor._req.put')
    async def test_update_monitor_fails_validation(self, mocked_update):
        mocked_update.return_value.status_code = 400
        with self.assertRaises(cronitor.APIValidationError):
            await cronitor.Monitor.put(schedule='* * * * *')

    @pytest.mark.asyncio
    @patch('cronitor.Monitor._put', return_value=YAML_FORMAT_MONITORS)
    async def test_create_monitors_yaml_body(self, mocked_create):
        monitors = await cronitor.Monitor.put(monitors=YAML_FORMAT_MONITORS, format='yaml')
        self.assertIn(MONITOR['key'], monitors['jobs'])
        self.assertIn(MONITOR_2['key'], monitors['jobs'])

    @pytest.mark.asyncio
    @patch('requests.delete')
    async def test_delete_no_id(self, mocked_delete):
        mocked_delete.return_value.status_code = 204
        monitor = cronitor.Monitor(MONITOR['key'])
        await monitor.delete()

