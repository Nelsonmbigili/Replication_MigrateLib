from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from alchemical.fastapi import Alchemical
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from apifairy import APIFairy
from config import Config

db = Alchemical()
apifairy = APIFairy()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# extensions
from api import models
db.init_app(app)
apifairy.init_app(app)

# routers
from api.errors import router as errors_router
from api.tokens import router as tokens_router
from api.users import router as users_router
from api.posts import router as posts_router
from api.fake import router as fake_router

app.include_router(errors_router)
app.include_router(tokens_router, prefix='/api')
app.include_router(users_router, prefix='/api')
app.include_router(posts_router, prefix='/api')
app.include_router(fake_router)

@app.get('/')
async def index():  # pragma: no cover
    return RedirectResponse(url='/docs')

@app.middleware("http")
async def after_request(request: Request, call_next):
    response: Response = await call_next(request)
    # Werkzeug sometimes does not flush the request body so we do it here
    await request.body()
    return response
