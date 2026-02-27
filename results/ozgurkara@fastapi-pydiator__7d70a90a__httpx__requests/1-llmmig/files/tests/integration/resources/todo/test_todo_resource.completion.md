### Explanation of Changes:
The original code uses `httpx` indirectly through the `test_app` object, which is likely a test client provided by a testing framework. Since the migration is to use the `requests` library, the `test_app` object is replaced with direct calls to `requests` methods (`get`, `post`, `put`, `delete`). The `requests` library does not have a built-in test client, so the base URL for the API (`/v1/todos`) is prefixed manually in each request.

Key changes:
1. Replaced `test_app.get`, `test_app.post`, `test_app.put`, and `test_app.delete` with `requests.get`, `requests.post`, `requests.put`, and `requests.delete`, respectively.
2. Added a `BASE_URL` variable to store the base URL of the API, which is prefixed to all endpoints.
3. Updated the `json` parameter in `requests` methods to match the behavior of `httpx`.

### Modified Code:
```python
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
```

### Notes:
- The `BASE_URL` variable is used to simulate the base URL of the API, which was previously handled by the `test_app` object.
- The `requests` library does not provide a test client, so this code assumes the API is running and accessible at the specified `BASE_URL`.
- If the `test_app` object was part of a testing framework (e.g., `pytest` with `httpx`), additional setup may be required to mock the API responses when using `requests`.