The following Python code currently uses the library "httpx" version 0.26.0.
Migrate this code to use the library "urllib3" version 2.4.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "httpx" to "urllib3".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "httpx" and "urllib3".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
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