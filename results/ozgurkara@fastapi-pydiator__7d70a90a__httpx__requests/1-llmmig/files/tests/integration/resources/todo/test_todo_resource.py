from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK
import requests


BASE_URL = "http://testserver"  # Replace with the actual base URL of your API


class TestTodo:

    def test_get_todo_all(self):
        response = requests.get(f"{BASE_URL}/v1/todos")
        items = response.json()["items"]

        assert response.status_code == HTTP_200_OK
        assert len(items) == 2
        assert items[0]["id"] == 1
        assert items[0]["title"] == "title 1"
        assert items[1]["id"] == 2
        assert items[1]["title"] == "title 2"

    def test_get_todo_by_id(self):
        response = requests.get(f"{BASE_URL}/v1/todos/1")

        assert response.status_code == HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["title"] == "title 1"

    def test_add_todo(self):
        response = requests.post(f"{BASE_URL}/v1/todos", json={
            "title": "title 3"
        })

        assert response.status_code == HTTP_200_OK
        assert response.json()["success"]

    def test_add_todo_should_return_unprocessable_when_invalid_entity(self):
        response = requests.post(f"{BASE_URL}/v1/todos", json=None)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_todo(self):
        response = requests.put(f"{BASE_URL}/v1/todos/1", json={
            "title": "title 1 updated"
        })

        assert response.status_code == HTTP_200_OK
        assert response.json()["success"]

    def test_update_todo_should_return_unprocessable_when_invalid_entity(self):
        response = requests.put(f"{BASE_URL}/v1/todos/1", json={

        })

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_todo(self):
        response = requests.delete(f"{BASE_URL}/v1/todos/1")

        assert response.status_code == HTTP_200_OK
        assert response.json()["success"]
