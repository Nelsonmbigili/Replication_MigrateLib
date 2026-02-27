### Explanation of Changes:
To migrate the code from `fastapi` to `sanic`, the following changes were made:
1. Replaced `fastapi.responses.JSONResponse` with `sanic.response.json` for handling JSON responses.
2. Removed the inheritance from `JSONResponse` since `sanic.response.json` is a function, not a class.
3. Implemented a custom function `DataScienceJsonResponse` that mimics the behavior of the original `render` method. This function uses `json.dumps` to serialize the content and explicitly encodes it in UTF-8.
4. The `media_type` attribute was removed because `sanic.response.json` automatically sets the `Content-Type` to `application/json`.

### Modified Code:
```python
import json as json
import typing

from sanic.response import json as sanic_json


def DataScienceJsonResponse(content: typing.Any) -> bytes:
    # We need to use the default json implementation and explicitly encode in utf-8 to
    # preserve `np.nan` and `np.inf` values.
    return sanic_json(json.loads(json.dumps(content).encode("utf-8")))
```