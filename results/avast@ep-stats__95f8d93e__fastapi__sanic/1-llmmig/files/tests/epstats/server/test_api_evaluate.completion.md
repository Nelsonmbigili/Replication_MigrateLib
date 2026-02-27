### Explanation of Changes:
To migrate the code from `fastapi` to `sanic`, the following changes were made:
1. **Sanic Test Client**: Replaced `fastapi.testclient.TestClient` with `sanic.SanicTestClient` for testing the API.
2. **Dependency Overrides**: Sanic does not have a direct equivalent for FastAPI's `dependency_overrides`. Instead, we directly configure the application with the required dependencies.
3. **Request Handling**: Updated the `client.post` and `client.get` calls to use Sanic's test client methods (`client.post` and `client.get`), which have a slightly different API.
4. **Sanic Application**: Replaced the `api` object (FastAPI app) with a `Sanic` app instance.
5. **Response Handling**: Adjusted response handling to match Sanic's response structure.

Below is the modified code:

---

### Modified Code:
```python
import pandas as pd
from epstats.server.req import Experiment
from sanic import Sanic
from sanic.testing import SanicTestClient

from src.epstats.main import api, get_dao, get_executor_pool
from src.epstats.server.res import Result
from src.epstats.toolkit.testing import (
    TestDao,
    assert_checks,
    assert_exposures,
    assert_metrics,
)

from .depend import dao_factory, get_test_dao, get_test_executor_pool

# Create a Sanic app instance
app = Sanic("epstats_app")

# Configure dependencies directly
app.ext.add_dependency(get_test_dao, type=get_dao)
app.ext.add_dependency(get_test_executor_pool, type=get_executor_pool)

# Use Sanic's test client
client = SanicTestClient(app)


def test_conversion_evaluate():
    json_blob = {
        "id": "test-conversion",
        "control_variant": "a",
        "unit_type": "test_unit_type",
        "metrics": [
            {
                "id": 1,
                "name": "Click-through Rate",
                "nominator": "count(test_unit_type.unit.click)",
                "denominator": "count(test_unit_type.global.exposure)",
            }
        ],
        "checks": [
            {
                "id": 1,
                "name": "SRM",
                "denominator": "count(test_unit_type.global.exposure)",
            }
        ],
    }

    Experiment.model_validate(json_blob)
    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 200
    assert_experiment(response.json, dao_factory.get_dao(), 1)


def test_real_valued_evaluate():
    json_blob = {
        "id": "test-real-valued",
        "control_variant": "a",
        "unit_type": "test_unit_type",
        "metrics": [
            {
                "id": 2,
                "name": "Average Bookings",
                "nominator": "value(test_unit_type.unit.conversion)",
                "denominator": "count(test_unit_type.global.exposure)",
            }
        ],
        "checks": [
            {
                "id": 1,
                "name": "SRM",
                "denominator": "count(test_unit_type.global.exposure)",
            }
        ],
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 200
    assert_experiment(response.json, dao_factory.get_dao(), 1)


def test_multiple_evaluate():
    json_blob = {
        "id": "test-multiple",
        "control_variant": "a",
        "unit_type": "test_unit_type",
        "metrics": [
            {
                "id": 1,
                "name": "Click-through Rate",
                "nominator": "count(test_unit_type.unit.click)",
                "denominator": "count(test_unit_type.global.exposure)",
            },
            {
                "id": 2,
                "name": "Average Bookings",
                "nominator": "value(test_unit_type.unit.conversion)",
                "denominator": "count(test_unit_type.global.exposure)",
            },
        ],
        "checks": [
            {
                "id": 1,
                "name": "SRM",
                "denominator": "count(test_unit_type.global.exposure)",
            }
        ],
    }

    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 200
    assert_experiment(response.json, dao_factory.get_dao(), 2)


def test_sequential():
    json_blob = {
        "id": "test-sequential-v2",
        "control_variant": "a",
        "date_from": "2020-01-01",
        "date_to": "2020-01-14",
        "date_for": "2020-01-10",
        "unit_type": "test_unit_type",
        "metrics": [
            {
                "id": 1,
                "name": "Average Bookings",
                "nominator": "value(test_unit_type.unit.conversion)",
                "denominator": "count(test_unit_type.global.exposure)",
            },
        ],
        "checks": [],
    }
    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 200
    assert_experiment(response.json, dao_factory.get_dao(), expected_metrics=1, expected_checks=0)

    json_blob = {
        "id": "test-sequential-v3",
        "control_variant": "a",
        "date_from": "2020-01-01",
        "date_to": "2020-01-14",
        "date_for": "2020-01-14",
        "unit_type": "test_unit_type",
        "metrics": [
            {
                "id": 1,
                "name": "Average Bookings",
                "nominator": "value(test_unit_type.unit.conversion)",
                "denominator": "count(test_unit_type.global.exposure)",
            },
        ],
        "checks": [],
    }
    request, response = client.post("/evaluate", json=json_blob)
    assert response.status == 200
    assert_experiment(response.json, dao_factory.get_dao(), expected_metrics=1, expected_checks=0)


def test_prometheus_metrics():
    request, prometheus_resp = client.get("/metrics")
    assert prometheus_resp.status == 200
    assert "evaluation_duration_seconds" in prometheus_resp.text


def assert_experiment(target, test_dao: TestDao, expected_metrics: int, expected_checks: int = 1) -> None:
    result = Result(**target)
    assert len(result.metrics) == expected_metrics
    assert len(result.checks) == expected_checks

    for m in target["metrics"]:
        assert len(m["stats"]) >= 2
        d = {
            "exp_variant_id": [],
            "diff": [],
            "mean": [],
            "std": [],
            "sum_value": [],
            "p_value": [],
            "confidence_interval": [],
            "confidence_level": [],
            "sample_size": [],
            "required_sample_size": [],
            "power": [],
            "false_positive_risk": [],
        }
        for s in m["stats"]:
            for i in s.items():
                d[i[0]].append(i[1])

        metric_df = pd.DataFrame(d)
        metric_df["exp_id"] = target["id"]
        metric_df["metric_id"] = m["id"]
        assert_metrics(target["id"], m["id"], metric_df, test_dao)

    for m in target["checks"]:
        d = {"variable_id": [], "value": []}
        for s in m["stats"]:
            for i in s.items():
                d[i[0]].append(i[1])
        metric_df = pd.DataFrame(d)
        metric_df["exp_id"] = target["id"]
        metric_df["check_id"] = m["id"]
        assert_checks(target["id"], m["id"], metric_df, test_dao)

    m = target["exposure"]
    d = {"exp_variant_id": [], "exposures": []}
    for s in m["stats"]:
        d["exp_variant_id"].append(s["exp_variant_id"])
        d["exposures"].append(s["count"])
    metric_df = pd.DataFrame(d)
    metric_df["exp_id"] = target["id"]
    assert_exposures(target["id"], metric_df, test_dao, unit_type="test_unit_type", agg_type="global")
```

---

### Key Notes:
- The `SanicTestClient` is used for testing, and its methods (`post`, `get`) return a tuple `(request, response)`.
- Dependency injection in Sanic is handled using `app.ext.add_dependency`.
- The response object in Sanic uses `response.json` instead of `response.json()` for accessing JSON data.