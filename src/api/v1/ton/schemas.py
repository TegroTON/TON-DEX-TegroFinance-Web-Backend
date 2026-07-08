from typing import Dict
from pydantic import BaseModel
from src.utils.address import ValidatedAddress
from src.ton.schemas import TokenInfo


class GetJettonsBalancesRequest(BaseModel):
    wallet_address: ValidatedAddress


class GetJettonsBalancesResponse(BaseModel):
    balances: Dict[ValidatedAddress, int]
    
    
class TokenInfoResponse(BaseModel):
    data: TokenInfo