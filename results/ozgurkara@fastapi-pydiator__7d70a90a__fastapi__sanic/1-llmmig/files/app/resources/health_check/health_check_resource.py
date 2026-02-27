from sanic import Sanic, response
from sanic.response import text

app = Sanic("MyApp")


@app.get("/")
async def get(request):
    return text("OK", status=200)
