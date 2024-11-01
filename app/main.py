import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware import Middleware

from app.config.settings import settings
from app.routes import auth_routes

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:8002"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
]

app = FastAPI(title=settings.app_name, debug=settings.debug, middleware=middleware)

# Mount the static directory at the root level
static_dir = os.path.join(os.path.dirname(__file__), "../static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include the authentication router
app.include_router(auth_routes.router)


@app.get("/")
async def root():
    return {"message": "Welcome to GateKeeper"}

@app.get("/ping")
async def ping():
    return {"message": "pong"}
