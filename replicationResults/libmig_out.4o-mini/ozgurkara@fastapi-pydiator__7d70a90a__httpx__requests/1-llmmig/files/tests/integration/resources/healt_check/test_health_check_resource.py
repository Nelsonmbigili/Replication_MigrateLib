from starlette.status import HTTP_200_OK
import requests


class TestTodo:

    def test_get(self, test_app):
        response = requests.get(test_app.url + "/health-check")

        assert response.status_code == HTTP_200_OK
        assert response.content == b"OK"
