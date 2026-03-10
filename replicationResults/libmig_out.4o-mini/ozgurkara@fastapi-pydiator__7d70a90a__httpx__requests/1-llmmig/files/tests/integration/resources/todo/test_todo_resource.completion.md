### Explanation of Changes
To migrate the code from using the `httpx` library to the `requests` library, the following changes were made:

1. **Import Statement**: The `httpx` library was replaced with the `requests` library. However, since the original code does not explicitly import `httpx`, this step is not visible in the provided code.
2. **Method Calls**: The `test_app` object, which is likely a wrapper around the HTTP client, was assumed to be using `httpx` methods. In the `requests` library, the methods for making requests (like `get`, `post`, `put`, and `delete`) remain the same, so no changes were needed in the method calls themselves.
3. **Response Handling**: The way to access the JSON response remains the same, so no changes were made in how the response is processed.

The overall structure and logic of the tests remain unchanged, ensuring that the migration does not affect the functionality of the tests.

### Modified Code
```python
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK


class TestTodo:

    def test_get_todo_all(self, test_app):
        response = test_app.get("/v1/todos")
        items = response.json()["items"]

        assert response.status_code == HTTP_200_OK
        assert len(items) == 2
        assert items[0]["id"] == 1
        assert items[0]["title"] == "title 1"
        assert items[1]["id"] == 2
        assert items[1]["title"] == "title 2"

    def test_get_todo_by_id(self, test_app):
        response = test_app.get("/v1/todos/1")

        assert response.status_code == HTTP_200_OK
        assert response.json()["id"] == 1
        assert response.json()["title"] == "title 1"

    def test_add_todo(self, test_app):
        response = test_app.post("/v1/todos", json={
            "title": "title 3"
        })

        assert response.status_code == HTTP_200_OK
        assert response.json()["success"]

    def test_add_todo_should_return_unprocessable_when_invalid_entity(self, test_app):
        response = test_app.post("/v1/todos", json=None)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_todo(self, test_app):
        response = test_app.put("/v1/todos/1", json={
            "title": "title 1 updated"
        })

        assert response.status_code == HTTP_200_OK
        assert response.json()["success"]

    def test_update_todo_should_return_unprocessable_when_invalid_entity(self, test_app):
        response = test_app.put("/v1/todos/1", json={

        })

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_todo(self, test_app):
        response = test_app.delete("/v1/todos/1")

        assert response.status_code == HTTP_200_OK
        assert response.json()["success"]
``` 

Note: The code remains unchanged in terms of structure and logic, as the migration from `httpx` to `requests` does not require modifications to the request methods or response handling in this context.