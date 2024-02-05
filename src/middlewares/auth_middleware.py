from typing import Callable
from fastapi.requests import Request
from fastapi.responses import Response
from src.auth.jwt import update_token_if_needed, set_token_cookie, TOKEN_KEY


async def auth_middleware(request: Request, call_next: Callable):
    token = request.cookies.get(TOKEN_KEY, None)

    if token:
        new_token = update_token_if_needed(token)

    response: Response = await call_next(request)

    if token and token != new_token:
        # print("new token: ", new_token)
        set_token_cookie(
            response=response,
            token=new_token,
        )

    return response
