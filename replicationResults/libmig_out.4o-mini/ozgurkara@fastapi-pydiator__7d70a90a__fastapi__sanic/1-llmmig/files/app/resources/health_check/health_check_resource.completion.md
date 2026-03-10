### Explanation of Changes
To migrate the code from using the FastAPI library to the Sanic library, the following changes were made:

1. **Import Statements**: Changed the import statements to use Sanic's equivalent classes and functions.
2. **Router Creation**: Instead of using `APIRouter` from FastAPI, we use Sanic's `Blueprint` to create a router.
3. **Response Handling**: Removed the `status_code` and `responses` parameters from the route decorator, as Sanic does not support these in the same way FastAPI does. Instead, we directly return the response.
4. **Response Class**: The `PlainTextResponse` from FastAPI is not needed in Sanic; we can return a string directly.

### Modified Code
```python
from sanic import Blueprint
from sanic.response import text

router = Blueprint("router")


@router.get("")
async def get(request):
    return text("OK", status=200)
```