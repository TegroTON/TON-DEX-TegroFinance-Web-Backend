import time
from typing import Dict
from fastapi import Response

import jwt
from src.config import config

TOKEN_TTL = 60 * 60 * 2
TOKEN_KEY = "tegro-dex-token"


def sign_jwt(
    user_id: str,
    user_address: str,
) -> str:
    payload = {
        "user_id": user_id,
        "user_address": user_address,
        "expires": time.time() + TOKEN_TTL,
    }

    token = jwt.encode(
        payload=payload,
        key=config.secret.get_secret_value(),
        algorithm=config.algorithm,
    )

    return token


def decode_jwt(token: str) -> Dict[str, str] | None:
    try:
        decoded_token = jwt.decode(
            jwt=token,
            key=config.secret.get_secret_value(),
            algorithms=[config.algorithm],
        )
        return (
            decoded_token if decoded_token["expires"] >= time.time() else None
        )
    except Exception:
        return {}


def update_token_if_needed(token: str) -> str | None:
    decoded_token = decode_jwt(token)

    if not decoded_token:
        return None

    expire_time = decoded_token["expires"]

    if expire_time - time.time() < TOKEN_TTL / 2:
        return sign_jwt(
            user_id=decoded_token["user_id"],
            user_address=decoded_token["user_address"],
        )

    return token


def set_token_cookie(response: Response, token: str):
    response.set_cookie(
        key=TOKEN_KEY,
        value=token,
        secure=config.jwt.cookie_secure,
        max_age=TOKEN_TTL,
        path="/",
    )
