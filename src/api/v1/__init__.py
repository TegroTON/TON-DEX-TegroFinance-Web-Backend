from fastapi import FastAPI

from . import dex, ton, auth


def register_routes(app: FastAPI):
    dex.register_routes(app)
    ton.register_routes(app)
    auth.register_routes(app)


__all__ = [
    "register_routes",
]
