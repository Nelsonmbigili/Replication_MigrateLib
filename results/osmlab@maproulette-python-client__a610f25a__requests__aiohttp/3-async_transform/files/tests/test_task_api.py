import maproulette
import unittest
from tests.sample_data import test_geojson
from unittest.mock import patch
import pytest


class TestTaskAPI(unittest.TestCase):

    config = maproulette.Configuration(api_key="API_KEY")
    api = maproulette.Task(config)
    url = config.api_url

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.get')
    async def test_get_task_by_id(self, mock_request, api_instance=api):
        test_task_id = '42914448'
        await api_instance.get_task_by_id(test_task_id)
        mock_request.assert_called_once_with(
            f'{self.url}/task/{test_task_id}',
            params=None)

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.get')
    async def test_get_task_history(self, mock_request, api_instance=api):
        test_task_id = '42914448'
        await api_instance.get_task_history(test_task_id)
        mock_request.assert_called_once_with(
            f'{self.url}/task/{test_task_id}/history',
            params=None)

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.post')
    async def test_create_task(self, mock_request, api_instance=api):
        geometries = test_geojson['features'][0]['geometry']
        test_task_model = maproulette.TaskModel(name='test_task',
                                                parent='12345',
                                                geometries=geometries)
        await api_instance.create_task(test_task_model)
        mock_request.assert_called_once_with(
            f'{self.url}/task',
            json=test_task_model.to_dict(),
            params=None)

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.post')
    async def test_create_tasks(self, mock_request, api_instance=api):
        test_tasks = []
        geometries = test_geojson['features'][0]['geometry']
        test_task_model = maproulette.TaskModel(name='test_task',
                                                parent='12345',
                                                geometries=geometries)
        test_tasks.append(test_task_model.to_dict())
        await api_instance.create_tasks(test_tasks)
        input_json_list = []
        for task in test_tasks:
            input_json_list.append({'name': task['name'],
                                    'parent': task['parent'],
                                    'geometries': task['geometries']})
        mock_request.assert_called_once_with(
            f'{self.url}/tasks',
            json=input_json_list,
            params=None)

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.post')
    async def test_create_cooperative_task(self, mock_request, api_instance=api):
        test_child_operation = maproulette.ChildOperationModel(
            operation="setTags",
            data={"test_tag_4": "True"})
        test_parent_operation = maproulette.ParentOperationModel(
            operation_type="modifyElement",
            element_type="way",
            osm_id="31110737",
            child_operations=test_child_operation.to_dict())
        test_cooperative_work = maproulette.CooperativeWorkModel(
            version=2,
            type=1,
            parent_operations=test_parent_operation)
        test_task = maproulette.TaskModel(
            name="Test_Coop_Task",
            parent=1234,
            geometries=test_geojson['features'][0]['geometry'],
            cooperative_work=test_cooperative_work)
        with self.assertRaises(ValueError):
            test_child_operation.operation = "invalid"
        with self.assertRaises(ValueError):
            test_parent_operation.operation_type = "invalid"
        with self.assertRaises(ValueError):
            test_parent_operation.element_type = "invalid"
        with self.assertRaises(ValueError):
            test_parent_operation.osm_id = "invalid"
        with self.assertRaises(ValueError):
            test_cooperative_work.type = "invalid"
        await api_instance.create_task(test_task)
        mock_request.assert_called_once_with(
            f'{self.url}/task',
            json=test_task.to_dict(),
            params=None)

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.put')
    async def test_update_tasks(self, mock_request, api_instance=api):
        geometries = test_geojson['features'][0]['geometry']
        test_task_model = maproulette.TaskModel(name='test_task',
                                                parent='12345',
                                                geometries=geometries)
        await api_instance.update_tasks(test_task_model)
        mock_request.assert_called_once_with(
            f'{self.url}/tasks',
            json=test_task_model,
            params=None)

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.get')
    async def test_get_task_tags(self, mock_request, api_instance=api):
        test_task_id = '42914448'
        await api_instance.get_task_tags(test_task_id)
        mock_request.assert_called_once_with(
            f'{self.url}/task/{test_task_id}/tags',
            params=None)

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.delete')
    async def test_delete_task_tags(self, mock_request, api_instance=api):
        task_id = '42914448'
        tags = 'test'
        await api_instance.delete_task_tags(task_id, tags)
        mock_request.assert_called_once_with(
            f'{self.url}/task/{task_id}/tags',
            params={'tags': tags})

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.get')
    async def test_get_tasks_by_tags(self, mock_request, api_instance=api):
        tags = 'test'
        await api_instance.get_tasks_by_tags(tags)
        mock_request.assert_called_once_with(
            f'{self.url}/tasks/tags',
            params={'tags': tags,
                    'limit': '10',
                    'page': '0'})

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.put')
    async def test_get_tasks_by_bounding_box(self, mock_request, api_instance=api):
        left = -1.22321018
        bottom = 47.690315
        right = -122.306191
        top = 47.706912
        await api_instance.get_tasks_by_bounding_box(
            left=left,
            bottom=bottom,
            right=right,
            top=top
        )
        mock_request.assert_called_once_with(
            f'{self.url}/tasks/box/{left}/{bottom}/{right}/{top}',
            json=None,
            params={
                "limit": '10000',
                "page": '0',
                "excludeLocked": 'false',
                "order": 'ASC',
                "includeTotal": 'false',
                "includeGeometries": 'false',
                "includeTags": 'false'})

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.get')
    async def test_update_task_tags(self, mock_request, api_instance=api):
        task_id = '42914448'
        tags = 'test'
        await api_instance.update_task_tags(task_id, tags)
        mock_request.assert_called_once_with(
            f'{self.url}/task/{task_id}/tags/update',
            params={'tags': tags})

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.put')
    async def test_update_task_status(self, mock_request, api_instance=api):
        task_id = '42914448'
        status = 3
        await api_instance.update_task_status(task_id, status)
        mock_request.assert_called_once_with(
            f'{self.url}/task/{task_id}/{status}',
            params={'comment': 'None',
                    'tags': 'None',
                    'requestReview': 'None'},
            json=None)

    @pytest.mark.asyncio
    @patch('maproulette.api.maproulette_server.requests.Session.get')
    async def test_get_task_comments(self, mock_request, api_instance=api):
        task_id = '42914448'
        await api_instance.get_task_comments(task_id)
        mock_request.assert_called_once_with(
            f'{self.url}/task/{task_id}/comments',
            params=None)

    def test_batch_generator(self, api_instance=api):

        batch_size = 10
        test_length = 1234
        test_list = [i for i in range(test_length)]
        running_total = 0
        for chunk in api_instance.batch_generator(test_list, batch_size):
            running_total += len(chunk)
            self.assertIsInstance(chunk, list)
            self.assertLessEqual(len(chunk), batch_size)
        self.assertEqual(test_length, running_total)
