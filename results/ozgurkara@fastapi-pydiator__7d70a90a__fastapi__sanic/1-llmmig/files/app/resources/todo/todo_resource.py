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
