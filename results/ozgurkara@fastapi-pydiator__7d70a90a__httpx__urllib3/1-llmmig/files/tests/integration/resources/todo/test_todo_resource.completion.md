### Explanation of Changes:
The original code uses `httpx` indirectly through the `test_app` object to make HTTP requests. To migrate to `urllib3`, we need to replace the `test_app` object with direct usage of `urllib3`'s `PoolManager` for making HTTP requests. The `PoolManager` is used to manage connections and send requests. 

Key changes:
1. Replaced `test_app.get`, `test_app.post`, `test_app.put`, and `test_app.delete` with `urllib3.PoolManager` methods (`request`).
2. Updated the request syntax to match `urllib3`'s API, which uses `method`, `url`, `headers`, and `body` parameters.
3. Converted JSON payloads to strings using `json.dumps` and set the `Content-Type` header to `application/json` for POST and PUT requests.
4. Parsed JSON responses using `json.loads` since `urllib3` does not automatically parse JSON responses like `httpx`.

### Modified Code:
```python
import json
from urllib3 import PoolManager
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_200_OK


class TestTodo:
    def setup_method(self):
        self.http = PoolManager()
        self.base_url = "http://testserver"  # Assuming the test server runs here

    def test_get_todo_all(self):
        response = self.http.request("GET", f"{self.base_url}/v1/todos")
        response_data = json.loads(response.data.decode("utf-8"))
        items = response_data["items"]

        assert response.status == HTTP_200_OK
        assert len(items) == 2
        assert items[0]["id"] == 1
        assert items[0]["title"] == "title 1"
        assert items[1]["id"] == 2
        assert items[1]["title"] == "title 2"

    def test_get_todo_by_id(self):
        response = self.http.request("GET", f"{self.base_url}/v1/todos/1")
        response_data = json.loads(response.data.decode("utf-8"))

        assert response.status == HTTP_200_OK
        assert response_data["id"] == 1
        assert response_data["title"] == "title 1"

    def test_add_todo(self):
        payload = json.dumps({"title": "title 3"})
        response = self.http.request(
            "POST",
            f"{self.base_url}/v1/todos",
            body=payload,
            headers={"Content-Type": "application/json"}
        )
        response_data = json.loads(response.data.decode("utf-8"))

        assert response.status == HTTP_200_OK
        assert response_data["success"]

    def test_add_todo_should_return_unprocessable_when_invalid_entity(self):
        response = self.http.request(
            "POST",
            f"{self.base_url}/v1/todos",
            body=None,
            headers={"Content-Type": "application/json"}
        )

        assert response.status == HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_todo(self):
        payload = json.dumps({"title": "title 1 updated"})
        response = self.http.request(
            "PUT",
            f"{self.base_url}/v1/todos/1",
            body=payload,
            headers={"Content-Type": "application/json"}
        )
        response_data = json.loads(response.data.decode("utf-8"))

        assert response.status == HTTP_200_OK
        assert response_data["success"]

    def test_update_todo_should_return_unprocessable_when_invalid_entity(self):
        payload = json.dumps({})
        response = self.http.request(
            "PUT",
            f"{self.base_url}/v1/todos/1",
            body=payload,
            headers={"Content-Type": "application/json"}
        )

        assert response.status == HTTP_422_UNPROCESSABLE_ENTITY

    def test_delete_todo(self):
        response = self.http.request("DELETE", f"{self.base_url}/v1/todos/1")
        response_data = json.loads(response.data.decode("utf-8"))

        assert response.status == HTTP_200_OK
        assert response_data["success"]
```

### Summary of Changes:
- Replaced `test_app` with `urllib3.PoolManager` for HTTP requests.
- Used `urllib3.request` methods with appropriate HTTP methods (`GET`, `POST`, `PUT`, `DELETE`).
- Added `json.dumps` to serialize JSON payloads and `json.loads` to parse JSON responses.
- Set `Content-Type: application/json` headers for requests with JSON payloads.