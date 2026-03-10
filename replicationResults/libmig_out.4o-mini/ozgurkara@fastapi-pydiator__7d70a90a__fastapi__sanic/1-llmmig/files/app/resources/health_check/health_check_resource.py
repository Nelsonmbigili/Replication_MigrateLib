from sanic import Blueprint
from sanic.response import text

router = Blueprint("router")


@router.get("")
async def get(request):
    return text("OK", status=200)
