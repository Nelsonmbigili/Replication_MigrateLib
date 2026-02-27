### Explanation of Changes:
To migrate the code from `fastapi` to `sanic`, the following changes were made:
1. **Sanic Imports**: Replaced `fastapi` imports (`APIRouter`, `status`, `PlainTextResponse`) with `Sanic`, `HTTPResponse`, and `text` from the `sanic` library.
2. **Router Replacement**: In `fastapi`, `APIRouter` is used to define routes. In `sanic`, routes are directly added to the `Sanic` app instance.
3. **Response Handling**: In `fastapi`, `PlainTextResponse` is used for plain text responses. In `sanic`, the `text` function is used to return plain text responses.
4. **Status Codes**: In `fastapi`, status codes are imported from `fastapi.status`. In `sanic`, status codes are directly specified as integers (e.g., `200` for HTTP 200 OK).
5. **Route Definition**: The `@router.get` decorator in `fastapi` is replaced with the `@app.get` decorator in `sanic`.

### Modified Code:
```python
from sanic import Sanic, response
from sanic.response import text

app = Sanic("MyApp")


@app.get("/")
async def get(request):
    return text("OK", status=200)
```

### Notes:
- The `responses` parameter in `fastapi` is used for OpenAPI documentation and is not directly supported in `sanic`. If OpenAPI documentation is required, additional plugins like `sanic-openapi` can be used, but this was not included as it is outside the scope of the migration.
- The `status_code` parameter in `fastapi` is replaced by directly specifying the status code in the `text` response function.