import time
from http import HTTPStatus

import pytest
from prometheus_client import REGISTRY
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.testclient import TestClient

import starlette_exporter
from starlette_exporter import (
    PrometheusMiddleware,
    from_header,
    from_response_header,
    handle_metrics,
    handle_openmetrics,
)
from starlette_exporter.optional_metrics import request_body_size, response_body_size


@pytest.fixture
def testapp():
    """create a test app with various endpoints for the test scenarios"""

    # unregister all the collectors before we start
    collectors = list(REGISTRY._collector_to_names.keys())
    for collector in collectors:
        REGISTRY.unregister(collector)

    PrometheusMiddleware._metrics = {}

    def _testapp(**middleware_options):
        app = Starlette()
        app.add_middleware(
            starlette_exporter.PrometheusMiddleware, **middleware_options
        )
        app.add_route("/metrics", handle_metrics)
        app.add_route("/openmetrics", handle_openmetrics)

        def normal_response(_):
            return JSONResponse({"message": "Hello World"}, headers={"foo": "baz"})

        app.add_route("/200", normal_response, methods=["GET", "POST", "OPTIONS"])
        app.add_route(
            "/200/{test_param}", normal_response, methods=["GET", "POST", "OPTIONS"]
        )

        def httpstatus_response(request):
            """
            Returns a JSON Response using status_code = HTTPStatus.OK if the param is set to OK
            otherewise it returns a JSON response with status_code = 200
            """
            if request.path_params["test_param"] == "OK":
                return Response(status_code=HTTPStatus.OK)
            else:
                return Response(status_code=200)

        app.add_route(
            "/200_or_httpstatus/{test_param}",
            httpstatus_response,
            methods=["GET", "OPTIONS"],
        )

        async def error(request):
            raise HTTPException(status_code=500, detail="this is a test error", headers={"foo":"baz"})

        app.add_route("/500", error)
        app.add_route("/500/{test_param}", error)

        async def unhandled(request):
            test_dict = {"yup": 123}
            return JSONResponse({"message": test_dict["value_error"]})

        app.add_route("/unhandled", unhandled)
        app.add_route("/unhandled/{test_param}", unhandled)

        async def background(request):
            def backgroundtask():
                time.sleep(0.1)

            task = BackgroundTask(backgroundtask)
            return JSONResponse({"message": "task started"}, background=task)

        app.add_route("/background", background)

        def healthcheck(request):
            return JSONResponse({"message": "Healthcheck route"})

        app.add_route("/health", healthcheck)

        # testing routes added using Mount
        async def test_mounted_function(request):
            return JSONResponse({"message": "Hello World"})

        async def test_mounted_function_param(request):
            return JSONResponse({"message": request.path_params.get("item")})

        mounted_routes = Mount(
            "/",
            routes=[
                Route("/test/{item}", test_mounted_function_param, methods=["GET"]),
                Route("/test", test_mounted_function),
            ],
        )

        app.mount("/mounted", mounted_routes)
        app.mount("/static", app=StaticFiles(directory="tests/static"), name="static")
        return app

    return _testapp


class TestMiddleware:
    @pytest.fixture
    def client(self, testapp):
        return TestClient(testapp())

    def test_200(self, client):
        """test that requests appear in the counter"""
        client.get("/200")
        metrics = client.get("/metrics").content.decode()
        assert (
            """starlette_requests_total{app_name="starlette",method="GET",path="/200",status_code="200"} 1.0"""
            in metrics
        )

    def test_500(self, client):
        """test that a handled exception (HTTPException) gets logged in the requests counter"""

        client.get("/500")
        metrics = client.get("/metrics").content.decode()

        assert (
            """starlette_requests_total{app_name="starlette",method="GET",path="/500",status_code="500"} 1.0"""
            in metrics
        )

    def test_404_filter_unhandled_paths_off(self, testapp):
        """test that an unknown path is captured in metrics if filter_unhandled_paths=False"""
        client = TestClient(testapp(filter_unhandled_paths=False))
        client.get("/404")
        metrics = client.get("/metrics").content.decode()

        assert (
            """starlette_requests_total{app_name="starlette",method="GET",path="/404",status_code="404"} 1.0"""
            in metrics
        )

    def test_404_filter(self, client):
        """test that a unknown path can be excluded from metrics"""

        try:
            client.get("/404")
        except:
            pass
        metrics = client.get("/metrics").content.decode()

        assert "/404" not in metrics

    def test_404_group_unhandled_paths_on(self, testapp):
        """test that an unknown path is captured in metrics if group_unhandled_paths=True"""

        client = TestClient(testapp(group_unhandled_paths=True, filter_unhandled_paths=False))
        client.get("/404")

        metrics = client.get("/metrics").content.decode()

        assert (
            """starlette_requests_total{app_name="starlette",method="GET",path="__unknown__",status_code="404"} 1.0"""
            in metrics
        )

    def test_unhandled(self, client):
        """test that an unhandled exception still gets logged in the requests counter"""

        with pytest.raises(KeyError, match="value_error"):
            client.get("/unhandled")

        metrics = client.get("/metrics").content.decode()

        assert (
            """starlette_requests_total{app_name="starlette",method="GET",path="/unhandled",status_code="500"} 1.0"""
            in metrics
        )

    def test_ungrouped_paths(self, testapp):
        """test that an endpoints parameters with group_paths=False are added to metrics"""

        client = TestClient(testapp(group_paths=False))

        client.get("/200/111")
        client.get("/500/1111")
        client.get("/404/11111")

        with pytest.raises(KeyError, match="value_error"):
            client.get("/unhandled/123")

        metrics = client.get("/metrics").content.decode()

        assert (
            """starlette_requests_total{app_name="starlette",method="GET",path="/200/111",status_code="200"} 1.0"""
            in metrics
        )
        assert (
            """starlette_requests_total{app_name="starlette",method="GET",path="/500/1111",status_code="500"} 1.0"""
            in metrics
        )
        assert "/404" not in metrics
        
        assert (
            """starlette_requests_total{app_name="starlette",method="GET",path="/unhandled/123",status_code="500"} 1.0"""
            in metrics
        )

    def test_histogram(self, client):
        """test that histogram buckets appear after making requests"""

        client.get("/200")
        client.get("/500")
        try:
            client.get("/unhandled")
        except:
            pass

        metrics = client.get("/metrics").content.decode()

        assert (
            """starlette_request_duration_seconds_bucket{app_name="starlette",le="0.005",method="GET",path="/200",status_code="200"}"""
            in metrics
        )
        assert (
            """starlette_request_duration_seconds_bucket{app_name="starlette",le="0.005",method="GET",path="/500",status_code="500"}"""
            in metrics
        )
        assert (
            """starlette_request_duration_seconds_bucket{app_name="starlette",le="0.005",method="GET",path="/unhandled",status_code="500"}"""
            in metrics
        )

    def test_histogram_custom_buckets(self, testapp):
        """test that custom histogram buckets appear after making requests"""

        buckets = (10, 20, 30, 40, 50)
        client = TestClient(testapp(buckets=buckets))
        client.get("/200")
