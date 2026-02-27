from starlette.status import HTTP_200_OK
import requests


class TestTodo:

    def test_get(self):
        response = requests.get("http://localhost:8000/health-check")

        assert response.status_code == HTTP_200_OK
        assert response.content == b"OK"
