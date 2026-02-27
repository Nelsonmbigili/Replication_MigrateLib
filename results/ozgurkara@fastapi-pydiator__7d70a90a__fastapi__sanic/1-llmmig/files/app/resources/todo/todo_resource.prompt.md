The following Python code currently uses the library "fastapi" version 0.109.1.
Migrate this code to use the library "sanic" version 25.3.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "fastapi" to "sanic".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "fastapi" and "sanic".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from typing import List
from fastapi import status, APIRouter, Response

from pydiator_core.mediatr import pydiator
from app.resources.todo.usecases.get_todo_all import GetTodoAllRequest, GetTodoAllResponse
from app.resources.todo.usecases.get_todo_by_id import GetTodoByIdRequest, GetTodoByIdResponse
from app.resources.todo.usecases.add_todo import AddTodoRequest, AddTodoResponse
from app.resources.todo.usecases.update_todo import UpdateTodoRequest, UpdateTodoResponse
from app.resources.todo.usecases.delete_todo_by_id import DeleteTodoByIdRequest, DeleteTodoByIdResponse
from app.utils.error.error_response import ErrorResponseModel, ErrorResponseExample

router = APIRouter()


@router.get("",
            status_code=status.HTTP_200_OK,
            responses={
                status.HTTP_200_OK: {"model": List[GetTodoAllResponse]},
                status.HTTP_400_BAD_REQUEST: {
                    "model": ErrorResponseModel,
                    "content": ErrorResponseExample.get_error_response(),
                },
            })
async def get_todo_all():
    return await pydiator.send(req=GetTodoAllRequest())


@router.get("/{id}",
            status_code=status.HTTP_200_OK,
            responses={
                status.HTTP_200_OK: {"model": GetTodoByIdResponse},
                status.HTTP_400_BAD_REQUEST: {
                    "model": ErrorResponseModel,
                    "content": ErrorResponseExample.get_error_response(),
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": ErrorResponseModel,
                    "content": ErrorResponseExample.get_validation_error_response(
                        invalid_field_location=["path", "id"]
                    ),
                },
            })
async def get_todo_by_id(id: int, response: Response):
    return await pydiator.send(req=GetTodoByIdRequest(id=id), response=response)


@router.post("",
             status_code=status.HTTP_200_OK,
             responses={
                 status.HTTP_200_OK: {"model": AddTodoResponse},
                 status.HTTP_400_BAD_REQUEST: {
                     "model": ErrorResponseModel,
                     "content": ErrorResponseExample.get_error_response(),
                 },
                 status.HTTP_422_UNPROCESSABLE_ENTITY: {
                     "model": ErrorResponseModel,
                     "content": ErrorResponseExample.get_validation_error_response(
                         invalid_field_location=["body", "title"]
                     ),
                 },
             })
async def add_todo(req: AddTodoRequest):
    return await pydiator.send(req=req)


@router.put("/{id}",
            responses={
                status.HTTP_200_OK: {"model": UpdateTodoResponse},
                status.HTTP_400_BAD_REQUEST: {
                    "model": ErrorResponseModel,
                    "content": ErrorResponseExample.get_error_response(),
                },
                status.HTTP_422_UNPROCESSABLE_ENTITY: {
                    "model": ErrorResponseModel,
                    "content": ErrorResponseExample.get_validation_error_response(
                        invalid_field_location=["path", "id"]
                    ),
                },
            })
async def update_todo(id: int, req: UpdateTodoRequest):
    req.CustomFields.id = id
    return await pydiator.send(req=req)


@router.delete("/{id}",
               responses={
                   status.HTTP_200_OK: {"model": DeleteTodoByIdResponse},
                   status.HTTP_400_BAD_REQUEST: {
                       "model": ErrorResponseModel,
                       "content": ErrorResponseExample.get_error_response(),
                   },
                   status.HTTP_422_UNPROCESSABLE_ENTITY: {
                       "model": ErrorResponseModel,
                       "content": ErrorResponseExample.get_validation_error_response(
                           invalid_field_location=["path", "id"]
                       ),
                   },
               })
async def delete_todo(id: int):
    return await pydiator.send(req=DeleteTodoByIdRequest(id=id))

```