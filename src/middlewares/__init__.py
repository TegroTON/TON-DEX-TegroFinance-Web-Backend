from .auth_middleware import auth_middleware
from fastapi import FastAPI


def register_middlewares(app: FastAPI):
    app.middleware("http")(auth_middleware)
