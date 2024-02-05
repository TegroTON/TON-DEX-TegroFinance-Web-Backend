from pydantic import BaseModel
from src.utils.address import ValidatedAddress


class PayloadRequest(BaseModel):
    pass


class PayloadResponse(BaseModel):
    payload: str


class TonProofDomain(BaseModel):
    length_bytes: int
    value: str


class TonProof(BaseModel):
    timestamp: int
    domain: TonProofDomain
    signature: str
    payload: str
    state_init: str | None = None
    public_key: str | None = None


class AuthWithTonProofRequest(BaseModel):
    affiliate_address: str | None = None
    address: ValidatedAddress
    network: int
    proof: TonProof


class TokenResponse(BaseModel):
    token: str


class ErrorResponse(BaseModel):
    message: str


class RefreshJwtTokenRequest(BaseModel):
    pass
