from fastapi import Depends

from src.config import config
from src.ton.ton_api import get_info_token

from .schemas import TokenInfoResponse


async def get_info_token_endpoint(
    address: str
):
    info_token = await get_info_token(address= address)
    response = TokenInfoResponse(data=info_token)
    return response
