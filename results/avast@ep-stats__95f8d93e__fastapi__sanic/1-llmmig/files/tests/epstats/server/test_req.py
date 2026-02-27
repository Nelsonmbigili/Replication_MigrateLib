from sanic import Sanic
from sanic.testing import SanicTestClient
from src.epstats.main import api as app, get_dao, get_executor_pool
from .depend import get_test_dao, get_test_executor_pool

# Inject test dependencies into the Sanic app
app.ext.get_dao = get_test_dao
app.ext.get_executor_pool = get_test_executor_pool

client = SanicTestClient(app)


def test_validate_control_variant():
    json_blob = {
        "id": "test-conversions",
        "controlvariant": "a",
        "metrics": [
            {
                "id": 1,
                "name": "Click-through Rate",
                "nominator": "count(test_unit_type.unit.click)",
                "denominator": "count(test_unit_type.global.exposure)",
            }
        ],
        "checks": [],
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 422
    json = response.json
    assert json["detail"][0]["loc"][1] == "control_variant"
    assert json["detail"][0]["type"] == "missing"


def test_validate_metric_nominator():
    json_blob = {
        "id": "test-binary",
        "control_variant": "a",
        "unit_type": "test_unit_type",
        "metrics": [
            {
                "id": 1,
                "name": "Click-through Rate",
                "nnominator": "count(test_unit_type.unit.click)",
                "denominator": "count(test_unit_type.global.exposure)",
            }
        ],
        "checks": [],
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 422
    json = response.json
    assert json["detail"][0]["loc"][3] == "nominator"
    assert json["detail"][0]["type"] == "missing"


def test_validate_metric_denominator():
    json_blob = {
        "id": "test-conversions",
        "control_variant": "a",
        "unit_type": "test_unit_type",
        "metrics": [
            {
                "id": 1,
                "name": "Click-through Rate",
                "nominator": "count(test_unit_type.unit.click)",
                "ddenominator": "count(test_unit_type.global.exposure)",
            }
        ],
        "checks": [],
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 422
    json = response.json
    assert json["detail"][0]["loc"][3] == "denominator"
    assert json["detail"][0]["type"] == "missing"


def test_validate_default_check_type():
    json_blob = {
        "id": "test-conversions",
        "control_variant": "a",
        "unit_type": "test_unit_type",
        "metrics": [],
        "checks": [
            {
                "id": 1,
                "name": "SRM",
                "denominator": "count(test_unit_type.global.exposure)",
            },
        ],
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 200


def test_validate_sum_ratio_nominator():
    json_blob = {
        "id": "test-conversions",
        "control_variant": "a",
        "unit_type": "test_unit_type",
        "metrics": [],
        "checks": [
            {
                "id": 1,
                "name": "SumRatio",
                "type": "SumRatio",
                "denominator": "count(test_unit_type.global.exposure)",
            },
        ],
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 422
    json = response.json
    assert json["detail"][0]["loc"][1] == "checks"
    assert json["detail"][0]["loc"][1] == "checks"
    assert json["detail"][0]["type"] == "value_error"


def test_validate_metric_parsing():
    json_blob = {
        "id": "test-conversions",
        "control_variant": "a",
        "unit_type": "test_unit_type",
        "metrics": [
            {
                "id": 1,
                "name": "Click-through Rate",
                "nominator": "count(test_unit_type.unit.click)",
                "denominator": "fce(test_unit_type.global.exposure)",
            }
        ],
        "checks": [],
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 422
    json = response.json
    assert json["detail"][0]["loc"][1] == "metrics"
    assert json["detail"][0]["type"] == "value_error"


def test_date_parsing():
    json_blob = {
        "id": "test-conversions",
        "control_variant": "a",
        "date_from": "2020-01-01",
        "date_to": "2020-01-14",
        "date_for": "2020-01-10",
        "metrics": [],
        "checks": [],
        "unit_type": "test_unit_type",
    }
    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 200

    json_blob = {
        "id": "test-conversions",
        "control_variant": "a",
        "date_from": "2020-01-40",
        "date_to": "2020-01-",
        "metrics": [],
        "checks": [],
        "unit_type": "test_unit_type",
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 422
    json = response.json
    assert json["detail"][0]["loc"][1] == "date_from"
    assert json["detail"][0]["type"] == "value_error"
    assert json["detail"][1]["loc"][1] == "date_to"
    assert json["detail"][1]["type"] == "value_error"


# The remaining tests follow the same pattern as above.
