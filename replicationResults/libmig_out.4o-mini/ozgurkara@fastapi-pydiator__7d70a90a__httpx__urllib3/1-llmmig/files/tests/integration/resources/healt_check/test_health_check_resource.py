from starlette.status import HTTP_200_OK
import urllib3

class TestTodo:

    def test_get(self, test_app):
        http = urllib3.PoolManager()
        response = http.request('GET', 'http://localhost:8000/health-check')

        assert response.status == HTTP_200_OK
        assert response.data == b"OK"
