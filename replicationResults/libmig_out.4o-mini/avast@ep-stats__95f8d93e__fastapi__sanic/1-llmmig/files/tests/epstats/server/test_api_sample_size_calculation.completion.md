### Explanation of Changes

To migrate the code from using the `fastapi` library to the `sanic` library, the following changes were made:

1. **Import Changes**: The `TestClient` from `fastapi.testclient` was replaced with `Sanic`'s built-in testing capabilities. In `sanic`, we can use the `Sanic` app instance directly to make requests.
  
2. **Client Initialization**: Instead of creating a `TestClient` instance, we directly use the `api` instance (which is assumed to be a `Sanic` app) to make requests.

3. **Dependency Overrides**: The concept of dependency overrides in `fastapi` does not exist in `sanic`. Therefore, the line that sets `api.dependency_overrides` was removed.

4. **Response Handling**: The response handling remains largely the same, but we access the response directly from the `api` instance.

Here is the modified code:

```python
from math import isnan

import pytest
from sanic import Sanic

from src.epstats.main import api, get_executor_pool

from .depend import get_test_executor_pool

# No TestClient in Sanic, we use the app instance directly
# api.dependency_overrides[get_executor_pool] = get_test_executor_pool  # Removed as it's not applicable in Sanic

@pytest.mark.parametrize(
    "n_variants, minimum_effect, mean, std, expected",
    [
        (2, 0.10, 0.2, 1.2, 56512),
        (2, 0.05, 0.4, None, 9489),
        (3, 0.05, 0.4, None, 11492),
        (2, 0.1, 0, 0, float("nan")),
        (2, 0.1, 0, 1, float("inf")),
    ],
)
def test_sample_size_calculation(n_variants, minimum_effect, mean, std, expected):
    json_blob = {
        "minimum_effect": minimum_effect,
        "mean": mean,
        "std": std,
        "n_variants": n_variants,
    }

    # Use the Sanic app instance directly to make a request
    resp = api.test_client.post("/sample-size-calculation", json=json_blob)
    assert resp.status == 200

    sample_size = resp.json["sample_size_per_variant"]

    assert sample_size == expected or (isnan(expected) and isnan(sample_size))


@pytest.mark.parametrize(
    "n_variants, minimum_effect, mean, expected_message",
    [
        (2, -0.4, 0.2, "minimum_effect must be greater than zero"),
        (2, 0.05, 1.4, "mean must be between zero and one"),
        (1, 0.05, 0.2, "must be at least two variants"),
    ],
)
def test_sample_size_calculation_error(n_variants, minimum_effect, mean, expected_message):
    json_blob = {
        "minimum_effect": minimum_effect,
        "mean": mean,
        "n_variants": n_variants,
    }

    # Use the Sanic app instance directly to make a request
    resp = api.test_client.post("/sample-size-calculation", json=json_blob)
    assert resp.status == 500
    assert expected_message in resp.body.decode()
```

### Note
- The `api.test_client` is used to simulate requests in `sanic`, which is different from how `fastapi` handles it with `TestClient`.
- The response status and body access methods have been adjusted to fit `sanic`'s response structure.