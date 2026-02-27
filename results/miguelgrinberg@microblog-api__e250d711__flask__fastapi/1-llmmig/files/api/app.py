from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from alchemical.fastapi import Alchemical  # Assuming Alchemical has a FastAPI-compatible version
from config import Config

db = Alchemical()

def create_app(config_class=Config):
    app = FastAPI()

    # CORS middleware
    if config_class.USE_CORS:  # pragma: no branch
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Adjust as needed
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Database initialization
    from api import models
    db.init_app(app)

    # Blueprints (converted to FastAPI routers)
    from api.errors import router as errors_router
    app.include_router(errors_router)
    from api.tokens import router as tokens_router
    app.include_router(tokens_router, prefix="/api")
    from api.users import router as users_router
    app.include_router(users_router, prefix="/api")
    from api.posts import router as posts_router
    app.include_router(posts_router, prefix="/api")
    from api.fake import router as fake_router
    app.include_router(fake_router)

    # Index route
    @app.get("/")
    async def index():  # pragma: no cover
        return RedirectResponse(url="/docs")  # FastAPI's built-in docs

    # Middleware to handle after-request logic
    @app.middleware("http")
    async def after_request(request: Request, call_next):
        response = await call_next(request)
        # FastAPI handles request body differently, so no need for `request.get_data()`
        return response

    return app
