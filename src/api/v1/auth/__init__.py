from typing import Union
from fastapi import FastAPI

from src.auth.models import (
    TokenResponse,
    ErrorResponse,
    PayloadResponse,
)

from .auth import (
    get_payload_endpoint,
    auth_with_ton_proof_endpoint,
    refresh_jwt_token_endpoint,
)

BASE_PATH = "/api/v1/auth"


def register_routes(app: FastAPI):
    app.add_api_route(
        path=f"{BASE_PATH}/get_payload",
        endpoint=get_payload_endpoint,
        response_model=PayloadResponse,
        methods=["GET"],
    )

    app.add_api_route(
        path=f"{BASE_PATH}/auth_with_ton_proof",
        endpoint=auth_with_ton_proof_endpoint,
        response_model=Union[TokenResponse, ErrorResponse],
        methods=["POST"],
    )

    app.add_api_route(
        path=f"{BASE_PATH}/refresh_token",
        endpoint=refresh_jwt_token_endpoint,
        response_model=Union[TokenResponse, ErrorResponse],
        methods=["POST"],
    )
