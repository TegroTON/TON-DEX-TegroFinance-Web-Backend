from fastapi.requests import Request

from src.auth.jwt import decode_jwt
from src.auth.models import ErrorResponse
from src.database.dal import account_dal


async def get_account_data_endpoint(request: Request):
    bearer_token = request.headers.get("authorization", None)

    if not bearer_token:
        return ErrorResponse(message="No token provided")

    token_data = decode_jwt(bearer_token[7:])

    if not token_data:
        return ErrorResponse(message="Invalid or expired token")

    user_address = token_data["user_address"]
    user_id = token_data["user_id"]

    user_account = await account_dal.get_account(user_address)

    return
