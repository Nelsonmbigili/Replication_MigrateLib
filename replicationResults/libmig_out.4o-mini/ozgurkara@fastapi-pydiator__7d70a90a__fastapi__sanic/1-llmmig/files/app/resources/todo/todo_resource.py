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
