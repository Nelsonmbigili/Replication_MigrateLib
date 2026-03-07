import json
import urllib3
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK

http = urllib3.PoolManager()

class TestTodo:

    def test_get_todo_all(self, test_app):
        response = http.request('GET', 'http://test_app/v1/todos')
        items = json.loads(response.data.decode('utf-8'))["items"]

        assert response.status == HTTP_200_OK
        assert len(items) == 2
        assert items[0]["id"] == 1
        assert items[0]["title"] == "title 1"
        assert items[1]["id"] == 2
        assert items[1]["title"] == "title 2"

    def test_get_todo_by_id(self, test_app):
        response = http.request('GET', 'http://test_app/v1/todos/1')

        assert response.status == HTTP_200_OK
        assert json.loads(response.data.decode('utf-8'))["id"] == 1
        assert json.loads(response.data.decode('utf-8'))["title"] == "title 1"

    def test_add_todo(self, test_app):
        response = http.request('POST', 'http://test_app/v1/todos', 
                                 body=json.dumps({"title": "title 3"}), 
                                 headers={'Content-Type': 'application/json'})

        assert response.status == HTTP_200_OK
        assert json.loads(response.data.decode('utf-8'))["success"]

    def test_add_todo_should_return_unprocessable_when_invalid_entity(self, test_app):
        response = http.request('POST', 'http://test_app/v1/todos', 
                                 body=json.dumps(None), 
                                 headers={'Content-Type': 'application/json'})

        assert response.status == HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_todo(self, test_app):
        response = http.request('PUT', 'http://test_app/v1/todos/1', 
                                 body=json.dumps({"title": "title 1 updated"}), 
                                 headers={'Content-Type': 'application/json'})

        assert response.status == HTTP_200_OK
        assert json.loads(response.data.decode('utf-8'))["success"]

    def test_update_todo_should_return_unprocessable_when_invalid_entity(self, test_app):
        response = http.request('PUT', 'http://test_app/v1/todos/1', 
                                 body=json.dumps({}), 
                                 headers={'Content-Type': 'application/json'})

        assert response.status == HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_todo(self, test_app):
        response = http.request('DELETE', 'http://test_app/v1/todos/1')

        assert response.status == HTTP_200_OK
        assert json.loads(response.data.decode('utf-8'))["success"]
