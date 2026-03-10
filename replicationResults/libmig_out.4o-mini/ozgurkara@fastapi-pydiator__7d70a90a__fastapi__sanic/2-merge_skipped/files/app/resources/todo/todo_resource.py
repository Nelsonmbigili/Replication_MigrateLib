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
async def delete_todo(request, id: int):
    return json(await pydiator.send(req=DeleteTodoByIdRequest(id=id)))