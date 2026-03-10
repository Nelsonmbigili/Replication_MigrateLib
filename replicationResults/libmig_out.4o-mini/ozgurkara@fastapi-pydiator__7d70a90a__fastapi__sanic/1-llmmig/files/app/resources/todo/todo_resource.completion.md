### Explanation of Changes

To migrate the code from FastAPI to Sanic, the following changes were made:

1. **Import Statements**: Changed the import from `fastapi` to `sanic` and adjusted the import for the router.
2. **Router Initialization**: Replaced `APIRouter` from FastAPI with `Sanic`'s routing mechanism.
3. **Response Handling**: Removed the `status_code` and `responses` parameters from the route decorators, as Sanic does not support these in the same way FastAPI does. Instead, we will handle responses directly in the function.
4. **Response Object**: The `Response` object is not used in the same way in Sanic, so it was removed from the function parameters where it was not necessary.
5. **Path Parameters**: The path parameters are still defined in the function signature, but the way they are handled in the route decorators is simplified.

Here is the modified code:

```python
from typing import List
from sanic import Sanic, response
from sanic.response import json

from pydiator_core.mediatr import pydiator
from app.resources.todo.usecases.get_todo_all import GetTodoAllRequest, GetTodoAllResponse
from app.resources.todo.usecases.get_todo_by_id import GetTodoByIdRequest, GetTodoByIdResponse
from app.resources.todo.usecases.add_todo import AddTodoRequest, AddTodoResponse
from app.resources.todo.usecases.update_todo import UpdateTodoRequest, UpdateTodoResponse
from app.resources.todo.usecases.delete_todo_by_id import DeleteTodoByIdRequest, DeleteTodoByIdResponse
from app.utils.error.error_response import ErrorResponseModel, ErrorResponseExample

app = Sanic(__name__)

@app.get("/todos")
async def get_todo_all(request):
    return json(await pydiator.send(req=GetTodoAllRequest()), status=200)

@app.get("/todos/<id:int>")
async def get_todo_by_id(request, id: int):
    return json(await pydiator.send(req=GetTodoByIdRequest(id=id)))

@app.post("/todos")
async def add_todo(request):
    req = request.json
    return json(await pydiator.send(req=AddTodoRequest(**req)), status=200)

@app.put("/todos/<id:int>")
async def update_todo(request, id: int):
    req = request.json
    req.CustomFields.id = id
    return json(await pydiator.send(req=req))

@app.delete("/todos/<id:int>")
async def delete_todo(request, id: int):
    return json(await pydiator.send(req=DeleteTodoByIdRequest(id=id)))
```

### Note
- The routes are now defined with the Sanic syntax, and the response handling is done using `json()` from the `sanic.response` module.
- The error handling and response models from FastAPI are not directly translated, as Sanic does not have built-in support for them in the same way. You may need to implement custom error handling if required.