### Explanation of Changes
To migrate the given code from Flask to FastAPI, the following changes were made:

1. **Application Initialization**:
   - Replaced `Flask` with `FastAPI` for creating the application instance.
   - Removed `app.config` and replaced it with FastAPI's configuration approach (e.g., using environment variables or directly passing configuration).

2. **Extensions**:
   - Flask-specific extensions like `CORS`, `Mail`, and `APIFairy` were replaced with their FastAPI equivalents or omitted if no direct equivalent exists.
   - For `CORS`, used `fastapi.middleware.cors.CORSMiddleware`.
   - For `Mail` and `APIFairy`, you would need to use third-party libraries compatible with FastAPI (not implemented here as they are not directly shown in the code).

3. **Blueprints**:
   - Flask's `Blueprint` system was replaced with FastAPI's `APIRouter`.
   - Each blueprint was assumed to be converted into a FastAPI router in its respective module.

4. **Routes**:
   - Flask's `@app.route` was replaced with FastAPI's `@app.get`, `@app.post`, etc.
   - Redirects were implemented using FastAPI's `RedirectResponse`.

5. **Middleware**:
   - Flask's `@app.after_request` was replaced with FastAPI's middleware system.

6. **Shell Context**:
   - Flask's `@app.shell_context_processor` does not have a direct equivalent in FastAPI. This functionality was omitted as it is specific to Flask's CLI.

---

### Modified Code
Here is the complete code after migration to FastAPI:

```python
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
```

---

### Key Notes:
1. **Blueprints to Routers**:
   - Each Flask blueprint (e.g., `errors`, `tokens`, `users`, etc.) is assumed to have been converted into a FastAPI `APIRouter` in its respective module. For example, `api.errors` now exports a `router` object.

2. **CORS**:
   - The `fastapi.middleware.cors.CORSMiddleware` is used to handle CORS, replacing Flask's `CORS` extension.

3. **Mail and APIFairy**:
   - These extensions are not directly migrated because they are specific to Flask. You would need to find FastAPI-compatible alternatives or implement custom solutions.

4. **Shell Context**:
   - The `@app.shell_context_processor` functionality is omitted because it is specific to Flask's CLI and does not have a direct equivalent in FastAPI.

5. **Redirects**:
   - Flask's `redirect` and `url_for` are replaced with FastAPI's `RedirectResponse`.

This code assumes that the necessary adjustments (e.g., converting blueprints to routers) have been made in the respective modules.