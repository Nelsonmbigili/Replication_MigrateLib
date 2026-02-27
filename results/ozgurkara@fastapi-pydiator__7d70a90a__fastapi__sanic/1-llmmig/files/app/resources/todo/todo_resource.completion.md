### Explanation of Changes

To migrate the code from `fastapi` to `sanic`, the following changes were made:

1. **Sanic App and Blueprint**: Replaced `APIRouter` with `Sanic`'s `Blueprint` for routing. The `router` object is now a `Blueprint` instance.
2. **Route Definitions**: Updated the route decorators from `@router.get`, `@router.post`, etc., to `@router.route` with the appropriate HTTP methods specified.
3. **Response Handling**: Sanic does not have a built-in `Response` object like FastAPI. Instead, it uses `json` or `text` methods to return responses. The `Response` parameter in the `get_todo_by_id` function was removed.
4. **Status Codes**: Sanic allows specifying status codes directly in the `json` or `text` response methods.
5. **Validation and Documentation**: Sanic does not natively support Pydantic models for request validation or OpenAPI documentation. These features were omitted, as they are not directly supported by Sanic without additional libraries.
6. **Path Parameters**: Sanic automatically parses path parameters, so no changes were needed for parameter handling.

### Modified Code

```python
from typing import List
from sanic import Blueprint, response
from sanic.response import json

from pydiator_core.mediatr import pydiator
from app.resources.todo.usecases.get_todo_all import GetTodoAllRequest, GetTodoAllResponse
from app.resources.todo.usecases.get_todo_by_id import GetTodoByIdRequest, GetTodoByIdResponse
from app.resources.todo.usecases.add_todo import AddTodoRequest, AddTodoResponse
from app.resources.todo.usecases.update_todo import UpdateTodoRequest, UpdateTodoResponse
from app.resources.todo.usecases.delete_todo_by_id import DeleteTodoByIdRequest, DeleteTodoByIdResponse
from app.utils.error.error_response import ErrorResponseModel, ErrorResponseExample

router = Blueprint("todo", url_prefix="/todo")


@router.route("/", methods=["GET"])
async def get_todo_all(request):
    result = await pydiator.send(req=GetTodoAllRequest())
    return json(result, status=200)


@router.route("/<id:int>", methods=["GET"])
async def get_todo_by_id(request, id: int):
    result = await pydiator.send(req=GetTodoByIdRequest(id=id))
    return json(result, status=200)


@router.route("/", methods=["POST"])
async def add_todo(request):
    req_data = request.json
    req = AddTodoRequest(**req_data)
    result = await pydiator.send(req=req)
    return json(result, status=200)


@router.route("/<id:int>", methods=["PUT"])
async def update_todo(request, id: int):
    req_data = request.json
    req = UpdateTodoRequest(**req_data)
    req.CustomFields.id = id
    result = await pydiator.send(req=req)
    return json(result, status=200)


@router.route("/<id:int>", methods=["DELETE"])
async def delete_todo(request, id: int):
    result = await pydiator.send(req=DeleteTodoByIdRequest(id=id))
    return json(result, status=200)
```

### Key Notes:
- The `ErrorResponseModel` and `ErrorResponseExample` were not used in the Sanic version because Sanic does not natively support OpenAPI documentation or response model validation. If needed, a third-party library like `sanic-openapi` can be integrated for similar functionality.
- The `Response` object from FastAPI was removed, as Sanic uses its own response methods like `json` and `text`.
- The `status_code` parameter in FastAPI route decorators was replaced by directly specifying the status code in the `json` response method.