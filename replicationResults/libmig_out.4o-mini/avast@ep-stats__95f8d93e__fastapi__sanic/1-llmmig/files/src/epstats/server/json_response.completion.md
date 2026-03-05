### Explanation of Changes
To migrate the code from using the `fastapi` library to the `sanic` library, the following changes were made:

1. **Import Statement**: The import for `JSONResponse` from `fastapi.responses` was replaced with the appropriate import from `sanic.response`.
2. **Class Inheritance**: The `DataScienceJsonResponse` class now inherits from `sanic.response.JSON` instead of `fastapi.responses.JSONResponse`.
3. **Render Method**: The `render` method remains largely the same, but it is now part of the `sanic` response class.

### Modified Code
```python
import json as json
import typing

from sanic.response import JSON


class DataScienceJsonResponse(JSON):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        # we need to use default json implementation and explicitly encode in utf-8 to
        # preserver `np.nan` and `np.inf` values.
        return json.dumps(content).encode("utf-8")
```