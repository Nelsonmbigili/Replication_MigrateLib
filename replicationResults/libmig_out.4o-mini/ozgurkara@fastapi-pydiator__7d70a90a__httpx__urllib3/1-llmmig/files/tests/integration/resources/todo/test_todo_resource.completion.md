### Explanation of Changes
To migrate the code from using the `httpx` library to the `urllib3` library, the following changes were made:

1. **Importing `urllib3`**: The `httpx` library is replaced with `urllib3`. This requires importing the `PoolManager` from `urllib3` to handle HTTP requests.
2. **Creating a Connection Pool**: An instance of `PoolManager` is created to manage connections.
3. **Making Requests**: The `test_app.get`, `test_app.post`, `test_app.put`, and `test_app.delete` methods are replaced with the corresponding methods from `urllib3`, which involve using `request` method with appropriate HTTP methods.
4. **Handling JSON**: The response from `urllib3` does not have a built-in `json()` method, so the response data is manually parsed using `json.loads()` after reading the response data.

Here is the modified code:

```python
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
``` 

This code now uses `urllib3` for making HTTP requests while maintaining the original structure and logic of the tests.