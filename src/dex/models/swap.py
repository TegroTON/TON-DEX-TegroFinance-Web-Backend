from pydantic import BaseModel

from src.utils.address import ValidatedAddress, ValidatedAddressOrNone


class SwapSimulateRequest(BaseModel):
    offer_address: ValidatedAddress
    ask_address: ValidatedAddress
    units: int
    slippage_tolerance: float
    referral_address: ValidatedAddressOrNone = None


class SwapSimulateResponse(BaseModel):
    ask_address: ValidatedAddress
    ask_units: int
    fee_address: ValidatedAddress
    fee_percent: float
    fee_units: int
    min_ask_units: int
    offer_address: ValidatedAddress
    offer_units: int
    pool_address: ValidatedAddress
    price_impact: float
    router_address: ValidatedAddress
    slippage_tolerance: float
    swap_rate: float
    ton_fee_units: int


class SwapRequest(BaseModel):
    userWalletAddress: ValidatedAddress
    offerJettonAddress: ValidatedAddress
    offerAmount: int
    askJettonAddress: ValidatedAddress
    minAskAmount: int
    forwardGasAmount: int | None = None
    queryId: int | None = None
    referralAddress: ValidatedAddressOrNone = None
