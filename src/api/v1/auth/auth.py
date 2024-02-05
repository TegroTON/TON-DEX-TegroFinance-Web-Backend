from fastapi.requests import Request
from fastapi.responses import Response

from src.auth.jwt import update_token_if_needed, sign_jwt, set_token_cookie
from src.auth.models import (
    AuthWithTonProofRequest,
    TokenResponse,
    ErrorResponse,
    PayloadResponse,
)
from src.auth.ton_proof import check_ton_proof, generate_payload
from src.database.dal import account_dal

PAYLOAD_TTL = 1000 * 60 * 20  # 20 minutes in ms


async def get_payload_endpoint():
    payload = generate_payload(PAYLOAD_TTL)

    ton_proof = await account_dal.save_ton_proof_payload(
        payload=payload, ttl=PAYLOAD_TTL
    )

    return PayloadResponse(payload=ton_proof.payload)


async def auth_with_ton_proof_endpoint(
    request: AuthWithTonProofRequest,
    response: Response,
):
    payload_dao = await account_dal.get_ton_proof_payload(
        request.proof.payload
    )

    if not payload_dao:
        return ErrorResponse(message="payload not found")

    is_ton_proof_correct = await check_ton_proof(
        payload=payload_dao.payload,
        user_address=request.address,
        request=request,
    )

    if not is_ton_proof_correct:
        return ErrorResponse(message="Wrong ton proof!")

    account = await account_dal.get_account(user_address=request.address)

    if not account:
        affiliate_address = request.affiliate_address
        account = await account_dal.create_account(
            user_address=request.address, affiliate_address=affiliate_address
        )

    token = sign_jwt(user_id=account.id, user_address=account.address)

    set_token_cookie(
        response=response,
        token=token,
    )

    return TokenResponse(token=token)


async def refresh_jwt_token_endpoint(request: Request):
    bearer_token = request.headers.get("authorization", None)

    if not bearer_token:
        return ErrorResponse(message="No token provided")

    token = bearer_token[7:]

    token = update_token_if_needed(token)

    if not token:
        return ErrorResponse(message="Invalid token")

    return TokenResponse(token=token)
